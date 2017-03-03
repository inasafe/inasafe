# coding=utf-8
"""Unittest for Earthquake Report."""
import os

import io

import shutil
import unittest

from jinja2.environment import Template

from safe.common.utilities import safe_dir
from safe.definitions.constants import ANALYSIS_SUCCESS
from safe.definitions.reports.components import (
    standard_impact_report_metadata_html,
    general_report_component)
from safe.impact_function.impact_function import ImpactFunction
from safe.report.impact_report import ImpactReport
from safe.report.report_metadata import ReportMetadata
from safe.test.utilities import (
    get_qgis_app,
    load_test_raster_layer)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = ':%H$'


class TestEarthquakeReport(unittest.TestCase):

    """Test Earthquake Report.

    .. versionadded:: 4.0
    """

    maxDiff = None

    @classmethod
    def fixtures_dir(cls, path):
        """Helper to return fixture path."""
        directory_name = os.path.dirname(__file__)
        return os.path.join(directory_name, 'fixtures', path)

    def assert_compare_file_control(self, control_path, actual_path):
        """Helper to compare file."""
        current_directory = safe_dir(sub_dir='../resources')
        context = {
            'current_directory': current_directory
        }
        with open(control_path) as control_file:
            template_string = control_file.read()
            template = Template(template_string)
            control_string = template.render(context).strip()

        with io.open(actual_path, encoding='utf-8') as actual_file:
            actual_string = actual_file.read().strip()
            self.assertEquals(control_string, actual_string)

    def test_earthquake_population_without_aggregation(self):
        """Testing Earthquake in Population without aggregation.

        .. versionadded:: 4.0
        """
        output_folder = self.fixtures_dir('../output/earthquake_population')

        # Classified vector with building-points
        shutil.rmtree(output_folder, ignore_errors=True)

        hazard_layer = load_test_raster_layer(
            'hazard', 'earthquake.tif')
        exposure_layer = load_test_raster_layer(
            'exposure', 'pop_binary_raster_20_20.asc')

        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.prepare()
        return_code, message = impact_function.run()

        self.assertEqual(return_code, ANALYSIS_SUCCESS, message)

        report_metadata = ReportMetadata(
            metadata_dict=standard_impact_report_metadata_html)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_function=impact_function)
        impact_report.output_folder = output_folder
        return_code, message = impact_report.process_component()

        self.assertEqual(
            return_code, ImpactReport.REPORT_GENERATION_SUCCESS, message)

        """Checking generated context"""
        empty_component_output_message = 'Empty component output'

        # Check Analysis Summary
        analysis_summary = impact_report.metadata.component_by_key(
            general_report_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'table_header': u'Estimated Number of people',
            'header': u'General Report',
            'summary': [
                {
                    'header_label': u'Hazard Zone',
                    'rows': [{'value': '0', 'name': u'X', 'key': 'X'},
                             {'value': '0', 'name': u'IX', 'key': 'IX'},
                             {'value': '200', 'name': u'VIII', 'key': 'VIII'},
                             {'value': '0', 'name': u'VII', 'key': 'VII'},
                             {'value': '0', 'name': u'VI', 'key': 'VI'},
                             {'value': '0', 'name': u'V', 'key': 'V'},
                             {'value': '0', 'name': u'IV', 'key': 'IV'},
                             {'value': '0', 'name': u'III', 'key': 'III'},
                             {'value': '0', 'name': u'II', 'key': 'II'},
                             {'value': '0', 'name': u'I', 'key': 'I'}],
                    'value_label': u'Count'
                },
                {
                    'header_label': u'Population',
                    'rows': [{'value': '200',
                              'name': u'Displaced',
                              'key':
                                  'displaced_field'},
                             {'value': '0 - 100',
                              'name':
                                  u'Fatalities',
                              'key':
                                  'fatalities_field'}],
                    'value_label': u'Count'
                }
            ]
        }
        actual_context = analysis_summary.context

        self.assertDictEqual(expected_context, actual_context)
        self.assertTrue(
            analysis_summary.output, empty_component_output_message)

        shutil.rmtree(output_folder, ignore_errors=True)
