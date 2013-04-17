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

from PyQt4.QtTest import QTest
from PyQt4.QtGui import QDialogButtonBox
from PyQt4.QtCore import Qt
import unittest
import os
from converter_dialog import ConverterDialog

from safe_interface import TESTDATA, unique_filename, temp_dir
from safe_qgis.utilities_test import getQgisTestApp
QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


class ConverterDialogTest(unittest.TestCase):
    def test_initDialog(self):
        """Test for showing table in the first."""
        myDialog = ConverterDialog(PARENT)
        assert myDialog is not None, 'Dialog is failed to created'
        # testing populate algorithm
        expected_algorithms = ['Nearest', 'Invdist']
        assert myDialog.cboAlgorithm.count() == len(expected_algorithms), \
            'Number of algorithm is not same'
        for i in list(xrange(len(expected_algorithms))):
            assert expected_algorithms[i] == str(
                myDialog.cboAlgorithm.itemText(i)), \
                ('Algorithm is not same, expect %s got %s') % \
                (expected_algorithms[i], myDialog.cboAlgorithm.itemText(i))

    def test_behaviour(self):
        """Test behaviour of elements in the dialog
        """
        myDialog = ConverterDialog(PARENT)
        myDialog.cBDefaultOutputLocation.setEnabled(True)
        my_grid_path = os.path.join(TESTDATA, 'grid.xml')
        myDialog.leInputPath.setText(my_grid_path)
        input_path = myDialog.leInputPath.text()
        output_path = myDialog.leOutputPath.text()
        assert myDialog.isEnabled(), 'Output location should be disabled'
        expected_output_path = input_path[:-3] + 'tif'
        assert output_path == expected_output_path, \
            'Expected %s got %s' % (expected_output_path, output_path)

    def Xtest_Converting(self):
        """Test converting a file
        """
        myDialog = ConverterDialog(PARENT)
        myDialog.test_mode = True
        myDialog.cBDefaultOutputLocation.setEnabled(False)
        my_grid_path = os.path.join(TESTDATA, 'grid.xml')
        my_output_raster = unique_filename(prefix='result_grid',
                                           suffix='.tif',
                                           dir=temp_dir('test'))
        myDialog.cBLoadLayer.setEnabled(True)
        myDialog.leInputPath.setText(my_grid_path)
        myDialog.leOutputPath.setText(my_output_raster)
        myButton = myDialog.buttonBox.button(QDialogButtonBox.Ok)
        QTest.mouseClick(myButton, Qt.LeftButton)
        assert os.path.exists(my_output_raster), 'Raster is not created'


if __name__ == "__main__":
    suite = unittest.makeSuite(ConverterDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
