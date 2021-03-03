Contributing
------------

If you find any bugs or other things that need improvement,
or would like to add additional features, please create an issue or a pull request at
https://github.com/sonos/pyFLAC
Contributions are always welcome!

You get started, grab the latest version of the code from GitHub::

   git clone https://github.com/sonos/pyFLAC.git
   cd pyflac

To build the package for development::

   python3 pyflac/builder/encoder.py

   python3 pyflac/builder/decoder.py

you can also install your local copy with pip::

   pip3 install .

Before submitting a pull request, make sure all tests are passing and the
test coverage has not been decreased.

Testing
-------

To run the test suite::

   tox -r

Documentation
-------------

If you make changes to the documentation, you can locally re-create the HTML
pages using Sphinx_.
You can install it and the read the docs theme with::

   pip3 install -r docs/requirements.txt

To create the HTML pages, use::

   python3 setup.py build_sphinx

The generated files will be available in the directory ``docs/_build/html``.

.. _Sphinx: http://sphinx-doc.org/
