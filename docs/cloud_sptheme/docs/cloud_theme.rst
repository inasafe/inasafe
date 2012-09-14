.. index:: cloud; sphinx theme

====================
"Cloud" sphinx theme
====================

Features
========
This package provides a theme called "Cloud", used to generate this documentation.
Aside from just being a Sphinx theme, it has a few special features:

*Toggleable sections*
    You can mark sections with ``.. rst-class:: html-toggle``,
    which will make the section default to being collapsed under html,
    with a "show section" toggle link to the right of the title.

*Additional CSS classes*
    It provides a couple of simple styling directives for adding
    variety to long Python library documentation:

    * You can mark tables with ``.. rst-class:: html-plain-table``
      to remove separating lines between rows.

    * You can mark ``<h3>`` sections with ``.. rst-class:: emphasized``
      to provide addition visual dividers between large numbers of sub-sub-sections.

*Navigation enhancements*
    It provides options (``roottarget``, ``logotarget``) which
    allow the table of contents to be a distinct
    from the front page (``index.html``) of the document. This allows
    a master table of contents to be maintained, while still allowing
    the front page to be fully customized to welcome readers.

*Additional styling options*
    It also provides a number of styling options controlling
    small details such as external links, document sizing, etc.
    See below.

    It also uses an adaptive layout to work well on all screen sizes
    from mobile phones to widescreen desktops.

*Google Analytics Integration*
    By enabling two theme options with ``conf.py``, Cloud will
    automatically insert a Google Analytics tracker to the bottom of each
    page, along with a polite link allowing users to set a cookie
    which opts them out.

List of Options
===============
``externalrefs``
    bool flag - whether references should be displayed with an icon.

``externalicon``
    optional image or string to prefix before any external links,
    requires ``externalrefs=true``.

``roottarget``
    sets which page which the title link in the navigation bar should point to.
    defaults to the special value ``"<toc>"``, which uses the table of contents.

``logotarget``
    sets the page which the sidebar logo (if any) should point to.
    defaults to the special value ``<root>``, which just mirrors ``roottarget``.

``docwidth``
    set the maximum document width, so the manual does not stretch
    too far on wide monitors. defaults to ``12in``.

``docheight``
    sets the minimum height of the page body. defaults to ``6in``.

``smallwidth``
    if width of device or browser page falls below this threshold,
    cloud is displayed in "minimal" mode, which hides the sidebar
    and eliminates some decorative margins. this is mainly
    intended to ease viewing on smartphones.
    defaults to ``700px``.

``googleanalytics_id``
    Setting this via ``html_theme_options`` to you GA id (e.g. ``UA-XXXXXXXX-X``)
    will enable a google analytics for all pages in the document.

``googleanalytics_path``
    Setting this allows limiting the tracker to a subpath,
    useful for shared documentation hosting.

.. note::

    An additional mess of undocumented options can be found within the source file:

        ``cloud_sptheme/themes/cloud/theme.conf``

Usage
=====
To use the cloud theme, open your documentation's Sphinx ``conf.py`` file,
make the following changes::

    # import Cloud
    import cloud_sptheme as csp

    # ... some contents omitted ...

    # set the html theme
    html_theme = "cloud"
        # NOTE: there is also a red-colored version named "redcloud"

    # ... some contents omitted ...

    # set the theme path to point to cloud's theme data
    html_theme_path = [csp.get_theme_dir()]

    # [optional] set some of the options listed above...
    html_theme_options = { "roottarget": "index" }

Feature Test / Demonstration
============================
The following demonstrates a few of the features listed above.

When ``externalrefs=true``, external links can be prefixed by an external link icon:

    `<http://www.google.com>`_.

By using the ``.. rst-class:: html-toggle`` flag before a section,
it can be made togglable:

.. rst-class:: html-toggle emphasized

.. _toggle-test-link:

Toggleable Section
------------------
This section is not shown by default.
But if a visitor follows a link to this section or something within it
(such as :ref:`this <toggle-test-link>`), it will automatically be expanded.

Admonition Styles
-----------------
.. note::
    This is a note.

.. warning::

    This is warning.

.. seealso::

    This is a "see also" message.

.. todo::

    This is a todo message.
