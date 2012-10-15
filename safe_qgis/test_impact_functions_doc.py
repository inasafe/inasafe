"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from PyQt4 import QtGui

__author__ = 'ismailsunni@yahoo.co.id'
__version__ = '0.5.0'
__date__ = '14/09/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import unittest
from impact_functions_doc import ImpactFunctionsDoc
from safe_qgis.utilities_test import getQgisTestApp
from PyQt4.QtTest import QTest
from PyQt4 import QtCore

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


def verifyColumn(table, col, strFilter, mode):
    """Helper function to verify the element in column.
        Args:
            * table = table to be verified
            * col = (integer) column number
            * strFilter = (string)
            * mode = enum(only, included, excluded)
        Returns:
            * bool = True or False about the verify
            * string contains message
    """
    strFilter = str(strFilter)  # make sure it is a string
    retval = True
    msg = 'Verified'
    elmt_col = table.column(col)
    if mode == 'only':
        for elmt in elmt_col:
            if elmt != strFilter:
                retval = False
                verb = 'to only has'
                break
    elif mode == 'included':
        for elmt in elmt_col:
            elmt_list = elmt.split(', ')
            if elmt_list.count(strFilter) < 1:
                retval = False
                verb = 'to included'
                break
    elif mode == 'excluded':
        for elmt in elmt_col:
            elmt_list = elmt.split(', ')
            if elmt_list.count(strFilter) != 1:
                retval = False
                verb = 'to excluded'
                break
    else:
        return False, 'Arg mode is not one of only, included, or excluded '

    if not retval:
        msg = ('Expected column %d %s %s but found %s'
                        % (col, verb, strFilter, elmt))
    assert retval, msg


class ImpactFunctionsDocTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testInitShowTable(self):
        """Test for showing table in the first."""
        myDialog = ImpactFunctionsDoc(PARENT)
        myStr = myDialog.if_table.toNewlineFreeString()
        assert len(myStr) > 1000, "Please check."

    def testFilterTable(self):
        """Test for filter the content of the table."""
        myDialog = ImpactFunctionsDoc(PARENT)
        list_category = myDialog.combo_box_content['category']
        for i in xrange(1, len(list_category)):
            myDialog.comboBox_category.setCurrentIndex(i)
            verifyColumn(myDialog.if_table, 2, list_category[i], 'only')

        myDialog.comboBox_datatype.setCurrentIndex(3)
        myDatatype = myDialog.comboBox_datatype.currentText()
        # datatype is the 5th column
        if myDatatype == 'sigab':
            verifyColumn(myDialog.if_table, 5, myDatatype, 'included')

    def testRestButton(self):
        """Test when reset button is pressed."""
        myDialog = ImpactFunctionsDoc(PARENT)
        expectedTable = myDialog.if_table.toNewlineFreeString()
        myDialog.comboBox_category.setCurrentIndex(1)
        myDialog.comboBox_subcategory.setCurrentIndex(1)
        realTableFilter = myDialog.if_table.toNewlineFreeString()
        resetButton = myDialog.myButtonBox.button(
                                            QtGui.QDialogButtonBox.Reset)
        QTest.mouseClick(resetButton, QtCore.Qt.LeftButton)
        realTableReset = myDialog.if_table.toNewlineFreeString()
        msgFilter = 'It should be different table because it is filtered.'
        assert expectedTable != realTableFilter, msgFilter
        msgReset = ('It should be the same table because reset button '
                    'is pressed.')
        assert expectedTable == realTableReset, msgReset

    def test_showHelp(self):
        """Test that help button works"""
        myDialog = ImpactFunctionsDoc(PARENT)
        myButton = myDialog.myButtonBox.button(QtGui.QDialogButtonBox.Help)
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myMessage = 'Help dialog was not created when help button pressed'
        assert myDialog.helpDialog is not None, myMessage

if __name__ == "__main__":
    suite = unittest.makeSuite(ImpactFunctionsDocTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
