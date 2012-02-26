.. Risk-In-A-Box documentation master file, created by
   sphinx-quickstart on Tue Jan 10 12:22:06 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Risk-In-A-Box's API documentation
=================================

This is the API documentation for the Risk-In-A-Box project. You can find out
more about the Risk-In-A-Box project by visiting `riskinabox.org
<http://riskinabox.org/>`_.

Packages
--------

Package::gui
..............
.. toctree::
   :maxdepth: 2
   
   gui/init
   gui/riab
   gui/riabdock
   gui/riabkeywordsdialog
   gui/riabhelp
   gui/riabclipper
   gui/impactcalculator
   gui/riabexceptions
   
Package::impact_functions
.........................
.. toctree::
   :maxdepth: 2
   
   impact_functions/core

Unit Tests
..........

Gui Unit Tests
..............

.. toctree::
   :maxdepth: 2
      
   gui/qgisinterface
   gui/test_riab
   gui/test_riabdock
   gui/test_impactcalculator
   gui/test_riabkeywordsdialog


Impact Function Unit Tests
..........................

.. toctree::
   :maxdepth: 2
      
   impact_functions/test_plugin_core
