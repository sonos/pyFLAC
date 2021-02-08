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
        message = _ffi.string(_lib.FLAC__StreamDecoderInitStatusString[code])
        super().__init__(message.decode())


class DecoderErrorException(Exception):
    """

    """
    def __init__(self, code):
        message = _ffi.string(_lib.FLAC__StreamDecoderErrorStatusString[code])
        super().__init__(message.decode())


class DecoderProcessException(Exception):
    """
    An exception raised if an error occurs during the
    processing of audio data.
    """
    pass


class Decoder:
    """
    A pyFLAC decoder.

    """
    def __init__(self):
        self._decoder = _lib.FLAC__stream_decoder_new()
        self._decoder_handle = _ffi.new_handle(self)

    def __del__(self):
        self.close()

    def close(self):
        """
        Frees memory used by the decoder.

        This should be explictly called at the end of the program to
        ensure there are no memory leaks.
        """
        if self._decoder:
            _lib.FLAC__stream_decoder_delete(self._decoder)
            self._decoder = None
            self._decoder_handle = None

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

        """
        if not _lib.FLAC__stream_decoder_process_until_end_of_stream(self._decoder):
            raise DecoderProcessException(self.state)

    def process_single(self):
        """

        """
        if not _lib.FLAC__stream_decoder_process_single(self._decoder):
            raise DecoderProcessException(self.state)


class StreamDecoder(Decoder):
    """
    A pyFLAC Stream Decoder.
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


class FileDecoder(Decoder):
    """
    A pyFLAC File Decoder.
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

    data = bytearray(int(num_bytes[0]))
    actual_bytes = decoder.read_callback(data)

    num_bytes[0] = actual_bytes
    _ffi.memmove(byte_buffer, data, actual_bytes)

    if actual_bytes == 0:
        return _lib.FLAC__STREAM_DECODER_READ_STATUS_END_OF_STREAM
    else:
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

    """
    decoder = _ffi.from_handle(client_data)

    channels = []
    bytes_per_frame = frame.header.blocksize * np.dtype(np.int32).itemsize

    if frame.header.bits_per_sample != 16:
        raise ValueError

    for ch in range(0, frame.header.channels):
        channels.append(
            np.frombuffer(_ffi.buffer(buffer[ch], bytes_per_frame), dtype='int32').astype(np.int16)
        )
    output = np.column_stack(channels)

    decoder.write_callback(
        output,
        frame,
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

    """
    logger = logging.getLogger(__name__)
    logger.error(f'decoder error: {status}')

    raise DecoderErrorException(status)
