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
import time
import threading
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

    def finish(self) -> bool:
        """
        Finish the decoding process.

        Flushes the decoding buffer, releases resources, resets the decoder
        settings to their defaults, and returns the decoder state to `DecoderState.UNINITIALIZED`.

        A well behaved program should always call this at the end.
        """
        return _lib.FLAC__stream_decoder_finish(self._decoder)

    # -- State

    @property
    def state(self) -> DecoderState:
        """
        DecoderState: Property to return the decoder state
        """
        return DecoderState(_lib.FLAC__stream_decoder_get_state(self._decoder))

    # -- Processing

    def process(self, data: bytes):
        """
        Instruct the decoder to process data until the read callback signifies
        the end of the stream.

        Note: This will block until the end of the stream, i.e, the read callback
        returns `None`, or if the read callback raises an exception.

        Raises:
            DecoderProcessException: if any fatal read, write, or memory allocation
                error occurred (meaning decoding must stop)
        """
        self._buffer.append(data)


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

        self.thread = threading.Thread(target=self._process)
        self.thread.start()

    def _process(self):
        result = _lib.FLAC__stream_decoder_process_until_end_of_stream(self._decoder)
        if self.state != DecoderState.END_OF_STREAM and not result:
            raise DecoderProcessException(str(self.state))

    def finish(self):
        while len(self._buffer) > 0:
            time.sleep(0.01)
        self._buffer.append(bytearray([]))
        super().finish()


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

        while self.state != DecoderState.END_OF_STREAM:
            time.sleep(0.01)
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
def _read_callback(decoder,
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

    maximum_bytes = int(num_bytes[0])
    while len(decoder._buffer) == 0:
        # ----------------------------------------------------------
        # Wait until there is something in the buffer
        # ----------------------------------------------------------
        time.sleep(0.1)

    if len(decoder._buffer[0]) == 0:
        num_bytes[0] = 0
        # ----------------------------------------------------------
        # Empty data in the buffer signifies the end of stream
        # ----------------------------------------------------------
        return _lib.FLAC__STREAM_DECODER_READ_STATUS_END_OF_STREAM

    data = bytes()
    if len(decoder._buffer[0]) == maximum_bytes:
        data = decoder._buffer.popleft()
    else:
        # ----------------------------------------------------------
        # Ensure only the maximum bytes or less is taken from
        # the thread safe queue.
        # ----------------------------------------------------------
        if len(decoder._buffer[0]) < maximum_bytes:
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
def _seek_callback(decoder,
                   absolute_byte_offset,
                   client_data):
    raise NotImplementedError


@_ffi.def_extern()
def _tell_callback(decoder,
                   absolute_byte_offset,
                   client_data):
    raise NotImplementedError


@_ffi.def_extern()
def _length_callback(decoder,
                     stream_length,
                     client_data):
    raise NotImplementedError


@_ffi.def_extern()
def _eof_callback(decoder,
                  client_data):
    raise NotImplementedError


@_ffi.def_extern(error=_lib.FLAC__STREAM_DECODER_WRITE_STATUS_ABORT)
def _write_callback(decoder,
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
def _metadata_callback(decoder,
                       metadata,
                       client_data):
    raise NotImplementedError


@_ffi.def_extern()
def _error_callback(decoder,
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
