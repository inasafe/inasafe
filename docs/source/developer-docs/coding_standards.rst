
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


All strings should be internationalisation enabled. Please see :doc:`i18n` 
for details.
