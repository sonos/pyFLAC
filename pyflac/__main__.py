#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC file reader/writer
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import argparse
import os

import soundfile as sf
from pyflac import FileEncoder, FileDecoder


class Encoder:

    def __init__(self, args):
        self.data, sr = sf.read(args.input_file, dtype='int16')
        self.encoder = FileEncoder(
            args.output_file,
            sample_rate=sr,
            blocksize=args.block_size,
            compression_level=args.compression_level,
            verify=args.verify
        )

    def process(self):
        self.encoder.process(self.data)


class Decoder:

    def __init__(self, args):
        self.args = args
        self.output = None
        self.decoder = FileDecoder(
            args.input_file,
            write_callback=self.callback
        )

    def process(self):
        self.decoder.process()

    def callback(self, data, sample_rate, num_channels, num_samples):
        if self.output is None:
            self.output = sf.SoundFile(
                self.args.output_file, mode='w', channels=num_channels,
                samplerate=sample_rate
            )
        self.output.write(data)


def get_args():
    parser = argparse.ArgumentParser(
        description='pyFLAC encoder/decoder',
        epilog='Convert WAV files to FLAC and vice versa'
    )
    parser.add_argument('input_file', help='Input WAV file to encode')
    parser.add_argument('-o', '--output-file', help='Output file')
    parser.add_argument('-c', '--compression-level', type=int, choices=range(0, 9), default=5,
                        help='0 is the fastest compression, 5 is the default, 8 is the highest compression')
    parser.add_argument('-b', '--block-size', type=int, default=0, help='The block size')
    parser.add_argument('-v', '--verify', action='store_false', default=True, help='Verify the compressed data')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    filename, extension = os.path.splitext(args.input_file)
    if extension == '.wav':
        args.output_file = 'output.flac' if args.output_file is None else args.output_file
        Encoder(args).process()
    elif extension == '.flac':
        args.output_file = 'output.wav' if args.output_file is None else args.output_file
        Decoder(args).process()
    else:
        raise ValueError('Please provide either a .wav or a .flac file')


if __name__ == '__main__':
    main()
