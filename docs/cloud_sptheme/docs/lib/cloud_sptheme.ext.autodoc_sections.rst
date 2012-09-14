===================================================================================
:mod:`cloud_sptheme.ext.autodoc_sections` - support for ReST sections in docstrings
===================================================================================

.. module:: cloud_sptheme.ext.autodoc_sections
    :synopsis: support for ReST sections in docstrings

This Sphinx extension should be used in conjunction with the Autodoc extension.
This extension allows docstrings (module, class, function, etc) to include
ReST-style headers; which normally cause problems if integrated
into Sphinx documentation via Autodoc.

This extension detects all single-line (not double-lined) headers,
and turned them into a series of definition lists, with the header
name as the term, and the header's content as the definition.

In order to allow additional styling to be added, each definition entry
has two html css styles added: ``nested-section``; and :samp:`nested-section-{level}`,
which allows styling of different indentation levels for each section.
The :doc:`/cloud_theme` natively provides css styling for these classes.

.. warning::

    This extension is currently somewhat fragile,
    it works reliably for the common cases,
    but may not behave properly given unexpected input.
