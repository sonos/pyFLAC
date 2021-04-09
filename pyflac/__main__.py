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
from pathlib import Path
import os

from pyflac import FileEncoder, FileDecoder


def get_args():
    parser = argparse.ArgumentParser(
        description='pyFLAC encoder/decoder',
        epilog='Convert WAV files to FLAC and vice versa'
    )
    parser.add_argument('input_file', type=Path, help='Input file to encode/decode')
    parser.add_argument('-o', '--output-file', type=Path, help='Output file')
    parser.add_argument('-c', '--compression-level', type=int, choices=range(0, 9), default=5,
                        help='0 is the fastest compression, 5 is the default, 8 is the highest compression')
    parser.add_argument('-b', '--block-size', type=int, default=0, help='The block size')
    parser.add_argument('-v', '--verify', action='store_false', default=True, help='Verify the compressed data')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    with open(args.input_file, 'rb') as f:
        header = f.read(4).decode().upper()

    filename, extension = os.path.splitext(args.input_file)
    if header == 'RIFF':
        args.output_file = f'{filename}.flac' if args.output_file is None else args.output_file
        encoder = FileEncoder(
            input_file=args.input_file,
            output_file=args.output_file,
            blocksize=args.block_size,
            compression_level=args.compression_level,
            verify=args.verify
        )
        encoder.process()
    elif header == 'FLAC':
        args.output_file = f'{filename}.wav' if args.output_file is None else args.output_file
        decoder = FileDecoder(args.input_file, args.output_file)
        decoder.process()
    else:
        raise ValueError('Please provide either a WAV or a FLAC file')


if __name__ == '__main__':
    main()
