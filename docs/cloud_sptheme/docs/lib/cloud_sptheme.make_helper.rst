====================================================================
:mod:`cloud_sptheme.make_helper` - sphinx-build Makefile replacement
====================================================================

.. module:: cloud_sptheme.make_helper
    :synopsis: sphinx-build Makefile replacement

This module was written to solve one specific task:
to provide an alternative to the ``Makefile`` and ``make.bat`` scripts
found in many Sphinx projects. Most sphinx projects rely on the presence
of :command:`make`, do not frequently need documentation built on windows,
and don't find the need to update the makefile once set up. However,
for the small subset of projects this doesn't include, this class
provides an easy pure-python way to make a cross-platform build script.

Usage
=====
In order to use this script, go to your documentation's source directory,
and include the following fragment as the file ``make.py``::

    "Makefile for Sphinx documentation, adapted to python"
    import os
    from cloud_sptheme.make_helper import SphinxMaker
    if __name__ == "__main__":
        SphinxMaker.execute(root_dir=os.path.join(__file__,os.pardir))

Once done, this script can be invoked via :samp:`python docs/make.py {options}`,
in the same manner as the Sphinx Makefile and make.bat script.

Any new features added to SphinxMaker via cloud_sptheme will automatically become
available to all packages using this stub.

Interface
=========

.. class:: SphinxMaker(root_dir=None)

    :param root_dir:
        absolute path pointing to documentation source directory.

    The following are class attributes, but they may be
    overridden via subclass, constructor, or environment variable
    (in increasing order of precedence).

    .. attribute:: BUILD

        the build directory. this defaults to ``_build``,

    .. attribute:: SPHINXBUILD

        path to sphinx-build script, defaults to ``sphinx-build``.

    .. attribute:: PAPER

        paper size for latex, defaults to ``letter``.

    .. attribute:: SERVEHTML_PORT

        port for ``servehtml`` to launch a webserver on, defaults to 8000.

.. todo::

    SphinxMaker does not currently include all the build targets that sphinx-quickstart's Makefile contains,
    this should be fixed.

    SphinxMaker may currently contain some assumptions which don't apply to some sphinx project layouts,
    these should be identified and made configurable.
