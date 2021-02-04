# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC decoder
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

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


class StreamDecoder(Decoder):
    """
    A pyFLAC Stream Decoder.
    """
    pass


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
            _lib._metadata_callback,
            _lib._error_callback,
            self._decoder_handle,
        )
        if rc != _lib.FLAC__STREAM_DECODER_INIT_STATUS_OK:
            raise DecoderInitException(rc)


@_ffi.def_extern()
def _read_callback(decoder,
                   byte_buffer,
                   bytes,
                   client_data):
    """
    Called internally when the decoder needs more input data.
    """
    decoder = _ffi.from_handle(client_data)
    return _lib.FLAC__STREAM_DECODER_READ_STATUS_CONTINUE
