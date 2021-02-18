# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC decoder test suite
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import unittest

from pyflac.decoder import Decoder


class TestDecoder(unittest.TestCase):
    """
    Test Suite for the generic decoder class
    """
    def setUp(self):
        self.decoder = Decoder()

    def tearDown(self):
        self.decoder.close()

    def test_state(self):
        """ Test that the state returns a valid string """
        self.assertEqual(self.decoder.state, 'FLAC__STREAM_DECODER_UNINITIALIZED')


if __name__ == '__main__':
    unittest.main(failfast=True)
