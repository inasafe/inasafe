===========================
Risk-in-a-box User Documentation
===========================

This is the project: Risk in a Box - QGIS plugin

The latest source code is available in https://github.com/AIFDR/risk_in_a_box
which contains modules for risk calculations, gis functionality and plugin
management.

For more information about Risk In a Box please look at
our documentation under docs/build/html.

Quick Installation Guide - Users
================================

.. note::
   
   This is a plugin for `Quantum GIS <http://qgis.org>`_ (QGIS). It requires version 1.7 of QGIS
   (or newer).

To install the plugin, use the plugin manager in QGIS::

  Plugins -> Fetch Python Plugins
  
Then search for 'Risk In A Box', select it and click the install button. The plugin will 
now be added to your plugins menu.

Quick Installation Guide - Developers
=====================================

To develop on the plugin, you first need to copy it to your local system. If you are a developer, 
the simplest way to do that is to clone it from our GitHub repository page like this::

  git clone git://github.com/AIFDR/risk_in_a_box.git
  
Place the local repository under `~/.qgis/python/plugins` and then restart QGIS. If you wish to 
an IDE for development, please refer to `this article <http://linfiniti.com/2011/12/remote-debugging-qgis-python-plugins-with-pydev/>`_ 
for detailed information on how you can do so. 

If you wish to debug the plugin, (referring once again to the above article), make a copy 
of pydevpath.txt.templ to pydevpath.txt e.g.::

  cp pydevpath.txt.templ pydevpath.txt

Then replace the path to your pydevd module as described in the above article.


.. note::

   If you are running with remote debugging enabled, be sure to start the 
   PyDev debug server first before launching the Risk-in-a-box QGIS plugin 
   otherwise QGIS will likely crash when it can't find the debug server.


If you wish to run the unit tests, please make a local copy of the qgispath.txt.templ template 
and adjust the path contained in that file to match your QGIS installation path e.g.::

  cp qgispath.txt.templ qgispath.txt




Contact:
Ole.Moller.Nielsen@gmail.com

