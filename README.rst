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

InaSAFE is a very new project. The current code development started
in earnest in January 2012 and there is still much to be done.
However, we work on the philosophy that stakeholders should have access
to the development and source code from the very beginning and invite
comments, suggestions and contributions.
See https://github.com/AIFDR/inasafe/issues/milestones and https://github.com/AIFDR/inasafe/issues?page=1&state=open for known bugs and outstanding tasks.


Disclaimer
==========

In addition to the NO WARRANTY clauses listed in the GPL license (LICENSE.TXT),
Neither AIFDR nor GFDRR take any responsibility for the correctness of
outputs from InaSAFE or decisions derived as a consequence.


