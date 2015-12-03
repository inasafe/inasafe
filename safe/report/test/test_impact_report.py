# coding=utf-8
"""**Tests for report creation using composition.**

"""
__author__ = 'akbargumbira@gmail.com'
__date__ = '06/01/2015'
__copyright__ = ('Copyright 2013, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import os
import logging

LOGGER = logging.getLogger('InaSAFE')

from safe.common.utilities import temp_dir, unique_filename
from safe.utilities.resources import resources_path
from safe.test.utilities import load_layer, get_qgis_app, test_data_path
from safe.report.impact_report import ImpactReport
from safe.utilities.gis import qgis_version

from qgis.core import (
    QgsMapLayerRegistry,
    QgsRectangle)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class ImpactReportTest(unittest.TestCase):
    """Test the InaSAFE Map generator"""

    def setUp(self):
        """Setup fixture run before each tests"""
        # noinspection PyArgumentList,PyUnresolvedReferences
        layer_registry = QgsMapLayerRegistry.instance()
        layer_registry.removeAllMapLayers()

    def test_get_map_title(self):
        """Getting the map title from the keywords"""
        impact_layer_path = test_data_path(
            'impact', 'population_affected_entire_area.shp')
        layer, _ = load_layer(impact_layer_path)

        template = resources_path(
            'qgis-composer-templates', 'a4-portrait-blue.qpt')
        report = ImpactReport(IFACE, template, layer)
        title = report.map_title
        expected_title = 'People affected by flood prone areas'
        message = 'Expected: %s\nGot:\n %s' % (expected_title, title)
        self.assertEqual(title, expected_title, message)

    def test_handle_missing_map_title(self):
        """Missing map title from the keywords fails gracefully"""
        # Use hazard layer as it won't have 'map_title' keyword
        layer_path = test_data_path('hazard', 'tsunami_wgs84.tif')
        layer, _ = load_layer(layer_path)
        template = resources_path(
            'qgis-composer-templates', 'a4-portrait-blue.qpt')
        report = ImpactReport(IFACE, template, layer)
        title = report.map_title
        expected_title = None
        message = 'Expected: %s\nGot:\n %s' % (expected_title, title)
        self.assertEqual(title, expected_title, message)

    def test_missing_elements(self):
        """Test missing elements set correctly."""
        impact_layer_path = test_data_path(
            'impact', 'population_affected_entire_area.shp')
        layer, _ = load_layer(impact_layer_path)

        template = resources_path(
            'qgis-composer-templates', 'a4-portrait-blue.qpt')
        report = ImpactReport(IFACE, template, layer)
        # There are missing elements in the template
        component_ids = ['safe-logo', 'north-arrow', 'organisation-logo',
                         'impact-map', 'impact-legend',
                         'i-added-element-id-here-nooo']
        report.component_ids = component_ids
        expected_missing_elements = ['i-added-element-id-here-nooo']
        message = 'The missing_elements should be %s, but it returns %s' % (
            report.missing_elements, expected_missing_elements)
        self.assertEqual(
            expected_missing_elements, report.missing_elements, message)

    def test_print_default_template(self):
        """Test printing report to pdf using default template works."""
        impact_layer_path = test_data_path(
            'impact', 'population_affected_entire_area.shp')
        layer, _ = load_layer(impact_layer_path)
        # noinspection PyUnresolvedReferences,PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        # noinspection PyCallingNonCallable
        rect = QgsRectangle(106.8194, -6.2108, 106.8201, -6.1964)
        CANVAS.setExtent(rect)
        CANVAS.refresh()

        template = resources_path(
            'qgis-composer-templates', 'a4-portrait-blue.qpt')
        report = ImpactReport(IFACE, template, layer)
        out_path = unique_filename(
            prefix='map_default_template_test',
            suffix='.pdf',
            dir=temp_dir('test'))
        report.print_map_to_pdf(out_path)

        # Check the file exists
        message = 'Rendered output does not exist: %s' % out_path
        self.assertTrue(os.path.exists(out_path), message)

        # Check the file is not corrupt
        message = 'The output file %s is corrupt' % out_path
        out_size = os.stat(out_path).st_size
        self.assertTrue(out_size > 0, message)

        # Check the components in composition are default components
        if qgis_version() < 20500:
            safe_logo = report.composition.getComposerItemById(
                'inasafe-logo').pictureFile()
            north_arrow = report.composition.getComposerItemById(
                'north-arrow').pictureFile()
            org_logo = report.composition.getComposerItemById(
                'organisation-logo').pictureFile()
        else:
            safe_logo = report.composition.getComposerItemById(
                'white-inasafe-logo').picturePath()
            north_arrow = report.composition.getComposerItemById(
                'north-arrow').picturePath()
            org_logo = report.composition.getComposerItemById(
                'organisation-logo').picturePath()

        expected_safe_logo = resources_path(
            'img', 'logos', 'inasafe-logo-url-white.svg')
        expected_north_arrow = resources_path(
            'img', 'north_arrows', 'simple_north_arrow.png')
        expected_org_logo = resources_path('img', 'logos', 'supporters.png')

        message = (
            'The safe logo path is not the default one: %s isn\'t %s' %
            (expected_safe_logo, safe_logo))
        self.assertEqual(expected_safe_logo, safe_logo, message)

        message = 'The north arrow path is not the default one'
        self.assertEqual(expected_north_arrow, north_arrow, message)

        message = 'The organisation logo path is not the default one'
        self.assertEqual(expected_org_logo, org_logo, message)

    def test_custom_logo(self):
        """Test that setting user-defined logo works."""
        LOGGER.info('Testing custom_logo')
        impact_layer_path = test_data_path(
            'impact', 'population_affected_entire_area.shp')
        layer, _ = load_layer(impact_layer_path)
        # noinspection PyUnresolvedReferences,PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        # noinspection PyCallingNonCallable
        rect = QgsRectangle(106.8194, -6.2108, 106.8201, -6.1964)
        CANVAS.setExtent(rect)
        CANVAS.refresh()

        template = resources_path(
            'qgis-composer-templates', 'a4-portrait-blue.qpt')
        report = ImpactReport(IFACE, template, layer)

        # Set custom logo
        custom_logo_path = resources_path('img', 'logos', 'supporters.png')
        report.organisation_logo = custom_logo_path

        out_path = unique_filename(
            prefix='map_custom_logo_test', suffix='.pdf', dir=temp_dir('test'))
        report.print_map_to_pdf(out_path)

        # Check the file exists
        message = 'Rendered output does not exist: %s' % out_path
        self.assertTrue(os.path.exists(out_path), message)

        # Check the file is not corrupt
        message = 'The output file %s is corrupt' % out_path
        out_size = os.stat(out_path).st_size
        self.assertTrue(out_size > 0, message)

        # Check the organisation logo in composition sets correctly to
        # logo-flower
        if qgis_version() < 20500:
            custom_img_path = report.composition.getComposerItemById(
                'organisation-logo').pictureFile()
        else:
            custom_img_path = report.composition.getComposerItemById(
                'organisation-logo').picturePath()

        message = 'The custom logo path is not set correctly'
        self.assertEqual(custom_logo_path, custom_img_path, message)

    def Xtest_print_impact_table(self):
        """Test print impact table to pdf."""
        impact_layer_path = test_data_path(
            'impact', 'population_affected_entire_area.shp')
        layer, _ = load_layer(impact_layer_path)
        # noinspection PyUnresolvedReferences,PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        # noinspection PyCallingNonCallable
        rect = QgsRectangle(106.8194, -6.2108, 106.8201, -6.1964)
        CANVAS.setExtent(rect)
        CANVAS.refresh()

        template = resources_path(
            'qgis-composer-templates', 'a4-portrait-blue.qpt')
        report = ImpactReport(IFACE, template, layer)
        report.template = template  # just to cover set template
        out_path = unique_filename(
            prefix='test_print_impact_table',
            suffix='.pdf',
            dir=temp_dir('test'))
        report.print_impact_table(out_path)

        # Check the file exists
        message = 'Rendered output does not exist: %s' % out_path
        self.assertTrue(os.path.exists(out_path), message)

        # Check the file is not corrupt
        message = 'The output file %s is corrupt' % out_path
        out_size = os.stat(out_path).st_size
        self.assertTrue(out_size > 0, message)

    # This a dirty hack to exclude from Travis test.
    Xtest_print_impact_table.slow = True

if __name__ == '__main__':
    suite = unittest.makeSuite(ImpactReport)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
