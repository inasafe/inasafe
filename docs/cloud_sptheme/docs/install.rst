.. index:: cloud; installation

=========================
Installation Instructions
=========================

Requirements
============
* `Sphinx <http://sphinx.pocoo.org/>`_ 1.0 or newer.

Installing
==========
* To install from source using ``setup.py``::

    python setup.py build
    sudo python setup.py install

* To install using easy_install::

   easy_install cloud_sptheme

* To install using pip::

   pip install cloud_sptheme

Documentation
=============
The latest copy of this documentation should always be available at:
    `<http://packages.python.org/cloud_sptheme>`_

If you wish to generate your own copy of the documentation,
you will need to:

1. install `Sphinx <http://sphinx.pocoo.org/>`_ (1.0 or better)
2. download the :mod:`!cloud_sptheme` source.
3. install :mod:`!cloud_sptheme` itself.
4. from the source directory, run ``python docs/make.py clean html``.
5. Once Sphinx is finished, point a web browser to the file :samp:`{$SOURCE}/docs/_build/html/index.html`.
