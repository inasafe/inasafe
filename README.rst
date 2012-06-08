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

InaSAFE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

The full GNU General Public License is available in LICENSE.TXT or
http://www.gnu.org/licenses


Disclaimer
==========

This work was produced at Australia Indonesia Facility for Disaster
Reduction (AIFDR) in partnership with Global Facility for Disaster
Reduction and Recovery (GFDRR). Neither the Australian Government, the
World Bank nor any of their employees make any warranty, express or
implied, or assume any liability or responsibility for the accuracy,
completeness, or usefulness of any information, product, or process
disclosed, or represent that its use would not infringe
privately-owned rights.  Reference herein to any specific commercial
products, process, or service by trade name, trademark, manufacturer,
or otherwise, does not necessarily constitute or imply its
endorsement, recommendation, or favoring by the Australian Government
or the World Bank. The views and opinions of authors expressed herein
do not necessarily state or reflect those of the Australian Government
or the World Bank, and shall not be used for advertising or product
endorsement purposes.

This document does not convey a warranty, express or implied, of
merchantability or fitness for a particular purpose.

The full license and no-warranty clauses are as defined by the GNU
General Public License version 3.
