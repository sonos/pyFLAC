# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC
#
#  Copyright (c) 2020-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

__title__ = 'pyFLAC'
__version__ = '2.2.0'
__all__ = [
    'StreamEncoder',
    'FileEncoder',
    'EncoderState',
    'EncoderInitException',
    'EncoderProcessException',
    'StreamDecoder',
    'FileDecoder',
    'DecoderState',
    'DecoderInitException',
    'DecoderProcessException'
]

import os
import platform

from cffi import FFI

# ------------------------------------------------------------------------------
# Fix DLL load for Windows
#
# Since there is no rpath equivalent for Windows, we just explicitly load
# the libFLAC DLL here.
# ------------------------------------------------------------------------------
if platform.system() == 'Windows':
    ffi = FFI()
    base_path = os.path.dirname(os.path.abspath(__file__))
    if platform.architecture()[0] == '32bit':
        libflac = ffi.dlopen(os.path.join(base_path, 'libraries', 'windows-i686', 'libFLAC.dll'))
    elif platform.architecture()[0] == '64bit':
        libflac = ffi.dlopen(os.path.join(base_path, 'libraries', 'windows-x86_64', 'libFLAC.dll'))


# flake8: noqa: F401
from .encoder import (
    StreamEncoder,
    FileEncoder,
    EncoderState,
    EncoderInitException,
    EncoderProcessException
)
from .decoder import (
    StreamDecoder,
    FileDecoder,
    DecoderState,
    DecoderInitException,
    DecoderProcessException
)
