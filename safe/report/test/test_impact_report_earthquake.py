# coding=utf-8

"""Unittest for Earthquake Report."""

import os

import io

import shutil
import unittest

from jinja2.environment import Template
from qgis.core import QgsCoordinateReferenceSystem

from safe.definitions.constants import ANALYSIS_SUCCESS
from safe.definitions.reports.components import (
    standard_impact_report_metadata_html,
    general_report_component,
    population_chart_svg_component, infographic_report)
from safe.impact_function.impact_function import ImpactFunction
from safe.report.impact_report import ImpactReport
from safe.report.report_metadata import ReportMetadata
from safe.test.utilities import (
    get_qgis_app,
    load_test_raster_layer)
from safe.utilities.resources import resources_path

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting='InaSAFETest')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


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
        current_directory = resources_path()
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
        impact_function.crs = QgsCoordinateReferenceSystem(4326)
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
        return_code, message = impact_report.process_components()

        self.assertEqual(
            return_code, ImpactReport.REPORT_GENERATION_SUCCESS, message)

        """Checking generated context."""
        empty_component_output_message = 'Empty component output'

        # Check Analysis Summary
        analysis_summary = impact_report.metadata.component_by_key(
            general_report_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'table_header': (
                u'Estimated Number of people affected per MMI intensity'),
            'header': u'General Report',
            'summary': [
                {
                    'header_label': u'Hazard Zone',
                    'rows': [
                        {'numbers': ['0'], 'name': u'X', 'key': 'X'},
                        {'numbers': ['0'], 'name': u'IX', 'key': 'IX'},
                        {'numbers': ['200'], 'name': u'VIII', 'key': 'VIII'},
                        {'numbers': ['0'], 'name': u'VII', 'key': 'VII'},
                        {'numbers': ['0'], 'name': u'VI', 'key': 'VI'},
                        {'numbers': ['0'], 'name': u'V', 'key': 'V'},
                        {'numbers': ['0'], 'name': u'IV', 'key': 'IV'},
                        {'numbers': ['0'], 'name': u'III', 'key': 'III'},
                        {'numbers': ['0'], 'name': u'II', 'key': 'II'},
                        {'numbers': ['0'], 'name': u'I', 'key': 'I'},
                        {
                            'as_header': True,
                            'key': 'total_exposed_field',
                            'name': u'Total Exposed',
                            'numbers': ['200']
                        }
                    ],
                    'value_labels': [u'Count']
                },
                {
                    'header_label': u'Population',
                    'rows': [
                        {
                            'numbers': ['200'],
                            'name': u'Affected',
                            'key': 'total_affected_field',
                        }, {
                            'key': 'total_not_affected_field',
                            'name': u'Not Affected',
                            'numbers': ['0']
                        }, {
                            'key': 'total_not_exposed_field',
                            'name': u'Not Exposed',
                            'numbers': ['0']},
                        {
                            'numbers': ['200'],
                            'name': u'Displaced',
                            'key': 'displaced_field'
                        }, {
                            'numbers': ['0 - 100'],
                            'name': u'Fatalities',
                            'key': 'fatalities_field'
                        }],
                    'value_labels': [u'Count']
                }
            ],
            'notes': [
                u'Exposed People: People who are present in hazard zones and '
                u'are thereby subject to potential losses. In InaSAFE, people '
                u'who are exposed are those people who are within the extent '
                u'of the hazard.',
                u'Affected People: People who are affected by a hazardous '
                u'event. People can be affected directly or indirectly. '
                u'Affected people may experience short-term or long-term '
                u'consequences to their lives, livelihoods or health and in '
                u'the economic, physical, social, cultural and environmental '
                u'assets. In InaSAFE, people who are killed during the event '
                u'are also considered affected.',
                u'Displaced People: Displaced people are people who, for '
                u'different reasons and circumstances because of risk or '
                u'disaster, have to leave their place of residence. '
                u'In InaSAFE, demographic and minimum needs reports are based '
                u'on displaced / evacuated people.'
            ]
        }
        actual_context = analysis_summary.context

        self.assertDictEqual(expected_context, actual_context)
        self.assertTrue(
            analysis_summary.output, empty_component_output_message)

        report_metadata = ReportMetadata(
            metadata_dict=infographic_report)
        infographic_impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_function=impact_function)

        infographic_impact_report.output_folder = output_folder
        return_code, message = infographic_impact_report.process_components()

        self.assertEqual(
            return_code, ImpactReport.REPORT_GENERATION_SUCCESS, message)

        # check population pie chart if we have 100% donut slice
        population_chart_svg = (
            infographic_impact_report.metadata.component_by_key(
                population_chart_svg_component['key'])
        )

        expected_slices = [
            {
                'value': 200,
                'show_label': True,
                'center': (224.0, 128.0),
                'stroke_opacity': 1,
                'path': 'M128.000000,0.000000a128.000000,128.000000 0 0 1 '
                        '0.000000,256.000000l-0.000000,-64.000000a64.000000,'
                        '64.000000 0 0 0 0.000000,-128.000000Z',
                'percentage': 100,
                'label': u'VIII',
                'stroke': u'#ff7000',
                'label_position': (256, 0),
                'fill': u'#ff7000'
            }, {
                'value': 100,
                'show_label': False,
                'center': (32.0, 128.0),
                'stroke_opacity': 1,
                'path': 'M128.000000,256.000000a128.000000,128.000000 0 0 1 '
                        '-0.000000,-256.000000l0.000000,64.000000a64.000000,'
                        '64.000000 0 0 0 0.000000,128.000000Z',
                'percentage': 50.0,
                'label': '',
                'stroke': u'#ff7000',
                'label_position': (256, 0),
                'fill': u'#ff7000'
            }, {
                'value': 0,
                'show_label': False,
                'center': (128.0, 224.0),
                'stroke_opacity': 1,
                'path': 'M128.000000,256.000000a128.000000,128.000000 0 0 1 '
                        '0.000000,0.000000l-0.000000,-64.000000a64.000000,'
                        '64.000000 0 0 0 0.000000,0.000000Z',
                'percentage': 0.0,
                'label': u'Total Not Affected',
                'stroke': '#fff',
                'label_position': (256, 0),
                'fill': u'#1a9641'
            }]

        actual_context = population_chart_svg.context['context']
        actual_slices = actual_context.slices

        self.assertEqual(expected_slices, actual_slices)
        self.assertTrue(
            population_chart_svg.output, empty_component_output_message)

        shutil.rmtree(output_folder, ignore_errors=True)
