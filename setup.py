# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC
#
#  Copyright (c) 2020-2023, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

from setuptools import setup

setup(
    setup_requires=["cffi>=1.4.0"],
    cffi_modules=[
        "pyflac/builder/encoder.py:ffibuilder",
        "pyflac/builder/decoder.py:ffibuilder",
    ],
    install_requires=[
        "cffi>=1.4.0",
        "numpy>=1.22",
        "SoundFile>=0.11",
    ],
)
