pyFLAC
======

.. image:: https://github.com/Sonos-Inc/pyFLAC/workflows/lint/badge.svg
    :target: https://github.com/Sonos-Inc/pyFLAC/actions?query=workflow%2Flint.yml
.. image:: https://github.com/Sonos-Inc/pyFLAC/workflows/tests/badge.svg
    :target: https://github.com/Sonos-Inc/pyFLAC/actions?query=workflow%2Ftests.yml


A simple Pythonic interface for `libFLAC <https://xiph.org/flac>`_.


Compiling FLAC
--------------

Download a release from https://xiph.org/flac/download.html

.. code-block:: bash

    CC=clang ./configure --with-ogg=no
    make
    make install
