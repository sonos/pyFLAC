# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC decoder
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

from collections import deque
from enum import Enum
import logging
from pathlib import Path
import tempfile
import threading
import time
from typing import Callable, Tuple

import numpy as np
import soundfile as sf

from pyflac._decoder import ffi as _ffi
from pyflac._decoder import lib as _lib


# -- State

class DecoderState(Enum):
    """
    The decoder state as a Python enumeration
    """
    SEARCH_FOR_METADATA = _lib.FLAC__STREAM_DECODER_SEARCH_FOR_METADATA
    READ_METADATA = _lib.FLAC__STREAM_DECODER_READ_METADATA
    SEARCH_FOR_FRAME_SYNC = _lib.FLAC__STREAM_DECODER_SEARCH_FOR_FRAME_SYNC
    READ_FRAME = _lib.FLAC__STREAM_DECODER_READ_FRAME
    END_OF_STREAM = _lib.FLAC__STREAM_DECODER_END_OF_STREAM
    OGG_ERROR = _lib.FLAC__STREAM_DECODER_OGG_ERROR
    SEEK_ERROR = _lib.FLAC__STREAM_DECODER_SEEK_ERROR
    ABORTED = _lib.FLAC__STREAM_DECODER_ABORTED
    MEMORY_ALLOCATION_ERROR = _lib.FLAC__STREAM_DECODER_MEMORY_ALLOCATION_ERROR
    UNINITIALIZED = _lib.FLAC__STREAM_DECODER_UNINITIALIZED

    def __str__(self):
        return _ffi.string(_lib.FLAC__StreamDecoderStateString[self.value]).decode()


# -- Exceptions

class DecoderInitException(Exception):
    """
    An exception raised if initialisation fails for a
    `StreamDecoder` or a `FileDecoder`.
    """
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return _ffi.string(_lib.FLAC__StreamDecoderInitStatusString[self.code]).decode()


class DecoderProcessException(Exception):
    """
    An exception raised if an error occurs during the
    processing of audio data.
    """
    pass


# -- Decoder

class _Decoder:
    """
    A pyFLAC decoder.

    This generic class handles interaction with libFLAC.
    """
    def __init__(self):
        """
        Create a new libFLAC instance.
        This instance is automatically released when there are no more references to the decoder.
        """
        self._error = None
        self._decoder = _ffi.gc(_lib.FLAC__stream_decoder_new(), _lib.FLAC__stream_decoder_delete)
        self._decoder_handle = _ffi.new_handle(self)
        self.logger = logging.getLogger(__name__)

    def finish(self):
        """
        Finish the decoding process.

        Flushes the decoding buffer, releases resources, resets the decoder
        settings to their defaults, and returns the decoder state to `DecoderState.UNINITIALIZED`.

        A well behaved program should always call this at the end.
        """
        _lib.FLAC__stream_decoder_finish(self._decoder)

    # -- State

    @property
    def state(self) -> DecoderState:
        """
        DecoderState: Property to return the decoder state
        """
        return DecoderState(_lib.FLAC__stream_decoder_get_state(self._decoder))

    # -- Processing

    def process(self):
        raise NotImplementedError


class StreamDecoder(_Decoder):
    """
    A pyFLAC stream decoder converts a stream of FLAC encoded bytes
    back to raw audio data.

    The compressed data is passed in via the `process` method, and
    blocks of raw uncompressed audio is passed back to the user via
    the `callback`.

    Args:
        callback (fn): Function to call when there is uncompressed
            audio data ready, see the example below for more information.

    Examples:
        An example callback which writes the audio data to file
        using SoundFile.

        .. code-block:: python
            :linenos:

            import soundfile as sf

            def callback(self,
                         audio: np.ndarray,
                         sample_rate: int,
                         num_channels: int,
                         num_samples: int):

                # ------------------------------------------------------
                # Note: num_samples is the number of samples per channel
                # ------------------------------------------------------
                if self.output is None:
                    self.output = sf.SoundFile(
                        'output.wav', mode='w', channels=num_channels,
                        samplerate=sample_rate
                    )
                self.output.write(audio)

    Raises:
        DecoderInitException: If initialisation of the decoder fails
    """
    def __init__(self,
                 callback: Callable[[np.ndarray, int, int, int], None]):
        super().__init__()

        self._done = False
        self._buffer = deque()
        self.callback = callback

        rc = _lib.FLAC__stream_decoder_init_stream(
            self._decoder,
            _lib._read_callback,
            _ffi.NULL,
            _ffi.NULL,
            _ffi.NULL,
            _ffi.NULL,
            _lib._write_callback,
            _ffi.NULL,
            _lib._error_callback,
            self._decoder_handle
        )
        if rc != _lib.FLAC__STREAM_DECODER_INIT_STATUS_OK:
            raise DecoderInitException(rc)

        self._thread = threading.Thread(target=self._process)
        self._thread.daemon = True
        self._thread.start()

    # -- Processing

    def _process(self):
        """
        Internal function to instruct the decoder to process until the end of
        the stream. This should be run in a separate thread.
        """
        if not _lib.FLAC__stream_decoder_process_until_end_of_stream(self._decoder):
            self._error = 'A fatal read, write, or memory allocation error occurred'

    def process(self, data: bytes):
        """
        Instruct the decoder to process some data.

        Note: This is a non-blocking function, data is processed in
        a background thread.

        Args:
            data (bytes): Bytes of FLAC data
        """
        self._buffer.append(data)

    def finish(self):
        """
        Finish the decoding process.

        This must be called at the end of the decoding process.

        Flushes the decoding buffer, closes the processing thread, releases resources, resets the decoder
        settings to their defaults, and returns the decoder state to `DecoderState.UNINITIALIZED`.

        Raises:
            DecoderProcessException: if any fatal read, write, or memory allocation
                error occurred.
        """
        # --------------------------------------------------------------
        # Finish processing what's in the buffer if there are no errors
        # --------------------------------------------------------------
        while self._thread.is_alive() and self._error is None and len(self._buffer) > 0:
            time.sleep(0.01)

        # --------------------------------------------------------------
        # Instruct the decoder to finish up and wait until it is done
        # --------------------------------------------------------------
        self._done = True
        super().finish()
        self._thread.join(timeout=3)
        if self._error:
            raise DecoderProcessException(self._error)


class FileDecoder(_Decoder):
    """
    The pyFLAC file decoder reads the encoded audio data directly from a FLAC
    file and writes to a WAV file.

    Args:
        input_file (pathlib.Path): Path to the input FLAC file
        output_file (pathlib.Path): Path to the output WAV file, a temporary
            file will be created if unspecified.

    Raises:
        DecoderInitException: If initialisation of the decoder fails
    """
    def __init__(self,
                 input_file: Path,
                 output_file: Path = None):
        super().__init__()

        self.__output = None
        self.callback = self._callback
        if output_file:
            self.__output_file = output_file
        else:
            output_file = tempfile.NamedTemporaryFile(suffix='.wav')
            self.__output_file = Path(output_file.name)

        c_input_filename = _ffi.new('char[]', str(input_file).encode('utf-8'))
        rc = _lib.FLAC__stream_decoder_init_file(
            self._decoder,
            c_input_filename,
            _lib._write_callback,
            _ffi.NULL,
            _lib._error_callback,
            self._decoder_handle,
        )
        _ffi.release(c_input_filename)
        if rc != _lib.FLAC__STREAM_DECODER_INIT_STATUS_OK:
            raise DecoderInitException(rc)

    def process(self) -> Tuple[np.ndarray, int]:
        """
        Process the audio data from the FLAC file.

        Returns:
            (tuple): A tuple of the decoded numpy audio array, and the sample rate of the audio data.

        Raises:
            DecoderProcessException: if any fatal read, write, or memory allocation
                error occurred (meaning decoding must stop)
        """
        result = _lib.FLAC__stream_decoder_process_until_end_of_stream(self._decoder)
        if self.state != DecoderState.END_OF_STREAM and not result:
            raise DecoderProcessException(str(self.state))

        self.finish()

        if self.__output:
            self.__output.close()
            return sf.read(str(self.__output_file), always_2d=True)

    def _callback(self, data: np.ndarray, sample_rate: int, num_channels: int, num_samples: int):
        """
        Internal callback to write the decoded data to a WAV file.
        """
        if self.__output is None:
            self.__output = sf.SoundFile(
                self.__output_file, mode='w', channels=num_channels,
                samplerate=sample_rate
            )
        self.__output.write(data)


@_ffi.def_extern(error=_lib.FLAC__STREAM_DECODER_READ_STATUS_ABORT)
def _read_callback(_decoder,
                   byte_buffer,
                   num_bytes,
                   client_data):
    """
    Called internally when the decoder needs more input data.

    If an exception is raised here, the abort status is returned.
    """
    decoder = _ffi.from_handle(client_data)
    if decoder._error:
        # ----------------------------------------------------------
        # If an error has been issued via the error callback, then
        # abort the processing of the stream.
        # ----------------------------------------------------------
        return _lib.FLAC__STREAM_DECODER_READ_STATUS_ABORT

    if decoder._done:
        # ----------------------------------------------------------
        # The end of the stream has been instructed by a call to
        # finish.
        # ----------------------------------------------------------
        num_bytes[0] = 0
        return _lib.FLAC__STREAM_DECODER_READ_STATUS_END_OF_STREAM

    maximum_bytes = int(num_bytes[0])
    while len(decoder._buffer) == 0:
        # ----------------------------------------------------------
        # Wait until there is something in the buffer
        # ----------------------------------------------------------
        time.sleep(0.01)

    # --------------------------------------------------------------
    # Ensure only the maximum bytes or less is taken from
    # the thread safe queue.
    # --------------------------------------------------------------
    data = bytes()
    if len(decoder._buffer[0]) <= maximum_bytes:
        data = decoder._buffer.popleft()
        maximum_bytes -= len(data)

    if len(decoder._buffer) > 0 and len(decoder._buffer[0]) > maximum_bytes:
        data += decoder._buffer[0][0:maximum_bytes]
        decoder._buffer[0] = decoder._buffer[0][maximum_bytes:]

    actual_bytes = len(data)
    num_bytes[0] = actual_bytes
    _ffi.memmove(byte_buffer, data, actual_bytes)
    return _lib.FLAC__STREAM_DECODER_READ_STATUS_CONTINUE


@_ffi.def_extern()
def _seek_callback(_decoder,
                   absolute_byte_offset,
                   client_data):
    raise NotImplementedError


@_ffi.def_extern()
def _tell_callback(_decoder,
                   absolute_byte_offset,
                   client_data):
    raise NotImplementedError


@_ffi.def_extern()
def _length_callback(_decoder,
                     stream_length,
                     client_data):
    raise NotImplementedError


@_ffi.def_extern()
def _eof_callback(_decoder,
                  client_data):
    raise NotImplementedError


@_ffi.def_extern(error=_lib.FLAC__STREAM_DECODER_WRITE_STATUS_ABORT)
def _write_callback(_decoder,
                    frame,
                    buffer,
                    client_data):
    """
    Called internally when the decoder has uncompressed
    raw audio data to output.

    If an exception is raised here, the abort status is returned.
    """
    channels = []
    decoder = _ffi.from_handle(client_data)

    # --------------------------------------------------------------
    # Data comes from libFLAC in a 32bit array, where the 16bit
    # audio data sits in the least significant bits.
    # --------------------------------------------------------------
    bytes_per_frame = frame.header.blocksize * np.dtype(np.int32).itemsize

    if frame.header.bits_per_sample != 16:
        raise ValueError('Only int16 data type is supported')

    # --------------------------------------------------------------
    # The buffer contains an array of pointers to decoded channels
    # of data. Each pointer will point to an array of signed samples
    # of length `frame.header.blocksize`.
    #
    # Channels will be ordered according to the FLAC specification.
    # --------------------------------------------------------------
    for ch in range(0, frame.header.channels):
        cbuffer = _ffi.buffer(buffer[ch], bytes_per_frame)
        channels.append(
            np.frombuffer(cbuffer, dtype='int32').astype(np.int16)
        )
    output = np.column_stack(channels)
    decoder.callback(
        output,
        int(frame.header.sample_rate),
        int(frame.header.channels),
        int(frame.header.blocksize)
    )

    return _lib.FLAC__STREAM_DECODER_WRITE_STATUS_CONTINUE


@_ffi.def_extern()
def _metadata_callback(_decoder,
                       metadata,
                       client_data):
    raise NotImplementedError


@_ffi.def_extern()
def _error_callback(_decoder,
                    status,
                    client_data):
    """
    Called whenever an error occurs during decoding.
    """
    decoder = _ffi.from_handle(client_data)
    message = _ffi.string(
        _lib.FLAC__StreamDecoderErrorStatusString[status]).decode()
    decoder.logger.error(f'Error in libFLAC decoder: {message}')
    decoder._error = message
