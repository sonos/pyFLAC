# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import os
import re
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

vstr = read('pyflac/__init__.py')
regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
version = re.search(regex, vstr, re.M)
__version__ = version.group(1)

setup(
    name='pyFLAC',
    version=__version__,
    description='A Python wrapper for libFLAC',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    author='Sonos, Inc',
    author_email='joe.todd@sonos.com',
    license='Apache License 2.0',
    url='http://pyflac.readthedocs.io/en/latest/',
    download_url='https://github.com/sonos/pyFLAC/archive/' + __version__ + '.tar.gz',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['cffi>=1.4.0'],
    cffi_modules=[
        'pyflac/builder/encoder.py:ffibuilder',
        'pyflac/builder/decoder.py:ffibuilder'
    ],
    install_requires=[
        'cffi>=1.4.0',
        'numpy; python_version >= "3.7.0"',
        'numpy<=1.19.5; python_version < "3.7.0"',
        'SoundFile>=0.8.0',
    ],
    test_suite='tests',
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'pyflac = pyflac.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Multimedia :: Sound/Audio',
    ],
)
