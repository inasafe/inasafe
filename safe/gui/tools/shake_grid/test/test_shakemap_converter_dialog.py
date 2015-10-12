# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'ismail@kartoza.com'
__date__ = '14/09/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# this import required to enable PyQt API v2 - DO NOT REMOVE!
# noinspection PyUnresolvedReferences
import unittest
import os

# This is to enable API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4.QtGui import QDialogButtonBox

from safe.gui.tools.shake_grid.shakemap_converter_dialog import (
    ShakemapConverterDialog)
from safe.common.utilities import unique_filename, temp_dir
from safe.test.utilities import test_data_path, get_qgis_app, TESTDATA

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class ShakemapImporterTest(unittest.TestCase):
    """Test class to facilitate importing shakemaps."""

    def test_init_dialog(self):
        """Test for showing table in the first."""
        shakemap_converter_dialog = ShakemapConverterDialog(PARENT)
        msg = 'Dialog is failed to create'
        self.assertIsNotNone(shakemap_converter_dialog, msg)

    def test_behaviour(self):
        """Test behaviour of elements in the dialog
        """
        shakemap_importer_dialog = ShakemapConverterDialog(PARENT)
        shakemap_importer_dialog.use_output_default.setEnabled(True)
        my_grid_path = os.path.join(TESTDATA, 'grid.xml')
        shakemap_importer_dialog.input_path.setText(my_grid_path)
        input_path = shakemap_importer_dialog.input_path.text()
        output_path = shakemap_importer_dialog.output_path.text()

        msg = 'Output location should be disabled'
        self.assertTrue(shakemap_importer_dialog.isEnabled(), msg)

        expected_output_path = input_path[:-3] + 'tif'
        msg = 'Expected %s got %s' % (expected_output_path, output_path)
        self.assertEqual(output_path, expected_output_path, msg)

    def test_converting(self):
        """Test converting grif file to tiff."""
        dialog = ShakemapConverterDialog(PARENT)
        dialog.use_output_default.setEnabled(False)
        grid_path = test_data_path(
            'hazard',
            'shake_data',
            '20131105060809',
            'output',
            'grid.xml')
        output_raster = unique_filename(
            prefix='result_grid',
            suffix='.tif',
            dir=temp_dir('test'))
        dialog.load_result.setEnabled(True)
        dialog.input_path.setText(grid_path)
        dialog.output_path.setText(output_raster)
        button = dialog.button_box.button(QDialogButtonBox.Ok)
        button.click()

        msg = 'Raster is not created'
        output_path = '%s-nearest.tif' % output_raster[:-4]
        self.assertTrue(os.path.exists(output_path), msg)


if __name__ == "__main__":
    # noinspection PyArgumentEqualDefault
    suite = unittest.makeSuite(ShakemapImporterTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
