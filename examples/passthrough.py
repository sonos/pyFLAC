#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC passthrough example
#
#  This example reads a WAV file, passes it through the FLAC encoder, and
#  then back through through the FLAC decoder. It also asserts that the
#  uncompressed output is exactly equal to the original signal.
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import argparse
from pathlib import Path
import queue

import numpy as np
import soundfile as sf
import pyflac


class Passthrough:

    def __init__(self, args):
        self.idx = 0
        self.total_bytes = 0
        self.queue = queue.SimpleQueue()
        self.data, self.sr = sf.read(args.input_file, dtype='int16', always_2d=True)

        self.encoder = pyflac.StreamEncoder(
            callback=self.encoder_callback,
            sample_rate=self.sr,
            blocksize=args.block_size,
        )

        self.decoder = pyflac.StreamDecoder(
            callback=self.decoder_callback
        )

    def encode(self):
        self.encoder.process(self.data)
        self.encoder.finish()

    def decode(self):
        while not self.queue.empty():
            self.decoder.process(self.queue.get())
        self.decoder.finish()

    def encoder_callback(self,
                         buffer: bytes,
                         num_bytes: int,
                         num_samples: int,
                         current_frame: int):
        self.total_bytes += num_bytes
        self.queue.put(buffer)

    def decoder_callback(self,
                         data: np.ndarray,
                         sample_rate: int,
                         num_channels: int,
                         num_samples: int):
        assert self.sr == sample_rate
        assert np.array_equal(data, self.data[self.idx:self.idx + num_samples])
        self.idx += num_samples


def main():
    parser = argparse.ArgumentParser(
        description='pyFLAC passthrough example',
        epilog='Pass a WAV file through the FLAC encoder/decoder and verify the output signal'
    )
    parser.add_argument('input_file', type=Path, help='Input WAV file to passthrough')
    parser.add_argument('-c', '--compression-level', type=int, choices=range(0, 9), default=5,
                        help='0 is the fastest compression, 5 is the default, 8 is the highest compression')
    parser.add_argument('-b', '--block-size', type=int, default=0, help='The block size')
    args = parser.parse_args()

    flac = Passthrough(args)
    flac.encode()
    flac.decode()

    print('Verified OK')
    print('Compression ratio = {ratio:.2f}%'.format(
        ratio=flac.total_bytes / flac.data.nbytes * 100
    ))


if __name__ == '__main__':
    main()
