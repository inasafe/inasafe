==================================================================================================
:mod:`cloud_sptheme.ext.escaped_samp_literals` - permits escaped bracket characters in *samp* role
==================================================================================================

.. module:: cloud_sptheme.ext.escaped_samp_literals
    :synopsis: support escaped bracket characters in SAMP role

This extension modifies how ``:samp:`` literals are parsed, replacing
the default Sphinx parser with an alternate one that allows embedding
literal ``{`` and ``}`` characters within the content, as well as validating
the input more strictly. To embed a literal ``{``, just use a double-backslash, e.g::

    :samp:`this is a {variable}, these are a literal \\{ and \\}`

... and it will be rendered as:

    :samp:`this is a {variable}, these are a literal \\{ and \\}`

.. note::

    This feature has been submitted to the Sphinx
    `issue tracker <http://bitbucket.org/birkenfeld/sphinx/issue/789/samp-text-role-lacks-ability-to-escape>`_.
    When and if the patch is accepted, or an alternative is added to Sphinx,
    this extension will be disabled, deprecated, and eventually removed.
