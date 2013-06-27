# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Test for Batch Runner Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'imajimatika@gmail.com'
__date__ = '24/06/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from PyQt4 import QtCore
from PyQt4.QtTest import QTest

from safe_qgis.batch.batch_dialog import BatchDialog
from safe_qgis.utilities.utilities_test import getQgisTestApp, SCENARIO_DIR
from safe_qgis.safe_interface import temp_dir
from safe_qgis.dock import Dock


# Get QGis app handle
QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
DOCK = Dock(IFACE)


class BatchDialogTest(unittest.TestCase):
    """Test for the script/batch runner dialog
    """

    def test_loadBatchDialog(self):
        """Definitely, this is a test. Test for BatchDialog behaviour
        """
        myDialog = BatchDialog(PARENT, IFACE, DOCK)
        myDialog.cbDefaultOutputDir.setChecked(True)
        myDialog.leSourceDir.setText(SCENARIO_DIR)
        numberRow = myDialog.tblScript.rowCount()
        assert numberRow == 2, 'Num scenario is wrong. I got %s' % numberRow
        myOutputDir = myDialog.leOutputDir.text()
        assert myOutputDir == SCENARIO_DIR, 'Ouput directory is ' + myOutputDir
        myDialog.cbDefaultOutputDir.setChecked(False)
        myDialog.leOutputDir.setText('not a dir')
        myOutputDir = myDialog.leOutputDir.text()
        myDialog.leSourceDir.setText(SCENARIO_DIR + 'a')
        myDialog.leSourceDir.setText(SCENARIO_DIR)
        assert myOutputDir != SCENARIO_DIR, 'Ouput directory is ' + myOutputDir

    def test_runSingleScenario(self):
        """Test run single scenario
        """
        myDialog = BatchDialog(PARENT, IFACE, DOCK)
        myDialog.cbDefaultOutputDir.setChecked(False)
        myDialog.leSourceDir.setText(SCENARIO_DIR)
        myOutputDir = temp_dir()
        myDialog.leOutputDir.setText(myOutputDir)
        myDialog.sboCount.setValue(1)
        myDialog.tblScript.selectRow(1)
        myButton = myDialog.btnRunSelected
        # noinspection PyArgumentList
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myStatus = myDialog.tblScript.item(1, 1).text()
        assert myStatus == 'Report Ok'

    def test_runAllScenario(self):
        """Test run single scenario
        """
        myDialog = BatchDialog(PARENT, IFACE, DOCK)
        myDialog.cbDefaultOutputDir.setChecked(False)
        myDialog.leSourceDir.setText(SCENARIO_DIR)
        myOutputDir = temp_dir()
        myDialog.leOutputDir.setText(myOutputDir)
        myButton = myDialog.pbnRunAll
        # noinspection PyArgumentList
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myStatus0 = myDialog.tblScript.item(0, 1).text()
        myStatus1 = myDialog.tblScript.item(1, 1).text()
        assert myStatus0 == 'Analysis Fail', myStatus0
        assert myStatus1 == 'Report Ok', myStatus1


if __name__ == '__main__':
    suite = unittest.makeSuite(BatchDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
