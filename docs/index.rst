.. default-role:: py:obj

.. include:: ../README.rst

.. only:: html


Encoder
=======

To encode raw audio data with pyFLAC you can either write encoded
data directly to a file or process in real-time.

.. autoclass:: pyflac.FileEncoder
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: pyflac.StreamEncoder
   :members:
   :undoc-members:
   :inherited-members:

Decoder
=======

.. autoclass:: pyflac.FileDecoder
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: pyflac.StreamDecoder
   :members:
   :undoc-members:
   :inherited-members:

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
