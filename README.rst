pyFLAC
======

.. image:: https://github.com/Sonos-Inc/pyFLAC/actions/workflows/lint.yml/badge.svg
    :target: https://github.com/Sonos-Inc/pyFLAC/actions/workflows/lint.yml
.. image:: https://github.com/Sonos-Inc/pyFLAC/actions/workflows/test.yml/badge.svg
    :target: https://github.com/Sonos-Inc/pyFLAC/actions/workflows/test.yml
.. image:: https://github.com/Sonos-Inc/pyFLAC/actions/workflows/build.yml/badge.svg
    :target: https://github.com/Sonos-Inc/pyFLAC/actions/workflows/build.yml


A simple Pythonic interface for `libFLAC <https://xiph.org/flac>`_.

    FLAC stands for Free Lossless Audio Codec, an audio format similar to MP3, but lossless,
    meaning that audio is compressed in FLAC without any loss in quality. This is similar to
    how Zip works, except with FLAC you will get much better compression because it is designed
    specifically for audio.

pyFLAC allows you to encode and decode raw audio data directly to/from a file, or in real-time
using callbacks.

Installation
------------

You can use pip to download and install the latest release with a single command. ::

    pip install pyflac

.. note::
    pyFLAC depends on `libsndfile`, which requires an extra install step on Linux distributions.
    See the `SoundFile <https://pysoundfile.readthedocs.io/en/latest/#installation>`_ documentation for more information.


Examples
--------

:download:`passthrough.py <../examples/passthrough.py>`

Read a WAV file and pass the audio through the encoder/decoder for the purposes of illustration. ::

    python passthrough.py


Supported platforms
-------------------

- macOS
- Linux
- RPi Zero/2/3/4
- Windows 7/8/10


CLI
---

pyFLAC comes bundled with a command line tool to quickly convert between WAV and FLAC files.
For more information, print the help info. ::

    pyflac --help
