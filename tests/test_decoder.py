# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC decoder test suite
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import os
import pathlib
import tempfile
import time
import unittest

import numpy as np
from pyflac.decoder import _Decoder
from pyflac import (
    FileDecoder,
    StreamDecoder,
    DecoderState,
    DecoderInitException,
    DecoderProcessException
)


class TestDecoder(unittest.TestCase):
    """
    Test Suite for the generic decoder class
    """
    def setUp(self):
        self.decoder = _Decoder()

    def test_state(self):
        """ Test that the state returns a valid string """
        self.assertEqual(self.decoder.state, DecoderState.UNINITIALIZED)
        self.assertEqual(str(self.decoder.state), 'FLAC__STREAM_DECODER_UNINITIALIZED')


class TestStreamDecoder(unittest.TestCase):
    """
    Test suite for the stream decoder class.
    """
    def setUp(self):
        self.decoder = None
        self.callback_called = False
        self.tests_path = pathlib.Path(__file__).parent.absolute()

    def _callback(self, data, rate, channels, samples):
        assert isinstance(data, np.ndarray)
        assert isinstance(rate, int)
        assert isinstance(channels, int)
        assert isinstance(samples, int)
        self.callback_called = True

    def test_process_invalid_data(self):
        """ Test that processing invalid data raises an exception """
        test_data = bytearray(os.urandom(100000))

        with self.assertRaises(DecoderProcessException):
            self.decoder = StreamDecoder(callback=self._callback)
            self.decoder.process(test_data)
            self.decoder.finish()

    def test_process(self):
        """ Test that FLAC data can be decoded """
        test_path = self.tests_path / 'data/stereo.flac'
        with open(test_path, 'rb') as flac:
            test_data = flac.read()

        self.decoder = StreamDecoder(callback=self._callback)
        time.sleep(0.05)

        self.decoder.process(test_data)
        self.decoder.finish()
        self.assertTrue(self.callback_called)

    def test_process_blocks(self):
        """ Test that FLAC data can be decoded in blocks """
        blocksize = 1024
        test_path = self.tests_path / 'data/stereo.flac'
        with open(test_path, 'rb') as flac:
            test_data = flac.read()
            data_length = len(test_data)

        self.decoder = StreamDecoder(callback=self._callback)
        for i in range(0, data_length - blocksize, blocksize):
            self.decoder.process(test_data[i:i + blocksize])

        self.decoder._done = True


class TestFileDecoder(unittest.TestCase):
    """
    Test suite for the file decoder class.
    """
    def setUp(self):
        self.decoder = None
        self.callback_called = False
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav')
        self.default_kwargs = {'input_file': None}

    def test_process_invalid_file(self):
        """ Test that an invalid file raises an error """
        self.default_kwargs['input_file'] = pathlib.Path('invalid.flac')
        with self.assertRaises(DecoderInitException):
            self.decoder = FileDecoder(**self.default_kwargs)

    def test_process_8bit_file(self):
        """ Test that an 8bit file raises an error """
        test_file = pathlib.Path(__file__).parent / 'data/8bit.flac'
        self.default_kwargs['input_file'] = test_file
        with self.assertRaises(DecoderProcessException):
            self.decoder = FileDecoder(**self.default_kwargs)
            self.decoder.process()

    def test_process_mono_file(self):
        """ Test that a mono FLAC file can be processed """
        test_file = pathlib.Path(__file__).parent / 'data/mono.flac'
        self.default_kwargs['input_file'] = test_file
        self.decoder = FileDecoder(**self.default_kwargs)
        self.assertIsNotNone(self.decoder.process())

    def test_process_stereo_file(self):
        """ Test that a stereo FLAC file can be processed """
        test_file = pathlib.Path(__file__).parent / 'data/stereo.flac'
        self.default_kwargs['input_file'] = test_file
        self.decoder = FileDecoder(**self.default_kwargs)
        self.assertIsNotNone(self.decoder.process())

    def test_process_5_1_surround_file(self):
        """ Test that a 5.1 surround FLAC file can be processed """
        test_file = pathlib.Path(__file__).parent / 'data/surround.flac'
        self.default_kwargs['input_file'] = test_file
        self.default_kwargs['output_file'] = pathlib.Path(self.temp_file.name)
        self.decoder = FileDecoder(**self.default_kwargs)
        self.assertIsNotNone(self.decoder.process())


if __name__ == '__main__':
    unittest.main(failfast=True)
