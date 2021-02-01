# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC encoder test suite
#
#  Copyright (c) 2011-2020, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import unittest

from pyflac.encoder import Encoder


class TestEncoder(unittest.TestCase):
    """
    Encoder Test Suite
    """
    def setUp(self):
        self.encoder = Encoder()

    def tearDown(self):
        self.encoder.close()

    def test_channels(self):
        """ Test that the channels setter returns the same value from libFLAC """
        test_channels = 3
        self.encoder.channels = test_channels
        self.assertEqual(self.encoder.channels, test_channels)

    def test_bits_per_sample(self):
        """ Test that the bits_per_sample setter returns the same value from libFLAC """
        test_bits_per_sample = 2
        self.encoder.bits_per_sample = test_bits_per_sample
        self.assertEqual(self.encoder.bits_per_sample, test_bits_per_sample)

    def test_sample_rate(self):
        """ Test that the sample_rate setter returns the same value from libFLAC """
        test_sample_rate = 48000
        self.encoder.sample_rate = test_sample_rate
        self.assertEqual(self.encoder.sample_rate, test_sample_rate)

    def test_blocksize(self):
        """ Test that the blocksize setter returns the same value from libFLAC """
        test_blocksize = 2048
        self.encoder.blocksize = test_blocksize
        self.assertEqual(self.encoder.blocksize, test_blocksize)


if __name__ == '__main__':
    unittest.main()
