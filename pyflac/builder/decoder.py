# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC decoder builder
#
#  Copyright (c) 2011-2020, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import cffi


ffibuilder = cffi.FFI()
ffibuilder.set_source(
    "pyflac._decoder",
    """
    #include <FLAC/format.h>
    #include <FLAC/stream_decoder.h>
    """,
    libraries=['flac']
)
ffibuilder.cdef("""

""")


if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
