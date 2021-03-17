# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC decoder
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

from enum import Enum
import logging
from pathlib import Path
import tempfile
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

    def process(self):
        """
        Instruct the decoder to process data until the read callback signifies
        the end of the stream.

        Note: This will block until the end of the stream, i.e, the read callback
        returns `None`, or if the read callback raises an exception.

        Raises:
            DecoderProcessException: if any fatal read, write, or memory allocation
                error occurred (meaning decoding must stop)
        """
        result = _lib.FLAC__stream_decoder_process_until_end_of_stream(self._decoder)
        if self.state != DecoderState.END_OF_STREAM and not result:
            raise DecoderProcessException(str(self.state))

    def process_frame(self):
        """
        Instruct the decoder to process at most one metadata block or audio frame.
        Unless the read callback raises an exception.

        Raises:
            DecoderProcessException: if any fatal read, write, or memory allocation
                error occurred (meaning decoding must stop)
        """
        if not _lib.FLAC__stream_decoder_process_single(self._decoder):
            raise DecoderProcessException(str(self.state))


class StreamDecoder(_Decoder):
    """
    A pyFLAC stream decoder converts a stream of FLAC encoded bytes
    back to raw audio data.

    The compressed data is requested via the `read_callback`, and
    blocks of raw uncompressed audio is passed back to the user via
    the `write_callback`.

    Args:
        read_callback (fn): Function to call when compressed bytes of
            FLAC data are required for processing.
        write_callback (fn): Function to call when there is uncompressed
            audio data ready, see the example below for more information.

    Examples:
        An example read callback returns bytes of compressed data to the
        decoder

        .. code-block:: python
            :linenos:

            def read_callback(self, num_bytes: int) -> bytes:
                data = self.data[self.idx:self.idx + num_bytes]
                self.idx += num_bytes
                return data

        An example write callback which writes the audio data to file
        using SoundFile.

        .. code-block:: python
            :linenos:

            import soundfile as sf

            def write_callback(self,
                               audio: np.ndarray,
                               sample_rate: int,
                               num_channels: int,
                               num_samples: int):

                # Note: num_samples is the number of samples per channel
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
                 read_callback: Callable[[int], bytearray],
                 write_callback: Callable[[np.ndarray, int, int, int], None]):
        super().__init__()

        self.excess = bytes()
        self.read_callback = read_callback
        self.write_callback = write_callback

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
        self.write_callback = self._write_callback
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
        super().process()
        while self.state != DecoderState.END_OF_STREAM:
            time.sleep(0.1)
        self.finish()

        if self.__output:
            self.__output.close()
            return sf.read(str(self.__output_file), always_2d=True)

    def _write_callback(self, data: np.ndarray, sample_rate: int, num_channels: int, num_samples: int):
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
    if decoder.excess:
        # ----------------------------------------------------------
        # Too many bytes were supplied in a previous callback, so
        # pass them to the decoder here before requesting more.
        # ----------------------------------------------------------
        data = decoder.excess[:maximum_bytes]
        decoder.excess = decoder.excess[maximum_bytes:]
    else:
        data = decoder.read_callback(maximum_bytes)

    if data:
        # ----------------------------------------------------------
        # If too much data has been provided, store it to process
        # in the next callback.
        # ----------------------------------------------------------
        actual_bytes = len(data)
        if actual_bytes > maximum_bytes:
            decoder.excess += data[maximum_bytes:]
            data = data[:maximum_bytes]
            actual_bytes = len(data)

        # ----------------------------------------------------------
        # Set the actual number of bytes provided by the user,
        # and move the data in to the byte buffer.
        # ----------------------------------------------------------
        num_bytes[0] = actual_bytes
        _ffi.memmove(byte_buffer, data, actual_bytes)
        return _lib.FLAC__STREAM_DECODER_READ_STATUS_CONTINUE
    else:
        num_bytes[0] = 0
        return _lib.FLAC__STREAM_DECODER_READ_STATUS_END_OF_STREAM


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
    decoder = _ffi.from_handle(client_data)

    channels = []
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
    decoder.write_callback(
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
    decoder.logger.error(f'decoder error: {message}')
    decoder._error = message
