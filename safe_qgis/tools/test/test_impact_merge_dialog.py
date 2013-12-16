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

# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

import unittest
import logging

import os
import tempfile

# this import required to enable PyQt API v2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611
from qgis.core import QgsVectorLayer, QgsRasterLayer

#noinspection PyPackageRequirements
from safe_qgis.tools.impact_merge_dialog import ImpactMergeDialog
from safe_qgis.utilities.utilities_for_testing import get_qgis_app
from safe_qgis.safe_interface import UNITDATA

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')
population_impact_path = os.path.join(
    UNITDATA,
    'impact',
    'population_affected_district_jakarta.shp')
building_impact_path = os.path.join(
    UNITDATA,
    'impact',
    'buildings_inundated_district_jakarta.shp')
aggregation_path = os.path.join(
    UNITDATA,
    'boundaries',
    'district_osm_jakarta.shp')


class ImpactMergeDialogTest(unittest.TestCase):
    """Test Impact Dialog widget
    """
    #noinspection PyPep8Naming
    def setUp(self):
        """Runs before each test."""
        self.impact_merge_dialog = ImpactMergeDialog(PARENT, IFACE)

    def test_validate_all_layers(self):
        """Test validate_all_layers function."""
        # Test normal case
        self.impact_merge_dialog.entire_area_mode = False
        self.impact_merge_dialog.first_impact_layer = QgsVectorLayer(
            population_impact_path,
            os.path.basename(population_impact_path),
            'ogr')
        self.impact_merge_dialog.second_impact_layer = QgsVectorLayer(
            building_impact_path,
            os.path.basename(building_impact_path),
            'ogr')

        self.impact_merge_dialog.chosen_aggregation_layer = QgsVectorLayer(
            aggregation_path,
            os.path.basename(aggregation_path),
            'ogr')

        self.impact_merge_dialog.validate_all_layers()

        self.assertIn(
            'Detailed gender report',
            self.impact_merge_dialog.first_postprocessing_report)
        self.assertIn(
            'Detailed building type report',
            self.impact_merge_dialog.second_postprocessing_report)
        self.assertIn(
            'Detailed gender report',
            self.impact_merge_dialog.first_postprocessing_report)
        self.assertEqual(
            'KAB_NAME',
            self.impact_merge_dialog.aggregation_attribute)

if __name__ == '__main__':
    suite = unittest.makeSuite(ImpactMergeDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
