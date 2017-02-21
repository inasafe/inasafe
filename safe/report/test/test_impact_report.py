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
from safe.definitions.fields import (
    total_not_affected_field,
    total_affected_field,
    total_not_exposed_field,
    total_field)
from safe.definitions.hazard_classifications import flood_hazard_classes
from safe.impact_function.impact_function import ImpactFunction
from safe.report.report_metadata import ReportMetadata
from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer,
    load_test_raster_layer)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import QgsMapLayerRegistry
from safe.definitions.reports.components import (
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
        # change displacement rate so the result is easily distinguished
        self.default_displacement_rate = flood_hazard_classes['classes'][0][
            'displacement_rate']
        flood_hazard_classes['classes'][0][
            'displacement_rate'] = 0.90

    def tearDown(self):
        # restore displacement rate
        flood_hazard_classes['classes'][0][
            'displacement_rate'] = self.default_displacement_rate

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
            'header': u'Estimated number of buildings',
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
                            'name': u'Affected',
                            'key': total_affected_field['key']
                        },
                        {
                            'value': '0',
                            'name': u'Not Affected',
                            'key': total_not_affected_field['key']
                        },
                        {
                            'value': '10',
                            'name': u'Not Exposed',
                            'key': total_not_exposed_field['key']
                        },
                        {
                            'value': '10',
                            'name': u'Total',
                            'key': total_field['key']
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
                u'cause discrepancies between subtotals and totals.',

                u'The extent and severity of the mapped scenario or hazard '
                u'zones may not be consistent with future events.',

                u'The impacts on roads, people, buildings and '
                u'other exposure elements may differ from the '
                u'analysis results due to local conditions '
                u'such as terrain and infrastructure type.',

                u'The analysis extent is limited to the extent '
                u'of the aggregation layer or analysis extent. '
                u'Hazard and exposure data outside the '
                u'analysis extent are not included in the '
                u'impact layer, impact map or impact reports.'
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
                    u'Total Not Affected',
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

    def test_minimum_needs_outputs(self):
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
                            'value': '10'
                        }],
                    'total_header': u'Total'
                },
                {
                    'header': u'Relief items to be provided weekly',
                    'needs': [
                        {
                            'header': u'Rice [kg]',
                            'value': '60'
                        },
                        {
                            'header': u'Drinking Water [l]',
                            'value': '340'
                        },
                        {
                            'header': u'Clean Water [l]',
                            'value': '1,300'
                        },
                        {
                            'header': u'Family Kits',
                            'value': '10'
                        }],
                    'total_header': u'Total'
                }
            ]
        }
        actual_context = minimum_needs.context

        self.assertDictEqual(expected_context, actual_context)
        self.assertTrue(
            minimum_needs.output, empty_component_output_message)

        # test displacement rates notes, since it is only showed up when
        # the rates is used, such as in this minimum needs report
        notes_assumptions = impact_report.metadata.component_by_key(
            notes_assumptions_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = (
            'For this analysis, the following displacement rates were used: '
            'Wet - 90.00%, Dry - 0.00%')
        actual_context = notes_assumptions.context['items'][-1]
        self.assertEqual(expected_context.strip(), actual_context.strip())

        """Check generated report"""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_aggregation_area_result_using_entire_area(self):
        """Test generate aggregation area results.

        This test should not handle postprocessors (covered in other tests).
        """
        output_folder = self.fixtures_dir(
            '../output/aggregation_entire_area_result')
        shutil.rmtree(output_folder, ignore_errors=True)

        # Only flood and earthquake who deals with evacuated population report
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_vector_layer(
            'exposure', 'buildings.shp')
        # Check when we doesn't use aggregation area.
        # In other words, Entire Area aggregations.

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

        """Check generated context"""
        empty_component_output_message = 'Empty component output'

        aggregation_result = impact_report.metadata.component_by_key(
            aggregation_result_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'aggregation_result': {
                'header_label': u'Aggregation area',
                'rows': [
                    {
                        'type_values': ['10', '30', '10', '10', '10', '10'],
                        'total': '40',
                        'name': u'Entire Area'
                    }
                ],
                'type_header_labels': [
                    u'Government',
                    u'Residential',
                    u'Commercial',
                    u'Education',
                    u'Place of worship',
                    u'Health'
                ],
                'total_in_aggregation_area_label': u'Total',
                'total_label': u'Total',
                'total_all': '40',
                'type_total_values': ['10', '30', '10', '10', '10', '10']
            },
            'header': u'Aggregation Result',
            'notes': u'Columns and rows containing only 0 or "No data" '
                     u'values are excluded from the tables.'
        }

        actual_context = aggregation_result.context

        self.assertDictEqual(expected_context, actual_context)
        self.assertTrue(
            aggregation_result.output, empty_component_output_message)

        """Check generated report"""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_aggregation_area_result(self):
        """Test generate aggregation area results.

        This test should not handle postprocessors (covered in other tests).
        """
        output_folder = self.fixtures_dir(
            '../output/aggregation_area_result')
        shutil.rmtree(output_folder, ignore_errors=True)

        # Only flood and earthquake who deals with evacuated population report
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_vector_layer(
            'exposure', 'buildings.shp')
        # Check when we use aggregation area
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

        """Check generated context"""
        empty_component_output_message = 'Empty component output'

        aggregation_result = impact_report.metadata.component_by_key(
            aggregation_result_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'aggregation_result': {
                'header_label': u'Aggregation area',
                'rows': [
                    {
                        'type_values': ['10', '0', '0', '10', '10', '0'],
                        'total': '10',
                        'name': u'B'
                    },
                    {
                        'type_values': ['0', '10', '0', '0', '0', '0'],
                        'total': '10',
                        'name': u'C'
                    },
                    {
                        'type_values': ['10', '10', '0', '10', '10', '0'],
                        'total': '20',
                        'name': u'F'
                    },
                    {
                        'type_values': ['0', '20', '10', '0', '0', '10'],
                        'total': '20',
                        'name': u'G'
                    }
                ],
                'type_header_labels': [
                    u'Government',
                    u'Residential',
                    u'Commercial',
                    u'Education',
                    u'Place of worship',
                    u'Health'
                ],
                'total_in_aggregation_area_label': u'Total',
                'total_label': u'Total',
                'total_all': '40',
                'type_total_values': ['10', '30', '10', '10', '10', '10']
            },
            'header': u'Aggregation Result',
            'notes': u'Columns and rows containing only 0 or "No data" '
                     u'values are excluded from the tables.'
        }

        actual_context = aggregation_result.context

        self.assertDictEqual(expected_context, actual_context)
        self.assertTrue(
            aggregation_result.output, empty_component_output_message)

        """Check generated report"""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

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

        expected_context = {
            'sections': OrderedDict([
                ('age', {
                    'header': u'Detailed Age Report',
                    'notes': u'Columns and rows containing only 0 or "No '
                             u'data" values are excluded from the tables.',
                    'rows': [[u'B', '3,000', '670', '1,800', '230'],
                             [u'C', '7,200', '1,700', '4,300', '570'],
                             [u'F', '7,900', '1,800', '4,700', '620'],
                             [u'G', '10,600', '2,500', '6,300', '830']],
                    'columns': [u'Aggregation area', u'Total Population',
                                'Youth Displaced Count',
                                'Adult Displaced Count',
                                'Elderly Displaced Count'],
                    'totals': [
                        u'Total', '103,000', '6,600', '16,900', '2,300']}),
                ('gender', {
                    'header': u'Detailed Gender Report',
                    'notes': u'Columns and rows containing only 0 or "No '
                             u'data" values are excluded from the tables.',
                    'rows': [
                        [u'B', '3,000', '1,400', '1,100', '130'],
                        [u'C', '7,200', '3,300', '2,600', '310'],
                        [u'F', '7,900', '3,600', '2,800', '330'],
                        [u'G', '10,600', '4,800', '3,800', '440']],
                    'columns': [
                        u'Aggregation area',
                        u'Total Population',
                        'Female Displaced Count',
                        'Weekly Hygiene Packs',
                        'Additional Weekly Rice kg for Pregnant and '
                        'Lactating Women [kg]'],
                    'totals': [
                        u'Total', '103,000', '12,900', '10,200', '1,200']}),
                ('minimum_needs', {
                    'header': u'Detailed Minimum Needs Report',
                    'notes': u'Columns and rows containing only 0 or "No '
                             u'data" values are excluded from the tables.',
                    'rows': [
                        [u'B', '3,000', '7,400', '45,800', '176,000',
                         '530', '140'],
                        [u'C', '7,200', '18,200', '114,000', '434,000',
                         '1,300', '330'],
                        [u'F', '7,900', '19,800', '124,000', '473,000',
                         '1,500', '360'],
                        [u'G', '10,600', '26,500', '166,000', '634,000',
                         '1,900', '480']],
                    'columns': [
                        u'Aggregation area',
                        u'Total Population',
                        'Rice [kg]',
                        'Drinking Water [l]',
                        'Clean Water [l]',
                        'Family Kits',
                        'Toilets'],
                    'totals': [
                        u'Total',
                        '103,000',
                        '71,700',
                        '449,000',
                        '1,716,000',
                        '5,200',
                        '1,300']})]),
            'use_aggregation': True
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

    def test_aggregate_post_processors_raster(self):
        """Test generate aggregate postprocessors sections.

        This test is not using actual displacement rate in order to
        distinguish the result more clearly.
        """

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

        expected_context = {
            'sections': OrderedDict([
                ('age', {
                    'header': u'Detailed Age Report',
                    'notes': u'Columns and rows containing only 0 or "No '
                             u'data" values are excluded from the tables.',
                    'rows': [[u'C', '10', '10', '10', '0'],
                             [u'F', '10', '0', '10', '0'],
                             [u'G', '10', '10', '10', '0'],
                             [u'K', '10', '0', '10', '0']],
                    'columns': [u'Aggregation area', u'Total Population',
                                'Youth Displaced Count',
                                'Adult Displaced Count',
                                'Elderly Displaced Count'],
                    'totals': [u'Total', '30', '10', '20', '10']}),
                ('gender', {
                    'header': u'Detailed Gender Report',
                    'notes': u'Columns and rows containing only 0 or "No '
                             u'data" values are excluded from the tables.',
                    'rows': [[u'C', '10', '10', '10', '0'],
                             [u'F', '10', '10', '10', '0'],
                             [u'G', '10', '10', '10', '0']],
                    'columns': [u'Aggregation area', u'Total Population',
                                'Female Displaced Count',
                                'Weekly Hygiene Packs',
                                'Additional Weekly Rice kg for Pregnant and '
                                'Lactating Women [kg]'],
                    'totals': [u'Total', '30', '10', '10', '0']}),
                ('minimum_needs', {
                    'header': u'Detailed Minimum Needs Report',
                    'notes': u'Columns and rows containing only 0 or "No '
                             u'data" values are excluded from the tables.',
                    'rows': [
                        [u'B', '10', '10', '20', '80', '10', '10'],
                        [u'C', '10', '20', '90', '340', '10', '10'],
                        [u'D', '10', '10', '10', '20', '10', '10'],
                        [u'F', '10', '20', '70', '260', '10', '10'],
                        [u'G', '10', '20', '110', '420', '10', '10'],
                        [u'H', '10', '10', '20', '60', '10', '10'],
                        [u'K', '10', '10', '40', '130', '10', '10'],
                        [u'L', '10', '10', '20', '70', '10', '10']],
                    'columns': [u'Aggregation area',
                                u'Total Population',
                                'Rice [kg]',
                                'Drinking Water [l]',
                                'Clean Water [l]',
                                'Family Kits',
                                'Toilets'],
                    'totals': [u'Total', '30', '60', '350', '1,400', '10',
                               '10']
                })]),
            'use_aggregation': True
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

    def test_population_infographic(self):
        """Test population infographic generation.

        This test is not using actual displacement rate in order to
        distinguish the result more clearly.
        """
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
        # Check population infographic
        population_infographic = impact_report.metadata.component_by_key(
            population_infographic_component['key']).context
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        # Check population chart
        expected_context = {
            'data': [30, 40],
            'total_value': 70,
            'labels': [u'Wet', u'Total Not Affected'],
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
            'number': '30'
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
                    'header': u'Female',
                    'number': '10',
                    'percentage': '47.4',
                },
                {
                    'header': u'Youth',
                    'number': '10',
                    'percentage': '26.3',
                },
                {
                    'header': u'Adult',
                    'number': '20',
                    'percentage': '68.4',
                },
                {
                    'header': u'Elderly',
                    'number': '10',
                    'percentage': '5.3',
                }
            ]
        }

        vulnerabilities_context = population_infographic['sections'][
            'vulnerability']

        actual_context = {
            'items': [
                {
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
                    'number': '60',
                    'unit': 'kg/weekly',
                },
                {
                    'header': 'Drinking Water',
                    'number': '350',
                    'unit': 'l/weekly',
                },
                {
                    'header': 'Clean Water',
                    'number': '1,400',
                    'unit': 'l/weekly',
                },
                {
                    'header': 'Family Kits',
                    'number': '10',
                    'unit': 'units',
                },
                {
                    'header': 'Toilets',
                    'number': '10',
                    'unit': 'units',
                },
            ]
        }

        needs_context = population_infographic['sections'][
            'minimum_needs']

        actual_context = {
            'items': [
                {
                    'header': item.header,
                    'number': item.number,
                    'unit': item.unit,
                } for item in needs_context['items']]
        }

        self.assertDictEqual(
            expected_context, actual_context)

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
        rendered_layer = impact_function.impact
        for layer in impact_function.outputs:
            layer_registry.addMapLayer(layer)

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
        for path in output_path.itervalues():
            self.assertTrue(os.path.exists(path), msg=path)

        output_path = impact_report.component_absolute_output_path(
            'a4-landscape-blue')

        for path in output_path.itervalues():
            self.assertTrue(os.path.exists(path), msg=path)

        shutil.rmtree(output_folder, ignore_errors=True)
