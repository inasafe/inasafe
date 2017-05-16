# coding=utf-8
"""Unittest for Impact Report generation."""

import io
import os
import shutil
import unittest
from collections import OrderedDict

from copy import deepcopy
from jinja2.environment import Template

from safe.common.utilities import safe_dir
from safe.definitions.constants import ANALYSIS_SUCCESS
from safe.definitions.fields import (
    total_not_affected_field,
    total_affected_field,
    total_not_exposed_field,
    total_field)
from safe.definitions.field_groups import (
    age_displaced_count_group,
    gender_displaced_count_group,
    vulnerability_displaced_count_group)
from safe.definitions.hazard_classifications import flood_hazard_classes
from safe.impact_function.impact_function import ImpactFunction
from safe.report.report_metadata import ReportMetadata
from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer,
    load_test_raster_layer)
from safe.definitions.reports.components import (
    report_a4_blue,
    standard_impact_report_metadata_html,
    standard_impact_report_metadata_pdf,
    general_report_component,
    action_checklist_component,
    notes_assumptions_component,
    analysis_detail_component,
    aggregation_result_component,
    minimum_needs_component,
    aggregation_postprocessors_component,
    population_infographic_component, analysis_provenance_details_component)
from safe.report.impact_report import ImpactReport

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import QgsMapLayerRegistry

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestImpactReport(unittest.TestCase):

    """Test Impact Report.

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

    def setUp(self):
        """Executed before test method."""
        self.maxDiff = None
        # change displacement rate so the result is easily distinguished
        self.default_displacement_rate = flood_hazard_classes['classes'][0][
            'displacement_rate']
        flood_hazard_classes['classes'][0][
            'displacement_rate'] = 0.90

    def tearDown(self):
        """Executed after test method."""
        # restore displacement rate
        flood_hazard_classes['classes'][0][
            'displacement_rate'] = self.default_displacement_rate

    def run_impact_report_scenario(
            self, output_folder,
            report_metadata,
            hazard_layer,
            exposure_layer,
            aggregation_layer=None):
        """Method to automate scenario runs.

        :param output_folder: the output folder
        :type output_folder: str

        :param report_metadata: report metadata to generate
        :type report_metadata: dict

        :param hazard_layer: QgsMapLayer for hazard
        :type hazard_layer: qgis.core.QgsMapLayer

        :param exposure_layer: QgsMapLayer for exposure
        :type exposure_layer: qgis.core.QgsMapLayer

        :return: will return impact_report object
        :rtype: safe.report.impact_report.ImpactReport

        .. versionadded:: 4.0
        """
        # clear folders before use
        shutil.rmtree(output_folder, ignore_errors=True)

        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.aggregation = aggregation_layer
        impact_function.prepare()
        return_code, message = impact_function.run()

        self.assertEqual(return_code, ANALYSIS_SUCCESS, message)

        report_metadata = ReportMetadata(
            metadata_dict=report_metadata)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_function=impact_function)
        impact_report.output_folder = output_folder
        return_code, message = impact_report.process_component()

        self.assertEqual(
            return_code, ImpactReport.REPORT_GENERATION_SUCCESS, message)

        return impact_report

    def test_general_report_from_impact_function(self):
        """Test generate analysis result from impact function.

        .. versionadded:: 4.0
        """
        output_folder = self.fixtures_dir('../output/general_report')

        # Classified vector with building-points
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_report = self.run_impact_report_scenario(
            output_folder,
            standard_impact_report_metadata_html,
            hazard_layer, exposure_layer,
            aggregation_layer=aggregation_layer)

        """Checking generated context"""
        empty_component_output_message = 'Empty component output'

        # Check Analysis Summary
        analysis_summary = impact_report.metadata.component_by_key(
            general_report_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'header': u'General Report',
            'table_header': (
                u'Estimated Number of buildings affected per hazard zone'),
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
                        },
                        {
                            'value': '10',
                            'name': u'Total',
                            'as_header': True,
                            'key': total_field['key']
                        }
                    ],
                    'value_label': u'Count'
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
                        }
                    ],
                    'value_label': u'Count'
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
                {
                    'item_category': 'general',
                    'item_header': 'general checklist',
                    'item_list': [
                        'Which structures have warning capacity '
                        '(e.g. sirens or speakers)?',
                        'Are the water and electricity services '
                        'still operating?',
                        'Are the schools and hospitals still active?',
                        'Are the health centres still open?',
                        'Are the other public services accessible?',
                        'Which buildings will be evacuation centres?',
                        'Where will we locate the operations centre?',
                        'Where will we locate warehouse and/or '
                        'distribution centres?'
                    ]
                }
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

        # TODO: this test is fragile and will break whenever we change
        # definitions. TS. I reduced the test fragments to snippets which
        # will hopefully make things a little less fragile.
        expected_context = {
            u'impacts on roads, people, buildings',
            u'overlapping the analysis extent',
            u'more than 1,000 and less than 100,000',
            u'cause discrepancies',
            u'zones may not be consistent with future events',
            u'terrain and infrastructure type',
            u'analysis extent is limited',
            u'Hazard and exposure data outside'
        }
        actual_context = notes_assumptions.context
        for expected_item in expected_context:
            current_flag = False
            # Iterate to see if expected_item is in at least one of the
            # actual content items ...
            for actual_item in actual_context['items']:
                for item in actual_item['item_list']:
                    if expected_item in item:
                        current_flag = True
            # It was not found in any item :-(
            self.assertTrue(
                current_flag,
                '"%s" not found in %s' % (
                    expected_item, actual_context['items']))

        self.assertTrue(
            notes_assumptions.output, empty_component_output_message)

        """Check output generated"""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_analysis_detail(self):
        """Test generate analysis breakdown and aggregation report.

        .. versionadded:: 4.0
        """
        output_folder = self.fixtures_dir('../output/analysis_detail')

        # Classified vector with buildings
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'buildings.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_report = self.run_impact_report_scenario(
            output_folder,
            standard_impact_report_metadata_html,
            hazard_layer, exposure_layer,
            aggregation_layer=aggregation_layer)

        """Checking generated context"""
        empty_component_output_message = 'Empty component output'

        # Check Analysis Breakdown
        analysis_detail = impact_report.metadata.component_by_key(
            analysis_detail_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'header': u'Analysis Detail',
            'notes': u'Columns and rows containing only 0 or "No data" '
                     u'values are excluded from the tables.',
            'group_border_color': u'#36454f',
            'detail_header': {
                'total_header_index': 5,
                'breakdown_header_index': 0,
                'header_hazard_group': {
                    'not_affected': {
                        'header': u'Not affected',
                        'hazards': [],
                        'total': [u'Total Not Affected'],
                        'start_index': 4
                    },
                    'affected': {
                        'header': u'Affected',
                        'hazards': [
                            u'High hazard zone',
                            u'Medium hazard zone',
                            u'Low hazard zone'],
                        'total': [u'Total Affected'],
                        'start_index': 1
                    }
                }
            },
            'detail_table': {
                'table_header': u'Estimated Number of buildings by '
                                u'Structure type',
                'headers': [
                    u'Structure type',
                    {
                        'start': True, 'colspan': 3,
                        'name': u'High hazard zone',
                        'header_group': 'affected'
                    },
                    {
                        'start': False,
                        'name': u'Medium hazard zone',
                        'header_group': 'affected'
                    },
                    {
                        'start': False,
                        'name': u'Total Affected',
                        'header_group': 'affected'
                    },
                    {
                        'start': True, 'colspan': 1,
                        'name': u'Total Not Affected',
                        'header_group': 'not_affected'
                    },
                    u'Total Not Exposed', u'Total'
                ],
                'details': [
                    [
                        u'Education',
                        {
                            'value': '10',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'affected'
                        },
                        {
                            'value': '10',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'not_affected'
                        },
                        '10', '10'
                    ],
                    [
                        u'Health',
                        {
                            'value': '10',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'affected'
                        },
                        {
                            'value': '10',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'not_affected'
                        },
                        '0', '10'
                    ],
                    [
                        u'Government',
                        {
                            'value': '0',
                            'header_group': 'affected'
                        },
                        {
                            'value': '10',
                            'header_group': 'affected'
                        },
                        {
                            'value': '10',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'not_affected'
                        },
                        '0', '10'
                    ],
                    [
                        u'Commercial',
                        {
                            'value': '10',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'affected'
                        },
                        {
                            'value': '10',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'not_affected'
                        },
                        '0', '10'
                    ],
                    [
                        u'Other',
                        {
                            'value': '0',
                            'header_group': 'affected'
                        },
                        {
                            'value': '10',
                            'header_group': 'affected'
                        },
                        {
                            'value': '10',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'not_affected'
                        },
                        '0', '10'
                    ],
                ],
                'footers': [
                    u'Total', {
                        'value': '10',
                        'header_group': 'affected'
                    },
                    {
                        'value': '10',
                        'header_group': 'affected'
                    },
                    {
                        'value': '10',
                        'header_group': 'affected'
                    },
                    {
                        'value': '0',
                        'header_group': 'not_affected'
                    },
                    '10', '10'
                ]
            }
        }
        actual_context = analysis_detail.context
        self.assertDictEqual(
            expected_context, actual_context)
        self.assertTrue(
            analysis_detail.output, empty_component_output_message)

        # Check Aggregate Report
        aggregate_result = impact_report.metadata.component_by_key(
            aggregation_result_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'notes': u'Columns and rows containing only 0 or "No data" '
                     u'values are excluded from the tables.',
            'aggregation_result': {
                'table_header': u'Estimated Number of buildings by '
                                u'aggregation area',
                'header_label': u'Aggregation area',
                'rows': [
                    {
                        'type_values': ['10', '0', '0', '10', '10'],
                        'total': '10',
                        'name': u'area 1'
                    },
                    {
                        'type_values': ['0', '0', '10', '0', '0'],
                        'total': '10',
                        'name': u'area 2'
                    },
                    {
                        'type_values': ['10', '10', '0', '0', '0'],
                        'total': '10',
                        'name': u'area 3'
                    }
                ],
                'type_header_labels': [
                    u'Education',
                    u'Health',
                    u'Government',
                    u'Commercial',
                    u'Other',
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

    def test_analysis_provenance_details(self):
        """Test generate analysis provenance details section.

        .. versionadded: 4.0
        """
        output_folder = self.fixtures_dir('../output/general_report')

        # Classified vector with building-points
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_report = self.run_impact_report_scenario(
            output_folder,
            standard_impact_report_metadata_html,
            hazard_layer, exposure_layer,
            aggregation_layer=aggregation_layer)

        """Checking generated context"""
        empty_component_output_message = 'Empty component output'

        impact_table = impact_report.metadata.component_by_key(
            analysis_provenance_details_component['key'])

        expected_context = {
            'header': u'Analysis details',
            'details': OrderedDict(
                [
                    ('hazard', {
                        'header': u'Hazard source',
                        'provenance': u'classified_vector - '
                                      u'InaSAFE v4 GeoJSON test layer - '}),
                    ('exposure', {
                        'header':
                            u'Exposure '
                            u'source',
                        'provenance':
                            u'building-points - '
                            u'InaSAFE v4 GeoJSON test layer - '}),
                    ('aggregation', {
                        'header': u'Aggregation source',
                        'provenance': u'small grid - '
                                      u'InaSAFE v4 GeoJSON test layer - '}),
                    ('impact_function', {
                        'header': u'Impact Function',
                        'provenance': u'Hazard_Generic '
                                      u'Polygon On '
                                      u'Structure Point'})
                ])
        }

        actual_context = impact_table.context

        self.assertDictEqual(
            expected_context, actual_context)
        self.assertTrue(
            impact_table.output, empty_component_output_message)

        """Check output generated"""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_minimum_needs_outputs(self):
        """Test generate minimum needs section.

        .. versionadded:: 4.0
        """
        output_folder = self.fixtures_dir('../output/minimum_needs')

        # Minimum needs only occured when population is displaced
        # so, use flood hazard.
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_raster_layer(
            'exposure', 'pop_binary_raster_20_20.asc')

        impact_report = self.run_impact_report_scenario(
            output_folder,
            standard_impact_report_metadata_html,
            hazard_layer, exposure_layer)

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
                            'value': '0'
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
        actual_context = notes_assumptions.context['items'][-1]['item_list'][0]
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

        .. versionadded:: 4.0
        """
        output_folder = self.fixtures_dir(
            '../output/aggregation_entire_area_result')

        # Only flood and earthquake who deals with evacuated population report
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_vector_layer(
            'exposure', 'buildings.shp')
        # Check when we doesn't use aggregation area.
        # In other words, Entire Area aggregations.

        impact_report = self.run_impact_report_scenario(
            output_folder,
            standard_impact_report_metadata_html,
            hazard_layer, exposure_layer)

        """Check generated context"""
        empty_component_output_message = 'Empty component output'

        aggregation_result = impact_report.metadata.component_by_key(
            aggregation_result_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'aggregation_result': {
                'table_header': u'Estimated Number of buildings by '
                                u'aggregation area',
                'header_label': u'Aggregation area',
                'rows': [
                    {
                        'type_values': ['30', '10', '10', '10', '10', '10'],
                        'total': '40',
                        'name': u'Entire Area'
                    }
                ],
                'type_header_labels': [
                    u'Residential',
                    u'Education',
                    u'Health',
                    u'Place of worship',
                    u'Government',
                    u'Commercial',
                ],
                'total_in_aggregation_area_label': u'Total',
                'total_label': u'Total',
                'total_all': '40',
                'type_total_values': ['30', '10', '10', '10', '10', '10']
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

        .. versionadded:: 4.0
        """
        output_folder = self.fixtures_dir(
            '../output/aggregation_area_result')

        # Only flood and earthquake who deals with evacuated population report
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_vector_layer(
            'exposure', 'buildings.shp')
        # Check when we use aggregation area
        aggregation_layer = load_test_vector_layer(
            'aggregation', 'grid_jakarta.geojson')

        impact_report = self.run_impact_report_scenario(
            output_folder,
            standard_impact_report_metadata_html,
            hazard_layer, exposure_layer,
            aggregation_layer=aggregation_layer)

        """Check generated context"""
        empty_component_output_message = 'Empty component output'

        aggregation_result = impact_report.metadata.component_by_key(
            aggregation_result_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'aggregation_result': {
                'table_header': u'Estimated Number of buildings by '
                                u'aggregation area',
                'header_label': u'Aggregation area',
                'rows': [
                    {
                        'type_values': ['0', '10', '0', '10', '10', '0'],
                        'total': '10',
                        'name': u'B'
                    },
                    {
                        'type_values': ['10', '0', '0', '0', '0', '0'],
                        'total': '10',
                        'name': u'C'
                    },
                    {
                        'type_values': ['10', '10', '0', '10', '10', '0'],
                        'total': '20',
                        'name': u'F'
                    },
                    {
                        'type_values': ['20', '0', '10', '0', '0', '10'],
                        'total': '20',
                        'name': u'G'
                    }
                ],
                'type_header_labels': [
                    u'Residential',
                    u'Education',
                    u'Health',
                    u'Place of worship',
                    u'Government',
                    u'Commercial',
                ],
                'total_in_aggregation_area_label': u'Total',
                'total_label': u'Total',
                'total_all': '40',
                'type_total_values': ['30', '10', '10', '10', '10', '10']
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
        """Test generate aggregate postprocessors sections.

        .. versionadded:: 4.0
        """
        output_folder = self.fixtures_dir(
            '../output/aggregate_post_processors')

        # Only flood and earthquake who deals with evacuated population report
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_vector_layer(
            'exposure', 'census.geojson')
        # We have to use aggregation layer now, because gender/age ratio is
        # there
        aggregation_layer = load_test_vector_layer(
            'aggregation', 'grid_jakarta.geojson')

        impact_report = self.run_impact_report_scenario(
            output_folder,
            standard_impact_report_metadata_html,
            hazard_layer, exposure_layer,
            aggregation_layer=aggregation_layer)

        """Checking generated context"""
        empty_component_output_message = 'Empty component output'

        # Check aggregation-postprocessors
        aggregation_postprocessors = impact_report.metadata.component_by_key(
            aggregation_postprocessors_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        actual_context = aggregation_postprocessors.context
        expected_context = {
            'sections': OrderedDict([
                ('age', {
                    'header': u'Detailed Age Report',
                    'notes': [u'Columns and rows containing only 0 or "No '
                              u'data" values are excluded from the '
                              u'tables.'] + age_displaced_count_group['notes'],
                    'rows': [[u'B', '2,700', '660', '1,800', '240'],
                             [u'C', '6,500', '1,700', '4,300', '590'],
                             [u'F', '7,100', '1,800', '4,700', '640'],
                             [u'G', '9,500', '2,400', '6,300', '860']],
                    'columns': [u'Aggregation area',
                                u'Total Displaced Population',
                                {
                                    'start_group_header': True,
                                    'name': u'Youth Displaced Count',
                                    'group_header': u'Age breakdown '
                                                    u'(in affected area)'
                                },
                                {
                                    'start_group_header': False,
                                    'name': u'Adult Displaced Count',
                                    'group_header': u'Age breakdown '
                                                    u'(in affected area)'
                                },
                                {
                                    'start_group_header': False,
                                    'name': u'Elderly Displaced Count',
                                    'group_header': u'Age breakdown '
                                                    u'(in affected area)'
                                }],
                    'group_header_colspan': 3,
                    'totals': [
                        u'Total', '25,700', '6,400', '16,900', '2,400']}),
                ('gender', {
                    'header': u'Detailed Gender Report',
                    'notes': [u'Columns and rows containing only 0 or "No '
                              u'data" values are excluded from the '
                              u'tables.'] + (
                        gender_displaced_count_group['notes']),
                    'rows': [
                        [u'B', '2,700', '1,400'],
                        [u'C', '6,500', '3,300'],
                        [u'F', '7,100', '3,600'],
                        [u'G', '9,500', '4,800']],
                    'columns': [
                        u'Aggregation area',
                        u'Total Displaced Population',
                        {
                            'start_group_header': True,
                            'name': u'Female Displaced Count',
                            'group_header': u'Gender breakdown '
                                            u'(in affected area)'
                        }],
                    'group_header_colspan': 1,
                    'totals': [
                        u'Total', '25,700', '12,900']}),
                ('vulnerability', {
                    'header': u'Detailed Vulnerability Report',
                    'message': u'Vulnerability ratio not exists. '
                               u'No calculations produced.',
                    'empty': True
                }),
                ('minimum_needs', {
                    'header': u'Detailed Minimum Needs Report',
                    'notes': [u'Columns and rows containing only 0 or "No '
                              u'data" values are excluded from the tables.'],
                    'rows': [
                        [u'B', '2,700', '7,400', '45,800', '176,000',
                         '530', '130'],
                        [u'C', '6,500', '18,200', '114,000', '434,000',
                         '1,300', '330'],
                        [u'F', '7,100', '19,800', '124,000', '473,000',
                         '1,500', '360'],
                        [u'G', '9,500', '26,500', '166,000', '634,000',
                         '1,900', '480']],
                    'columns': [
                        u'Aggregation area',
                        u'Total Displaced Population',
                        {
                            'start_group_header': True,
                            'name': u'Rice [kg]',
                            'group_header': u'Minimum needs breakdown '
                                            u'(in affected area)'
                        },
                        {
                            'start_group_header': False,
                            'name': u'Drinking Water [l]',
                            'group_header': u'Minimum needs breakdown '
                                            u'(in affected area)'
                        },
                        {
                            'start_group_header': False,
                            'name': u'Clean Water [l]',
                            'group_header': u'Minimum needs breakdown '
                                            u'(in affected area)'
                        },
                        {
                            'start_group_header': False,
                            'name': u'Family Kits',
                            'group_header': u'Minimum needs breakdown '
                                            u'(in affected area)'
                        },
                        {
                            'start_group_header': False,
                            'name': u'Toilets',
                            'group_header': u'Minimum needs breakdown '
                                            u'(in affected area)'
                        }],
                    'group_header_colspan': 5,
                    'totals': [
                        u'Total',
                        '25,700',
                        '71,700',
                        '449,000',
                        '1,716,000',
                        '5,200',
                        '1,300']})]),
            'use_aggregation': True
        }

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

        .. versionadded:: 4.0
        """
        output_folder = self.fixtures_dir(
            '../output/aggregate_post_processors')

        # Only flood and earthquake who deals with evacuated population report
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_raster_layer(
            'exposure', 'pop_binary_raster_20_20.asc')
        # We have to use aggregation layer now, because gender/age ratio is
        # there
        aggregation_layer = load_test_vector_layer(
            'aggregation', 'grid_jakarta.geojson')

        impact_report = self.run_impact_report_scenario(
            output_folder,
            standard_impact_report_metadata_html,
            hazard_layer, exposure_layer,
            aggregation_layer=aggregation_layer)

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
                    'notes': [u'Columns and rows containing only 0 or "No '
                              u'data" values are excluded from the '
                              u'tables.'] + age_displaced_count_group['notes'],
                    'rows': [[u'B', '10', '0', '0', '0'],
                             [u'C', '10', '10', '10', '0'],
                             [u'F', '10', '0', '10', '0'],
                             [u'G', '10', '10', '10', '0'],
                             [u'K', '10', '0', '10', '0']],
                    'columns': [u'Aggregation area',
                                u'Total Displaced Population',
                                {
                                    'start_group_header': True,
                                    'name': u'Youth Displaced Count',
                                    'group_header': u'Age breakdown '
                                                    u'(in affected area)'
                                },
                                {
                                    'start_group_header': False,
                                    'name': u'Adult Displaced Count',
                                    'group_header': u'Age breakdown '
                                                    u'(in affected area)'
                                },
                                {
                                    'start_group_header': False,
                                    'name': u'Elderly Displaced Count',
                                    'group_header': u'Age breakdown '
                                                    u'(in affected area)'
                                }],
                    'group_header_colspan': 3,
                    'totals': [u'Total', '20', '10', '20', '10']}),
                ('gender', {
                    'header': u'Detailed Gender Report',
                    'notes': [u'Columns and rows containing only 0 or "No '
                              u'data" values are excluded from the '
                              u'tables.'] + (
                        gender_displaced_count_group['notes']),
                    'rows': [[u'B', '10', '0'],
                             [u'C', '10', '10'],
                             [u'F', '10', '10'],
                             [u'G', '10', '10'],
                             [u'K', '10', '0']],
                    'columns': [
                        u'Aggregation area',
                        u'Total Displaced Population',
                        {
                            'start_group_header': True,
                            'name': u'Female Displaced Count',
                            'group_header': u'Gender breakdown '
                                            u'(in affected area)'
                        }],
                    'group_header_colspan': 1,
                    'totals': [u'Total', '20', '10']}),
                ('vulnerability', {
                    'header': u'Detailed Vulnerability Report',
                    'message': u'Vulnerability ratio not exists. '
                               u'No calculations produced.',
                    'empty': True
                }),
                ('minimum_needs', {
                    'header': u'Detailed Minimum Needs Report',
                    'notes': [u'Columns and rows containing only 0 or "No '
                              u'data" values are excluded from the tables.'],
                    'rows': [
                        [u'B', '10', '10', '20', '80', '0', '0'],
                        [u'C', '10', '20', '90', '340', '0', '0'],
                        [u'F', '10', '10', '70', '260', '0', '0'],
                        [u'G', '10', '20', '110', '410', '10', '0'],
                        [u'K', '10', '10', '40', '130', '0', '0']],
                    'columns': [
                        u'Aggregation area',
                        u'Total Displaced Population',
                        {
                            'start_group_header': True,
                            'name': u'Rice [kg]',
                            'group_header': u'Minimum needs breakdown '
                                            u'(in affected area)'
                        },
                        {
                            'start_group_header': False,
                            'name': u'Drinking Water [l]',
                            'group_header': u'Minimum needs breakdown '
                                            u'(in affected area)'
                        },
                        {
                            'start_group_header': False,
                            'name': u'Clean Water [l]',
                            'group_header': u'Minimum needs breakdown '
                                            u'(in affected area)'
                        },
                        {
                            'start_group_header': False,
                            'name': u'Family Kits',
                            'group_header': u'Minimum needs breakdown '
                                            u'(in affected area)'
                        },
                        {
                            'start_group_header': False,
                            'name': u'Toilets',
                            'group_header': u'Minimum needs breakdown '
                                            u'(in affected area)'
                        }],
                    'group_header_colspan': 5,
                    'totals': [u'Total', '20', '60', '350', '1,400', '10', '0']
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

        .. versionadded:: 4.0
        """
        output_folder = self.fixtures_dir(
            '../output/population_infographic')

        # Only flood and earthquake who deals with evacuated population report
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_raster_layer(
            'exposure', 'pop_binary_raster_20_20.asc')
        # We have to use aggregation layer now, because gender/age ratio is
        # there
        aggregation_layer = load_test_vector_layer(
            'aggregation', 'grid_jakarta.geojson')

        impact_report = self.run_impact_report_scenario(
            output_folder,
            standard_impact_report_metadata_html,
            hazard_layer, exposure_layer,
            aggregation_layer=aggregation_layer)

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

        # Check people section affected
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

        # Check people section displaced
        expected_context = {
            'number': '20'
        }

        people_context = population_infographic['sections']['people'][
            'items'][1]
        """:type: safe.report.extractors.infographics.PeopleInfographicElement
        """

        actual_context = {
            'number': people_context.number
        }

        self.assertDictEqual(
            expected_context, actual_context)

        # Check vulnerabilities section
        expected_context = {
            'header': u'Vulnerability',
            'small_header': u'from 20 displaced',
            'items': [
                {
                    'bootstrap_column': 'col-xs-3',
                    'element_column': 'col-xs-12',
                    'group_header': u'Gender group',
                    'items': [
                        {
                            'header': u'Female',
                            'header_note': None,
                            'number': '10',
                            'percentage': '47.4',
                        },
                    ]
                },
                {
                    'bootstrap_column': 'col-xs-9',
                    'element_column': 'col-xs-4',
                    'group_header': u'Age group',
                    'items': [
                        {
                            'header': u'Youth',
                            'header_note': None,
                            'number': '10',
                            'percentage': '21.1',
                        },
                        {
                            'header': u'Adult',
                            'header_note': None,
                            'number': '20',
                            'percentage': '68.4',
                        },
                        {
                            'header': u'Elderly',
                            'header_note': None,
                            'number': '10',
                            'percentage': '5.3',
                        }
                    ]
                },
            ]
        }

        vulnerabilities_context = population_infographic['sections'][
            'vulnerability']

        actual_context = deepcopy(vulnerabilities_context)
        actual_context['items'] = [
            {
                'bootstrap_column': group['bootstrap_column'],
                'element_column': group['element_column'],
                'group_header': group['group_header'],
                'items': [
                    {
                        'header': item.header,
                        'header_note': None,
                        'number': item.number,
                        'percentage': item.percentage,
                    } for item in group['items']
                ]
            } for group in vulnerabilities_context['items']
        ]

        self.assertDictEqual(
            expected_context, actual_context)

        # Check minimum needs section
        expected_context = {
            'items': [
                {
                    'header': u'Rice',
                    'number': '60',
                    'unit': u'kg/weekly',
                },
                {
                    'header': u'Drinking Water',
                    'number': '350',
                    'unit': u'l/weekly',
                },
                {
                    'header': u'Clean Water',
                    'number': '1,400',
                    'unit': u'l/weekly',
                },
                {
                    'header': u'Family Kits',
                    'number': '10',
                    'unit': u'units',
                },
                {
                    'header': 'Toilets',
                    'number': '0',
                    'unit': u'units',
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
        """Test generate analysis breakdown and aggregation report.

        .. versionadded:: 4.0
        """
        output_folder = self.fixtures_dir('../output/impact_summary_pdf')

        # Classified vector with buildings
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'buildings.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_report = self.run_impact_report_scenario(
            output_folder,
            standard_impact_report_metadata_pdf,
            hazard_layer, exposure_layer,
            aggregation_layer=aggregation_layer)

        output_path = impact_report.component_absolute_output_path(
            'impact-report-pdf')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_qgis_map_pdf_report(self):
        """Test generate analysis map report.

        .. versionadded:: 4.0
        """
        output_folder = self.fixtures_dir('../output/impact_map_pdf')

        # Classified vector with buildings
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
        layer_registry.addMapLayers(
            [hazard_layer, exposure_layer, aggregation_layer])
        rendered_layer = impact_function.impact
        layer_registry.addMapLayers(impact_function.outputs)

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
