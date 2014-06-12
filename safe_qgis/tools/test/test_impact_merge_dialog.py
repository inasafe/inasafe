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
__author__ = 'akbargumbira@gmail.com'
__date__ = '23/10/2013'
__copyright__ = ('Copyright 2013, Australia Indonesia Facility for '
                 'Disaster Reduction')

# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

import unittest
import logging

import os
from xml.dom import minidom
from glob import glob
import shutil

#noinspection PyPackageRequirements
from PyQt4 import QtCore

from qgis.core import (
    QgsMapLayerRegistry,
    QgsMapRenderer,
    QgsComposition)

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

#noinspection PyPackageRequirements
from safe_qgis.tools.impact_merge_dialog import ImpactMergeDialog
from safe_qgis.utilities.utilities_for_testing import load_layer
from safe_qgis.exceptions import (
    ReportCreationError,
    KeywordNotFoundError,
    InvalidLayerError)
from safe_qgis.safe_interface import (
    UNITDATA,
    temp_dir)

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
    """Test Impact Merge Dialog widget."""

    #noinspection PyPep8Naming
    def setUp(self):
        """Runs before each test."""
        #noinspection PyArgumentList
        self.map_layer_registry = QgsMapLayerRegistry.instance()
        self.register_layers()

        # Create Impact Merge Dialog
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

    #noinspection PyPep8Naming
    def tearDown(self):
        """Runs after each test."""
        # Remove Map Layers
        if len(self.map_layer_registry.mapLayers().values()) > 0:
            self.map_layer_registry.removeAllMapLayers()

        # Delete test dir
        #noinspection PyUnresolvedReferences
        test_impact_merge_dir = os.path.join(
            TEST_DATA_DIR, 'test-impact-merge')
        shutil.rmtree(test_impact_merge_dir)

    def register_layers(self):
        """Register needed layers to QgsMapLayerRegistry."""
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

        layer_list = [self.population_entire_jakarta_layer,
                      self.population_district_jakarta_layer,
                      self.building_entire_jakarta_layer,
                      self.building_district_jakarta_layer,
                      self.district_jakarta_layer]

        # noinspection PyArgumentList
        self.map_layer_registry.addMapLayers(layer_list)

    def mock_the_dialog(self, test_entire_mode):
        impact_layer_count = self.impact_merge_dialog.first_layer.count()
        aggregation_layer_count = \
            self.impact_merge_dialog.aggregation_layer.count()

        if test_entire_mode:
            # First impact layer = population entire
            # Second impact layer = buildings entire
            self.impact_merge_dialog.entire_area_mode = True
            # Set the current Index of the combobox
            for index in range(0, impact_layer_count):
                first_combobox = self.impact_merge_dialog.first_layer
                layer_source = first_combobox.itemData(index).source()
                if 'population_affected_entire_area' in layer_source:
                    self.impact_merge_dialog.first_layer.setCurrentIndex(
                        index)

            for index in range(0, impact_layer_count):
                second_combobox = self.impact_merge_dialog.second_layer
                layer_source = second_combobox.itemData(index).source()
                if 'buildings_inundated_entire_area' in layer_source:
                    self.impact_merge_dialog.second_layer.setCurrentIndex(
                        index)

            # Aggregation Layer = Entire Area
            for index in range(0, aggregation_layer_count):
                layer = \
                    self.impact_merge_dialog.aggregation_layer.itemData(
                        index, QtCore.Qt.UserRole)
                if layer is None:
                    self.impact_merge_dialog.aggregation_layer.\
                        setCurrentIndex(index)

            # Set Output Directory
            #noinspection PyUnresolvedReferences
            self.impact_merge_dialog.output_directory.setText(
                os.path.join(
                    TEST_DATA_DIR, 'test-impact-merge', 'entire'))
        else:
            self.impact_merge_dialog.entire_area_mode = False
            # Set the current Index of the combobox
            for index in range(0, impact_layer_count):
                first_combobox = self.impact_merge_dialog.first_layer
                layer_source = first_combobox.itemData(index).source()
                if 'population_affected_district_jakarta' in layer_source:
                    self.impact_merge_dialog.first_layer.setCurrentIndex(index)

            for index in range(0, impact_layer_count):
                second_combobox = self.impact_merge_dialog.second_layer
                layer_source = second_combobox.itemData(index).source()
                if 'buildings_inundated_district_jakarta' in layer_source:
                    self.impact_merge_dialog.second_layer.setCurrentIndex(
                        index)

            # Aggregation Layer = District Jakarta
            for index in range(0, aggregation_layer_count):
                layer = \
                    self.impact_merge_dialog.aggregation_layer.itemData(
                        index, QtCore.Qt.UserRole)
                if layer is not None:
                    self. \
                        impact_merge_dialog.aggregation_layer. \
                        setCurrentIndex(index)

            # Set output directory
            #noinspection PyUnresolvedReferences
            self.impact_merge_dialog.output_directory.setText(
                os.path.join(
                    TEST_DATA_DIR, 'test-impact-merge', 'aggregated'))

    def test_get_project_layers(self):
        """Test get_project_layers function."""
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
        # NORMAL CASE
        # Test Entire Area
        self.mock_the_dialog(test_entire_mode=True)
        self.impact_merge_dialog.prepare_input()

        # First impact layer should be the population entire
        first_layer_source = \
            self.impact_merge_dialog.first_impact['layer'].source()
        self.assertIn('population_affected_entire_area', first_layer_source)

        # Second impact layer should be the buildings entire
        second_layer_source = \
            self.impact_merge_dialog.second_impact['layer'].source()
        self.assertIn('buildings_inundated_entire_area', second_layer_source)

        # Chosen aggregaton layer must be none
        aggregation_layer = self.impact_merge_dialog.aggregation['layer']
        self.assertIsNone(aggregation_layer)

        # NORMAL CASE
        # Test Aggregated
        self.mock_the_dialog(test_entire_mode=False)
        self.impact_merge_dialog.prepare_input()

        # First impact layer should be the population entire
        first_layer_source = \
            self.impact_merge_dialog.first_impact['layer'].source()
        self.assertIn(
            'population_affected_district_jakarta',
            first_layer_source)

        # Second impact layer should be the population entire
        second_layer_source = \
            self.impact_merge_dialog.second_impact['layer'].source()
        self.assertIn(
            'buildings_inundated_district_jakarta',
            second_layer_source)

        # Chosen aggregaton layer must be not none
        aggregation_layer_source = \
            self.impact_merge_dialog.aggregation['layer'].source()
        self.assertIn('district_osm_jakarta', aggregation_layer_source)

        # FALL CASE
        # First layer combobox index < 0
        self.mock_the_dialog(test_entire_mode=True)
        self.impact_merge_dialog.first_layer.setCurrentIndex(-1)
        self.assertRaises(
            InvalidLayerError,
            self.impact_merge_dialog.prepare_input)

        # FALL CASE
        # Second layer combobox index < 0
        self.mock_the_dialog(test_entire_mode=True)
        self.impact_merge_dialog.second_layer.setCurrentIndex(-1)
        self.assertRaises(
            InvalidLayerError,
            self.impact_merge_dialog.prepare_input)

        # FALL CASE
        # First impact layer = second impact layer
        self.mock_the_dialog(test_entire_mode=True)
        self.impact_merge_dialog.first_layer.setCurrentIndex(1)
        self.impact_merge_dialog.second_layer.setCurrentIndex(1)
        self.assertRaises(
            InvalidLayerError,
            self.impact_merge_dialog.prepare_input)

    def test_require_directory(self):
        """Test require_directory function."""
        self.mock_the_dialog(test_entire_mode=True)
        self.impact_merge_dialog.prepare_input()
        self.impact_merge_dialog.require_directory()

    def test_validate_all_layers(self):
        """Test validate_all_layers function."""
        # NORMAL CASE
        # Test Entire Area mode
        self.mock_the_dialog(test_entire_mode=True)
        self.impact_merge_dialog.prepare_input()
        self.impact_merge_dialog.validate_all_layers()

        first_postprocessing_report = \
            self.impact_merge_dialog.first_impact['postprocessing_report']
        self.assertIn(
            'Detailed gender report',
            first_postprocessing_report)

        second_postprocessing_report = \
            self.impact_merge_dialog.second_impact['postprocessing_report']
        self.assertIn(
            'Detailed building type report',
            second_postprocessing_report)

        self.assertEqual(
            None,
            self.impact_merge_dialog.aggregation['aggregation_attribute'])

        # NORMAL CASE
        # Test Aggregated Area mode
        self.mock_the_dialog(test_entire_mode=False)
        self.impact_merge_dialog.prepare_input()
        self.impact_merge_dialog.validate_all_layers()
        first_postprocessing_report = \
            self.impact_merge_dialog.first_impact['postprocessing_report']
        self.assertIn(
            'Detailed gender report',
            first_postprocessing_report)
        second_postprocessing_report = \
            self.impact_merge_dialog.second_impact['postprocessing_report']
        self.assertIn(
            'Detailed building type report',
            second_postprocessing_report)
        self.assertEqual(
            'KAB_NAME',
            self.impact_merge_dialog.aggregation['aggregation_attribute'])

        # FALL CASE
        # There is no keyword post_processing in first_impact_layer
        self.mock_the_dialog(test_entire_mode=True)
        self.impact_merge_dialog.prepare_input()
        # Change first impact layer to aggregation layer that doesn't have the
        # keywords
        self.impact_merge_dialog.first_impact['layer'] = \
            self.district_jakarta_layer
        self.assertRaises(
            KeywordNotFoundError,
            self.impact_merge_dialog.validate_all_layers)

        # FALL CASE
        # There is no keyword post_processing in second_impact_layer
        self.mock_the_dialog(test_entire_mode=True)
        self.impact_merge_dialog.prepare_input()
        # Change second impact layer to aggregation layer that doesn't have the
        # keywords
        self.impact_merge_dialog.second_impact['layer'] = \
            self.district_jakarta_layer
        self.assertRaises(
            KeywordNotFoundError,
            self.impact_merge_dialog.validate_all_layers)

        # FALL CASE
        # There is no keyword 'aggregation attribute' in aggregation layer
        self.mock_the_dialog(test_entire_mode=False)
        self.impact_merge_dialog.prepare_input()
        # Change aggregation layer to impact layer that doesn't have the
        # keywords
        self.impact_merge_dialog.aggregation['layer'] = \
            self.population_district_jakarta_layer
        self.assertRaises(
            KeywordNotFoundError,
            self.impact_merge_dialog.validate_all_layers)

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

    def test_generate_report_dictionary_from_dom(self):
        """Test generate_report_dictionary_from_dom function."""
        self.mock_the_dialog(test_entire_mode=False)
        self.impact_merge_dialog.prepare_input()
        self.impact_merge_dialog.validate_all_layers()

        # Create the DOM
        first_postprocessing_report = \
            self.impact_merge_dialog.first_impact['postprocessing_report']
        second_postprocessing_report = \
            self.impact_merge_dialog.second_impact['postprocessing_report']
        first_report = (
            '<body>' +
            first_postprocessing_report +
            '</body>')
        second_report = (
            '<body>' +
            second_postprocessing_report +
            '</body>')

        # Now create a dom document for each
        first_document = minidom.parseString(first_report)
        second_document = minidom.parseString(second_report)
        tables = first_document.getElementsByTagName('table')
        tables += second_document.getElementsByTagName('table')

        report_dict = \
            self.impact_merge_dialog.generate_report_dictionary_from_dom(
                tables)
        # There should be 4 keys in that dict
        # (3 for each aggregation unit and 1 for total in aggregation unit)
        expected_number_of_keys = 4
        self.assertEqual(len(report_dict), expected_number_of_keys)

    def test_generate_report_summary(self):
        """Test generate_report_summary function."""
        self.mock_the_dialog(test_entire_mode=False)
        self.impact_merge_dialog.prepare_input()
        self.impact_merge_dialog.validate_all_layers()

        first_postprocessing_report = \
            self.impact_merge_dialog.first_impact['postprocessing_report']
        second_postprocessing_report = \
            self.impact_merge_dialog.second_impact['postprocessing_report']
        first_report = (
            '<body>' +
            first_postprocessing_report +
            '</body>')
        second_report = (
            '<body>' +
            second_postprocessing_report +
            '</body>')

        # Now create a dom document for each
        first_document = minidom.parseString(first_report)
        second_document = minidom.parseString(second_report)
        first_impact_tables = first_document.getElementsByTagName('table')
        second_impact_tables = second_document.getElementsByTagName('table')

        first_report_dict = \
            self.impact_merge_dialog.generate_report_dictionary_from_dom(
                first_impact_tables)
        second_report_dict = \
            self.impact_merge_dialog.generate_report_dictionary_from_dom(
                second_impact_tables)

        self.impact_merge_dialog.generate_report_summary(
            first_report_dict, second_report_dict)

        # There should be 4 keys in that dict
        # (3 for each aggregation unit and 1 for total in aggregation unit)
        expected_number_of_keys = 4
        self.assertEqual(len(self.impact_merge_dialog.summary_report),
                         expected_number_of_keys)

    def test_generate_html_reports(self):
        """Test generate_html_reports function."""
        self.mock_the_dialog(test_entire_mode=False)
        self.impact_merge_dialog.prepare_input()
        self.impact_merge_dialog.validate_all_layers()

        first_postprocessing_report = \
            self.impact_merge_dialog.first_impact['postprocessing_report']
        second_postprocessing_report = \
            self.impact_merge_dialog.second_impact['postprocessing_report']
        first_report = (
            '<body>' +
            first_postprocessing_report +
            '</body>')
        second_report = (
            '<body>' +
            second_postprocessing_report +
            '</body>')

        # Now create a dom document for each
        first_document = minidom.parseString(first_report)
        second_document = minidom.parseString(second_report)
        first_impact_tables = first_document.getElementsByTagName('table')
        second_impact_tables = second_document.getElementsByTagName('table')

        first_report_dict = \
            self.impact_merge_dialog.generate_report_dictionary_from_dom(
                first_impact_tables)
        second_report_dict = \
            self.impact_merge_dialog.generate_report_dictionary_from_dom(
                second_impact_tables)

        self.impact_merge_dialog.generate_html_reports(
            first_report_dict, second_report_dict)

        # There should be 4 HTML files generated on temp_dir()
        html_list = glob(
            os.path.join(temp_dir(), '*.html'))
        expected_html_number = 4
        self.assertEqual(len(html_list), expected_html_number)

    def test_generate_reports(self):
        """Test generate_reports function."""
        self.mock_the_dialog(test_entire_mode=False)
        self.impact_merge_dialog.prepare_input()
        self.impact_merge_dialog.validate_all_layers()

        # Create the DOM
        first_postprocessing_report = \
            self.impact_merge_dialog.first_impact['postprocessing_report']
        second_postprocessing_report = \
            self.impact_merge_dialog.second_impact['postprocessing_report']
        first_report = (
            '<body>' +
            first_postprocessing_report +
            '</body>')
        second_report = (
            '<body>' +
            second_postprocessing_report +
            '</body>')

        # Now create a dom document for each
        first_document = minidom.parseString(first_report)
        second_document = minidom.parseString(second_report)
        first_impact_tables = first_document.getElementsByTagName('table')
        second_impact_tables = second_document.getElementsByTagName('table')

        first_report_dict = \
            self.impact_merge_dialog.generate_report_dictionary_from_dom(
                first_impact_tables)
        second_report_dict = \
            self.impact_merge_dialog.generate_report_dictionary_from_dom(
                second_impact_tables)

        self.impact_merge_dialog.generate_report_summary(
            first_report_dict, second_report_dict)
        self.impact_merge_dialog.generate_html_reports(
            first_report_dict, second_report_dict)

        # Generate PDF Reports
        self.impact_merge_dialog.generate_reports()

        # There should be 3 pdf files in self.impact_merge_dialog.out_dir
        report_list = glob(
            os.path.join(
                self.impact_merge_dialog.out_dir,
                '*.pdf'))
        expected_reports_number = 3
        self.assertEqual(len(report_list), expected_reports_number)

    def test_load_template(self):
        """Test load_template function."""
        self.mock_the_dialog(test_entire_mode=False)
        self.impact_merge_dialog.prepare_input()
        self.impact_merge_dialog.validate_all_layers()

        # Setup Map Renderer and set all the layer
        renderer = QgsMapRenderer()
        layer_set = [self.impact_merge_dialog.first_impact['layer'].id(),
                     self.impact_merge_dialog.second_impact['layer'].id()]

        # If aggregated, append chosen aggregation layer
        if not self.impact_merge_dialog.entire_area_mode:
            layer_set.append(
                self.impact_merge_dialog.aggregation['layer'].id())

        # Set Layer set to renderer
        renderer.setLayerSet(layer_set)

        # NORMAL CASE: It can find the template
        # Create composition
        composition = self.impact_merge_dialog.load_template(renderer)
        # The type of this composition must be QgsComposition
        self.assertEqual(type(composition), QgsComposition)

        #FALL CASE: It cannot find the template
        self.impact_merge_dialog.template_path = '/it/will/fail/tmp.qpt'
        expected_message = 'Error loading template %s' % \
                           self.impact_merge_dialog.template_path
        with self.assertRaises(ReportCreationError) as context:
            self.impact_merge_dialog.load_template(renderer)
        self.assertEqual(context.exception.message, expected_message)

if __name__ == '__main__':
    suite = unittest.makeSuite(ImpactMergeDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
