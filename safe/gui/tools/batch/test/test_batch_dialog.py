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

__author__ = 'ismail@kartoza.com'
__date__ = '24/06/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# this import required to enable PyQt API v2 - DO NOT REMOVE!
# noinspection PyUnresolvedReferences
import unittest

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import standard_data_path, get_qgis_app, get_dock
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

import logging

from safe.gui.tools.batch.batch_dialog import BatchDialog
from safe.common.utilities import temp_dir

LOGGER = logging.getLogger('InaSAFE')


class BatchDialogTest(unittest.TestCase):
    """Tests for the script/batch runner dialog."""

    def setUp(self):
        self.dock = get_dock()

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_load_batch_dialog(self):
        """Test for BatchDialog behaviour.
        """
        scenarios_dir = standard_data_path('control', 'scenarios')
        dialog = BatchDialog(PARENT, IFACE, self.dock)
        dialog.show_results_popup = False
        dialog.scenario_directory_radio.setChecked(True)
        dialog.source_directory.setText(scenarios_dir)
        dialog.source_directory.textChanged.emit(scenarios_dir)
        number_row = dialog.table.rowCount()
        self.assertEquals(
            number_row, 2, 'Num scenario should be 2, but got %s' % number_row)
        out_path = dialog.output_directory.text()
        self.assertEquals(out_path, scenarios_dir)
        dialog.scenario_directory_radio.setChecked(False)
        dialog.output_directory.setText('not a dir')
        out_path = dialog.output_directory.text()
        dialog.scenario_directory_radio.setText(scenarios_dir + 'a')
        dialog.scenario_directory_radio.setText(scenarios_dir)
        self.assertNotEqual(out_path, scenarios_dir)

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_run_single_scenario(self):
        """Test run single scenario."""
        scenarios_dir = standard_data_path('control', 'scenarios')
        dialog = BatchDialog(PARENT, IFACE, self.dock)
        dialog.show_results_popup = False
        dialog.scenario_directory_radio.setChecked(False)
        dialog.source_directory.setText(scenarios_dir)
        dialog.source_directory.textChanged.emit(scenarios_dir)
        out_path = temp_dir()
        dialog.output_directory.setText(out_path)
        dialog.table.selectRow(1)
        button = dialog.run_selected_button
        button.click()
        status = dialog.table.item(1, 1).text()
        expected_status = 'Report Ok'
        message = 'Expected %s but got %s' % (expected_status, status)
        self.assertEqual(status, expected_status, message)

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_run_all_scenario(self):
        """Test run all scenarii."""
        scenarios_dir = standard_data_path('control', 'scenarios')
        dialog = BatchDialog(PARENT, IFACE, self.dock)
        dialog.show_results_popup = False
        dialog.scenario_directory_radio.setChecked(False)
        dialog.source_directory.setText(scenarios_dir)
        dialog.source_directory.textChanged.emit(scenarios_dir)
        out_path = temp_dir()
        dialog.output_directory.setText(out_path)
        button = dialog.run_all_button
        button.click()
        status0 = dialog.table.item(0, 1).text()
        status1 = dialog.table.item(1, 1).text()
        self.assertEquals(status0, 'Analysis Fail')
        self.assertEquals(status1, 'Report Ok')


if __name__ == '__main__':
    suite = unittest.makeSuite(BatchDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
