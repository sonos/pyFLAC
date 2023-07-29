#!/bin/sh

python3 pyflac/builder/encoder.py
python3 pyflac/builder/decoder.py
pip3 install -e .
