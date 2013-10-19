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

# this import required to enable PyQt API v2
import qgis  # pylint: disable=W0611

from safe_qgis.batch.batch_dialog import BatchDialog
from safe_qgis.utilities.utilities_for_testing import (
    get_qgis_app, SCENARIO_DIR)
from safe_qgis.safe_interface import temp_dir
from safe_qgis.widgets.dock import Dock


# Get QGis app handle
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
DOCK = Dock(IFACE)


class BatchDialogTest(unittest.TestCase):
    """Tests for the script/batch runner dialog.
    """

    def test_loadBatchDialog(self):
        """Definitely, this is a test. Test for BatchDialog behaviour
        """
        myDialog = BatchDialog(PARENT, IFACE, DOCK)
        myDialog.show_results_popup = False
        myDialog.scenario_directory_radio.setChecked(True)
        myDialog.source_directory.setText(SCENARIO_DIR)
        myDialog.source_directory.textChanged.emit(SCENARIO_DIR)
        print "Testing using : %s" % SCENARIO_DIR
        numberRow = myDialog.table.rowCount()
        assert numberRow == 2, 'Num scenario is wrong. I got %s' % numberRow
        myOutputDir = myDialog.output_directory.text()
        assert myOutputDir == SCENARIO_DIR, 'Output directory is ' + \
                                            myOutputDir
        myDialog.scenario_directory_radio.setChecked(False)
        myDialog.output_directory.setText('not a dir')
        myOutputDir = myDialog.output_directory.text()
        myDialog.scenario_directory_radio.setText(SCENARIO_DIR + 'a')
        myDialog.scenario_directory_radio.setText(SCENARIO_DIR)
        assert myOutputDir != SCENARIO_DIR, 'Output directory is ' + \
                                            myOutputDir

    def test_runSingleScenario(self):
        """Test run single scenario."""
        myDialog = BatchDialog(PARENT, IFACE, DOCK)
        myDialog.show_results_popup = False
        myDialog.scenario_directory_radio.setChecked(False)
        myDialog.source_directory.setText(SCENARIO_DIR)
        myDialog.source_directory.textChanged.emit(SCENARIO_DIR)
        myOutputDir = temp_dir()
        myDialog.output_directory.setText(myOutputDir)
        myDialog.table.selectRow(1)
        myButton = myDialog.run_selected_button
        myButton.click()
        myStatus = myDialog.table.item(1, 1).text()
        assert myStatus == 'Report Ok'

    def test_runAllScenario(self):
        """Test run single scenario.
        """
        myDialog = BatchDialog(PARENT, IFACE, DOCK)
        myDialog.show_results_popup = False
        myDialog.scenario_directory_radio.setChecked(False)
        myDialog.source_directory.setText(SCENARIO_DIR)
        myDialog.source_directory.textChanged.emit(SCENARIO_DIR)
        myOutputDir = temp_dir()
        myDialog.output_directory.setText(myOutputDir)
        myButton = myDialog.run_all_button
        myButton.click()
        myStatus0 = myDialog.table.item(0, 1).text()
        myStatus1 = myDialog.table.item(1, 1).text()
        assert myStatus0 == 'Analysis Fail', myStatus0
        assert myStatus1 == 'Report Ok', myStatus1


if __name__ == '__main__':
    suite = unittest.makeSuite(BatchDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
