# coding=utf-8
import io
import os
import shutil
import unittest

from jinja2.environment import Template

from safe.common.utilities import safe_dir
from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.impact_function_v4.impact_function import ImpactFunction
from safe.reportv4.extractors.composer import qgis_composer_extractor
from safe.reportv4.processors.default import (
    qgis_composer_renderer)
from safe.reportv4.report_metadata import ReportMetadata
from safe.test.utilities import (
    get_qgis_app,
    load_path_vector_layer,
    load_test_vector_layer,
    load_test_raster_layer)
from safe.utilities.i18n import tr

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from PyQt4.QtCore import QSettings
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry
from safe.definitionsv4.report import (
    report_a4_portrait_blue,
    standard_impact_report_metadata_html,
    standard_impact_report_metadata_pdf, analysis_result_component,
    action_checklist_component, notes_assumptions_component,
    analysis_breakdown_component, aggregation_result_component,
    minimum_needs_component)
from safe.reportv4.impact_report import ImpactReport

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
        needs_profile = NeedsProfile()
        needs_profile.load()

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
        impact_function.run()

        report_metadata = ReportMetadata(
            metadata_dict=standard_impact_report_metadata_html)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_function=impact_function,
            minimum_needs_profile=needs_profile)
        impact_report.output_folder = output_folder
        impact_report.process_component()

        """Checking generated context"""
        different_context_message = 'Different context generated'
        empty_component_output_message = 'Empty component output'

        # Check Analysis Summary
        analysis_summary = impact_report.metadata.component_by_key(
            analysis_result_component['key'])
        """:type: safe.reportv4.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'header': tr('Analysis Results'),
            'title': tr('Structures affected'),
            'summary': [
                {
                    'header_label': u'Hazard Zone',
                    'rows': [
                        {
                            'value': 4.0,
                            'name': u'Total High Hazard Zone',
                            'key': 'high'
                        },
                        {
                            'value': 1.0,
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
                            'value': 5.0,
                            'name': u'Total Affected',
                            'key': 'total_affected_field'
                        },
                        {
                            'value': 0.0,
                            'name': u'Total Unaffected',
                            'key': 'total_unaffected_field'
                        },
                        {
                            'value': 5.0,
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
        """:type: safe.reportv4.report_metadata.Jinja2ComponentsMetadata"""
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
        """:type: safe.reportv4.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'header': u'Notes and assumptions',
            'items': [
                u'The impacts on roads, people, buildings and other '
                u'exposure elements may be under estimated if the exposure '
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
        needs_profile = NeedsProfile()
        needs_profile.load()

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
        impact_function.run()

        report_metadata = ReportMetadata(
            metadata_dict=standard_impact_report_metadata_html)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_function=impact_function,
            minimum_needs_profile=needs_profile)
        impact_report.output_folder = output_folder
        impact_report.process_component()

        """Checking generated context"""
        different_context_message = 'Different context generated'
        empty_component_output_message = 'Empty component output'

        # Check Analysis Breakdown
        analysis_breakdown = impact_report.metadata.component_by_key(
            analysis_breakdown_component['key'])
        """:type: safe.reportv4.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'header': u'Estimated number of Structures by type',
            'detail_table': {
                'headers': [
                    u'Structures type', u'High Hazard Zone',
                    u'Medium Hazard Zone', u'Low Hazard Zone',
                    u'Total Affected', u'Total Unaffected', u'Total'
                ],
                'details': [],
                'footers': [
                    u'Total', 4.0, 2.0, 0, 6.0, 0.0, 6.0
                ]
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
        """:type: safe.reportv4.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {
            'aggregation_result': {
                'header_label': u'Aggregation area',
                'rows': [
                    {
                        'type_values': [1.0, 0.0, 1.0,
                                        1.0, 0.0],
                        'total': 3.0,
                        'name': u'area 1'
                    },
                    {
                        'type_values': [0.0, 1.0, 0.0,
                                        0.0, 0.0],
                        'total': 1.0,
                        'name': u'area 2'
                    },
                    {
                        'type_values': [0.0, 0.0, 0.0,
                                        1.0, 1.0],
                        'total': 2.0,
                        'name': u'area 3'
                    }
                ],
                'type_header_labels': [
                    u'Other',
                    u'Government',
                    u'Commercial',
                    u'Education',
                    u'Health'
                ],
                'type_total_values': [],
                'total_label': u'Total',
                'total_all': 6.0
            },
            'header': u'Aggregation Result'
        }
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

    def test_minimum_needs(self):
        """Test generate minimum needs section."""
        needs_profile = NeedsProfile()
        needs_profile.load()

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
        impact_function.run()

        report_metadata = ReportMetadata(
            metadata_dict=standard_impact_report_metadata_html)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_function=impact_function,
            minimum_needs_profile=needs_profile)
        impact_report.output_folder = output_folder
        impact_report.process_component()

        """Checking generated context"""
        different_context_message = 'Different context generated'
        empty_component_output_message = 'Empty component output'

        # Check Minimum Needs
        minimum_needs = impact_report.metadata.component_by_key(
            minimum_needs_component['key'])
        """:type: safe.reportv4.report_metadata.Jinja2ComponentsMetadata"""

        expected_context = {}
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

    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False),
        'Under development')
    def test_analysis_result(self):
        """Test generate analysis result."""

        output_folder = self.fixtures_dir('../output')

        shutil.rmtree(output_folder, ignore_errors=True)

        exposure_json = self.fixtures_dir(
            'analysis_sample/1-exposure.geojson')
        exposure_layer = load_path_vector_layer(exposure_json)

        hazard_json = self.fixtures_dir('analysis_sample/2-hazard.geojson')
        hazard_layer = load_path_vector_layer(hazard_json)

        impact_json = self.fixtures_dir('analysis_sample/14-impact.geojson')
        impact_layer = load_path_vector_layer(impact_json)

        analysis_json = self.fixtures_dir(
            'analysis_sample/18-analysis.geojson')
        analysis_layer = load_path_vector_layer(analysis_json)

        breakdown_csv = self.fixtures_dir(
            'analysis_sample/16-breakdown.csv')
        exposure_breakdown = load_path_vector_layer(breakdown_csv)

        minimum_needs = NeedsProfile()
        minimum_needs.load()

        report_metadata = ReportMetadata(
            metadata_dict=standard_impact_report_metadata_html)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            exposure=exposure_layer,
            hazard=hazard_layer,
            impact=impact_layer,
            analysis=analysis_layer,
            exposure_breakdown=exposure_breakdown,
            minimum_needs_profile=minimum_needs)
        impact_report.output_folder = output_folder
        impact_report.process_component()

        output_path = impact_report.component_absolute_output_path(
            'impact-report')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_qgis_html_pdf_report(self):
        """Test generate analysis breakdown and aggregation report."""
        needs_profile = NeedsProfile()
        needs_profile.load()

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
        impact_function.run()

        report_metadata = ReportMetadata(
            metadata_dict=standard_impact_report_metadata_pdf)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_function=impact_function,
            minimum_needs_profile=needs_profile)
        impact_report.output_folder = output_folder
        impact_report.process_component()

        output_path = impact_report.component_absolute_output_path(
            'impact-report-pdf')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    def test_qgis_map_pdf_report(self):
        """Test generate analysis map report."""
        needs_profile = NeedsProfile()
        needs_profile.load()

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
        impact_function.run()

        # insert layer to registry
        layer_registry = QgsMapLayerRegistry.instance()
        layer_registry.removeAllMapLayers()
        rendered_layer = impact_function.exposure_impacted
        layer_registry.addMapLayer(rendered_layer)

        # Create impact report
        report_metadata = ReportMetadata(
            metadata_dict=report_a4_portrait_blue)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_function=impact_function,
            minimum_needs_profile=needs_profile)
        impact_report.output_folder = output_folder

        # Get other setting
        settings = QSettings()
        logo_path = settings.value(
            'inasafe/organisation_logo_path', '', type=str)
        impact_report.inasafe_context.organisation_logo = logo_path

        disclaimer_text = settings.value(
            'inasafe/reportDisclaimer', '', type=str)
        impact_report.inasafe_context.disclaimer = disclaimer_text

        north_arrow_path = settings.value(
            'inasafe/north_arrow_path', '', type=str)
        impact_report.inasafe_context.north_arrow = north_arrow_path

        impact_report.qgis_composition_context.extent = rendered_layer.extent()

        impact_report.process_component()

        output_path = impact_report.component_absolute_output_path(
            'a4-portrait-blue')

        # for now, test that output exists
        self.assertTrue(os.path.exists(output_path))

        shutil.rmtree(output_folder, ignore_errors=True)

    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False),
        'Under development')
    def test_default_qgis_report(self):
        """Test generate qgis composition"""
        sample_report_metadata_dict = {
            'key': 'a3-portrait-blue',
            'name': 'a3-portrait-blue',
            'template_folder': '../resources/report-templates/',
            'components': [
                {
                    'key': 'a3-portrait-blue',
                    'type': 'QGISComposer',
                    'processor': qgis_composer_renderer,
                    'extractor': qgis_composer_extractor,
                    'output_format': 'pdf',
                    'template': 'standard-template/'
                                'qgis-composer/'
                                'a4-portrait-blue.qpt',
                    'output_path': 'a4-portrait-blue.pdf',
                    'extra_args': {
                        'page_dpi': 300,
                        'page_width': 210,
                        'page_height': 297,
                    }
                }
            ]
        }
        impact_json = self.fixtures_dir('analysis_sample/13-impact.geojson')
        impact_layer = QgsVectorLayer(impact_json, '', 'ogr')
        analysis_json = self.fixtures_dir(
            'analysis_sample/analysis-summary.geojson')
        analysis_layer = QgsVectorLayer(analysis_json, '', 'ogr')
        minimum_needs = NeedsProfile()
        minimum_needs.load()

        # insert layer to registry
        layer_registry = QgsMapLayerRegistry.instance()
        layer_registry.removeAllMapLayers()
        layer_registry.addMapLayer(impact_layer)

        report_metadata = ReportMetadata(
            metadata_dict=sample_report_metadata_dict)
        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_layer,
            analysis_layer,
            minimum_needs_profile=minimum_needs)

        # Get other setting
        settings = QSettings()
        logo_path = settings.value(
            'inasafe/organisation_logo_path', '', type=str)
        impact_report.inasafe_context.organisation_logo = logo_path

        disclaimer_text = settings.value(
            'inasafe/reportDisclaimer', '', type=str)
        impact_report.inasafe_context.disclaimer = disclaimer_text

        north_arrow_path = settings.value(
            'inasafe/north_arrow_path', '', type=str)
        impact_report.inasafe_context.north_arrow = north_arrow_path

        impact_report.qgis_composition_context.extent = impact_layer.extent()
        impact_report.output_folder = self.fixtures_dir('../output')

        impact_report.process_component()

    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False),
        'Under development')
    def test_generate_default_report(self):
        """Test generate default map report"""
        impact_json = self.fixtures_dir('impact.geojson')
        impact_layer = QgsVectorLayer(impact_json, '', 'ogr')
        analysis_json = self.fixtures_dir(
            'analysis_sample/analysis-summary.geojson')
        analysis_layer = QgsVectorLayer(analysis_json, '', 'ogr')
        report_metadata = ReportMetadata(
            metadata_dict=report_a4_portrait_blue)
        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_layer,
            analysis_layer)

        # Get other setting
        settings = QSettings()
        logo_path = settings.value(
            'inasafe/organisation_logo_path', '', type=str)
        impact_report.inasafe_context.organisation_logo = logo_path

        disclaimer_text = settings.value(
            'inasafe/reportDisclaimer', '', type=str)
        impact_report.inasafe_context.disclaimer = disclaimer_text

        north_arrow_path = settings.value(
            'inasafe/north_arrow_path', '', type=str)
        impact_report.inasafe_context.north_arrow = north_arrow_path

        impact_report.qgis_composition_context.extent = impact_layer.extent()
        impact_report.output_folder = self.fixtures_dir('output')

        impact_report.process_component()
