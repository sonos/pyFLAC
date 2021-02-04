# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC encoder test suite
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import pathlib
import tempfile
import unittest

import numpy as np
import soundfile as sf
from pyflac.encoder import _Encoder, StreamEncoder, FileEncoder


class TestEncoder(unittest.TestCase):
    """
    Test Suite for the generic encoder class
    """
    def setUp(self):
        self.encoder = _Encoder()

    def tearDown(self):
        self.encoder.close()

    def test_channels(self):
        """ Test that the channels setter returns the same value from libFLAC """
        test_channels = 2
        self.encoder.channels = test_channels
        self.assertEqual(self.encoder.channels, test_channels)

    def test_bits_per_sample(self):
        """ Test that the bits_per_sample setter returns the same value from libFLAC """
        test_bits_per_sample = 24
        self.encoder.bits_per_sample = test_bits_per_sample
        self.assertEqual(self.encoder.bits_per_sample, test_bits_per_sample)

    def test_sample_rate(self):
        """ Test that the sample_rate setter returns the same value from libFLAC """
        test_sample_rate = 48000
        self.encoder.sample_rate = test_sample_rate
        self.assertEqual(self.encoder.sample_rate, test_sample_rate)

    def test_blocksize(self):
        """ Test that the blocksize setter returns the same value from libFLAC """
        test_blocksize = 128
        self.encoder.blocksize = test_blocksize
        self.assertEqual(self.encoder.blocksize, test_blocksize)

    def test_state(self):
        """ Test that the state returns a valid string """
        self.assertEqual(self.encoder.state, 'FLAC__STREAM_ENCODER_UNINITIALIZED')


class TestStreamEncoder(unittest.TestCase):
    """
    Test Suite for the stream encoder class
    """
    CHANNELS = 1
    SAMPLE_RATE = 44100
    BITS_PER_SAMPLE = 16
    BLOCKSIZE = 1024

    def setUp(self):
        self.encoder = StreamEncoder(
            channels=self.CHANNELS,
            sample_rate=self.SAMPLE_RATE,
            bits_per_sample=self.BITS_PER_SAMPLE,
            blocksize=self.BLOCKSIZE,
            callback=self.callback,
        )

    def tearDown(self):
        if self.encoder:
            self.encoder.close()

    def callback(self):
        pass

    def test_process_invalid_channels(self):
        """ Test that an exception is raised if the number of channels does not match """
        test_samples = np.random.rand(self.BLOCKSIZE, 2).astype('int16')
        with self.assertRaises(ValueError):
            self.encoder.process(test_samples)

    def test_process_invalid_bits_per_sample(self):
        """ Test that an exception is raised if the bits per sample do not match """
        test_samples = np.random.rand(self.BLOCKSIZE, self.CHANNELS).astype('float32')
        with self.assertRaises(ValueError):
            self.encoder.process(test_samples)

    def test_process_mono(self):
        """ Test that an array of int16 mono samples can be processed """
        self.encoder.close()
        self.encoder = StreamEncoder(
            channels=1,
            sample_rate=self.SAMPLE_RATE,
            bits_per_sample=self.BITS_PER_SAMPLE,
            blocksize=self.BLOCKSIZE,
            callback=self.callback,
            verify=True
        )
        test_samples = np.random.rand(self.BLOCKSIZE, 1).astype('int16')
        self.encoder.process(test_samples)

    def test_process_stereo(self):
        """ Test that an array of int16 stereo samples can be processed """
        self.encoder.close()
        self.encoder = StreamEncoder(
            channels=2,
            sample_rate=self.SAMPLE_RATE,
            bits_per_sample=self.BITS_PER_SAMPLE,
            blocksize=self.BLOCKSIZE,
            callback=self.callback,
            verify=True
        )
        test_samples = np.random.rand(self.BLOCKSIZE, 2).astype('int16')
        self.encoder.process(test_samples)


class TestFileEncoder(unittest.TestCase):
    """
    Test Suite for the file encoder class.
    """
    CHANNELS = 1
    SAMPLE_RATE = 44100
    BITS_PER_SAMPLE = 16
    BLOCKSIZE = 1024

    def setUp(self):
        self.encoder = None
        self.file = tempfile.NamedTemporaryFile(suffix='.flac')

    def tearDown(self):
        if self.encoder:
            self.encoder.close()

    def test_state(self):
        """ Test that the initial state is ok """
        self.encoder = FileEncoder(
            filename=self.file.name,
            channels=1,
            sample_rate=self.SAMPLE_RATE,
            bits_per_sample=self.BITS_PER_SAMPLE,
            blocksize=self.BLOCKSIZE,
            verify=True
        )
        self.assertEqual(self.encoder.state, 'FLAC__STREAM_ENCODER_OK')

    def test_process_stereo_file(self):
        """ Test that a stereo WAV file can be processed """
        test_path = pathlib.Path(__file__).parent.absolute() / 'data/piano.wav'
        test_samples, sr = sf.read(test_path, dtype='int16')
        self.encoder = FileEncoder(
            filename=self.file.name,
            channels=test_samples.shape[1],
            sample_rate=sr,
            bits_per_sample=test_samples.dtype.itemsize * 8,
            blocksize=0,
            verify=True
        )
        self.encoder.process(test_samples)
        self.encoder.finish()


if __name__ == '__main__':
    unittest.main()
