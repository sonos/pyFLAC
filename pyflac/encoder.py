# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC encoder
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import logging
import numpy as np

from pyflac._encoder import ffi as _ffi
from pyflac._encoder import lib as _lib

from .exceptions import EncoderInitException


class Encoder:
    """
    A pyFLAC Encoder.

    """
    def __init__(self):
        self._encoder = _lib.FLAC__stream_encoder_new()
        self._encoder_handle = _ffi.new_handle(self)

    def __del__(self):
        self.close()

    def close(self):
        """
        Frees memory used by the encoder.

        This should be explictly called at the end of the program to
        ensure there are no memory leaks.
        """
        if self._encoder:
            _lib.FLAC__stream_encoder_delete(self._encoder)
            self._encoder = None
            self._encoder_handle = None

    # -- Processing

    def process(self, samples: np.ndarray) -> bool:
        """
        Process some samples.

        This method ensures the samples are contiguous in memory and then
        passes a pointer to the numpy array to the FLAC encoder to process.
        """
        if not isinstance(samples, np.ndarray):
            raise ValueError('Processing only supports numpy arrays')

        if self.channels != samples.shape[1]:
            raise ValueError('Number of channels does not match the configured value')

        if self.bits_per_sample != samples.dtype.itemsize * 8:
            raise ValueError('The number of bits per sample does not match the configured value')

        samples = np.ascontiguousarray(samples)
        samples_ptr = _ffi.from_buffer('int32_t[]', samples)

        if not _lib.FLAC__stream_encoder_process_interleaved(self._encoder, samples_ptr, len(samples)):
            raise RuntimeError(self.state)

    def finish(self) -> bool:
        """
        Finish the encoding process. This flushes the encoding buffer,
        releases resources, resets the encoder settings to their defaults,
        and returns the encoder state to `FLAC__STREAM_ENCODER_UNINITIALIZED`.
        """
        return _lib.FLAC__stream_encoder_finish(self._encoder)

    # -- State

    @property
    def state(self) -> str:
        """
        str: Property to return the encoder state as a human readable string
        """
        c_state = _lib.FLAC__stream_encoder_get_resolved_state_string(self._encoder)
        return _ffi.string(c_state).decode()

    # -- Getters & Setters

    @property
    def verify(self) -> bool:
        """
        bool: Property to get/set the encoder verify functionality.
            If set `True`, the encoder will verify its own encoded output
            by feeding it through an internal decoder and comparing
            the original signal against the decoded signal.
        """
        return _lib.FLAC__stream_encoder_get_verify(self._encoder)

    @verify.setter
    def verify(self, value: bool):
        if not _lib.FLAC__stream_encoder_set_verify(self._encoder, bool(value)):
            raise ValueError(f'Failed to set verify to {value}')

    @property
    def channels(self) -> int:
        """
        int: Property to get/set the number of audio channels to encode.
        """
        return _lib.FLAC__stream_encoder_get_channels(self._encoder)

    @channels.setter
    def channels(self, value: int):
        if not isinstance(value, int):
            raise ValueError('Number of channels must be an integer')

        if not _lib.FLAC__stream_encoder_set_channels(self._encoder, value):
            raise ValueError(f'Failed to set channels to {value}')

    @property
    def bits_per_sample(self) -> int:
        """
        int: Property to get/set the resolution of the input to be encoded.
        """
        return _lib.FLAC__stream_encoder_get_bits_per_sample(self._encoder)

    @bits_per_sample.setter
    def bits_per_sample(self, value: int):
        if not isinstance(value, int):
            raise ValueError('Number of bits per sample must be an integer')

        if not _lib.FLAC__stream_encoder_set_bits_per_sample(self._encoder, value):
            raise ValueError(f'Failed to set bits per sample to {value}')

    @property
    def sample_rate(self) -> int:
        """
        int: Property to get/set the sample rate (in Hz) of the input to be encoded.
        """
        return _lib.FLAC__stream_encoder_get_sample_rate(self._encoder)

    @sample_rate.setter
    def sample_rate(self, value: int):
        if not isinstance(value, int):
            raise ValueError('The sample rate must be an integer in Hz')

        if not _lib.FLAC__stream_encoder_set_sample_rate(self._encoder, value):
            raise ValueError(f'Failed to set sample rate to {value}Hz')

    @property
    def blocksize(self) -> int:
        """
        int: Property to get/set the number of samples to use per frame.
            Use `0` to let the encoder estimate a blocksize - this is usually best.
        """
        return _lib.FLAC__stream_encoder_get_blocksize(self._encoder)

    @blocksize.setter
    def blocksize(self, value: int):
        if not isinstance(value, int):
            raise ValueError('The block size must be an integer')

        if not _lib.FLAC__stream_encoder_set_blocksize(self._encoder, value):
            raise ValueError(f'Failed to set block size to {value}')

    @property
    def compression_level(self) -> int:
        raise NotImplementedError

    @compression_level.setter
    def compression_level(self, value: int):
        if not isinstance(value, int):
            raise ValueError('The block size must be an integer')

        if not _lib.FLAC__stream_encoder_set_compression_level(self._encoder, value):
            raise ValueError(f'Failed to set block size to {value}')


class StreamEncoder(Encoder):
    """
    A pyFLAC Stream Encoder.
    """
    def __init__(self,
                 callback,
                 channels: int,
                 sample_rate: int,
                 bits_per_sample: int,
                 blocksize: int = 0,
                 verify: bool = False):
        super().__init__()

        self.channels = channels
        self.sample_rate = sample_rate
        self.bits_per_sample = bits_per_sample
        self.blocksize = blocksize
        self.verify = verify

        rc = _lib.FLAC__stream_encoder_init_stream(
            self._encoder,
            _lib._write_callback,
            _lib._seek_callback,
            _lib._tell_callback,
            _lib._metadata_callback,
            self._encoder_handle
        )
        if rc != _lib.FLAC__STREAM_ENCODER_INIT_STATUS_OK:
            raise EncoderInitException(rc)


class FileEncoder(Encoder):
    """
    A pyFLAC File Encoder.
    """
    def __init__(self,
                 filename: str,
                 channels: int,
                 sample_rate: int,
                 bits_per_sample: int,
                 blocksize: int = 0,
                 verify: bool = False):
        super().__init__()

        self.channels = channels
        self.sample_rate = sample_rate
        self.bits_per_sample = bits_per_sample
        self.blocksize = blocksize
        self.verify = verify

        c_filename = _ffi.new('char[]', filename.encode('utf-8'))
        rc = _lib.FLAC__stream_encoder_init_file(
            self._encoder,
            c_filename,
            _lib._progress_callback,
            self._encoder_handle,
        )
        if rc != _lib.FLAC__STREAM_ENCODER_INIT_STATUS_OK:
            raise EncoderInitException(rc)


@_ffi.def_extern()
def _read_callback(encoder,
                   byte_buffer,
                   bytes,
                   client_data):
    """
    Called internally when the encoder needs to read back encoded data.
    """
    encoder = _ffi.from_handle(client_data)
    return _lib.FLAC__STREAM_ENCODER_READ_STATUS_CONTINUE


@_ffi.def_extern()
def _write_callback(encoder,
                    byte_buffer,
                    bytes,
                    samples,
                    current_frame,
                    client_data):
    encoder = _ffi.from_handle(client_data)
    return _lib.FLAC__STREAM_ENCODER_WRITE_STATUS_OK


@_ffi.def_extern()
def _seek_callback(encoder,
                   absolute_byte_offset,
                   client_data):
    encoder = _ffi.from_handle(client_data)
    return _lib.FLAC__STREAM_ENCODER_SEEK_STATUS_OK


@_ffi.def_extern()
def _tell_callback(encoder,
                   absolute_byte_offset,
                   client_data):
    encoder = _ffi.from_handle(client_data)
    return _lib.FLAC__STREAM_ENCODER_TELL_STATUS_OK


@_ffi.def_extern()
def _metadata_callback(encoder,
                       metadata,
                       client_data):
    encoder = _ffi.from_handle(client_data)


@_ffi.def_extern()
def _progress_callback(encoder,
                       bytes_written,
                       samples_written,
                       frames_written,
                       total_frames_estimate,
                       client_data):
    logger = logging.getLogger(__name__)
    logger.debug(f'{frames_written} frames written')
