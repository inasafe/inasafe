.. InaSAFE documentation master file, created by
   sphinx-quickstart on Tue Jan 10 12:22:06 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

InaSAFE's API documentation
===========================

This is the API documentation for the InaSAFE project. You can find out
more about the InaSAFE project by visiting `riskinabox.org
<http://www.inasafe.org/>`_.

Packages
--------

Package::gui
............
.. toctree::
   :maxdepth: 2

   gui/init
   gui/is_plugin
   gui/is_dock
   gui/is_map
   gui/is_keywords_dialog
   gui/is_help
   gui/is_clipper
   gui/is_impact_calculator
   gui/is_exceptions
   gui/is_safe_interface
   gui/is_keyword_io

Package::impact_functions
.........................
.. toctree::
   :maxdepth: 2

   impact_functions/core

Package::engine
...............
.. toctree::
   :maxdepth: 2

   engine/interpolation2d

Unit Tests
..........

Gui Unit Tests
..............

.. toctree::
   :maxdepth: 2

   gui/qgis_interface
   gui/test_is_plugin
   gui/test_is_dock
   gui/test_is_map
   gui/test_is_impact_calculator
   gui/test_is_keywords_dialog
   gui/test_is_safe_interface
   gui/test_is_keyword_io

Impact Function Unit Tests
..........................

.. toctree::
   :maxdepth: 2

   impact_functions/test_plugin_core
