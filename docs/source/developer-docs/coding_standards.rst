
Coding Standards
================

Please observe the following coding standards when working on the codebase:

* Docstrings quoted with :samp:`"""`
* Simple strings in source code should be quoted with :samp:`'`
* Coding must follow a style guide. In case of Python it is `pep8 <http://www.python.org/dev/peps/pep-0008>`_ and
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
* Each source file should include a standard header containing copyright,
  authorship and version metadata as shown in the exampled below.

**Example standard header**::

   """
   Disaster risk assessment tool developed by AusAid -
     **QGIS plugin implementation.**
   
   Contact : ole.moller.nielsen@gmail.com
   
   .. note:: This program is free software; you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation; either version 2 of the License, or
        (at your option) any later version.
   
   """
   
   __author__ = 'tim@linfiniti.com'
   __version__ = '0.0.1'
   __date__ = '10/01/2011'
   __copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
   __copyright__ += 'Disaster Reduction'


