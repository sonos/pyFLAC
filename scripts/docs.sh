#!/bin/sh

cd docs
make html
cd ..
python3 -m http.server --directory docs/_build/html
