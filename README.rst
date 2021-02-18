pyFLAC
======

[![lint](https://github.com/Sonos-Inc/pyFLAC/workflows/lint/badge.svg)](https://github.com/Sonos-Inc/pyFLAC/actions?query=workflow%3Alint)
[![tests](https://github.com/Sonos-Inc/pyFLAC/workflows/tests/badge.svg)](https://github.com/Sonos-Inc/pyFLAC/actions?query=workflow%3Atests)

A Python wrapper around libFLAC


Compiling FLAC
--------------

Download a release from https://xiph.org/flac/download.html

```
CC=clang ./configure --with-ogg=no
make
make install
```
