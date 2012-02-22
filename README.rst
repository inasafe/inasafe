====================
RISK IN A BOX - QGIS
====================

This is the project: Risk in a Box - QGIS

.. figure::  ../../../gui/resources/img/screenshot.jpg
   :align:   center

The latest source code is available in https://github.com/AIFDR/risk_in_a_box
which contains modules for risk calculations, gis functionality and functions for impact modelling.

For more information about Risk In a Box please look at
the documentation at http://risk-in-a-box.readthedocs.org

Risk in a Box - QGis web site: http://aifdr.github.com/risk_in_a_box

========================
Quick Installation Guide
========================

.. note::

  Risk in a Box is a plugin for `Quantum GIS <http://qgis.org>`_ (QGIS), so
  QGIS must be installed first.


To install the Risk in a Box, use the plugin manager in QGIS::

  Plugins -> Fetch Python Plugins

Then search for 'Risk In A Box', select it and click the install button.
The plugin will now be added to your plugins menu.


-------------------
System Requirements
-------------------

 - A standard PC with at least 4GB of RAM running Windows, Linux or Mac OS X
 - The Open Source Geographic Information System QGIS (http://www.qgis.org).
   Risk in a Box requires QGIS version 1.7 or newer.



===========
LIMITATIONS
===========

Risk in a Box is a very new project. The current code development started
in earnest in March 2011 and there is still much to be done.
However, we work on the philosophy that stakeholders should have access
to the development and source code from the very beginning and invite
comments, suggestions and contributions.


As such, Risk in a Box currently has some major limitations, including

 * Hazard layers must be provided as raster data
 * Exposure data must be either raster data or vector data but only
   point, line and polygon types are supported.
 * All data must be provided in WGS84 geographic coordinates
 * Neither AIFDR nor GFDRR take any responsibility for the correctness of
   outputs from Risk in a Box or decisions derived as a consequence


