Contributing
------------

To install the package for development, first build the encoder/decoder libraries using CFFI.

   python3 pyflac/builder/encoder.py

   python3 pyflac/builder/decoder.py

and then install with pip.

   pip3 install .

Before submitting a pull request, make sure all tests are passing,
and all of the example scripts run as they as should.

If you make changes to the documentation, you can locally re-create the HTML
pages using Sphinx_.
You can install it and the read the docs theme with::

   pip3 install -r docs/requirements.txt

To create the HTML pages, use::

   python3 setup.py build_sphinx

The generated files will be available in the directory ``docs/_build/html``.

.. _Sphinx: http://sphinx-doc.org/
