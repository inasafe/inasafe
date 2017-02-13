# coding=utf-8
"""Test Impact Report."""

import io
import os
import shutil
import unittest
from collections import OrderedDict

from jinja2.environment import Template

from safe.common.utilities import safe_dir
from safe.definitions.constants import ANALYSIS_SUCCESS
from safe.impact_function.impact_function import ImpactFunction
from safe.report.report_metadata import ReportMetadata
from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer,
    load_test_raster_layer)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import QgsMapLayerRegistry
from safe.definitions.report import (
    report_a4_blue,
    standard_impact_report_metadata_html,
    standard_impact_report_metadata_pdf,
    analysis_result_component,
    action_checklist_component,
    notes_assumptions_component,
    analysis_breakdown_component,
    aggregation_result_component,
    minimum_needs_component,
    aggregation_postprocessors_component,
    population_infographic_component)
from safe.report.impact_report import ImpactReport

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = ':%H$'


class TestImpactReport(unittest.TestCase):
    """Test Impact Report."""

    maxDiff = None

    @classmethod
    def fixtures_dir(cls, path):
        directory_name = os.path.dirname(__file__)
        return os.path.join(directory_name, 'fixtures', path)

    def assertCompareFileControl(self, control_path, actual_path):
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

    def setUp(self):
        self.maxDiff = None

    def test_analysis_result_from_impact_function(self):
        """Test generate analysis result from impact function."""

        output_folder = self.fixtures_dir('../output/analysis_result')

        # Classified vector with building-points
        shutil.rmtree(output_folder, ignore_errors=True)

        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_function = ImpactFunction()
        impact_function.aggregation = aggregation_layer
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
            analysis_result_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'header': u'Analysis Results',
            'title': u'In the event of a Generic, how many Structures might '
                     u'be affected?',
            'summary': [
                {
                    'header_label': u'Hazard Zone',
                    'rows': [
                        {
                            'value': '10',
                            'name': u'High hazard zone',
                            'key': 'high'
                        },
                        {
                            'value': '10',
                            'name': u'Medium hazard zone',
                            'key': 'medium'
                        },
                        {
                            'value': 0,
                            'name': u'Low hazard zone',
                            'key': 'low'
                        }
                    ],
                    'value_label': 'Count'
                },
                {
                    'header_label': u'Structures',
                    'rows': [
                        {
                            'value': '10',
                            'name': u'Total Affected',
                            'key': 'total_affected_field'
                        },
                        {
                            'value': '0',
                            'name': u'Total Unaffected',
                            'key': 'total_unaffected_field'
                        },
                        {
                            'value': '10',
                            'name': u'Total Not Exposed',
                            'key': 'total_not_exposed_field',
                        },
                        {
                            'value': '10',
                            'name': u'Total',
                            'key': 'total_field'
                        }
                    ],
                    'value_label': 'Count'
                }
            ]
        }
        actual_context = analysis_summary.context

        self.assertDictEqual(expected_context, actual_context)
        self.assertTrue(
            analysis_summary.output, empty_component_output_message)

        # Check Action Notes
        action_notes = impact_report.metadata.component_by_key(
            action_checklist_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""
        expected_context = {
            'header': u'Action Checklist',
            'items': [
                u'Which structures have warning capacity (e.g. sirens or '
                u'speakers)?',
                u'Are the water and electricity services still operating?',
                u'Are the schools and hospitals still active?',
                u'Are the health centres still open?',
                u'Are the other public services accessible?',
                u'Which buildings will be evacuation centres?',
                u'Where will we locate the operations centre?',
                u'Where will we locate warehouse and/or distribution centres?'
            ]
        }
        actual_context = action_notes.context

        self.assertDictEqual(expected_context, actual_context)
        self.assertTrue(
            action_notes.output, empty_component_output_message)

        # Check notes assumptions
        notes_assumptions = impact_report.metadata.component_by_key(
            notes_assumptions_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'header': u'Notes and assumptions',
            'items': [
                u'The impacts on roads, people, buildings and other exposure '
                u'elements may be underestimated if the exposure data are '
                u'incomplete.',
                u'Structures overlapping the analysis extent may be assigned '
                u'a hazard status lower than that to which they are exposed '
                u'outside the analysis area.',
                u'Numbers reported for structures have been rounded to the '
                u'nearest 10 if the total is less than 1,000; nearest 100 if '
                u'more than 1,000and less than 100,000; and nearest 1000 if '
                u'more than 100,000.',
                u'Rounding is applied to all structure counts, which may '
                u'cause discrepancies between subtotals and totals.'
            ]
        }
        actual_context = notes_assumptions.context

        self.assertDictEqual(expected_context, actual_context)
        self.assertTrue(
            notes_assumptions.output, empty_component_output_message)

        """Check output generated"""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_analysis_breakdown_detail(self):
        """Test generate analysis breakdown and aggregation report."""
        output_folder = self.fixtures_dir('../output/analysis_breakdown')

        # Classified vector with buildings
        shutil.rmtree(output_folder, ignore_errors=True)

        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'buildings.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_function = ImpactFunction()
        impact_function.aggregation = aggregation_layer
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

        # Check Analysis Breakdown
        analysis_breakdown = impact_report.metadata.component_by_key(
            analysis_breakdown_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'header': u'Estimated number of Structures by type',
            'notes': u'Columns and rows containing only 0 or "No data" '
                     u'values are excluded from the tables.',
            'detail_table': {
                'headers': [
                    u'Structures type',
                    u'High hazard zone',
                    u'Medium hazard zone',
                    u'Total Affected',
                    u'Total Unaffected',
                    u'Total Not Exposed',
                    u'Total'
                ],
                'details': [
                    [u'government', '0', '10', '10', '0', '0', '10'],
                    [u'education', '10', '0', '10', '0', '10', '10'],
                    [u'other', '0', '10', '10', '0', '0', '10'],
                    [u'commercial', '10', '0', '10', '0', '0', '10'],
                    [u'health', '10', '0', '10', '0', '0', '10']
                ],
                'footers': [u'Total', '10', '10', '10', '0', '10', '10']
            }
        }
        actual_context = analysis_breakdown.context
        self.assertDictEqual(
            expected_context, actual_context)
        self.assertTrue(
            analysis_breakdown.output, empty_component_output_message)

        # Check Aggregate Report
        aggregate_result = impact_report.metadata.component_by_key(
            aggregation_result_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'notes': u'Columns and rows containing only 0 or "No data" '
                     u'values are excluded from the tables.',
            'aggregation_result': {
                'header_label': u'Aggregation area',
                'rows': [
                    {
                        'type_values': ['0', '10', '10', '10', '0'],
                        'total': '10',
                        'name': u'area 1'
                    },
                    {
                        'type_values': ['10', '0', '0', '0', '0'],
                        'total': '10',
                        'name': u'area 2'
                    },
                    {
                        'type_values': ['0', '0', '0', '10', '10'],
                        'total': '10',
                        'name': u'area 3'
                    }
                ],
                'type_header_labels': [
                    u'Government',
                    u'Other',
                    u'Commercial',
                    u'Education',
                    u'Health'
                ],
                'type_total_values': ['10', '10', '10', '10', '10'],
                'total_label': u'Total',
                'total_all': '10',
                'total_in_aggregation_area_label': u'Total'},
            'header': u'Aggregation Result'}
        actual_context = aggregate_result.context

        self.assertDictEqual(
            expected_context, actual_context)
        self.assertTrue(
            aggregate_result.output, empty_component_output_message)

        """Check output generated"""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    # expected to fail until postprocessor calculation in analysis
    # impacted is fixed
    @unittest.expectedFailure
    def test_minimum_needs(self):
        """Test generate minimum needs section."""

        output_folder = self.fixtures_dir('../output/minimum_needs')
        shutil.rmtree(output_folder, ignore_errors=True)

        # Minimum needs only occured when population is displaced
        # so, use flood hazard.
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
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

        # Check Minimum Needs
        minimum_needs = impact_report.metadata.component_by_key(
            minimum_needs_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'header': u'Minimum needs', 'needs': [
                {
                    'header': u'Relief items to be provided single',
                    'needs': [
                        {
                            'header': u'Toilets',
                            'value': 0
                        }],
                    'total_header': u'Total'
                },
                {
                    'header': u'Relief items to be provided weekly',
                    'needs': [
                        {
                            'header': u'Rice [kg]',
                            'value': 26
                        },
                        {
                            'header': u'Drinking Water [l]',
                            'value': 162
                        },
                        {
                            'header': u'Clean Water [l]',
                            'value': 623
                        },
                        {
                            'header': u'Family Kits',
                            'value': 1
                        }],
                    'total_header': u'Total'
                }
            ]
        }
        actual_context = minimum_needs.context

        self.assertDictEqual(expected_context, actual_context)
        self.assertTrue(
            minimum_needs.output, empty_component_output_message)

        """Check generated report"""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    # expected to fail until postprocessor calculation in analysis
    # impacted is fixed
    @unittest.expectedFailure
    def test_aggregate_post_processors_vector(self):
        """Test generate aggregate postprocessors sections."""

        output_folder = self.fixtures_dir(
            '../output/aggregate_post_processors')
        shutil.rmtree(output_folder, ignore_errors=True)

        # Only flood and earthquake who deals with evacuated population report
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_vector_layer(
            'exposure', 'census.geojson')
        # We have to use aggregation layer now, because gender/age ratio is
        # there
        aggregation_layer = load_test_vector_layer(
            'aggregation', 'grid_jakarta.geojson')

        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.aggregation = aggregation_layer
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

        # Check aggregation-postprocessors
        aggregation_postprocessors = impact_report.metadata.component_by_key(
            aggregation_postprocessors_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        # TODO: This has possible wrong number, expect to be fixed soon.
        expected_context = {
            'sections': OrderedDict(
                [
                    ('age', {
                        'header': u'Detailed Age Report',
                        'rows': [[u'area 1', 20, 3, 9, 1],
                                 [u'area 2', 20, 3, 9, 1],
                                 [u'area 3', 20, 3, 7, 1]],
                        'columns': [
                            u'Aggregation area',
                            u'Total Population',
                            u'Youth Count',
                            u'Adult Count',
                            u'Elderly Count'],
                        'totals': [
                            u'Total',
                            50,
                            9,
                            30,
                            3]
                    }),
                    ('gender', {
                         'header': u'Detailed Gender '
                                   u'Report',
                         'rows': [[u'area 1', 20, 7, 7],
                                  [u'area 2', 20, 7, 7],
                                  [u'area 3', 20, 6, 6]],
                         'columns': [
                             u'Aggregation area',
                             u'Total Population',
                             u'Female Count',
                             u'Male Count'],
                         'totals': [
                             u'Total',
                             50,
                             20,
                             20]
                    }),
                    ('minimum_needs', {
                        'header': u'Detailed Minimum Needs Report',
                        'rows': [[u'area 1', 15, 42, 262, 1005, 3, 0],
                                 [u'area 2', 15, 42, 262, 1005, 3, 0],
                                 [u'area 3', 12, 33, 210, 804, 2, 0]],
                        'columns': [
                            u'Aggregation area',
                            u'Total Population',
                            'Rice',
                            'Drinking Water',
                            'Clean Water',
                            'Family Kits',
                            'Toilets'],
                        'totals': [
                            u'Total',
                            50,
                            117,
                            734,
                            2814,
                            7,
                            1]
                    })
                ])
        }
        actual_context = aggregation_postprocessors.context

        self.assertDictEqual(expected_context, actual_context)
        self.assertTrue(
            aggregation_postprocessors.output, empty_component_output_message)

        """Check generated report"""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    # expected to fail until postprocessor calculation in analysis
    # impacted is fixed
    @unittest.expectedFailure
    def test_aggregate_post_processors_raster(self):
        """Test generate aggregate postprocessors sections."""

        output_folder = self.fixtures_dir(
            '../output/aggregate_post_processors')
        shutil.rmtree(output_folder, ignore_errors=True)

        # Only flood and earthquake who deals with evacuated population report
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_raster_layer(
            'exposure', 'pop_binary_raster_20_20.asc')
        # We have to use aggregation layer now, because gender/age ratio is
        # there
        aggregation_layer = load_test_vector_layer(
            'aggregation', 'grid_jakarta.geojson')

        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.aggregation = aggregation_layer
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

        # Check aggregation-postprocessors
        aggregation_postprocessors = impact_report.metadata.component_by_key(
            aggregation_postprocessors_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        # TODO: This has possible wrong number, expect to be fixed soon.
        expected_context = {
            'sections': OrderedDict(
                [
                    ('age', {
                        'header': u'Detailed Age Report',
                        'rows': [
                            [u'Entire Area', 10, 2, 6, 0]],
                        'columns': [
                            u'Aggregation area',
                            u'Total Population',
                            u'Youth Count',
                            u'Adult Count',
                            u'Elderly Count'],
                        'totals': [
                            u'Total',
                            10,
                            2,
                            6,
                            0]
                    }),
                    ('gender', {
                         'header': u'Detailed Gender '
                                   u'Report',
                         'rows': [
                             [u'Entire Area', 10, 4, 4]],
                         'columns': [
                             u'Aggregation area',
                             u'Total Population',
                             u'Female Count',
                             u'Male Count'],
                         'totals': [
                             u'Total',
                             10,
                             4,
                             4]
                    }),
                    ('minimum_needs', {
                        'header': u'Detailed Minimum Needs Report',
                        'rows': [
                            [u'Entire Area', 10, 25, 161, 616, 1, 0]],
                        'columns': [
                            u'Aggregation area',
                            u'Total Population',
                            'Rice',
                            'Drinking Water',
                            'Clean Water',
                            'Family Kits',
                            'Toilets'],
                        'totals': [
                            u'Total',
                            10,
                            25,
                            161,
                            616,
                            1,
                            0]
                    })
                ])
        }
        actual_context = aggregation_postprocessors.context

        self.assertDictEqual(
            expected_context, actual_context)
        self.assertTrue(
            aggregation_postprocessors.output, empty_component_output_message)

        """Check generated report"""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    # expected to fail until postprocessor calculation in analysis
    # impacted is fixed
    @unittest.expectedFailure
    def test_population_infographic(self):
        """Test population infographic generation."""
        output_folder = self.fixtures_dir(
            '../output/population_infographic')
        shutil.rmtree(output_folder, ignore_errors=True)

        # Only flood and earthquake who deals with evacuated population report
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_raster_layer(
            'exposure', 'pop_binary_raster_20_20.asc')
        # We have to use aggregation layer now, because gender/age ratio is
        # there
        aggregation_layer = load_test_vector_layer(
            'aggregation', 'grid_jakarta.geojson')

        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.aggregation = aggregation_layer
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

        # Check population infographic
        population_infographic = impact_report.metadata.component_by_key(
            population_infographic_component['key']).context
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        # TODO: This has possible wrong number, expect to be fixed soon.

        # Check population chart
        expected_context = {
            'data': [30, 125.88367290531815],
            'total_value': 155.883672905,
            'labels': [u'Wet', u'Total Unaffected'],
            'colors': [u'#f03b20', u'#1a9641'],
        }

        donut_context = population_infographic['sections'][
            'population_chart']['context']
        """:type: safe.report.extractors.infographic_elements.svg_charts.
            DonutChartContext"""

        actual_context = {
            'data': donut_context.data,
            'total_value': donut_context.total_value,
            'labels': donut_context.labels,
            'colors': donut_context.colors,
        }

        self.assertDictEqual(
            expected_context, actual_context)

        # Check people section
        expected_context = {
            'number': 30
        }

        people_context = population_infographic['sections']['people'][
            'items'][0]
        """:type: safe.report.extractors.infographics.PeopleInfographicElement
        """

        actual_context = {
            'number': people_context.number
        }

        self.assertDictEqual(
            expected_context, actual_context)

        # Check vulnerabilities section
        expected_context = {
            'items': [
                {
                    'header': 'Female',
                    'number': 80,
                    'percentage': 50.0,
                },
                {
                    'header': 'Youth',
                    'number': 40,
                    'percentage': 25.0,
                },
                {
                    'header': 'Adult',
                    'number': 100,
                    'percentage': 62.5,
                },
                {
                    'header': 'Elderly',
                    'number': 20,
                    'percentage': 12.5,
                }
            ]
        }

        vulnerabilities_context = population_infographic['sections'][
            'vulnerability']

        actual_context = {
            'items': [{
                'header': item.header,
                'number': item.number,
                'percentage': item.percentage
            } for item in vulnerabilities_context['items']]
        }

        self.assertDictEqual(
            expected_context, actual_context)

        # Check minimum needs section
        expected_context = {
            'items': [
                {
                    'header': 'Rice',
                    'number': 420,
                    'unit': 'kg/weekly',
                },
                {
                    'header': 'Drinking Water',
                    'number': 2600,
                    'unit': 'l/weekly',
                },
                {
                    'header': 'Clean Water',
                    'number': 10000,
                    'unit': 'l/weekly',
                },
                {
                    'header': 'Family Kits',
                    'number': 30,
                    'unit': 'units',
                },
                {
                    'header': 'Toilets',
                    'number': 10,
                    'unit': 'units',
                },
            ]
        }

        needs_context = population_infographic['sections'][
            'minimum_needs']

        actual_context = {
            'items': [{
                'header': item.header,
                'number': item.number,
                'percentage': item.percentage,
            } for item in needs_context['items']]
        }

        self.assertDictEqual(
            expected_context, actual_context)

        # Check output

        self.assertTrue(
            population_infographic.output, empty_component_output_message)

        """Check generated report"""

        output_path = impact_report.component_absolute_output_path(
            'infographic-layout')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_qgis_html_pdf_report(self):
        """Test generate analysis breakdown and aggregation report."""

        output_folder = self.fixtures_dir('../output/impact_summary_pdf')

        # Classified vector with buildings
        shutil.rmtree(output_folder, ignore_errors=True)

        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'buildings.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_function = ImpactFunction()
        impact_function.aggregation = aggregation_layer
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.prepare()
        return_code, message = impact_function.run()

        self.assertEqual(return_code, ANALYSIS_SUCCESS, message)

        report_metadata = ReportMetadata(
            metadata_dict=standard_impact_report_metadata_pdf)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_function=impact_function)
        impact_report.output_folder = output_folder
        return_code, message = impact_report.process_component()

        self.assertEqual(
            return_code, ImpactReport.REPORT_GENERATION_SUCCESS, message)

        output_path = impact_report.component_absolute_output_path(
            'impact-report-pdf')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_qgis_map_pdf_report(self):
        """Test generate analysis map report."""

        output_folder = self.fixtures_dir('../output/impact_map_pdf')

        # Classified vector with buildings
        shutil.rmtree(output_folder, ignore_errors=True)

        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'buildings.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_function = ImpactFunction()
        impact_function.aggregation = aggregation_layer
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.prepare()
        return_code, message = impact_function.run()

        self.assertEqual(return_code, ANALYSIS_SUCCESS, message)

        # insert layer to registry
        layer_registry = QgsMapLayerRegistry.instance()
        layer_registry.removeAllMapLayers()
        rendered_layer = impact_function.exposure_impacted
        layer_registry.addMapLayer(rendered_layer)

        # Create impact report
        report_metadata = ReportMetadata(
            metadata_dict=report_a4_blue)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_function=impact_function)
        impact_report.output_folder = output_folder

        impact_report.qgis_composition_context.extent = \
            rendered_layer.extent()

        return_code, message = impact_report.process_component()

        self.assertEqual(
            return_code, ImpactReport.REPORT_GENERATION_SUCCESS, message)

        output_path = impact_report.component_absolute_output_path(
            'a4-portrait-blue')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        output_path = impact_report.component_absolute_output_path(
            'a4-landscape-blue')

        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)
