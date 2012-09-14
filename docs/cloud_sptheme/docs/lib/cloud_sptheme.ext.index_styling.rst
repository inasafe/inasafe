==========================================================================
:mod:`cloud_sptheme.ext.index_styling` - improves css styling for genindex
==========================================================================

.. module:: cloud_sptheme.ext.index_styling
    :synopsis: adds additional css styling to general index

This sphinx extension intercepts & modifies the general index data
before it is rendered to html; and does the following:

All index entries are wrapped in ``<span>`` elements,
where each element has the format :samp:`<span class="category {type}">`.
:samp:`{type}` in turn is one of ``attribute``, ``method``, ``class``, ``function``, ``module``.
The name of the entry itself is wrapped in an addtional ``<span class="subject">`` element.
Entries which don't fit into one of the above categories are not modified.

The purpose of this class is solely to allow themes (such as the :doc:`/cloud_theme`)
to provide addtional per-type styling for index entries.
