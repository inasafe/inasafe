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

From Zip Archive
----------------

We make regular releases of the InaSAFE plugin and they are available at
https://github.com/AIFDR/inasafe/downloads. Simply choose the most recent (i.e.
the one with the largest version number) and save it to your hard disk.

Now extract the zip file into the QGIS plugins directory. Under windows the
plugins directory is under :file:`c:\\Users\\<your username>\\.qgis\\python\\plugins`.

After extracting the plugin, it should be available as
:file:`c:\\Users\\<your username>\\.qgis\\python\\plugins\\inasafe\\`.

Mac and Linux users need to follow the same procedure but instead the plugin
directory will be under your $HOME directory.

Once the plugin is extracted, start QGIS and enable it from the plugin manager.
To do this open the plugin manager (:menuselection:`Plugins --> Manage plugins...`)
and type :samp:`insafe` into the filter box. You should see the InaSAFE plugin
appear in the list. Now tick the checkbox next to it to enable the plugin.

.. figure:: ../../plugin-manager.png
   :align: center

Via QGIS Plugin Manager
-----------------------

.. note:: This installation method is not yet supported - watch this space it
   will be available in the near future.

System Requirements
-------------------

 - A standard PC with at least 4GB of RAM running Windows, Linux or Mac OS X
 - The Open Source Geographic Information System QGIS (http://www.qgis.org).
   InaSAFE requires QGIS version 1.7 or newer.

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


License
=======

InaSAFE is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License version 3 (GPLv3) as
published by the Free Software Foundation.

The full GNU General Public License is available in LICENSE.TXT or
http://www.gnu.org/licenses/gpl.html


Disclaimer of Warranty (GPLv3)
==============================

There is no warranty for the program, to the extent permitted by
applicable law. Except when otherwise stated in writing the copyright
holders and/or other parties provide the program "as is" without warranty
of any kind, either expressed or implied, including, but not limited to,
the implied warranties of merchantability and fitness for a particular
purpose. The entire risk as to the quality and performance of the program
is with you. Sshould the program prove defective, you assume the cost of
all necessary servicing, repair or correction.


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



