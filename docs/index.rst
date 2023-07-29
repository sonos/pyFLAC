.. default-role:: py:obj

.. include:: ../README.rst

.. only:: html

Examples
--------

:download:`passthrough.py <../examples/passthrough.py>`

Read a WAV file and pass the audio through the encoder/decoder for the purposes of illustration. ::

      python3 passthrough.py

This example asserts that the uncompressed data is exactly equal to the original signal.

:download:`stream.py <../examples/stream.py>`

Stream audio from the microphone input and pass through the encoder printing the effectiveness
of the compression to the terminal. ::

      python3 stream.py

.. note::
      This example requires `sounddevice`, which can be installed with pip.
      See the `sounddevice <https://python-sounddevice.readthedocs.io/>`_ documentation for more information.


Limitations
-----------

- pyFLAC only supports 16-bit and 32-bit audio.
- FLAC metadata handling is not implemented.
- The built in libraries do not include OGG support.


API Reference
=============

Encoder
-------

To encode raw audio data with pyFLAC you can either write encoded
data directly to a file or process in real-time.

.. autoclass:: pyflac.FileEncoder
   :members:
   :undoc-members:

.. autoclass:: pyflac.StreamEncoder
   :members:
   :undoc-members:
   :inherited-members:

Decoder
-------

To decode compressed data with pyFLAC you can either read the compressed
data directly from a file or process in real-time.

.. autoclass:: pyflac.FileDecoder
   :members:
   :undoc-members:

.. autoclass:: pyflac.StreamDecoder
   :members:
   :undoc-members:
   :inherited-members:

State
-----

.. autoclass:: pyflac.EncoderState
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: pyflac.DecoderState
   :members:
   :undoc-members:
   :inherited-members:

Exceptions
----------

.. autoclass:: pyflac.EncoderInitException

.. autoclass:: pyflac.EncoderProcessException

.. autoclass:: pyflac.DecoderInitException

.. autoclass:: pyflac.DecoderProcessException


Development
===========

.. only:: html

.. include:: ../CONTRIBUTING.rst

.. include:: ../CHANGELOG.rst

License
=======

pyFLAC is distributed under an Apache 2.0 license allowing users to use the software for any purpose,
to distribute it and to modify it.

pyFLAC includes prebuilt binaries of libFLAC for different architectures, these binaries are distributed
under the following libFLAC license.

.. include:: ../pyflac/libraries/LICENSE
   :literal:

Index
=====

* :ref:`genindex`
