# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC exceptions
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

from pyflac._encoder import lib as _lib
from pyflac._encoder import ffi as _ffi


class EncoderInitException(Exception):

    def __init__(self, code):
        message = _ffi.string(_lib.FLAC__StreamEncoderInitStatusString[code])
        super().__init__(message.decode())
