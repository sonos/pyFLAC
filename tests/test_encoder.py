# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC encoder test suite
#
#  Copyright (c) 2020-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import pathlib
import tempfile
import unittest

import numpy as np
import soundfile as sf
from pyflac.encoder import _Encoder
from pyflac import (
    StreamEncoder,
    FileEncoder,
    EncoderState,
    EncoderInitException,
)

DEFAULT_CHANNELS = 1
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_BITS_PER_SAMPLE = 16
DEFAULT_BLOCKSIZE = 1024


class TestEncoder(unittest.TestCase):
    """
    Test Suite for the generic encoder class
    """
    def setUp(self):
        self.encoder = _Encoder()

    def test_verify(self):
        """ Test that the verify setter returns the same value from libFLAC """
        self.encoder._verify = True
        self.assertTrue(self.encoder._verify)

    def test_channels(self):
        """ Test that the channels setter returns the same value from libFLAC """
        test_channels = 2
        self.encoder._channels = test_channels
        self.assertEqual(self.encoder._channels, test_channels)

    def test_bits_per_sample(self):
        """ Test that the bits_per_sample setter returns the same value from libFLAC """
        test_bits_per_sample = 24
        self.encoder._bits_per_sample = test_bits_per_sample
        self.assertEqual(self.encoder._bits_per_sample, test_bits_per_sample)

    def test_sample_rate(self):
        """ Test that the sample_rate setter returns the same value from libFLAC """
        test_sample_rate = 48000
        self.encoder._sample_rate = test_sample_rate
        self.assertEqual(self.encoder._sample_rate, test_sample_rate)

    def test_blocksize(self):
        """ Test that the blocksize setter returns the same value from libFLAC """
        test_blocksize = 128
        self.encoder._blocksize = test_blocksize
        self.assertEqual(self.encoder._blocksize, test_blocksize)

    def test_streamable_subset(self):
        """ Test that the streamable_subset setter returns the same value from libFLAC """
        test_streamable_subset = False
        self.encoder._streamable_subset = test_streamable_subset
        self.assertEqual(self.encoder._streamable_subset, test_streamable_subset)

    def test_compression_level(self):
        """ Test that the compression level setter returns the same value from libFLAC """
        test_compression_level = 8
        self.encoder._compression_level = test_compression_level

    def test_limit_min_bitrate(self):
        """ Test that the limit_min_bitrate setter returns the same value from libFLAC """
        self.assertFalse(self.encoder._limit_min_bitrate)
        self.encoder._limit_min_bitrate = True
        self.assertTrue(self.encoder._limit_min_bitrate)

    def test_state(self):
        """ Test that the state returns uninitialised """
        self.assertEqual(self.encoder.state, EncoderState.UNINITIALIZED)
        self.assertEqual(str(self.encoder.state), 'FLAC__STREAM_ENCODER_UNINITIALIZED')

    def test_invalid_process(self):
        """ Test that an error is returned if a numpy array is not provided """
        with self.assertRaises(TypeError):
            self.encoder.process([1, 2, 3, 4])


class TestStreamEncoder(unittest.TestCase):
    """
    Test suite for the stream encoder class
    """
    def setUp(self):
        self.write_callback_called = False
        self.seek_callback_called = False
        self.tell_callback_called = False
        self.metadata_callback_called = False
        self.encoder = None
        self.default_kwargs = {
            'sample_rate': DEFAULT_SAMPLE_RATE,
            'blocksize': DEFAULT_BLOCKSIZE,
            'write_callback': self._write_callback,
            'verify': True,
        }

    def tearDown(self):
        if self.encoder:
            self.encoder.finish()

    def _write_callback(self,
                  buffer: bytes,
                  num_bytes: int,
                  num_samples: int,
                  current_frame: int):
        assert isinstance(buffer, bytes)
        assert isinstance(num_bytes, int)
        assert isinstance(num_samples, int)
        assert isinstance(current_frame, int)
        self.write_callback_called = True

    def _seek_callback(self, offset: int):
        assert isinstance(offset, int)
        self.seek_callback_called = True

    def _tell_callback(self):
        self.tell_callback_called = True
        return 0

    def _metadata_callback(self, metadata):
        self.metadata_callback_called = True

    def test_invalid_sample_rate(self):
        self.default_kwargs['sample_rate'] = 2000000
        self.encoder = StreamEncoder(**self.default_kwargs)
        with self.assertRaisesRegex(EncoderInitException, 'FLAC__STREAM_ENCODER_INIT_STATUS_INVALID_SAMPLE_RATE'):
            self.encoder._init()

    def test_invalid_blocksize(self):
        """ Test than an exception is raised if given an invalid block size """
        self.default_kwargs['blocksize'] = 1000000
        self.encoder = StreamEncoder(**self.default_kwargs)
        with self.assertRaisesRegex(EncoderInitException, 'FLAC__STREAM_ENCODER_INIT_STATUS_INVALID_BLOCK_SIZE'):
            self.encoder._init()

    def test_blocksize_streamable_subset(self):
        """ Test that an exception is raised if blocksize is outside the streamable subset and streamable is unset """
        self.default_kwargs['blocksize'] = 65535
        self.encoder = StreamEncoder(**self.default_kwargs)
        with self.assertRaisesRegex(EncoderInitException, 'FLAC__STREAM_ENCODER_INIT_STATUS_NOT_STREAMABLE'):
            self.encoder._init()

    def test_blocksize_lax(self):
        """ Test that an exception is not raised on large blocks when in lax mode """
        self.default_kwargs['blocksize'] = 65535
        self.default_kwargs['streamable_subset'] = False
        self.encoder = StreamEncoder(**self.default_kwargs)
        self.encoder._init()

    def test_process_mono(self):
        """ Test that an array of int16 mono samples can be processed """
        self.encoder = StreamEncoder(**self.default_kwargs)
        test_samples = np.random.rand(DEFAULT_BLOCKSIZE, 1).astype('int16')
        self.encoder.process(test_samples)
        self.encoder.finish()
        self.assertTrue(self.write_callback_called)

    def test_process_stereo(self):
        """ Test that an array of int16 stereo samples can be processed """
        self.encoder = StreamEncoder(**self.default_kwargs)
        test_samples = np.random.rand(DEFAULT_BLOCKSIZE, 2).astype('int16')
        self.encoder.process(test_samples)
        self.encoder.finish()
        self.assertTrue(self.write_callback_called)

    def test_process_int32(self):
        """ Test that an array of int32 stereo samples can be processed """
        self.encoder = StreamEncoder(**self.default_kwargs)
        test_samples = np.random.rand(DEFAULT_BLOCKSIZE, 2).astype('int32')
        self.encoder.process(test_samples)
        self.encoder.finish()
        self.assertTrue(self.write_callback_called)

    def test_seek_tell(self):
        """ Test that seek and tell callbacks are used """
        self.default_kwargs['seek_callback'] = self._seek_callback
        self.default_kwargs['tell_callback'] = self._tell_callback
        self.encoder = StreamEncoder(**self.default_kwargs)
        test_samples = np.random.rand(DEFAULT_BLOCKSIZE, 1).astype('int16')
        self.encoder.process(test_samples)
        self.encoder.finish()
        self.assertTrue(self.write_callback_called)
        self.assertTrue(self.seek_callback_called)
        self.assertTrue(self.tell_callback_called)

    def test_seek_only(self):
        """ Supplying only one of seek or tell is not allowed """
        self.default_kwargs['seek_callback'] = self._seek_callback
        self.encoder = StreamEncoder(**self.default_kwargs)
        with self.assertRaisesRegex(EncoderInitException, 'FLAC__STREAM_ENCODER_INIT_STATUS_INVALID_CALLBACKS'):
            self.encoder._init()

    def test_metadata(self):
        """ Test that the metadata callback is called """
        self.default_kwargs['metadata_callback'] = self._metadata_callback
        self.encoder = StreamEncoder(**self.default_kwargs)
        test_samples = np.random.rand(DEFAULT_BLOCKSIZE, 1).astype('int16')
        self.encoder.process(test_samples)
        self.encoder.finish()
        self.assertTrue(self.write_callback_called)
        self.assertTrue(self.metadata_callback_called)

class TestFileEncoder(unittest.TestCase):
    """
    Test Suite for the file encoder class.
    """
    def setUp(self):
        self.encoder = None
        self.test_file = pathlib.Path(__file__).parent.absolute() / 'data/mono.wav'
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.flac')
        self.default_kwargs = {
            'input_file': self.test_file,
            'blocksize': DEFAULT_BLOCKSIZE,
            'verify': True
        }

    def test_invalid_blocksize(self):
        """ Test than an exception is raised if given an invalid block size """
        self.default_kwargs['blocksize'] = 1000000
        self.encoder = FileEncoder(**self.default_kwargs)
        with self.assertRaisesRegex(EncoderInitException, 'FLAC__STREAM_ENCODER_INIT_STATUS_INVALID_BLOCK_SIZE'):
            self.encoder._init()

    def test_invalid_dtype(self):
        """ Test than an exception is raised if given an invalid dtype """
        self.default_kwargs['dtype'] = 'int24'
        with self.assertRaisesRegex(ValueError, 'FLAC encoding data type must be either int16 or int32'):
            self.encoder = FileEncoder(**self.default_kwargs)

    def test_blocksize_streamable_subset(self):
        """ Test that an exception is raised if blocksize is outside the streamable subset """
        self.default_kwargs['blocksize'] = 65535
        self.encoder = FileEncoder(**self.default_kwargs)
        with self.assertRaisesRegex(EncoderInitException, 'FLAC__STREAM_ENCODER_INIT_STATUS_NOT_STREAMABLE'):
            self.encoder._init()

    def test_blocksize_lax(self):
        """ Test that an exception is not raised on large blocks when in lax mode """
        self.default_kwargs['blocksize'] = 65535
        self.default_kwargs['streamable_subset'] = False
        self.encoder = FileEncoder(**self.default_kwargs)
        self.encoder._init()

    def test_state(self):
        """ Test that the initial state is ok """
        self.encoder = FileEncoder(**self.default_kwargs)
        self.assertEqual(self.encoder.state, EncoderState.UNINITIALIZED)

    def test_process_mono_file(self):
        """ Test that a mono WAV file can be processed """
        test_path = pathlib.Path(__file__).parent.absolute() / 'data/mono.wav'
        self.default_kwargs['input_file'] = test_path
        self.default_kwargs['output_file'] = pathlib.Path(self.temp_file.name)
        self.encoder = FileEncoder(**self.default_kwargs)
        self.encoder.process()

    def test_process_stereo_file(self):
        """ Test that a stereo WAV file can be processed """
        test_path = pathlib.Path(__file__).parent.absolute() / 'data/stereo.wav'
        self.default_kwargs['input_file'] = test_path
        self.default_kwargs['output_file'] = pathlib.Path(self.temp_file.name)
        self.encoder = FileEncoder(**self.default_kwargs)
        self.encoder.process()

    def test_process_5_1_surround_file(self):
        """ Test that a 5.1 surround WAV file can be processed """
        test_path = pathlib.Path(__file__).parent.absolute() / 'data/surround.wav'
        self.default_kwargs['input_file'] = test_path
        self.default_kwargs['output_file'] = pathlib.Path(self.temp_file.name)
        self.encoder = FileEncoder(**self.default_kwargs)
        self.encoder.process()

    def test_process_32_bit_file(self):
        """ Test that a 32 bit WAV file can be processed """
        test_path = pathlib.Path(__file__).parent.absolute() / 'data/32bit.wav'
        self.default_kwargs['input_file'] = test_path
        self.default_kwargs['output_file'] = pathlib.Path(self.temp_file.name)
        self.default_kwargs['dtype'] = 'int32'
        self.encoder = FileEncoder(**self.default_kwargs)
        self.encoder.process()


if __name__ == '__main__':
    unittest.main(failfast=True)
