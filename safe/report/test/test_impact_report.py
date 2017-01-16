# coding=utf-8
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
    aggregation_postprocessors_component)
from safe.report.impact_report import ImpactReport

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = ':%H$'


class TestImpactReport(unittest.TestCase):
    @classmethod
    def fixtures_dir(cls, path):
        dirname = os.path.dirname(__file__)
        return os.path.join(dirname, 'fixtures', path)

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
        impact_report.process_component()

        """Checking generated context"""
        different_context_message = 'Different context generated'
        empty_component_output_message = 'Empty component output'

        # Check Analysis Summary
        analysis_summary = impact_report.metadata.component_by_key(
            analysis_result_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'header': u'Analysis Results',
            'title': u'Structures affected', 'summary': [
                {
                    'header_label': u'Hazard Zone',
                    'rows': [
                        {
                            'value': 4,
                            'name': u'Total High Hazard Zone',
                            'key': 'high'
                        },
                        {
                            'value': 1,
                            'name': u'Total Medium Hazard Zone',
                            'key': 'medium'
                        },
                        {
                            'value': 0,
                            'name': u'Total Low Hazard Zone',
                            'key': 'low'
                        }
                    ],
                    'value_label': u'Count'
                },
                {
                    'header_label': u'Structures',
                    'rows': [
                        {
                            'value': 5,
                            'name': u'Total Affected',
                            'key': 'total_affected_field'
                        },
                        {
                            'value': 4,
                            'name': u'Total Unaffected',
                            'key': 'total_unaffected_field'
                        },
                        {
                            'value': 9,
                            'name': u'Total',
                            'key': 'total_field'
                        }
                    ],
                    'value_label': u'Count'
                }
            ]
        }
        actual_context = analysis_summary.context

        self.assertDictEqual(
            expected_context, actual_context, different_context_message)
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

        self.assertDictEqual(
            expected_context, actual_context, different_context_message)
        self.assertTrue(
            action_notes.output, empty_component_output_message)

        # Check notes assumptions
        notes_assumptions = impact_report.metadata.component_by_key(
            notes_assumptions_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'header': u'Notes and assumptions',
            'items': [
                u'The impacts on roads, people, buildings and other '
                u'exposure elements may be underestimated if the exposure '
                u'data are incomplete.',
                u'Numbers reported for structures have not been rounded.'
            ]
        }
        actual_context = notes_assumptions.context

        self.assertDictEqual(
            expected_context, actual_context, different_context_message)
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
        impact_report.process_component()

        """Checking generated context"""
        different_context_message = 'Different context generated'
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
                'headers': [u'Structures type', u'High Hazard Zone',
                            u'Medium Hazard Zone', u'Total Affected',
                            u'Total Unaffected', u'Total'],
                'details': [[u'government', 0, 1, 1, 0, 1],
                            [u'health', 1, 0, 1, 0, 1],
                            [u'education', 2, 0, 2, 3, 5],
                            [u'other', 0, 1, 1, 0, 1],
                            [u'commercial', 1, 0, 1, 0, 1]],
                'footers': [u'Total', 4, 2, 6, 3, 9]
            }
        }
        actual_context = analysis_breakdown.context

        self.assertDictEqual(
            expected_context, actual_context, different_context_message)
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
                'rows': [{'type_values': [0, 1, 1, 1, 0],
                          'total': 3, 'name': u'area 1'},
                         {'type_values': [1, 0, 0, 0, 0],
                          'total': 1, 'name': u'area 2'},
                         {'type_values': [0, 0, 1, 0, 1],
                          'total': 2, 'name': u'area 3'}],
                'type_header_labels': [u'Government',
                                       u'Other',
                                       u'Education',
                                       u'Commercial',
                                       u'Health'],
                'type_total_values': [1, 1, 2, 1, 1],
                'total_label': u'Total',
                'total_all': 6,
                'total_in_aggregation': u'Total in aggregation areas'},
            'header': u'Aggregation Result'}
        actual_context = aggregate_result.context

        self.assertDictEqual(
            expected_context, actual_context, different_context_message)
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
        # tsunami raster with population raster
        shutil.rmtree(output_folder, ignore_errors=True)

        hazard_layer = load_test_raster_layer(
            'hazard', 'tsunami_wgs84.tif')
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
        impact_report.process_component()

        """Checking generated context"""
        different_context_message = 'Different context generated'
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

        self.assertDictEqual(
            expected_context, actual_context, different_context_message)
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

        # TODO: Should add with and without aggregation layer test

        output_folder = self.fixtures_dir(
            '../output/aggregate_post_processors')
        # tsunami raster with population raster
        shutil.rmtree(output_folder, ignore_errors=True)

        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'buildings.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

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
        impact_report.process_component()

        """Checking generated context"""
        different_context_message = 'Different context generated'
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

        self.assertDictEqual(
            expected_context, actual_context, different_context_message)
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

        # TODO: Should add with and without aggregation layer test

        output_folder = self.fixtures_dir(
            '../output/aggregate_post_processors')
        # tsunami raster with population raster
        shutil.rmtree(output_folder, ignore_errors=True)

        hazard_layer = load_test_raster_layer(
            'hazard', 'tsunami_wgs84.tif')
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
        impact_report.process_component()

        """Checking generated context"""
        different_context_message = 'Different context generated'
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
            expected_context, actual_context, different_context_message)
        self.assertTrue(
            aggregation_postprocessors.output, empty_component_output_message)

        """Check generated report"""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

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
        impact_report.process_component()

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

        impact_report.process_component()

        output_path = impact_report.component_absolute_output_path(
            'a4-portrait-blue')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        output_path = impact_report.component_absolute_output_path(
            'a4-landscape-blue')

        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)
