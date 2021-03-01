# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC decoder
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import logging
from typing import Callable

import numpy as np

from pyflac._decoder import ffi as _ffi
from pyflac._decoder import lib as _lib


class DecoderInitException(Exception):
    """
    An exception raised if initialisation fails for a
    `StreamDecoder` or a `FileDecoder`.
    """
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return _ffi.string(_lib.FLAC__StreamDecoderInitStatusString[self.code]).decode()


class DecoderErrorException(Exception):
    """
    An exception raised if the error callback is called.
    """
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return _ffi.string(_lib.FLAC__StreamDecoderErrorStatusString[self.code]).decode()


class DecoderProcessException(Exception):
    """
    An exception raised if an error occurs during the
    processing of audio data.
    """
    pass


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
        self._decoder = _ffi.gc(_lib.FLAC__stream_decoder_new(), _lib.FLAC__stream_decoder_delete)
        self._decoder_handle = _ffi.new_handle(self)
        self.logger = logging.getLogger(__name__)

    def finish(self) -> bool:
        """
        Finish the decoding process. Flushes the decoding buffer,
        releases resources, resets the decoder settings to their defaults,
        and returns the decoder state to `FLAC__STREAM_DECODER_UNINITIALIZED`.
        """
        return _lib.FLAC__stream_decoder_finish(self._decoder)

    # -- State

    @property
    def state(self) -> str:
        """
        str: Property to return the decoder state as a human readable string
        """
        c_state = _lib.FLAC__stream_decoder_get_resolved_state_string(self._decoder)
        return _ffi.string(c_state).decode()

    # -- Processing

    def process(self):
        """
        Instruct the decoder to process data until the read callback signifies
        the end of the stream.
        """
        if not _lib.FLAC__stream_decoder_process_until_end_of_stream(self._decoder):
            raise DecoderProcessException(self.state)

    def process_single(self):
        """
        Decode one metadata block or audio frame.
        """
        if not _lib.FLAC__stream_decoder_process_single(self._decoder):
            raise DecoderProcessException(self.state)


class StreamDecoder(_Decoder):
    """
    A pyFLAC stream decoder converts a stream of FLAC encoded bytes
    back to raw audio data.

    The compressed data is passed in via the `process` method, and
    blocks of raw uncompressed audio is passed back to the user via
    the `write_callback`.

    Args:
        write_callback (fn): Function to call when there is uncompressed
            audio data ready, see the example below for more information.

    Examples:
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
                 read_callback: Callable[[bytearray], int],
                 write_callback: Callable[[bytearray, int], int]):
        super().__init__()

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
    The pyFLAC file decoder writes the decoded audio data directly to a file.

    Args:
        filename (str): Path to the output FLAC file

    Raises:
        DecoderInitException: If initialisation of the decoder fails
    """
    def __init__(self, filename: str):
        super().__init__()

        c_filename = _ffi.new('char[]', filename.encode('utf-8'))
        rc = _lib.FLAC__stream_decoder_init_file(
            self._decoder,
            c_filename,
            _lib._write_callback,
            _ffi.NULL,
            _lib._error_callback,
            self._decoder_handle,
        )
        _ffi.release(c_filename)
        if rc != _lib.FLAC__STREAM_DECODER_INIT_STATUS_OK:
            raise DecoderInitException(rc)


@_ffi.def_extern()
def _read_callback(decoder,
                   byte_buffer,
                   num_bytes,
                   client_data):
    """
    Called internally when the decoder needs more input data.
    """
    decoder = _ffi.from_handle(client_data)

    maximum_bytes = int(num_bytes[0])
    data = bytearray(maximum_bytes)
    actual_bytes = decoder.read_callback(data, maximum_bytes)

    if actual_bytes > maximum_bytes:
        return _lib.FLAC__STREAM_DECODER_READ_STATUS_ABORT
    elif actual_bytes == 0:
        num_bytes[0] = 0
        return _lib.FLAC__STREAM_DECODER_READ_STATUS_END_OF_STREAM
    elif actual_bytes == -1:
        return _lib.FLAC__STREAM_DECODER_READ_STATUS_ABORT
    else:
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


@_ffi.def_extern()
def _write_callback(decoder,
                    frame,
                    buffer,
                    client_data):
    """
    Called internally when the decoder has uncompressed
    raw audio data to output.
    """
    decoder = _ffi.from_handle(client_data)

    channels = []
    bytes_per_frame = frame.header.blocksize * np.dtype(np.int32).itemsize

    if frame.header.bits_per_sample != 16:
        raise ValueError('Only int16 data type is supported')

    metadata = {
        'block_size': int(frame.header.blocksize),
        'channels': int(frame.header.channels),
        'sample_rate': int(frame.header.sample_rate),
        'bits_per_sample': int(frame.header.bits_per_sample)
    }

    for ch in range(0, frame.header.channels):
        cbuffer = _ffi.buffer(buffer[ch], bytes_per_frame)
        channels.append(
            np.frombuffer(cbuffer, dtype='int32').astype(np.int16)
        )
    output = np.column_stack(channels)
    decoder.write_callback(output, metadata)

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

    raise DecoderErrorException(status)
