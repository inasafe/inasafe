"""
Disaster risk assessment tool developed by AusAid - **QGIS plugin test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
from qgis.gui import QgsMapCanvas
from qgisinterface import QgisInterface
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QWidget
from utilities_test import getQgisTestApp

from gui.riab import Riab

QGISAPP = getQgisTestApp()


class RiabTest(unittest.TestCase):
    """Test suite for Risk in a Box QGis plugin"""

    def test_load(self):
        """Risk in a Box QGis plugin can be loaded"""

        myParent = QWidget()
        myCanvas = QgsMapCanvas(myParent)
        myIface = QgisInterface(myCanvas)
        Riab(myIface)

    def test_setupI18n(self):
        """Gui translations are working."""
        myUntranslatedString = 'Sponsored by AusAID and World Bank'
        myExpectedString = 'Funded by AusAID and World Bank'
        myParent = QWidget()
        myCanvas = QgsMapCanvas(myParent)
        myIface = QgisInterface(myCanvas)
        Riab(myIface)
        myContext = 'RiabDock'
        myTranslation = QCoreApplication.translate(
                                    myContext, myUntranslatedString)
        myMessage = 'Expected: %s\nGot: %s' % (
                            myExpectedString, myTranslation)
        assert myTranslation == myExpectedString, myMessage

if __name__ == '__main__':
    unittest.main()
