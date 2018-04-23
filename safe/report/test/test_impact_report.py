# coding=utf-8
"""Unittest for Impact Report generation."""

import io
import json
import os
import shutil
import unittest
from collections import OrderedDict
from osgeo import gdal
from qgis.core import QGis

from copy import deepcopy
from jinja2.environment import Template

from PyQt4.Qt import PYQT_VERSION_STR
from PyQt4.QtCore import QT_VERSION_STR

from safe.common.version import get_version
from safe.definitions.constants import (
    ANALYSIS_SUCCESS, PREPARE_SUCCESS, INASAFE_TEST)
from safe.definitions.fields import (
    total_not_affected_field,
    total_affected_field,
    total_not_exposed_field,
    total_exposed_field)
from safe.definitions.field_groups import (
    age_displaced_count_group,
    gender_displaced_count_group)
from safe.definitions.hazard_classifications import flood_hazard_classes
from safe.definitions.hazard import hazard_flood
from safe.definitions.provenance import provenance_use_rounding
from safe.gis.tools import full_layer_uri
from safe.impact_function.impact_function import ImpactFunction
from safe.impact_function.multi_exposure_wrapper import \
    MultiExposureImpactFunction
from safe.report.report_metadata import ReportMetadata
from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer,
    load_test_raster_layer)
from safe.utilities.utilities import readable_os_version
from safe.definitions.reports.components import (
    map_report,
    standard_impact_report_metadata_html,
    standard_impact_report_metadata_pdf,
    general_report_component,
    action_checklist_component,
    notes_assumptions_component,
    analysis_detail_component,
    aggregation_result_component,
    minimum_needs_component,
    aggregation_postprocessors_component,
    population_infographic_component,
    analysis_provenance_details_component,
    analysis_provenance_details_simplified_component,
    standard_multi_exposure_impact_report_metadata_html)
from safe.definitions.utilities import update_template_component
from safe.report.impact_report import ImpactReport
from safe.utilities.resources import resources_path
from safe.definitions.utilities import (
    get_displacement_rate, generate_default_profile, is_affected)
from safe.utilities.settings import setting, set_setting, delete_setting

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from qgis.core import QgsMapLayerRegistry, QgsCoordinateReferenceSystem

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
        directory_name = os.path.join('fixture', path)
        return os.path.abspath(directory_name)

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

    def setUp(self):
        """Executed before test method."""
        self.maxDiff = None
        self.custom_displacement_rate = 0.90

        # Change displacement rate so the result is easily distinguished
        self.default_displacement_rate = flood_hazard_classes['classes'][0][
            'displacement_rate']

        # Preserve profile from setting
        self.original_profile = setting(
            key='population_preference', default='NO_PROFILE')
        # Set new profile in the QSettings
        current_profile = generate_default_profile()
        current_profile[hazard_flood['key']][flood_hazard_classes['key']][
            'wet']['displacement_rate'] = self.custom_displacement_rate
        set_setting(key='population_preference', value=current_profile)

    def tearDown(self):
        """Executed after test method."""
        # Restore displacement rate
        flood_hazard_classes['classes'][0][
            'displacement_rate'] = self.default_displacement_rate

        # Set the profile to the original one
        if self.original_profile == 'NO_PROFILE':
            delete_setting('population_preference')
        else:
            set_setting('population_preference', self.original_profile)

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
        if aggregation_layer:
            impact_function.aggregation = aggregation_layer
        else:
            impact_function.crs = QgsCoordinateReferenceSystem(4326)
        impact_function.prepare()
        return_code, message = impact_function.run()

        self.assertEqual(return_code, ANALYSIS_SUCCESS, message)

        components = [report_metadata]
        ordered_layers = [
            full_layer_uri(impact_function.aggregation_summary),
            full_layer_uri(impact_function.hazard)
        ]
        return_code, message = impact_function.generate_report(
            components,
            output_folder=output_folder,
            iface=IFACE,
            ordered_layers_uri=ordered_layers)

        self.assertEqual(
            return_code, ImpactReport.REPORT_GENERATION_SUCCESS, message)

        return impact_function._impact_report

    def run_multi_exposure_impact_function_scenario(
            self, output_folder,
            report_metadata,
            hazard_layer,
            exposure_layers,
            aggregation_layer=None):
        """Method to automate scenario runs.

        :param output_folder: the output folder
        :type output_folder: str

        :param report_metadata: report metadata to generate
        :type report_metadata: dict

        :param hazard_layer: QgsMapLayer for hazard
        :type hazard_layer: qgis.core.QgsMapLayer

        :param exposure_layer: List of QgsMapLayer for exposure
        :type exposure_layer: list

        :return: will return impact_report object
        :rtype: safe.report.impact_report.ImpactReport

        .. versionadded:: 4.3
        """
        # clear folders before use
        shutil.rmtree(output_folder, ignore_errors=True)

        impact_function = MultiExposureImpactFunction()
        impact_function.hazard = hazard_layer
        impact_function.exposures = exposure_layers
        if aggregation_layer:
            impact_function.aggregation = aggregation_layer
        else:
            impact_function.crs = QgsCoordinateReferenceSystem(4326)

        code, message = impact_function.prepare()
        self.assertEqual(code, PREPARE_SUCCESS, message)

        code, message, exposure = impact_function.run()
        self.assertEqual(code, ANALYSIS_SUCCESS, message)

        components = [report_metadata]
        ordered_layers = [
            full_layer_uri(impact_function.aggregation_summary),
            full_layer_uri(impact_function.hazard)
        ]
        return_code, message = impact_function.generate_report(
            components,
            output_folder=output_folder,
            iface=IFACE,
            ordered_layers_uri=ordered_layers)

        self.assertEqual(
            return_code, ImpactReport.REPORT_GENERATION_SUCCESS, message)

        return impact_function._impact_report

    def test_general_report_from_impact_function(self):
        """Test generate analysis result from impact function.

        .. versionadded:: 4.0
        """
        output_folder = os.path.join('..', 'output', 'general_report')
        output_folder = self.fixtures_dir(output_folder)

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

        """Checking generated context."""
        empty_component_output_message = 'Empty component output'

        # Check Analysis Summary
        analysis_summary = impact_report.metadata.component_by_key(
            general_report_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'component_key': 'general-report',
            'header': u'General Report',
            'table_header': (
                u'Estimated Number of structures affected per hazard zone'),
            'summary': [
                {
                    'header_label': u'Hazard Zone',
                    'rows': [
                        {
                            'numbers': ['4'],
                            'name': u'High',
                            'key': 'high'
                        },
                        {
                            'numbers': ['1'],
                            'name': u'Medium',
                            'key': 'medium'
                        },
                        {
                            'numbers': ['0'],
                            'name': u'Low',
                            'key': 'low'
                        },
                        {
                            'numbers': ['5'],
                            'name': u'Total Exposed',
                            'as_header': True,
                            'key': total_exposed_field['key']
                        }
                    ],
                    'value_labels': [u'Count']
                },
                {
                    'header_label': u'Structures',
                    'rows': [
                        {
                            'numbers': ['5'],
                            'name': u'Affected',
                            'key': total_affected_field['key']
                        },
                        {
                            'numbers': ['0'],
                            'name': u'Not Affected',
                            'key': total_not_affected_field['key']
                        },
                        {
                            'numbers': ['4'],
                            'name': u'Not Exposed',
                            'key': total_not_exposed_field['key']
                        }
                    ],
                    'value_labels': [u'Count']
                }
            ],
            'notes': [
                u'Affected: An exposure element (e.g. people, roads, '
                u'buildings, land cover) that experiences a hazard (e.g. '
                u'tsunami, flood, earthquake) and endures consequences (e.g. '
                u'damage, evacuation, displacement, death) due to that hazard.'
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
            'component_key': 'action-checklist',
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

        """Check output generated."""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_general_report_from_multi_exposure_impact_function(self):
        """Test generate analysis result from multi exposure impact function.

        .. versionadded:: 4.3
        """
        output_folder = os.path.join('..', 'output', 'general_report')
        output_folder = self.fixtures_dir(output_folder)

        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        building_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        population_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population.geojson')
        roads_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'roads.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')
        exposure_layers = [building_layer, population_layer, roads_layer]

        impact_report = self.run_multi_exposure_impact_function_scenario(
            output_folder,
            standard_multi_exposure_impact_report_metadata_html,
            hazard_layer,
            exposure_layers,
            aggregation_layer=aggregation_layer)

        """Checking generated context."""
        empty_component_output_message = 'Empty component output'

        # Check Analysis Summary
        analysis_summary = impact_report.metadata.component_by_key(
            general_report_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        context = analysis_summary.context
        self.assertTrue(context)
        self.assertEqual(len(context['summary']), 2)

        """Checking generated context from multi-classifications analysis."""

        hazard_layer = load_test_raster_layer(
            'gisv4', 'hazard', 'earthquake.asc')
        place_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'places.geojson')
        exposure_layers.append(place_layer)

        impact_report = self.run_multi_exposure_impact_function_scenario(
            output_folder,
            standard_multi_exposure_impact_report_metadata_html,
            hazard_layer,
            exposure_layers,
            aggregation_layer=aggregation_layer)

        # Check Analysis Summary
        analysis_summary = impact_report.metadata.component_by_key(
            general_report_component['key'])

        context = analysis_summary.context
        self.assertTrue(context)
        self.assertEqual(len(context['summary']), 3)

    def test_analysis_detail(self):
        """Test generate analysis breakdown and aggregation report.

        .. versionadded:: 4.0
        """
        output_folder = os.path.join('..', 'output', 'analysis_detail')
        output_folder = self.fixtures_dir(output_folder)

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

        """Checking generated context."""
        empty_component_output_message = 'Empty component output'

        # Check Analysis Breakdown
        analysis_detail = impact_report.metadata.component_by_key(
            analysis_detail_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'component_key': 'analysis-detail',
            'header': u'Analysis Detail',
            'notes': [],
            'group_border_color': u'#36454f',
            'extra_table': {},
            'detail_header': {
                'total_header_index': 5,
                'breakdown_header_index': 0,
                'header_hazard_group': {
                    'not_affected': {
                        'header': u'Not affected',
                        'hazards': [
                            u'Low'],
                        'total': [u'Total Not Affected'],
                        'start_index': 4
                    },
                    'affected': {
                        'header': u'Affected',
                        'hazards': [
                            u'High',
                            u'Medium'],
                        'total': [u'Total Affected'],
                        'start_index': 1
                    }
                }
            },
            'detail_table': {
                'table_header': u'Estimated Number of structures affected by '
                                u'Structure type',
                'headers': [
                    u'Structure type',
                    {
                        'start': True, 'colspan': 3,
                        'name': u'High',
                        'header_group': 'affected'
                    },
                    {
                        'start': False,
                        'name': u'Medium',
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
                            'value': '2',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'affected'
                        },
                        {
                            'value': '2',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'not_affected'
                        },
                        '3', '5'
                    ],
                    [
                        u'Health',
                        {
                            'value': '1',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'affected'
                        },
                        {
                            'value': '1',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'not_affected'
                        },
                        '0', '1'
                    ],
                    [
                        u'Government',
                        {
                            'value': '0',
                            'header_group': 'affected'
                        },
                        {
                            'value': '1',
                            'header_group': 'affected'
                        },
                        {
                            'value': '1',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'not_affected'
                        },
                        '0', '1'
                    ],
                    [
                        u'Commercial',
                        {
                            'value': '1',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'affected'
                        },
                        {
                            'value': '1',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'not_affected'
                        },
                        '0', '1'
                    ],
                    [
                        u'Other',
                        {
                            'value': '0',
                            'header_group': 'affected'
                        },
                        {
                            'value': '1',
                            'header_group': 'affected'
                        },
                        {
                            'value': '1',
                            'header_group': 'affected'
                        },
                        {
                            'value': '0',
                            'header_group': 'not_affected'
                        },
                        '0', '1'
                    ],
                ],
                'footers': [
                    u'Total', {
                        'value': '4',
                        'header_group': 'affected'
                    },
                    {
                        'value': '2',
                        'header_group': 'affected'
                    },
                    {
                        'value': '6',
                        'header_group': 'affected'
                    },
                    {
                        'value': '0',
                        'header_group': 'not_affected'
                    },
                    '3', '9'
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
            'component_key': 'aggregation-result',
            'header': u'Aggregation Result',
            'notes': [],
            'aggregation_result': {
                'table_header': u'Estimated Number of structures affected by '
                                u'aggregation area',
                'header_label': u'Aggregation area',
                'rows': [
                    {
                        'type_values': ['1', '0', '0', '1', '1'],
                        'total': '3',
                        'name': u'area 1'
                    },
                    {
                        'type_values': ['0', '0', '1', '0', '0'],
                        'total': '1',
                        'name': u'area 2'
                    },
                    {
                        'type_values': ['1', '1', '0', '0', '0'],
                        'total': '2',
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
                'type_total_values': ['2', '1', '1', '1', '1'],
                'total_label': u'Total',
                'total_all': '6',
                'total_in_aggregation_area_label': u'Total'
            }
        }
        actual_context = aggregate_result.context

        self.assertDictEqual(
            expected_context, actual_context)
        self.assertTrue(
            aggregate_result.output, empty_component_output_message)

        """Check output generated."""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_analysis_provenance_details_simplified(self):
        """Test generate analysis provenance details section.

        .. versionadded: 4.0
        """
        output_folder = os.path.join('..', 'output', 'general_report')
        output_folder = self.fixtures_dir(output_folder)

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

        """Checking generated context."""
        empty_component_output_message = 'Empty component output'

        impact_table = impact_report.metadata.component_by_key(
            analysis_provenance_details_simplified_component['key'])

        expected_context = {
            'component_key': 'analysis-provenance-details-simplified',
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
                        'provenance': u'Generic Hazard '
                                      u'Polygon On '
                                      u'Structures Point'})
                ])
        }

        actual_context = impact_table.context

        self.assertDictEqual(
            expected_context, actual_context)
        self.assertTrue(
            impact_table.output, empty_component_output_message)

        """Check output generated."""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_analysis_provenance_tree_details(self):
        """Test generate analysis provenance tree details section.

        .. versionadded: 4.1
        """
        output_folder = os.path.join('..', 'output', 'general_report')
        output_folder = self.fixtures_dir(output_folder)

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

        """Checking generated context."""
        empty_component_output_message = 'Empty component output'

        impact_table = impact_report.metadata.component_by_key(
            analysis_provenance_details_component['key'])

        expected_context = {
            'component_key': 'analysis-provenance-details',
            'header': u'Analysis details',
            'details': OrderedDict([('impact_function', {
                'header': u'Impact Function',
                'provenances': u'Generic Hazard Polygon On Structures Point'
            }), ('hazard', {
                'header': u'Hazard',
                'provenances': OrderedDict([('title', {
                    'content': u'classified_vector',
                    'header': 'Title '
                }), ('source', {
                    'content': u'InaSAFE v4 GeoJSON test layer',
                    'header': 'Source '
                }), ('layer_purpose', {
                    'content': u'hazard',
                    'header': 'Layer Purpose '
                }), ('layer_geometry', {
                    'content': u'polygon',
                    'header': 'Layer Geometry '
                }), ('hazard', {
                    'content': u'hazard_generic',
                    'header': 'Hazard '
                }), ('hazard_category', {
                    'content': u'single_event',
                    'header': 'Hazard Category '
                }), ('value_maps', {
                    'content':
                        u'<table class="table table-condensed table-striped">'
                        u'\n'
                        u'<tbody>\n'
                        u'<tr>\n'
                        u'<td colspan=1><strong>Exposure</strong></td>\n'
                        u'<td colspan=1>Structures</td>\n'
                        u'</tr>\n'
                        u'<tr>\n'
                        u'<td colspan=1><strong>Classification</strong></td>\n'
                        u'<td colspan=1>Generic classes</td>\n'
                        u'</tr>\n'
                        u'<tr>\n'
                        u'<td colspan=1>Class name</td>\n'
                        u'<td colspan=1>Values</td>\n'
                        u'</tr>\n'
                        u'<tr>\n'
                        u'<td colspan=1>Low</td>\n'
                        u'<td colspan=1>low</td>\n'
                        u'</tr>\n'
                        u'<tr>\n'
                        u'<td colspan=1>Medium</td>\n'
                        u'<td colspan=1>medium</td>\n'
                        u'</tr>\n'
                        u'<tr>\n'
                        u'<td colspan=1>High</td>\n'
                        u'<td colspan=1>high</td>\n'
                        u'</tr>\n'
                        u'</tbody>\n'
                        u'</table>\n',
                    'header': 'Value Map '
                }), ('inasafe_fields', {
                    'content':
                        u'<table class="table table-condensed">\n'
                        u'<tbody>\n'
                        u'<tr>\n'
                        u'<td colspan=1><strong>Hazard ID</strong></td>\n'
                        u'<td colspan=1>hazard_id</td>\n'
                        u'</tr>\n'
                        u'<tr>\n'
                        u'<td colspan=1><strong>Hazard Value</strong>'
                        u'</td>\n<td colspan=1>hazard_value</td>\n'
                        u'</tr>\n'
                        u'</tbody>\n'
                        u'</table>\n',
                    'header': 'InaSAFE Fields '
                }), ('layer_mode', {
                    'content': u'classified',
                    'header': 'Layer Mode '
                }), ('hazard_layer', {
                    'content': hazard_layer.source(),
                    'header': 'Hazard Layer '
                }), ('keyword_version', {
                    'content': u'4.0',
                    'header': 'Keyword Version '
                })])
            }), ('exposure', {
                'header': u'Exposure',
                'provenances': OrderedDict([('title', {
                    'content': u'building-points',
                    'header': 'Title '
                }), ('source', {
                    'content': u'InaSAFE v4 GeoJSON test layer',
                    'header': 'Source '
                }), ('layer_purpose', {
                    'content': u'exposure',
                    'header': 'Layer Purpose '
                }), ('layer_geometry', {
                    'content': u'point',
                    'header': 'Layer Geometry '
                }), ('exposure', {
                    'content': u'structure',
                    'header': 'Exposure '
                }), ('value_map', {
                    'content':
                        u'<table class="table table-condensed">\n'
                        u'<tbody>\n'
                        u'<tr>\n'
                        u'<td colspan=1><strong>Commercial</strong></td>\n'
                        u'<td colspan=1>shop</td>\n'
                        u'</tr>\n'
                        u'<tr>\n'
                        u'<td colspan=1><strong>Education</strong></td>\n'
                        u'<td colspan=1>school</td>\n'
                        u'</tr>\n'
                        u'<tr>\n'
                        u'<td colspan=1><strong>Government</strong></td>\n'
                        u'<td colspan=1>ministry</td>\n'
                        u'</tr>\n'
                        u'<tr>\n'
                        u'<td colspan=1><strong>Health</strong></td>\n'
                        u'<td colspan=1>hospital</td>\n'
                        u'</tr>\n'
                        u'<tr>\n'
                        u'<td colspan=1><strong>Residential</strong></td>\n'
                        u'<td colspan=1>house</td>\n'
                        u'</tr>\n'
                        u'</tbody>\n'
                        u'</table>\n',
                    'header': 'Value Map '
                }), ('inasafe_fields', {
                    'content': u'<table class="table table-condensed">\n'
                               u'<tbody>\n<tr>\n<td colspan=1><strong>'
                               u'Exposure ID</strong></td>\n<td colspan=1>'
                               u'exposure_id</td>\n</tr>\n<tr>\n<td colspan=1>'
                               u'<strong>Exposure Type</strong></td>\n'
                               u'<td colspan=1>exposure_type</td>\n</tr>\n'
                               u'</tbody>\n</table>\n',
                    'header': 'InaSAFE Fields '
                }), ('layer_mode', {
                    'content': u'classified',
                    'header': 'Layer Mode '
                }), ('exposure_layer', {
                    'content': exposure_layer.source(),
                    'header': 'Exposure Layer '
                }), ('classification', {
                    'content': u'generic_structure_classes',
                    'header': 'Classification '
                }), ('keyword_version', {
                    'content': u'4.0',
                    'header': 'Keyword Version '
                })])
            }), ('aggregation', {
                'header': u'Aggregation',
                'provenances': OrderedDict([('title', {
                    'content': u'small grid',
                    'header': 'Title '
                }), ('source', {
                    'content': u'InaSAFE v4 GeoJSON test layer',
                    'header': 'Source '
                }), ('layer_purpose', {
                    'content': u'aggregation',
                    'header': 'Layer Purpose '
                }), ('layer_geometry', {
                    'content': u'polygon',
                    'header': 'Layer Geometry '
                }), ('inasafe_fields', {
                    'content':
                        u'<table class="table table-condensed">\n'
                        u'<tbody>\n'
                        u'<tr>\n'
                        u'<td colspan=1><strong>Aggregation ID</strong></td>\n'
                        u'<td colspan=1>area_id</td>\n'
                        u'</tr>\n'
                        u'<tr>\n'
                        u'<td colspan=1><strong>Aggregation Name</strong>'
                        u'</td>\n'
                        u'<td colspan=1>area_name</td>\n'
                        u'</tr>\n'
                        u'<tr>\n'
                        u'<td colspan=1><strong>Female Ratio</strong>'
                        u'</td>\n'
                        u'<td colspan=1>ratio_female</td>\n'
                        u'</tr>\n'
                        u'</tbody>\n'
                        u'</table>\n',
                    'header': 'InaSAFE Fields '
                }), ('inasafe_default_values', {
                    'content': u'<table class="table table-condensed">\n'
                               u'<tbody>\n<tr>\n<td colspan=1><strong>'
                               u'Lactating Ratio</strong></td>\n'
                               u'<td colspan=1>0.03</td>\n</tr>\n<tr>\n'
                               u'<td colspan=1><strong>Pregnant Ratio</strong>'
                               u'</td>\n<td colspan=1>0.02</td>\n</tr>\n'
                               u'</tbody>\n</table>\n',
                    'header': 'InaSAFE Default Values '
                }), ('aggregation_layer', {
                    'content': aggregation_layer.source(),
                    'header': 'Aggregation Layer '
                }), ('keyword_version', {
                    'content': u'4.1',
                    'header': 'Keyword Version '
                })])
            }), ('analysis_environment', {
                'header': u'Analysis Environment',
                'provenances': OrderedDict([('os', {
                    'content': readable_os_version(),
                    'header': 'OS '
                }), ('inasafe_version', {
                    'content': get_version(),
                    'header': 'InaSAFE Version '
                }), (provenance_use_rounding['provenance_key'], {
                    'content': 'On',
                    'header': provenance_use_rounding['name'] + ' '
                }), ('debug_mode', {
                    'content': 'Off',
                    'header': 'Debug Mode '
                }), ('qgis_version', {
                    'content': QGis.QGIS_VERSION,
                    'header': 'QGIS Version '
                }), ('qt_version', {
                    'content': QT_VERSION_STR,
                    'header': 'Qt Version '
                }), ('gdal_version', {
                    'content': gdal.__version__,
                    'header': 'GDAL Version '
                }), ('pyqt_version', {
                    'content': PYQT_VERSION_STR,
                    'header': 'PyQt Version '
                })])
            })])
        }

        actual_context = impact_table.context

        # TODO: Make it easier to fix the test:
        # 1. Use smaller dict comparison
        # 2. Just check the content, exclude the html
        self.assertDictEqual(
            expected_context, actual_context)
        self.assertTrue(
            impact_table.output, empty_component_output_message)

        """Check output generated."""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        # shutil.rmtree(output_folder, ignore_errors=True)

    def test_minimum_needs_outputs(self):
        """Test generate minimum needs section.

        .. versionadded:: 4.0
        """
        # Make sure that the displacement rate is the correct one that has
        # been set in setUp method.
        displacement_rate = get_displacement_rate(
            hazard_flood['key'], flood_hazard_classes['key'], 'wet')
        self.assertEqual(displacement_rate, self.custom_displacement_rate)

        output_folder = os.path.join('..', 'output', 'minimum_needs')
        output_folder = self.fixtures_dir(output_folder)

        # Minimum needs only occurred when population is displaced
        # so, use flood hazard.
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_raster_layer(
            'exposure', 'pop_binary_raster_20_20.asc')

        impact_report = self.run_impact_report_scenario(
            output_folder,
            standard_impact_report_metadata_html,
            hazard_layer, exposure_layer)

        """Checking generated context."""
        empty_component_output_message = 'Empty component output'

        # Check Minimum Needs
        minimum_needs = impact_report.metadata.component_by_key(
            minimum_needs_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'component_key': 'minimum-needs',
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
                        },
                        {
                            'header': u'Hygiene Packs',
                            'value': '10'
                        },
                        {
                            'header': u'Additional Rice [kg]',
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
            'Wet - 90%, Dry - 0%')
        actual_context = notes_assumptions.context['items'][-1]['item_list'][0]
        message = expected_context.strip() + '\n' + actual_context.strip()
        self.assertEqual(
            expected_context.strip(), actual_context.strip(), message)

        """Check generated report."""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_minimum_needs_outputs_modified(self):
        """Test generate minimum needs section with updated profile.

        .. versionadded: 4.3
        """
        # Make sure that the displacement rate is the correct one that has
        # been set in setUp method.
        displacement_rate = get_displacement_rate(
            hazard_flood['key'], flood_hazard_classes['key'], 'wet')
        self.assertEqual(displacement_rate, self.custom_displacement_rate)

        # Change affected
        profile = setting(key='population_preference')
        profile[hazard_flood['key']][flood_hazard_classes['key']][
            'wet']['affected'] = False
        profile[hazard_flood['key']][flood_hazard_classes['key']][
            'dry']['affected'] = True
        profile[hazard_flood['key']][flood_hazard_classes['key']][
            'dry']['displacement_rate'] = 0.5
        set_setting(key='population_preference', value=profile)
        wet_is_affected = is_affected(
            hazard_flood['key'],
            flood_hazard_classes['key'],
            'wet'
        )
        dry_is_affected = is_affected(
            hazard_flood['key'],
            flood_hazard_classes['key'],
            'dry'
        )
        displacement_rate_wet = get_displacement_rate(
            hazard_flood['key'], flood_hazard_classes['key'], 'wet')
        displacement_rate_dry = get_displacement_rate(
            hazard_flood['key'], flood_hazard_classes['key'], 'dry')

        self.assertFalse(wet_is_affected)
        self.assertTrue(dry_is_affected)
        self.assertEqual(displacement_rate_dry, 0.5)
        self.assertEqual(displacement_rate_wet, 0)

        output_folder = os.path.join('..', 'output', 'minimum_needs')
        output_folder = self.fixtures_dir(output_folder)

        # Minimum needs only occurred when population is displaced
        # so, use flood hazard.
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_raster_layer(
            'exposure', 'pop_binary_raster_20_20.asc')

        impact_report = self.run_impact_report_scenario(
            output_folder,
            standard_impact_report_metadata_html,
            hazard_layer, exposure_layer)

        """Checking generated context."""
        empty_component_output_message = 'Empty component output'

        # Check Minimum Needs
        minimum_needs = impact_report.metadata.component_by_key(
            minimum_needs_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'component_key': 'minimum-needs',
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
                            'value': '40'
                        },
                        {
                            'header': u'Drinking Water [l]',
                            'value': '260'
                        },
                        {
                            'header': u'Clean Water [l]',
                            'value': '970'
                        },
                        {
                            'header': u'Family Kits',
                            'value': '10'
                        },
                        {
                            'header': u'Hygiene Packs',
                            'value': '10'
                        },
                        {
                            'header': u'Additional Rice [kg]',
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

        # Affected notes
        # Dry is set to affected, but Wet is set to not affected.
        expected_context = (
            'Exposures in the following hazard classes are considered '
            'affected: Dry')
        actual_context = notes_assumptions.context['items'][-2]['item_list'][0]
        message = expected_context.strip() + '\n' + actual_context.strip()
        self.assertEqual(
            expected_context.strip(), actual_context.strip(), message)

        # Displacement rate notes
        expected_context = (
            'For this analysis, the following displacement rates were used: '
            'Wet - 0%, Dry - 50%')
        actual_context = notes_assumptions.context['items'][-1]['item_list'][0]
        message = expected_context.strip() + '\n' + actual_context.strip()
        self.assertEqual(
            expected_context.strip(), actual_context.strip(), message)

        """Check generated report."""

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
        output_folder = os.path.join(
            '..', 'output', 'aggregation_entire_area_result')
        output_folder = self.fixtures_dir(output_folder)

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

        """Check generated context."""
        aggregation_result = impact_report.metadata.component_by_key(
            aggregation_result_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        # We comment below code because currently we want to remove aggregation
        # table if there is no aggregation area used. We might want to use this
        # test later if somehow we change our mind.

        # expected_context = {
        #     'aggregation_result': {
        #         'table_header': u'Estimated Number of structures by '
        #                         u'aggregation area',
        #         'header_label': u'Aggregation area',
        #         'rows': [
        #             {
        #                 'type_values': ['21', '2', '1', '4', '4', '1'],
        #                 'total': '33',
        #                 'name': u'Entire Area'
        #             }
        #         ],
        #         'type_header_labels': [
        #             u'Residential',
        #             u'Education',
        #             u'Health',
        #             u'Place of worship',
        #             u'Government',
        #             u'Commercial',
        #         ],
        #         'total_in_aggregation_area_label': u'Total',
        #         'total_label': u'Total',
        #         'total_all': '33',
        #         'type_total_values': ['21', '2', '1', '4', '4', '1']
        #     },
        #     'header': u'Aggregation Result',
        #     'notes': []
        # }
        # empty_component_output_message = 'Empty component output'
        # self.assertTrue(
        #     aggregation_result.output, empty_component_output_message)

        actual_context = aggregation_result.context

        self.assertFalse(actual_context)

        """Check generated report."""

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
        output_folder = os.path.join('..', 'output', 'aggregation_area_result')
        output_folder = self.fixtures_dir(output_folder)

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

        """Check generated context."""
        empty_component_output_message = 'Empty component output'

        aggregation_result = impact_report.metadata.component_by_key(
            aggregation_result_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'aggregation_result': {
                'table_header': u'Estimated Number of structures affected by '
                                u'aggregation area',
                'header_label': u'Aggregation area',
                'rows': [
                    {
                        'type_values': ['0', '1', '0', '1', '3', '0'],
                        'total': '5',
                        'name': u'B'
                    },
                    {
                        'type_values': ['2', '0', '0', '0', '0', '0'],
                        'total': '2',
                        'name': u'C'
                    },
                    {
                        'type_values': ['6', '1', '0', '3', '1', '0'],
                        'total': '11',
                        'name': u'F'
                    },
                    {
                        'type_values': ['13', '0', '1', '0', '0', '1'],
                        'total': '15',
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
                'total_all': '33',
                'type_total_values': ['21', '2', '1', '4', '4', '1']
            },
            'component_key': 'aggregation-result',
            'header': u'Aggregation Result',
            'notes': []
        }

        actual_context = aggregation_result.context

        self.assertDictEqual(expected_context, actual_context)
        self.assertTrue(
            aggregation_result.output, empty_component_output_message)

        """Check generated report."""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_aggregate_post_processors_vector(self):
        """Test generate aggregate postprocessors sections.

        .. versionadded:: 4.0
        """
        # Make sure that the displacement rate is the correct one that has
        # been set in setUp method.
        displacement_rate = get_displacement_rate(
            hazard_flood['key'], flood_hazard_classes['key'], 'wet')
        self.assertEqual(displacement_rate, self.custom_displacement_rate)

        output_folder = os.path.join(
            '..', 'output', 'aggregate_post_processors')
        output_folder = self.fixtures_dir(output_folder)

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

        """Checking generated context."""
        empty_component_output_message = 'Empty component output'

        # Check aggregation-postprocessors
        aggregation_postprocessors = impact_report.metadata.component_by_key(
            aggregation_postprocessors_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""

        actual_context = aggregation_postprocessors.context
        expected_context = {
            'component_key': 'aggregation-postprocessors',
            'header': u'Detailed demographic breakdown',
            'sections': OrderedDict([
                ('age', [
                    {
                        'header': u'Estimated number of people displaced by '
                                  u'Age per aggregation area',
                        'notes': age_displaced_count_group['notes'],
                        'rows': [[u'B', '2,600', '640', '1,700', '230'],
                                 [u'C', '6,500', '1,700', '4,300', '590'],
                                 [u'F', '7,200', '1,800', '4,700', '640'],
                                 [u'G', '9,500', '2,400', '6,300', '850']],
                        'columns': [u'Aggregation area',
                                    u'Total Displaced Population',
                                    {
                                        'start_group_header': True,
                                        'name': u'Youth',
                                        'group_header': u'Age breakdown'
                                    },
                                    {
                                        'start_group_header': False,
                                        'name': u'Adult',
                                        'group_header': u'Age breakdown'
                                    },
                                    {
                                        'start_group_header': False,
                                        'name': u'Elderly',
                                        'group_header': u'Age breakdown'
                                    }],
                        'group_header_colspan': 3,
                        'totals': [
                            u'Total', '25,600', '6,400', '16,900', '2,400']
                    }
                ]),
                ('gender', [
                    {
                        'header': u'Estimated number of people displaced by '
                                  u'Gender per aggregation area',
                        'notes': gender_displaced_count_group['notes'],
                        'rows': [
                            [u'B', '2,600', '1,300'],
                            [u'C', '6,500', '3,300'],
                            [u'F', '7,200', '3,600'],
                            [u'G', '9,500', '4,800']],
                        'columns': [
                            u'Aggregation area',
                            u'Total Displaced Population',
                            {
                                'start_group_header': True,
                                'name': u'Female',
                                'group_header': u'Gender breakdown'
                            }],
                        'group_header_colspan': 1,
                        'totals': [
                            u'Total', '25,600', '12,800']
                    }
                ]),
                ('vulnerability', [
                    {
                        'header': u'Estimated number of people displaced by '
                                  u'Age Vulnerability per aggregation area',
                        'message': u'Vulnerability ratio is not found. '
                                   u'No calculations produced.',
                        'empty': True
                    },
                    {
                        'header': u'Estimated number of people displaced by '
                                  u'Gender Vulnerability per aggregation area',
                        'message': u'Vulnerability ratio is not found. '
                                   u'No calculations produced.',
                        'empty': True
                    },
                    {
                        'header': u'Estimated number of people displaced by '
                                  u'Disability Vulnerability per '
                                  u'aggregation area',
                        'message': u'Vulnerability ratio is not found. '
                                   u'No calculations produced.',
                        'empty': True
                    }
                ]),
                ('minimum_needs', [
                    {
                        'header': u'Estimated number of minimum needs '
                                  u'per week',
                        'notes': [],
                        'rows': [
                            [u'B', '2,600', '7,200', '44,400', '170,000',
                             '510', '130', '1,100'],
                            [u'C', '6,500', '18,200', '114,000', '434,000',
                             '1,300', '330', '2,600'],
                            [u'F', '7,200', '20,000', '125,000', '477,000',
                             '1,500', '360', '2,900'],
                            [u'G', '9,500', '26,500', '166,000', '634,000',
                             '1,900', '480', '3,800']],
                        'columns': [
                            u'Aggregation area',
                            u'Total Displaced Population',
                            {
                                'start_group_header': True,
                                'name': u'Rice [kg]',
                                'group_header': u'Minimum needs breakdown'
                            },
                            {
                                'start_group_header': False,
                                'name': u'Drinking Water [l]',
                                'group_header': u'Minimum needs breakdown'
                            },
                            {
                                'start_group_header': False,
                                'name': u'Clean Water [l]',
                                'group_header': u'Minimum needs breakdown'
                            },
                            {
                                'start_group_header': False,
                                'name': u'Family Kits',
                                'group_header': u'Minimum needs breakdown'
                            },
                            {
                                'start_group_header': False,
                                'name': u'Toilets',
                                'group_header': u'Minimum needs breakdown'
                            },
                            {
                                'start_group_header': False,
                                'name': u'Hygiene Packs',
                                'group_header': u'Minimum needs breakdown'
                            }],
                        'group_header_colspan': 6,
                        'totals': [
                            u'Total',
                            '25,600',
                            '71,700',
                            '448,000',
                            '1,714,000',
                            '5,200',
                            '1,300',
                            '10,200']
                    }
                ])
            ]),
            'use_aggregation': True
        }

        self.assertDictEqual(expected_context, actual_context)
        self.assertTrue(
            aggregation_postprocessors.output, empty_component_output_message)

        """Check generated report."""

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
        # Make sure that the displacement rate is the correct one that has
        # been set in setUp method.
        displacement_rate = get_displacement_rate(
            hazard_flood['key'], flood_hazard_classes['key'], 'wet')
        self.assertEqual(displacement_rate, self.custom_displacement_rate)

        output_folder = os.path.join(
            '..', 'output', 'aggregate_post_processors')
        output_folder = self.fixtures_dir(output_folder)

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

        """Checking generated context."""
        empty_component_output_message = 'Empty component output'

        # Check aggregation-postprocessors
        aggregation_postprocessors = impact_report.metadata.component_by_key(
            aggregation_postprocessors_component['key'])
        """:type: safe.report.report_metadata.Jinja2ComponentsMetadata"""
        expected_context = {
            'component_key': 'aggregation-postprocessors',
            'header': u'Detailed demographic breakdown',
            'sections': OrderedDict([
                ('age', [
                    {
                        'header': u'Estimated number of people displaced by '
                                  u'Age per aggregation area',
                        'notes': age_displaced_count_group['notes'],
                        'rows': [[u'B', '10', '0', '0', '0'],
                                 [u'C', '10', '10', '10', '0'],
                                 [u'F', '10', '0', '10', '0'],
                                 [u'G', '10', '10', '10', '0'],
                                 [u'K', '10', '0', '10', '0']],
                        'columns': [u'Aggregation area',
                                    u'Total Displaced Population',
                                    {
                                        'start_group_header': True,
                                        'name': u'Youth',
                                        'group_header': u'Age breakdown'
                                    },
                                    {
                                        'start_group_header': False,
                                        'name': u'Adult',
                                        'group_header': u'Age breakdown'
                                    },
                                    {
                                        'start_group_header': False,
                                        'name': u'Elderly',
                                        'group_header': u'Age breakdown'
                                    }],
                        'group_header_colspan': 3,
                        'totals': [u'Total', '20', '10', '20', '10']
                    }
                ]),
                ('gender', [
                    {
                        'header': u'Estimated number of people displaced by '
                                  u'Gender per aggregation area',
                        'notes': gender_displaced_count_group['notes'],
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
                                'name': u'Female',
                                'group_header': u'Gender breakdown'
                            }],
                        'group_header_colspan': 1,
                        'totals': [u'Total', '20', '10']
                    }
                ]),
                ('vulnerability', [
                    {
                        'header': u'Estimated number of people displaced by '
                                  u'Age Vulnerability per aggregation area',
                        'message': u'Vulnerability ratio is not found. '
                                   u'No calculations produced.',
                        'empty': True
                    },
                    {
                        'header': u'Estimated number of people displaced by '
                                  u'Gender Vulnerability per aggregation area',
                        'message': u'Vulnerability ratio is not found. '
                                   u'No calculations produced.',
                        'empty': True
                    },
                    {
                        'header': u'Estimated number of people displaced by '
                                  u'Disability Vulnerability per '
                                  u'aggregation area',
                        'message': u'Vulnerability ratio is not found. '
                                   u'No calculations produced.',
                        'empty': True
                    }
                ]),
                ('minimum_needs', [
                    {
                        'header': u'Estimated number of minimum needs '
                                  u'per week',
                        'notes': [],
                        'rows': [
                            [u'B', '10', '10', '20', '80', '0', '0', '0'],
                            [u'C', '10', '20', '90', '340', '0', '0', '10'],
                            [u'F', '10', '10', '70', '260', '0', '0', '10'],
                            [u'G', '10', '20', '110', '410', '10', '0', '10'],
                            [u'K', '10', '10', '40', '130', '0', '0', '0']],
                        'columns': [
                            u'Aggregation area',
                            u'Total Displaced Population',
                            {
                                'start_group_header': True,
                                'name': u'Rice [kg]',
                                'group_header': u'Minimum needs breakdown'
                            },
                            {
                                'start_group_header': False,
                                'name': u'Drinking Water [l]',
                                'group_header': u'Minimum needs breakdown'
                            },
                            {
                                'start_group_header': False,
                                'name': u'Clean Water [l]',
                                'group_header': u'Minimum needs breakdown'
                            },
                            {
                                'start_group_header': False,
                                'name': u'Family Kits',
                                'group_header': u'Minimum needs breakdown'
                            },
                            {
                                'start_group_header': False,
                                'name': u'Toilets',
                                'group_header': u'Minimum needs breakdown'
                            },
                            {
                                'start_group_header': False,
                                'name': u'Hygiene Packs',
                                'group_header': u'Minimum needs breakdown'
                            }],
                        'group_header_colspan': 6,
                        'totals': [
                            u'Total',
                            '20',
                            '60',
                            '350',
                            '1,400',
                            '10',
                            '0',
                            '10']
                    }
                ])
            ]),
            'use_aggregation': True
        }

        actual_context = aggregation_postprocessors.context

        self.assertDictEqual(
            expected_context, actual_context)
        self.assertTrue(
            aggregation_postprocessors.output, empty_component_output_message)

        """Check generated report."""

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    # we disable infographic for now until infographic with qpt template ready
    @unittest.expectedFailure
    def test_population_infographic(self):
        """Test population infographic generation.

        This test is not using actual displacement rate in order to
        distinguish the result more clearly.

        .. versionadded:: 4.0
        """
        output_folder = os.path.join('..', 'output', 'population_infographic')
        output_folder = self.fixtures_dir(output_folder)

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

        """Checking generated context."""
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

        """Check generated report."""

        output_path = impact_report.component_absolute_output_path(
            'infographic-layout')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_qgis_html_pdf_report(self):
        """Test generate analysis breakdown and aggregation report.

        .. versionadded:: 4.0
        """
        output_folder = os.path.join('..', 'output', 'impact_summary_pdf')
        output_folder = self.fixtures_dir(output_folder)

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
        output_folder = os.path.join('..', 'output', 'impact_map_pdf')
        output_folder = self.fixtures_dir(output_folder)

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
        project = QgsProject.instance()
        project.addMapLayers(
            [hazard_layer, exposure_layer, aggregation_layer])
        project.addMapLayers(impact_function.outputs)

        return_code, message = impact_function.generate_report(
            [map_report], output_folder=output_folder, iface=IFACE)

        self.assertEqual(
            return_code, ImpactReport.REPORT_GENERATION_SUCCESS, message)

        impact_report = impact_function.impact_report

        output_path = impact_report.component_absolute_output_path(
            'inasafe-map-report-portrait')

        # for now, test that output exists
        for path in output_path.values():
            self.assertTrue(os.path.exists(path), msg=path)

        output_path = impact_report.component_absolute_output_path(
            'inasafe-map-report-landscape')

        for path in output_path.values():
            self.assertTrue(os.path.exists(path), msg=path)

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_custom_layer_order_qgis_map_pdf_report(self):
        """Test generate map report using custom layer order.

        .. versionadded: 4.3.2
        """

        """Single Exposure ImpactFunction"""

        output_folder = os.path.join('..', 'output', 'impact_map_pdf')
        output_folder = self.fixtures_dir(output_folder)

        # Classified vector with buildings
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'buildings.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_report = self.run_impact_report_scenario(
            output_folder,
            map_report,
            hazard_layer,
            exposure_layer,
            aggregation_layer=aggregation_layer)

        output_path = impact_report.component_absolute_output_path(
            'inasafe-map-report-portrait')

        # for now, test that output exists
        for path in output_path.values():
            self.assertTrue(os.path.exists(path), msg=path)

        output_path = impact_report.component_absolute_output_path(
            'inasafe-map-report-landscape')

        for path in output_path.values():
            self.assertTrue(os.path.exists(path), msg=path)

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_custom_layer_order_qgis_map_pdf_report_multi_exposure(self):
        """Test generate multi exposure map report using custom layer order.

        .. versionadded: 4.3.2
        """

        """Multi Exposure ImpactFunction"""

        output_folder = os.path.join('..', 'output', 'impact_map_pdf')
        output_folder = self.fixtures_dir(output_folder)

        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        building_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        population_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population.geojson')
        roads_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'roads.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')
        exposure_layers = [building_layer, population_layer, roads_layer]

        impact_report = self.run_multi_exposure_impact_function_scenario(
            output_folder,
            map_report,
            hazard_layer,
            exposure_layers,
            aggregation_layer=aggregation_layer)

        output_path = impact_report.component_absolute_output_path(
            'inasafe-map-report-portrait')

        # for now, test that output exists
        for path in output_path.values():
            self.assertTrue(os.path.exists(path), msg=path)

        output_path = impact_report.component_absolute_output_path(
            'inasafe-map-report-landscape')

        for path in output_path.values():
            self.assertTrue(os.path.exists(path), msg=path)

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_report_urls_metadata(self):
        """Test report urls metadata.

        .. versionadded:: 4.3
        """

        output_folder = os.path.join('..', 'output')
        output_folder = self.fixtures_dir(output_folder)

        # Classified vector with building-points
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        _ = self.run_impact_report_scenario(
            output_folder,
            standard_impact_report_metadata_html,
            hazard_layer, exposure_layer,
            aggregation_layer=aggregation_layer)

        # check the report metadata in output folder
        report_metadata_path = os.path.join(
            output_folder, 'report_metadata.json')
        self.assertTrue(bool(os.path.exists(report_metadata_path)))

        with open(report_metadata_path) as report_metadata_file:
            actual_report_urls_metadata = json.loads(
                report_metadata_file.read())

        expected_report_urls_metadata = {
            u'pdf_product_tag': {},
            u'html_product_tag': {
                u'impact-report': os.path.join(
                    output_folder, 'impact-report-output.html'),
                u'action-checklist-report': os.path.join(
                    output_folder, 'action-checklist-output.html'),
                u'analysis-provenance-details-report': os.path.join(
                    output_folder,
                    'analysis-provenance-details-report-output.html')
            },
            u'qpt_product_tag': {}
        }

        self.assertDictEqual(
            actual_report_urls_metadata, expected_report_urls_metadata)

        shutil.rmtree(output_folder, ignore_errors=True)
