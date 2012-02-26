
============================
Maintining the documentation
============================

The documentation for Risk in a Box is written using ReSTructured text (.rst)
and the Sphinx documenation builder. The best way to learn how to write .rst
is to look at the source of existing documentation - the markup syntax is
very simple. There are a number of useful tags that you can use to make 
your documentation clear and visually interesting, the more commonly used in 
this document are listed below. For a more detailed list, please visit 
the `Spinx Inline Markup page <http://sphinx.pocoo.org/markup/inline.html>`_

A complete list of supported .rst markup is also available `here <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#block-quotes>`_.

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

   