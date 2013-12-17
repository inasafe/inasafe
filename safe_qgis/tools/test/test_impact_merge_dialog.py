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
from glob import glob
import shutil

#noinspection PyPackageRequirements
from PyQt4 import QtCore

# this import required to enable PyQt API v2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611
from qgis.core import QgsMapLayerRegistry

#noinspection PyPackageRequirements
from safe_qgis.tools.impact_merge_dialog import ImpactMergeDialog
from safe_qgis.utilities.utilities_for_testing import (
    get_qgis_app,
    load_layer)
from safe_qgis.safe_interface import UNITDATA

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')

population_entire_jakarta_impact_path = os.path.join(
    UNITDATA,
    'impact',
    'population_affected_entire_area.shp')
population_district_jakarta_impact_path = os.path.join(
    UNITDATA,
    'impact',
    'population_affected_district_jakarta.shp')
building_entire_jakarta_impact_path = os.path.join(
    UNITDATA,
    'impact',
    'buildings_inundated_entire_area.shp')
building_district_jakarta_impact_path = os.path.join(
    UNITDATA,
    'impact',
    'buildings_inundated_district_jakarta.shp')
district_jakarta_boundary_path = os.path.join(
    UNITDATA,
    'boundaries',
    'district_osm_jakarta.shp')

TEST_DATA_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), '../../test/test_data/test_files'))


class ImpactMergeDialogTest(unittest.TestCase):
    """Test Impact Dialog widget
    """
    #noinspection PyPep8Naming
    def setUp(self):
        """Runs before each test."""
        self.impact_merge_dialog = ImpactMergeDialog(PARENT, IFACE)

        # Create test dir
        #noinspection PyUnresolvedReferences
        test_impact_merge_dir = os.path.join(
            TEST_DATA_DIR, 'test-impact-merge')
        if not os.path.exists(test_impact_merge_dir):
            os.makedirs(test_impact_merge_dir)

        # Create test dir for aggregated
        #noinspection PyUnresolvedReferences
        test_aggregated_dir = os.path.join(
            test_impact_merge_dir, 'aggregated')
        if not os.path.exists(test_aggregated_dir):
            os.makedirs(test_aggregated_dir)

        # Create test dir for entire
        test_entire_dir = os.path.join(
            test_impact_merge_dir, 'entire')
        if not os.path.exists(test_entire_dir):
            os.makedirs(test_entire_dir)

        # Register 4 impact layers and aggregation layer
        self.population_entire_jakarta_layer, _ = load_layer(
            population_entire_jakarta_impact_path,
            directory=None)
        self.building_entire_jakarta_layer, _ = load_layer(
            building_entire_jakarta_impact_path,
            directory=None)
        self.population_district_jakarta_layer, _ = load_layer(
            population_district_jakarta_impact_path,
            directory=None)
        self.building_district_jakarta_layer, _ = load_layer(
            building_district_jakarta_impact_path,
            directory=None)
        self.district_jakarta_layer, _ = load_layer(
            district_jakarta_boundary_path,
            directory=None)

        # Add layers to registry
        self.register_layers()

    #noinspection PyPep8Naming
    def tearDown(self):
        """Runs after each test."""
        # Delete test dir
        #noinspection PyUnresolvedReferences
        test_impact_merge_dir = os.path.join(
            TEST_DATA_DIR, 'test-impact-merge')
        shutil.rmtree(test_impact_merge_dir)
        # Remove Layers from registry
        QgsMapLayerRegistry().instance().removeAllMapLayers()

    def register_layers(self):
        """Register needed layers to QgsMapLayerRegistry."""
        layer_list = [self.population_entire_jakarta_layer,
                      self.population_district_jakarta_layer,
                      self.building_entire_jakarta_layer,
                      self.building_district_jakarta_layer,
                      self.district_jakarta_layer]
        # noinspection PyArgumentList
        QgsMapLayerRegistry().instance().addMapLayers(layer_list)

    def mock_the_dialog(self, test_entire_mode):
        # Populate layers on registry to dialog
        self.impact_merge_dialog.get_project_layers()
        if test_entire_mode:
            self.impact_merge_dialog.entire_area_mode = True
            # Set the current Index of the combobox
            first_layer_count = self.impact_merge_dialog.first_layer.count()
            for index in range(0, first_layer_count):
                layer_name = \
                    self.impact_merge_dialog.first_layer.itemData(
                        index, QtCore.Qt.UserRole).name().lower()
                if ('population' in layer_name) and ('entire' in layer_name):
                    self.impact_merge_dialog.first_layer.setCurrentIndex(index)

            second_layer_count = self.impact_merge_dialog.first_layer.count()
            for index in range(0, second_layer_count):
                layer_name = \
                    self.impact_merge_dialog.second_layer.itemData(
                        index, QtCore.Qt.UserRole).name().lower()
                if ('buildings' in layer_name) and ('entire' in layer_name):
                    self.impact_merge_dialog.second_layer.setCurrentIndex(
                        index)

            # Aggregation Layer = Entire Area
            aggregation_layer_count = \
                self.impact_merge_dialog.aggregation_layer.count()
            for index in range(0, aggregation_layer_count):
                layer = \
                    self.impact_merge_dialog.aggregation_layer.itemData(
                        index, QtCore.Qt.UserRole)
                if layer is None:
                    self.impact_merge_dialog.aggregation_layer.\
                        setCurrentIndex(index)

            #noinspection PyUnresolvedReferences
            self.impact_merge_dialog.output_directory.setText(
                os.path.join(
                    TEST_DATA_DIR, 'test-impact-merge', 'entire'))
        else:
            self.impact_merge_dialog.entire_area_mode = False
            # Set the current Index of the combobox
            first_layer_count = self.impact_merge_dialog.first_layer.count()
            for index in range(0, first_layer_count):
                layer_name = \
                    self.impact_merge_dialog.first_layer.itemData(
                        index, QtCore.Qt.UserRole).name()
                if ('population' in layer_name) and ('district' in layer_name):
                    self.impact_merge_dialog.first_layer.setCurrentIndex(index)

            second_layer_count = self.impact_merge_dialog.second_layer.count()
            for index in range(0, second_layer_count):
                layer_name = \
                    self.impact_merge_dialog.second_layer.itemData(
                        index, QtCore.Qt.UserRole).name()
                if ('building' in layer_name) and ('district' in layer_name):
                    self.impact_merge_dialog.second_layer.setCurrentIndex(index)

            # Aggregation Layer = District Jakarta
            aggregation_layer_count = \
                self.impact_merge_dialog.aggregation_layer.count()
            for index in range(0, aggregation_layer_count):
                layer = \
                    self.impact_merge_dialog.aggregation_layer.itemData(
                        index, QtCore.Qt.UserRole)
                if layer is not None:
                    self. \
                        impact_merge_dialog.aggregation_layer. \
                        setCurrentIndex(index)

            #noinspection PyUnresolvedReferences
            self.impact_merge_dialog.output_directory.setText(
                os.path.join(
                    TEST_DATA_DIR, 'test-impact-merge', 'aggregated'))

    def test_accept(self):
        """Test accept function."""
        self.mock_the_dialog(test_entire_mode=True)
        self.impact_merge_dialog.accept()

        # There should be 1 pdf files in self.impact_merge_dialog.out_dir
        report_list = glob(
            os.path.join(
                self.impact_merge_dialog.out_dir,
                '*.pdf'))
        expected_reports_number = 1
        self.assertEqual(len(report_list), expected_reports_number)

    def test_get_project_layers(self):
        """Test get_project_layers function."""
        self.register_layers()
        # Test the get_project_layers
        self.impact_merge_dialog.get_project_layers()

        # On self.impact_merge_dialog.first_layer there must be 4 items
        first_layer_expected_number = 4
        self.assertEqual(
            first_layer_expected_number,
            self.impact_merge_dialog.first_layer.count())

        # On self.impact_merge_dialog.second_layer there must be 4 items
        second_layer_expected_number = 4
        self.assertEqual(
            second_layer_expected_number,
            self.impact_merge_dialog.second_layer.count())

        # On self.impact_merge_dialog.aggregation_layer there must be 2 items
        aggregation_layer_expected_number = 2
        self.assertEqual(
            aggregation_layer_expected_number,
            self.impact_merge_dialog.aggregation_layer.count())

    def test_prepare_input(self):
        """Test prepare_input function."""
        # Test Entire Area
        self.mock_the_dialog(test_entire_mode=True)
        self.impact_merge_dialog.prepare_input()

        # First impact layer should be the population entire
        first_layer_name = self.impact_merge_dialog.first_impact_layer.name()
        self.assertIn('population', first_layer_name)
        self.assertIn('entire', first_layer_name)

        # Second impact layer should be the population entire
        second_layer_name = self.impact_merge_dialog.second_impact_layer.name()
        self.assertIn('buildings', second_layer_name)
        self.assertIn('entire', second_layer_name)

        # Chosen aggregaton layer must be none
        aggregation_layer = self.impact_merge_dialog.chosen_aggregation_layer
        self.assertIsNone(aggregation_layer)

        # Test Aggregated
        self.mock_the_dialog(test_entire_mode=False)
        self.impact_merge_dialog.prepare_input()

        # First impact layer should be the population entire
        first_layer_name = self.impact_merge_dialog.first_impact_layer.name()
        self.assertIn('population', first_layer_name)
        self.assertIn('district', first_layer_name)

        # Second impact layer should be the population entire
        second_layer_name = self.impact_merge_dialog.second_impact_layer.name()
        self.assertIn('buildings', second_layer_name)
        self.assertIn('district', second_layer_name)

        # Chosen aggregaton layer must be not none
        aggregation_layer_name = \
            self.impact_merge_dialog.chosen_aggregation_layer.name()
        self.assertEqual(self.district_jakarta_layer.name(),
                         aggregation_layer_name)

    def test_require_directory(self):
        """Test require_directory function."""
        self.mock_the_dialog(test_entire_mode=True)
        self.impact_merge_dialog.prepare_input()
        self.impact_merge_dialog.require_directory()

    def test_validate_all_layers(self):
        """Test validate_all_layers function."""
        # Test Entire Area mode
        self.mock_the_dialog(test_entire_mode=True)
        self.impact_merge_dialog.prepare_input()
        self.impact_merge_dialog.validate_all_layers()
        self.assertIn(
            'Detailed gender report',
            self.impact_merge_dialog.first_postprocessing_report)
        self.assertIn(
            'Detailed building type report',
            self.impact_merge_dialog.second_postprocessing_report)
        self.assertEqual(
            None,
            self.impact_merge_dialog.aggregation_attribute)

        # Test Aggregated Area mode
        self.mock_the_dialog(test_entire_mode=False)
        self.impact_merge_dialog.prepare_input()
        self.impact_merge_dialog.validate_all_layers()
        self.assertIn(
            'Detailed gender report',
            self.impact_merge_dialog.first_postprocessing_report)
        self.assertIn(
            'Detailed building type report',
            self.impact_merge_dialog.second_postprocessing_report)
        self.assertEqual(
            'KAB_NAME',
            self.impact_merge_dialog.aggregation_attribute)

    def test_merge(self):
        """Test merge function."""
        # Test Entire Area merged
        self.mock_the_dialog(test_entire_mode=True)
        self.impact_merge_dialog.prepare_input()
        self.impact_merge_dialog.validate_all_layers()
        self.impact_merge_dialog.merge()
        # There should be 1 pdf files in self.impact_merge_dialog.out_dir
        report_list = glob(
            os.path.join(
                self.impact_merge_dialog.out_dir,
                '*.pdf'))
        expected_reports_number = 1
        self.assertEqual(len(report_list), expected_reports_number)

        # Test Aggregated Area merged
        self.mock_the_dialog(test_entire_mode=False)
        self.impact_merge_dialog.prepare_input()
        self.impact_merge_dialog.validate_all_layers()
        self.impact_merge_dialog.merge()
        # There should be 3 pdf files in self.impact_merge_dialog.out_dir
        report_list = glob(
            os.path.join(
                self.impact_merge_dialog.out_dir,
                '*.pdf'))
        expected_reports_number = 3
        self.assertEqual(len(report_list), expected_reports_number)

if __name__ == '__main__':
    suite = unittest.makeSuite(ImpactMergeDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
