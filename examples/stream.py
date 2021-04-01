#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC audio stream example
#
#  This example streams audio from the microphone input, passes it through
#  the FLAC encoder and prints the effectiveness of the data compression.
#
#  Requires sounddevice.
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import argparse
from pathlib import Path
import queue
import threading
import time

import pyflac
import sounddevice as sd
import soundfile as sf


class ProcessingThread(threading.Thread):

    def __init__(self, args, stream):
        super().__init__()
        self.output_file = None
        self.queue = queue.SimpleQueue()
        self.sample_size = stream.samplesize

        self.encoder = pyflac.StreamEncoder(write_callback=self.encoder_callback,
                                            sample_rate=int(stream.samplerate),
                                            compression_level=args.compression_level)

        if args.output_file:
            self.output_file = open(args.output_file, 'wb')

    def start(self):
        self.running = True
        super().start()

    def stop(self):
        self.running = False

    def encoder_callback(self, buffer, num_bytes, num_samples, current_frame):
        if num_samples == 0:
            print('FLAC header')
        else:
            print('Encoded {actual_bytes} bytes in {num_bytes} bytes: {ratio:.2f}%'.format(
                actual_bytes=num_samples * self.sample_size,
                num_bytes=num_bytes,
                ratio=num_bytes / (num_samples * self.sample_size) * 100
            ))

        if self.output_file:
            self.output_file.write(buffer)
            self.output_file.flush()

    def run(self):
        while self.running:
            while not self.queue.empty():
                self.encoder.process(self.queue.get())

        self.encoder.finish()
        if self.output_file:
            print(f'Wrote output to {self.output_file.name}')
            self.output_file.close()


class AudioStream:

    def __init__(self, args):
        self.stream = sd.InputStream(
            dtype='int16',
            channels=1,
            blocksize=args.block_size,
            callback=self.audio_callback
        )
        self.thread = ProcessingThread(args, self.stream)

    def start(self):
        self.thread.start()
        self.stream.start()

    def stop(self):
        self.stream.stop()
        self.thread.stop()

    def audio_callback(self, indata, frames, sd_time, status):
        self.thread.queue.put(indata)


def main():
    parser = argparse.ArgumentParser(
        description='pyFLAC audio stream example',
        epilog='Stream audio data from the microphone and pass it through the pyFLAC encoder'
    )
    parser.add_argument('-o', '--output-file', type=Path, help='Optionally save to output FLAC file')
    parser.add_argument('-c', '--compression-level', type=int, choices=range(0, 9), default=5,
                        help='0 is the fastest compression, 5 is the default, 8 is the highest compression')
    parser.add_argument('-b', '--block-size', type=int, default=0, help='The block size')
    args = parser.parse_args()

    try:
        stream = AudioStream(args)
        stream.start()
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        stream.stop()


if __name__ == '__main__':
    main()