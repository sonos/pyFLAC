.. image:: https://github.com/sonos/pyFLAC/blob/378f4df189ae43b89f5d1cebd21871501295f0aa/assets/logo-black.png
    :target: https://pyflac.readthedocs.io

.. image:: https://github.com/sonos/pyFLAC/actions/workflows/lint.yml/badge.svg
    :target: https://github.com/sonos/pyFLAC/actions/workflows/lint.yml
.. image:: https://github.com/sonos/pyFLAC/actions/workflows/test.yml/badge.svg
    :target: https://github.com/sonos/pyFLAC/actions/workflows/test.yml
.. image:: https://github.com/sonos/pyFLAC/actions/workflows/build.yml/badge.svg
    :target: https://github.com/sonos/pyFLAC/actions/workflows/build.yml
.. image:: https://coveralls.io/repos/github/sonos/pyFLAC/badge.svg
    :target: https://coveralls.io/github/sonos/pyFLAC
.. image:: https://readthedocs.org/projects/pyflac/badge
    :target: https://pyflac.readthedocs.io/en/latest/
.. image:: https://badge.fury.io/py/pyFLAC.svg
    :target: https://badge.fury.io/py/pyFLAC
.. image:: https://img.shields.io/pypi/pyversions/pyFLAC
    :target: https://pypi.org/project/pyFLAC

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

    pip3 install pyflac

.. note::
    pyFLAC depends on `libsndfile`, which requires an extra install step on Linux distributions.
    See the `SoundFile <https://pysoundfile.readthedocs.io/en/latest/#installation>`_ documentation for more information.


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

.. note::
    If you didn't install pyFLAC globally then the command line tool will not be installed on your PATH.
    However you should still be able to access the tool with `python3 -m pyflac`.
