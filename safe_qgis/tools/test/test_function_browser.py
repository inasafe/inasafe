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

# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

import unittest

from nose import SkipTest

from PyQt4.QtGui import QDialogButtonBox

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe_qgis.tools.function_browser import FunctionBrowser


def verifyColumn(table, col, strFilter, mode):
    """Helper function to verify the element in column.

        :param table: Table to be verified.

        :param col: Column number.
        :type col: int

        :param strFilter: A filter string.
        :type strFilter: str

        :param mode: Filter mode one of enum(only, included, excluded).

        :returns: Tuple of bool, string where:
            * bool = True or False about the verify
            * string contains message
        :rtype: (bool, str)
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
    """Tests for the function browser gui."""
    def setUp(self):
        """Setup."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testInitShowTable(self):
        """Test for showing table in the first."""
        myDialog = FunctionBrowser(PARENT)
        myStr = myDialog.table.toNewlineFreeString()
        assert len(myStr) > 1000, "Please check."

    def testFilterTable(self):
        """Test for filter the content of the table."""
        myDialog = FunctionBrowser(PARENT)
        list_category = myDialog.combo_box_content['category']
        for i in xrange(1, len(list_category)):
            myDialog.comboBox_category.setCurrentIndex(i)
            verifyColumn(myDialog.table, 2, list_category[i], 'only')

        myDialog.comboBox_datatype.setCurrentIndex(3)
        myDatatype = myDialog.comboBox_datatype.currentText()
        # datatype is the 5th column
        if myDatatype == 'sigab':
            verifyColumn(myDialog.table, 5, myDatatype, 'included')

    def testRestButton(self):
        """Test when reset button is pressed."""
        # ... and this is how you skip it using nosetests
        #prevent unreachable code errors in pylint
        #pylint: disable=W0101
        raise SkipTest("This test hangs Jenkins.")
        myDialog = FunctionBrowser(PARENT)
        expectedTable = myDialog.table.toNewlineFreeString()
        myDialog.comboBox_category.setCurrentIndex(1)
        myDialog.comboBox_subcategory.setCurrentIndex(1)
        resetButton = myDialog.myButtonBox.button(QDialogButtonBox.Reset)
        realTableFilter = myDialog.table.toNewlineFreeString()
        resetButton.click()
        realTableReset = myDialog.table.toNewlineFreeString()
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
        myButton.click()
        message = 'Help dialog was not created when help button pressed'
        assert myDialog.helpDialog is not None, message
        #pylint: enable=W0101

if __name__ == "__main__":
    suite = unittest.makeSuite(FunctionBrowserTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
