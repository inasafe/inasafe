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

# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import unittest

import qgis  # pylint: disable=W0611

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe_qgis.tools.batch.batch_dialog import BatchDialog
from safe_qgis.utilities.utilities_for_testing import (
    SCENARIO_DIR)
from safe_qgis.safe_interface import temp_dir
from safe_qgis.widgets.dock import Dock

DOCK = Dock(IFACE)


class BatchDialogTest(unittest.TestCase):
    """Tests for the script/batch runner dialog."""
    def test_load_batch_dialog(self):
        """Test for BatchDialog behaviour.
        """
        dialog = BatchDialog(PARENT, IFACE, DOCK)
        dialog.show_results_popup = False
        dialog.scenario_directory_radio.setChecked(True)
        dialog.source_directory.setText(SCENARIO_DIR)
        dialog.source_directory.textChanged.emit(SCENARIO_DIR)
        print "Testing using : %s" % SCENARIO_DIR
        number_row = dialog.table.rowCount()
        self.assertTrue(
            number_row == 2, 'Num scenario is wrong. I got %s' % number_row)
        out_path = dialog.output_directory.text()
        self.assertTrue(
            out_path == SCENARIO_DIR, 'Output directory is %s' % out_path)
        dialog.scenario_directory_radio.setChecked(False)
        dialog.output_directory.setText('not a dir')
        out_path = dialog.output_directory.text()
        dialog.scenario_directory_radio.setText(SCENARIO_DIR + 'a')
        dialog.scenario_directory_radio.setText(SCENARIO_DIR)
        self.assertTrue(
            out_path != SCENARIO_DIR, 'Output directory is %s' % out_path)

    def test_run_single_scenario(self):
        """Test run single scenario."""
        dialog = BatchDialog(PARENT, IFACE, DOCK)
        dialog.show_results_popup = False
        dialog.scenario_directory_radio.setChecked(False)
        dialog.source_directory.setText(SCENARIO_DIR)
        dialog.source_directory.textChanged.emit(SCENARIO_DIR)
        out_path = temp_dir()
        dialog.output_directory.setText(out_path)
        dialog.table.selectRow(1)
        button = dialog.run_selected_button
        button.click()
        status = dialog.table.item(1, 1).text()
        self.assertTrue(status == 'Report Ok')

    def test_run_all_scenario(self):
        """Test run single scenario.
        """
        dialog = BatchDialog(PARENT, IFACE, DOCK)
        dialog.show_results_popup = False
        dialog.scenario_directory_radio.setChecked(False)
        dialog.source_directory.setText(SCENARIO_DIR)
        dialog.source_directory.textChanged.emit(SCENARIO_DIR)
        out_path = temp_dir()
        dialog.output_directory.setText(out_path)
        button = dialog.run_all_button
        button.click()
        status0 = dialog.table.item(0, 1).text()
        status1 = dialog.table.item(1, 1).text()
        self.assertTrue(status0 == 'Analysis Fail', status0)
        self.assertTrue(status1 == 'Report Ok', status1)


if __name__ == '__main__':
    suite = unittest.makeSuite(BatchDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
