# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Impact Merge Dialog Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__date__ = '23/10/2013'
__copyright__ = ('Copyright 2013, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import logging

import os
import tempfile

# this import required to enable PyQt API v2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611
from qgis.core import QgsVectorLayer, QgsRasterLayer

#noinspection PyPackageRequirements
from PyQt4.QtGui import QDialog
from safe_qgis.tools.impact_merge_dialog import ImpactMergeDialog
from safe_qgis.utilities.utilities_for_testing import get_qgis_app, load_layer
from safe_qgis.safe_interface import UNITDATA

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')
shapefile_path = os.path.join(UNITDATA, 'impact', 'impact_merge_1.shp')
tif_path = os.path.join(UNITDATA, 'impact', 'impact_merge_2.tif')


class ImpactMergeDialogTest(unittest.TestCase):
    """Test Impact Dialog widget
    """
    #noinspection PyPep8Naming
    def setUp(self):
        """Runs before each test."""
        self.impact_dialog = ImpactMergeDialog(PARENT, IFACE)

    def test_download(self):
        """Test download method."""
        output_directory = tempfile.mkdtemp()
        self.impact_dialog.output_directory.setText(output_directory)

        impact_layer_1 = QgsVectorLayer(
            shapefile_path,
            os.path.basename(shapefile_path),
            'ogr')
        impact_layer_2 = QgsRasterLayer(
            tif_path,
            os.path.basename(tif_path),
            'ogr')
        self.assertIsNotNone(self.impact_dialog.output_directory.text())

if __name__ == '__main__':
    suite = unittest.makeSuite(ImpactMergeDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
