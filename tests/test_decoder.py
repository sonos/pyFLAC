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
import unittest

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

    def tearDown(self):
        if self.decoder:
            self.decoder.finish()

    def _callback(self, data, rate, channels, samples):
        self.callback_called = True

    # def test_read_invalid_data(self):
    #     """ Test that reading invalid data raises an exception """
    #     test_data = bytearray(os.urandom(100000))

    #     with self.assertRaises(DecoderProcessException):
    #         self.decoder = StreamDecoder(callback=self._callback)
    #         self.decoder.process(test_data)

    # def test_read_callback_exception(self):
    #     """ Test that raising an exception in the callback aborts processing """
    #     self.data = bytearray(os.urandom(1000000))
    #     self.data_length = len(self.data)

    #     with self.assertRaises(DecoderProcessException):
    #         self.decoder = StreamDecoder(
    #             read_callback=self._read_callback_with_exception,
    #             write_callback=self._write_callback
    #         )
    #         self.decoder.process_frame()

    # def test_too_much_data(self):
    #     """ Test that passing too much data doesn't actually break anything """
    #     test_path = self.test_path / 'data/stereo.flac'
    #     with open(test_path, 'rb') as flac:
    #         self.data = flac.read()
    #         self.data_length = len(self.data)

    #     self.decoder = StreamDecoder(
    #         read_callback=self._read_too_much_callback,
    #         write_callback=self._write_callback
    #     )
    #     self.decoder.process()
    #     self.assertTrue(self.write_callback_called)

    # def test_end_of_stream(self):
    #     """ Test that when the state reflects the end of stream from the callback """
    #     self.decoder = StreamDecoder(
    #         read_callback=self._read_callback_end_of_stream,
    #         write_callback=self._write_callback
    #     )
    #     self.decoder.process()
    #     self.assertEqual(self.decoder.state, DecoderState.END_OF_STREAM)

    def test_process(self):
        """ Test that FLAC data can be decoded """
        test_path = self.tests_path / 'data/stereo.flac'
        with open(test_path, 'rb') as flac:
            test_data = flac.read()

        self.decoder = StreamDecoder(callback=self._callback)
        self.decoder.process(test_data)


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
