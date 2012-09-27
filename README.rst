========================================================
InaSAFE - Indonesian Scenario Assessment for Emergencies
========================================================

This is the project: InaSAFE a Quantum GIS plugin

For more information about InaSAFE please visit
`www.inasafe.org <http://www.inasafe.org>`_ and look at the documentation at
`inasafe.readthedocs.org <http://inasafe.readthedocs.org>`_

The latest source code is available at
`https://github.com/AIFDR/inasafe <https://github.com/AIFDR/inasafe>`_
which contains modules for risk calculations, gis functionality and functions
for impact modelling.

========================
Quick Installation Guide
========================

To install the |project_name|, use the plugin manager in QGIS::

  Plugins -> Fetch Python Plugins

Then search for '|project_name|', select it and click the install button.
The plugin will now be added to your plugins menu.


System Requirements
-------------------

 - A standard PC with at least 4GB of RAM running Windows, Linux or Mac OS X
 - The Open Source Geographic Information System QGIS (http://www.qgis.org).
   InaSAFE requires QGIS version 1.7 or newer.

===========
Limitations
===========

InaSAFE is a new project. The current code development started in
earnest in January 2012 and there is still much to be done.  However,
we work on the philosophy that stakeholders should have access to the
development and source code from the very beginning and invite
comments, suggestions and contributions.  See
https://github.com/AIFDR/inasafe/issues/milestones and
https://github.com/AIFDR/inasafe/issues?page=1&state=open for known
bugs and outstanding tasks.


=======
License
=======

InaSAFE is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License version 3 (GPLv3) as
published by the Free Software Foundation.

The full GNU General Public License is available in LICENSE.TXT or
http://www.gnu.org/licenses/gpl.html


==============================
Disclaimer of Warranty (GPLv3)
==============================

There is no warranty for the program, to the extent permitted by
applicable law. Except when otherwise stated in writing the copyright
holders and/or other parties provide the program "as is" without warranty
of any kind, either expressed or implied, including, but not limited to,
the implied warranties of merchantability and fitness for a particular
purpose. The entire risk as to the quality and performance of the program
is with you. Should the program prove defective, you assume the cost of
all necessary servicing, repair or correction.


===============================
Limitation of Liability (GPLv3)
===============================

In no event unless required by applicable law or agreed to in writing
will any copyright holder, or any other party who modifies and/or conveys
the program as permitted above, be liable to you for damages, including any
general, special, incidental or consequential damages arising out of the
use or inability to use the program (including but not limited to loss of
data or data being rendered inaccurate or losses sustained by you or third
parties or a failure of the program to operate with any other programs),
even if such holder or other party has been advised of the possibility of
such damages.



=============
Documentation
=============

To generate the current documentation in English, run the command :kbd:`make
html` in the :file:`docs` directory. You will need to use Linux, and might need
to install some dependencies. The standard documentation is available under
:kbd:`docs/build/html`.

====================
Internationalization
====================

Adding a language
-----------------

- Edit the file :file:`docs/source/pre_translate.sh` and add the two-letter
  code for your chosen language to the :kbd:`LOCALES` list.
- Also add it to both occurrences of the :kbd:`LOCALES` list in
  :file:`post_translate.sh`.
- Run :file:`pre_translate.sh`.
- Translation files for the documentation are now available as
  :kbd:`docs/source/i18n/[language code]/LC_MESSAGES/*.po`.

Updating translation strings
----------------------------

Whenever you have changed the source documentation, or want to begin
translating, it's a good idea to update the translation strings first:

- Run :file:`pre_translate.sh`. This will ensure that the sentences you are
  translating actually reflect the latest content.

Translating documents
---------------------

- Open the :kbd:`.po` files for your chosen language in a translator tool such
  as Qt Linguist.
- Edit and save the :kbd:`.po` files.

Building translated documentation
---------------------------------

- Run :file:`post_translate.sh`.
- The output directory is :file:`docs/source/_build/html/` and contains
  directories corresponding to the languages in :file:`post_translate.sh`. 
