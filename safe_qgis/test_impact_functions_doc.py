"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'ismailsunni@yahoo.co.id'
__version__ = '0.5.0'
__date__ = '13/09/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import unittest

from PyQt4 import QtGui, QtCore, QtTest
from PyQt4.QtTest import QTest
from safe_qgis.utilities_test import getQgisTestApp

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


from impact_functions_doc import ImpactFunctionsDoc


class ImpactFunctionsDocTest(unittest.TestCase):

    def setUp(self):
        """Create fresh dialog for each test"""
        pass

    def tearDown(self):
        """Destroy the dialog after each test"""
        pass

#==============================================================================
#    def testApplyButton(self):
#        """Test when apply button is pressed"""
#        myDialog = ImpactFunctionsDoc(PARENT)
#        applyButton = myDialog.ui.myButtonBox.button(
#                                        QtGui.QDialogButtonBox.Apply)
#        QTest.mouseClick(applyButton, QtCore.Qt.LeftButton)
#
#        myDialog.ui.comboBox_category.setCurrentIndex(1)
#        realString = myDialog.ui.comboBox_category.currentText()
#        expString = 'hazard'
#        msg = "Should be %s, but got %s" % (expString, realString)
#        assert realString == expString, msg
#        QTest.mouseClick(applyButton, QtCore.Qt.LeftButton)
#        pass
#==============================================================================


if __name__ == "__main__":
    suite = unittest.makeSuite(ImpactFunctionsDocTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
