Inasafe for QGIS 3 API break backwards incompatible changes
===========================================================


This page tries to maintain a list with incompatible changes that happened in previous releases.


QGIS Version 3.0 brings changes to many underlying dependencies which QGIS is built upon. Any existing PyQGIS code will
need to be updated to address the changes made within these libraries.

Python 3.0
----------

QGIS 3.0 introduces a move to Python 3. This version brings many changes to both the Python language and individual Python
libraries. A good place to start learning about the changes involved, and how to port your code to Python 3, is available
in the official Python documentation: [Porting Python 2 Code to Python 3](https://docs.python.org/3/howto/pyporting.html).

Qt 5
----

QGIS 3.0 is based off version 5 of the underlying Qt libraries. Many changes and API breaks were introduced in Qt5. While
it is c++ specific, a good place to read about the major changes introduced in Qt5 is at the Qt docs:
[C++ API changes](http://doc.qt.io/qt-5/sourcebreaks.html)


PyQt 5
------

Together with the Python and Qt version changes, the PyQt libraries which expose Qt classes to Python have also had their
version bumped to PyQt 5. The changes introduced in PyQt 5 and the steps required to upgrade existing code are summarised at:
[Differences Between PyQt4 and PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/pyqt4_differences.html)


Moved Classes
-------------

- Class XXXXXX was moved to module YYYYYY.


Renamed Classes
---------------

- Class XXXXXX was renamed to YYYYYY.


Removed Classes
---------------

- XXXXXX was removed. This was replaced by YYYYYY



General changes
---------------


- added environment variable DISABLE_WELCOME_MESSAGE, when set the welcome message will not be shown
