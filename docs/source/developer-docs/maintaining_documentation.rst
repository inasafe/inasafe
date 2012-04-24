
=============================
Maintaining the documentation
=============================

The documentation for |project_name| is written using ReSTructured text (.rst)
and the Sphinx documenation builder. The best way to learn how to write .rst
is to look at the source of existing documentation - the markup syntax is
very simple. There are a number of useful tags that you can use to make
your documentation clear and visually interesting, the more commonly used in
this document are listed below. For a more detailed list, please visit
the `Spinx Inline Markup page <http://sphinx.pocoo.org/markup/inline.html>`_

A complete list of supported .rst markup is also available
`here <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#block-quotes>`_.

Common tags
...........

Here are some common useful tags::

   Heading
   =======

   SubHeading
   ----------

   Sub subheading
   ..............

   `web link<http://foo.org>`_

   :doc:filename  (rst file without  extension)

   *italics*

   **bold**

   .. note:: Note in a little call out box

   .. todo:: Todo item in a call out box

   .. table:: table title

   ============  ================
     Key         Allowed Values
   ============  ================
   units         m
   units         wet/dry
   units         feet
   ============  ================

   :menuselection:`Plugins --> Manage Plugins`

   :kbd:`Control-x Control-f`

   :guilabel:`Ok Button`


.. _api-documentation-howto-label:

Creating API Documentation
--------------------------

Each class method and function in the code base must include a docstring
explaining its usage and purpose as per the example listed below (taken from
the riab.py setupI18n method)::

        """Setup internationalisation for the plugin.

        See if QGIS wants to override the system locale
        and then see if we can get a valid translation file
        for whatever locale is effectively being used.

        Args:
           thePreferredLocale - optional parameter which if set
           will override any other way of determining locale.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """

There should be a blank line between each paragraph and before the Args option.

Where multiple inputs or outputs are used, a ReSTructured text bullet list
should be used to list them.

.. note:: You can use any ReSTructured text withing the docstring to deliver
   rich markup in the final API documentation outputs.

In order for a new module's documentation to appear in the API docs, the
following steps are required:

* Create a new file in :file:`docs/source/api-docs/<package_name>`
  named after the module. For example, for the gui/riab.py module we would
  create :file:`docs/source/api-docs/gui/riab.rst` (note the .rst extension).
  See below for an example of its contents
* Add the new file to the API docs master index 
  (:file:`docs/source/api-docs/index.rst`).
  The .rst extension is not needed or desired when adding to the index list.
* Regenerate the documentation using the :command:`make docs` command from
  the top level directory in the source tree.
* Add the new .rst file and generated html files to the revision control system.

.. note:: It is probably most expedient to simply copy and rename one of the
   existing API documentation files and replace the python module paths therein.

An example of the contents of a module's API .rst if provided below::

   Module: riab
   ============
   This page contains the documentation for the  InaSAFE code **riab**
   module.

   .. automodule:: gui.riab
      :members:

A couple of things should be noted here:

* Sphinx provides automodule and autoclass directives. We have opted to use
  **automodule** for all API documentation because autoclass requires that
  each class be enumerated and anonymous functions need to be explicitly listed.
* Automodule must point to a fully qualified python module path.
* The **members** directive instructs autodocs to enumerate all classes and
  functions in that module.


Once the new document has been added and the documentation generated, you
should see it appear in the API section of the |project_name| documentation.


.. _documenting-new-features-howto-label:

Documenting new features
------------------------

New features should be well documented and that documentation should be made
available uder the :file:`user-docs` subfolder of the sphinx sources tree.

For example, when the keywords editor dialog feature was introduced, we created
a new sphinx document :file:`docs/sources/user-docs/keywords.rst` which
documents this new feature. Additionally, the help button is set to launch
the help dialog in the context of the new help document e.g.::

   def showHelp(self):
      """Load the help text for the keywords gui"""
      if not self.helpDialog:
         self.helpDialog = RiabHelp(self.iface.mainWindow(), 'keywords')
      self.helpDialog.show()

Where the 'keywords' parameter indicates the user-docs/\*.rst document that
should be opened when the help button is clicked. The general style and
approach used in existing documentation should inform your documentation
process so that all the documentation is constent.
