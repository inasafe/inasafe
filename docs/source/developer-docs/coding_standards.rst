
Coding Standards
================

Code Style
----------

Please observe the following coding standards when working on the codebase:

* Docstrings quoted with :samp:`"""`
* Simple strings in source code should be quoted with :samp:`'`
* Coding must follow a style guide. In case of Python it is
  `pep8 <http://www.python.org/dev/peps/pep-0008>`_ and
  using the command line tool pep8 (or :samp:`make pep8`) to enforce this
* `Python documentation guide <http://www.python.org/dev/peps/pep-0257>`_
* Adherence to regression/unit testing wherever possible (:samp:`make test`)
* Use of github for revision control, issue tracking and management
* Simple deployment procedure - all dependencies must be delivered with
  the plugin installer for QGIS or exist in standard QGIS installs.
* Develop in the spirit of XP/Agile, i.e. frequent releases, continuous
  integration and iterative development. The master branch should always
  be assumed to represent a working demo with all tests passing.
* All strings should be internationalisation enabled. Please see :doc:`i18n`
  for details.
* All code should pass lint validation. You can test this using the make target
  ``make jenkins-lint``. In some cases you may wish to override a line or
  group of lines so that they are not validated by lint. You can do this by
  adding either::

     import foo  # pylint: diable=W1203

  or::

     # pylint: disable=W1234
     print 'hello'
     print 'goodbye'
     # pylint: enable=W1234

  The relevant id (W1234) is provided on the output of the above mentioned lint
  command's output.

* Each source file should include a standard header containing copyright,
  authorship and version metadata as shown in the exampled below.

**Example standard header**::

   """
   InaSAFE Disaster risk assessment tool developed by AusAid -
     **QGIS plugin implementation.**

   Contact : ole.moller.nielsen@gmail.com

   .. note:: This program is free software; you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation; either version 2 of the License, or
        (at your option) any later version.

   """

   __author__ = 'tim@linfiniti.com'
   __version__ = '0.0.1'
   __revision__ = '$Format:%H$'
   __date__ = '10/01/2011'
   __copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
   __copyright__ += 'Disaster Reduction'

.. note:: Please see :ref:`faq-revision-label` for details on how the revision
   tag is replaced with the SHA1 for the file when the release packages are
   made.

.. _hig-label:

Human Interface Guidelines
..........................

For consistency of user experience, the user interfaces created in Risk
in a Box should adhere to the QGIS Human Interface Guidelines (HIG) which
are listed here for your convenience:

+ Group related elements using group boxes:
  Try to identify elements that can be grouped together and then use group
  boxes with a label to identify the topic of that group.  Avoid using group
  boxes with only a single widget / item inside.
+ Capitalise first letter only in labels:
  Labels (and group box labels) should be written as a phrase with leading
  capital letter, and all remaing words written with lower case first letters
+ Do not end labels for widgets or group boxes with a colon:
  Adding a colon causes visual noise and does not impart additional meaning,
  so don't use them. An exception to this rule is when you have two labels next
  to each other e.g.: Label1 [Plugin Path:] Label2 [/path/to/plugins]
+ Keep harmful actions away from harmless ones:
  If you have actions for 'delete', 'remove' etc, try to impose adequate space
  between the harmful action and innocuous actions so that the users is less
  likely to inadvertantly click on the harmful action.
+ Always use a QButtonBox for 'OK', 'Cancel' etc buttons:
  Using a button box will ensure that the order of 'OK' and 'Cancel' etc,
  buttons is consistent with the operating system / locale / desktop
  environment that the user is using.
+ Tabs should not be nested. If you use tabs, follow the style of the
  tabs used in QgsVectorLayerProperties / QgsProjectProperties etc.
  i.e. tabs at top with icons at 22x22.
+ Widget stacks should be avoided if at all possible. They cause problems with
  layouts and inexplicable (to the user) resizing of dialogs to accommodate
  widgets that are not visible.
+ Try to avoid technical terms and rather use a laymans equivalent e.g. use
  the word 'Transparency' rather than 'Alpha Channel' (contrived example),
  'Text' instead of 'String' and so on.
+ Use consistent iconography. If you need an icon or icon elements, please
  contact Robert Szczepanek on the mailing list for assistance.
+ Place long lists of widgets into scroll boxes. No dialog should exceed 580
  pixels in height and 1000 pixels in width.
+ Separate advanced options from basic ones. Novice users should be able to
  quickly access the items needed for basic activities without needing to
  concern themselves with complexity of advanced features. Advanced features
  should either be located below a dividing line, or placed onto a separate tab.
+ Don't add options for the sake of having lots of options. Strive to keep the
  user interface minimalistic and use sensible defaults.
+ If clicking a button will spawn a new dialog, an ellipsis (...) should be
  suffixed to the button text.


Code statistics
...............

* https://www.ohloh.net/p/inasafe/analyses/latest
* https://github.com/AIFDR/inasafe/network
* https://github.com/AIFDR/inasafe/graphs
