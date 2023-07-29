#!/bin/sh

rm -rf dist
python3 pyflac/builder/encoder.py
python3 pyflac/builder/decoder.py
python3 setup.py sdist
