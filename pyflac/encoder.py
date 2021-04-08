# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC encoder
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

from enum import Enum
import logging
from pathlib import Path
import tempfile
from typing import Callable

import numpy as np
import soundfile as sf

from pyflac._encoder import ffi as _ffi
from pyflac._encoder import lib as _lib


# -- State

class EncoderState(Enum):
    """
    The encoder state as a Python enumeration
    """
    OK = _lib.FLAC__STREAM_ENCODER_OK
    UNINITIALIZED = _lib.FLAC__STREAM_ENCODER_UNINITIALIZED
    OGG_ERROR = _lib.FLAC__STREAM_ENCODER_OGG_ERROR
    VERIFY_DECODER_ERROR = _lib.FLAC__STREAM_ENCODER_VERIFY_DECODER_ERROR
    VERIFY_MISMATCH_IN_AUDIO_DATA = _lib.FLAC__STREAM_ENCODER_VERIFY_MISMATCH_IN_AUDIO_DATA
    CLIENT_ERROR = _lib.FLAC__STREAM_ENCODER_CLIENT_ERROR
    IO_ERROR = _lib.FLAC__STREAM_ENCODER_IO_ERROR
    FRAMING_ERROR = _lib.FLAC__STREAM_ENCODER_FRAMING_ERROR
    MEMORY_ALLOCATION_ERROR = _lib.FLAC__STREAM_ENCODER_MEMORY_ALLOCATION_ERROR

    def __str__(self):
        return _ffi.string(_lib.FLAC__StreamEncoderStateString[self.value]).decode()


class EncoderInitException(Exception):
    """
    An exception raised if initialisation fails for a
    `StreamEncoder` or a `FileEncoder`.
    """
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return _ffi.string(_lib.FLAC__StreamEncoderInitStatusString[self.code]).decode()


class EncoderProcessException(Exception):
    """
    An exception raised if an error occurs during the
    processing of audio data.
    """
    pass


class _Encoder:
    """
    A pyFLAC Encoder.

    This generic class handles interaction with libFLAC.
    """
    def __init__(self):
        """
        Create a new libFLAC instance.
        This instance is automatically released when there are no more references to the encoder.
        """
        self._initialised = False
        self._encoder = _ffi.gc(_lib.FLAC__stream_encoder_new(), _lib.FLAC__stream_encoder_delete)
        self._encoder_handle = _ffi.new_handle(self)
        self.logger = logging.getLogger(__name__)

    def _init(self):
        raise NotImplementedError

    # -- Processing

    def process(self, samples: np.ndarray):
        """
        Process some samples.

        This method ensures the samples are contiguous in memory and then
        passes a pointer to the numpy array to the FLAC encoder to process.

        On processing the first buffer of samples, the encoder is set up
        for the given amount of channels and data type. This is automatically
        determined from the numpy array.

        Raises:
            TypeError: if a numpy array of samples is not provided
            EncoderProcessException: if an error occurs when processing the samples
        """
        if not isinstance(samples, np.ndarray):
            raise TypeError('Processing only supports numpy arrays')

        if not self._initialised:
            try:
                self._channels = samples.shape[1]
            except IndexError:
                self._channels = 1
            self._bits_per_sample = samples.dtype.itemsize * 8
            self._init()

        samples = np.ascontiguousarray(samples).astype(np.int32)
        samples_ptr = _ffi.from_buffer('int32_t[]', samples)

        result = _lib.FLAC__stream_encoder_process_interleaved(self._encoder, samples_ptr, len(samples))
        _ffi.release(samples_ptr)

        if not result:
            raise EncoderProcessException(str(self.state))

    def finish(self) -> bool:
        """
        Finish the encoding process. This flushes the encoding buffer,
        releases resources, resets the encoder settings to their defaults,
        and returns the encoder state to `EncoderState.UNINITIALIZED`.

        A well behaved program should always call this at the end.

        Returns:
            (bool): `True` if successful, `False` otherwise.
        """
        return _lib.FLAC__stream_encoder_finish(self._encoder)

    # -- State

    @property
    def state(self) -> EncoderState:
        """
        EncoderState: Property to return the encoder state
        """
        return EncoderState(_lib.FLAC__stream_encoder_get_state(self._encoder))

    # -- Getters & Setters

    @property
    def _verify(self) -> bool:
        """
        bool: Property to get/set the encoder verify functionality.
            If set `True`, the encoder will verify its own encoded output
            by feeding it through an internal decoder and comparing
            the original signal against the decoded signal.
        """
        return _lib.FLAC__stream_encoder_get_verify(self._encoder)

    @_verify.setter
    def _verify(self, value: bool):
        _lib.FLAC__stream_encoder_set_verify(self._encoder, bool(value))

    @property
    def _channels(self) -> int:
        """
        int: Property to get/set the number of audio channels to encode.
        """
        return _lib.FLAC__stream_encoder_get_channels(self._encoder)

    @_channels.setter
    def _channels(self, value: int):
        _lib.FLAC__stream_encoder_set_channels(self._encoder, value)

    @property
    def _bits_per_sample(self) -> int:
        """
        int: Property to get/set the resolution of the input to be encoded.
        """
        return _lib.FLAC__stream_encoder_get_bits_per_sample(self._encoder)

    @_bits_per_sample.setter
    def _bits_per_sample(self, value: int):
        _lib.FLAC__stream_encoder_set_bits_per_sample(self._encoder, value)

    @property
    def _sample_rate(self) -> int:
        """
        int: Property to get/set the sample rate (in Hz) of the input to be encoded.
        """
        return _lib.FLAC__stream_encoder_get_sample_rate(self._encoder)

    @_sample_rate.setter
    def _sample_rate(self, value: int):
        _lib.FLAC__stream_encoder_set_sample_rate(self._encoder, value)

    @property
    def _blocksize(self) -> int:
        """
        int: Property to get/set the number of samples to use per frame.
            Use `0` to let the encoder estimate a blocksize - this is usually best.
        """
        return _lib.FLAC__stream_encoder_get_blocksize(self._encoder)

    @_blocksize.setter
    def _blocksize(self, value: int):
        _lib.FLAC__stream_encoder_set_blocksize(self._encoder, value)

    @property
    def _compression_level(self) -> int:
        raise NotImplementedError

    @_compression_level.setter
    def _compression_level(self, value: int):
        _lib.FLAC__stream_encoder_set_compression_level(self._encoder, value)


class StreamEncoder(_Encoder):
    """
    The pyFLAC stream encoder is used for real-time compression of
    raw audio data.

    Raw audio data is passed in via the `process` method, and chunks
    of compressed data is passed back to the user via the `callback`.

    Args:
        sample_rate (int): The raw audio sample rate (Hz)
        callback (fn): Function to call when there is compressed
            data ready, see the example below for more information.
        compression_level (int): The compression level parameter that
            varies from 0 (fastest) to 8 (slowest). The default setting
            is 5, see https://en.wikipedia.org/wiki/FLAC for more details.
        blocksize (int): The size of the block to be returned in the
            callback. The default is 0 which allows libFLAC to determine
            the best block size.
        verify (bool): If `True`, the encoder will verify its own
            encoded output by feeding it through an internal decoder and
            comparing the original signal against the decoded signal.
            If a mismatch occurs, the `process` method will raise a
            `EncoderProcessException`.  Note that this will slow the
            encoding process by the extra time required for decoding and comparison.

    Examples:
        An example callback which adds the encoded data to a queue for
        later processing.

        .. code-block:: python
            :linenos:

            def callback(self,
                         buffer: bytes,
                         num_bytes: int,
                         num_samples: int,
                         current_frame: int):
                if num_samples == 0:
                    # If there are no samples in the encoded data, this is
                    # a FLAC header. The header data will arrive in several
                    # different callbacks. Otherwise `num_samples` will be
                    # the block size value.
                    pass

                self.queue.append(buffer)
                self.total_bytes += num_bytes

    Raises:
        ValueError: If any invalid values are passed in to the constructor.
    """
    def __init__(self,
                 sample_rate: int,
                 callback: Callable[[bytes, int, int, int], None],
                 compression_level: int = 5,
                 blocksize: int = 0,
                 verify: bool = False):
        super().__init__()

        self.callback = callback

        self._sample_rate = sample_rate
        self._blocksize = blocksize
        self._compression_level = compression_level
        self._verify = verify

    def _init(self):
        rc = _lib.FLAC__stream_encoder_init_stream(
            self._encoder,
            _lib._write_callback,
            _ffi.NULL,
            _ffi.NULL,
            _ffi.NULL,
            self._encoder_handle
        )
        if rc != _lib.FLAC__STREAM_ENCODER_INIT_STATUS_OK:
            raise EncoderInitException(rc)

        self._initialised = True


class FileEncoder(_Encoder):
    """
    The pyFLAC file encoder reads the raw audio data from the WAV file and
    writes the encoded audio data to a FLAC file.

    Args:
        input_file (pathlib.Path): Path to the input WAV file
        output_file (pathlib.Path): Path to the output FLAC file, a temporary
            file will be created if unspecified.
        compression_level (int): The compression level parameter that
            varies from 0 (fastest) to 8 (slowest). The default setting
            is 5, see https://en.wikipedia.org/wiki/FLAC for more details.
        blocksize (int): The size of the block to be returned in the
            callback. The default is 0 which allows libFLAC to determine
            the best block size.
        verify (bool): If `True`, the encoder will verify its own
            encoded output by feeding it through an internal decoder and
            comparing the original signal against the decoded signal.
            If a mismatch occurs, the `process` method will raise a
            `EncoderProcessException`.  Note that this will slow the
            encoding process by the extra time required for decoding and comparison.

    Raises:
        ValueError: If any invalid values are passed in to the constructor.
    """
    def __init__(self,
                 input_file: Path,
                 output_file: Path = None,
                 compression_level: int = 5,
                 blocksize: int = 0,
                 verify: bool = False):
        super().__init__()

        self.__raw_audio, sample_rate = sf.read(str(input_file), dtype='int16')
        if output_file:
            self.__output_file = output_file
        else:
            output_file = tempfile.NamedTemporaryFile(suffix='.flac')
            self.__output_file = Path(output_file.name)

        self._sample_rate = sample_rate
        self._blocksize = blocksize
        self._compression_level = compression_level
        self._verify = verify

    def _init(self):
        """
        Initialise the encoder to write to a file.

        Raises:
            EncoderInitException: if initialisation fails.
        """
        c_output_filename = _ffi.new('char[]', str(self.__output_file).encode('utf-8'))
        rc = _lib.FLAC__stream_encoder_init_file(
            self._encoder,
            c_output_filename,
            _lib._progress_callback,
            self._encoder_handle,
        )
        _ffi.release(c_output_filename)
        if rc != _lib.FLAC__STREAM_ENCODER_INIT_STATUS_OK:
            raise EncoderInitException(rc)

        self._initialised = True

    def process(self) -> bytes:
        """
        Process the audio data from the WAV file.

        Returns:
            (bytes): The FLAC encoded bytes.

        Raises:
            EncoderProcessException: if an error occurs when processing the samples
        """
        super().process(self.__raw_audio)
        self.finish()
        with open(self.__output_file, 'rb') as f:
            return f.read()


@_ffi.def_extern(error=_lib.FLAC__STREAM_ENCODER_WRITE_STATUS_FATAL_ERROR)
def _write_callback(_encoder,
                    byte_buffer,
                    num_bytes,
                    num_samples,
                    current_frame,
                    client_data):
    """
    Called internally when the encoder has compressed
    data ready to write.

    If an exception is raised here, the abort status is returned.
    """
    encoder = _ffi.from_handle(client_data)
    buffer = bytes(_ffi.buffer(byte_buffer, num_bytes))
    encoder.callback(
        buffer,
        num_bytes,
        num_samples,
        current_frame
    )
    return _lib.FLAC__STREAM_ENCODER_WRITE_STATUS_OK


@_ffi.def_extern()
def _seek_callback(_encoder,
                   absolute_byte_offset,
                   client_data):
    raise NotImplementedError


@_ffi.def_extern()
def _tell_callback(_encoder,
                   absolute_byte_offset,
                   client_data):
    raise NotImplementedError


@_ffi.def_extern()
def _metadata_callback(_encoder,
                       metadata,
                       client_data):
    """
    Called once at the end of encoding with the populated
    STREAMINFO structure. This is so the client can seek back
    to the beginning of the file and write the STREAMINFO block
    with the correct statistics after encoding (like minimum/maximum
    frame size and total samples).
    """
    raise NotImplementedError


@_ffi.def_extern()
def _progress_callback(_encoder,
                       bytes_written,
                       samples_written,
                       frames_written,
                       total_frames_estimate,
                       client_data):
    encoder = _ffi.from_handle(client_data)
    encoder.logger.debug(f'{frames_written} frames written')
