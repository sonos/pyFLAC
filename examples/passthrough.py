# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC passthrough example
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import argparse
import queue

import numpy as np
import soundfile as sf
from pyflac import StreamEncoder, StreamDecoder


class Codec:

    def __init__(self, args):
        self.total_bytes = 0
        self.queue = queue.SimpleQueue()
        self.data, self.sr = sf.read(args.input_file, dtype='int16')

        self.encoder = StreamEncoder(
            write_callback=self.encoder_callback,
            sample_rate=self.sr,
            blocksize=args.block_size,
            verify=args.verify
        )

        self.decoder = StreamDecoder(
            read_callback=self.decoder_read_callback,
            write_callback=self.decoder_write_callback
        )

    def process(self):
        self.encoder.process(self.data)
        self.decoder.process()

    def encoder_callback(self,
                         buffer: bytes,
                         num_bytes: int,
                         num_samples: int,
                         current_frame: int):
        self.total_bytes += num_bytes
        self.queue.put({'data': buffer, 'num_bytes': num_bytes})

    def decoder_read_callback(self, buffer: bytearray, max_bytes: int) -> int:
        try:
            data = self.queue.get(block=False)
            buffer[:] = data['data']
            return data['num_bytes']
        except queue.Empty:
            return 0

    def decoder_write_callback(self, data: np.ndarray, frame: dict):
        assert self.sr == frame['sample_rate']


def main():
    parser = argparse.ArgumentParser(
        description='pyFLAC encoder/decoder',
        epilog='Convert WAV files to FLAC and vice versa'
    )
    parser.add_argument('input_file', help='Input WAV file to encode')
    parser.add_argument('-o', '--output-file', help='Output file')
    parser.add_argument('-c', '--compression-level', type=int, choices=range(0, 9),
                        help='0 is the fastest compression, 5 is the default, 8 is the highest compression')
    parser.add_argument('-b', '--block-size', type=int, default=0, help='The block size')
    parser.add_argument('-v', '--verify', action='store_false', default=True, help='Verify the output')
    args = parser.parse_args()

    codec = Codec(args)
    codec.process()


if __name__ == '__main__':
    main()
