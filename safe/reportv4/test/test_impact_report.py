# coding=utf-8
import io
import os
import unittest

import shutil
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

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.PyQt.QtCore import QSettings
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry
from safe.definitionsv4.report import (
    report_a3_portrait_blue,
    standard_impact_report_metadata)
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
            metadata_dict=standard_impact_report_metadata)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_function=impact_function,
            minimum_needs_profile=needs_profile)
        impact_report.output_folder = output_folder
        impact_report.process_component()

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
            metadata_dict=standard_impact_report_metadata)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_function=impact_function,
            minimum_needs_profile=needs_profile)
        impact_report.output_folder = output_folder
        impact_report.process_component()

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
            metadata_dict=standard_impact_report_metadata)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_function=impact_function,
            minimum_needs_profile=needs_profile)
        impact_report.output_folder = output_folder
        impact_report.process_component()

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
            metadata_dict=standard_impact_report_metadata)

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
            metadata_dict=report_a3_portrait_blue)
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
