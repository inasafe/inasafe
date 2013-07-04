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
__date__ = '14/09/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from nose import SkipTest
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialogButtonBox

from safe_qgis.tools.function_browser import FunctionBrowser
from safe_qgis.utilities.utilities_test import getQgisTestApp


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
    elmt = ''
    verb = ''
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


class FunctionBrowserTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testInitShowTable(self):
        """Test for showing table in the first."""
        myDialog = FunctionBrowser(PARENT)
        myStr = myDialog.if_table.toNewlineFreeString()
        assert len(myStr) > 1000, "Please check."

    def testFilterTable(self):
        """Test for filter the content of the table."""
        myDialog = FunctionBrowser(PARENT)
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
        # ... and this is how you skip it using nosetests
        #prevent unreachable code errors in pylint
        #pylint: disable=W0101
        raise SkipTest("This test hangs Jenkins.")
        myDialog = FunctionBrowser(PARENT)
        expectedTable = myDialog.if_table.toNewlineFreeString()
        myDialog.comboBox_category.setCurrentIndex(1)
        myDialog.comboBox_subcategory.setCurrentIndex(1)
        resetButton = myDialog.myButtonBox.button(QDialogButtonBox.Reset)
        realTableFilter = myDialog.if_table.toNewlineFreeString()
        # noinspection PyArgumentList
        QTest.mouseClick(resetButton, Qt.LeftButton)
        realTableReset = myDialog.if_table.toNewlineFreeString()
        msgFilter = 'It should be different table because it is filtered.'
        assert expectedTable != realTableFilter, msgFilter
        msgReset = ('It should be the same table because reset button '
                    'is pressed.')
        assert expectedTable == realTableReset, msgReset

    # This is how you skip a test when using unittest ...
    @unittest.skip('Skipping as this test hangs Jenkins if docs not found.')
    def test_showHelp(self):
        """Test that help button works"""
        # ... and this is how you skip it using nosetests
        #pylint: disable=W0101
        raise SkipTest("This test hangs Jenkins if docs dir not present.")
        myDialog = FunctionBrowser(PARENT)
        myButton = myDialog.buttonBox.button(QDialogButtonBox.Help)
        # noinspection PyArgumentList
        QTest.mouseClick(myButton, Qt.LeftButton)
        myMessage = 'Help dialog was not created when help button pressed'
        assert myDialog.helpDialog is not None, myMessage
        #pylint: enable=W0101

if __name__ == "__main__":
    suite = unittest.makeSuite(FunctionBrowserTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
