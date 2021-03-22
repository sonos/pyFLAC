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

import queue
import threading
import time

import pyflac
import sounddevice as sd


class ProcessingThread(threading.Thread):

    def __init__(self, sample_rate):
        super().__init__()
        self.queue = queue.SimpleQueue()
        self.encoder = pyflac.StreamEncoder(write_callback=self.encoder_callback,
                                            sample_rate=sample_rate)

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
                actual_bytes=num_samples * 2,
                num_bytes=num_bytes,
                ratio=num_bytes / (num_samples * 2) * 100
            ))

    def run(self):
        while self.running:
            while not self.queue.empty():
                data = self.queue.get(block=False)
                self.encoder.process(data)
            time.sleep(0.1)
        self.encoder.finish()


class Stream:

    def __init__(self):
        self.stream =  sd.InputStream(dtype='int16', callback=self.audio_callback)
        self.thread = ProcessingThread(int(self.stream.samplerate))

    def start(self):
        self.thread.start()
        self.stream.start()

    def stop(self):
        self.stream.stop()
        self.thread.stop()

    def audio_callback(self, indata, frames, sd_time, status):
        self.thread.queue.put(indata)


try:
    stream = Stream()
    stream.start()
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    stream.stop()
