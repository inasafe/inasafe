# coding=utf-8
import io
import os
import unittest
from jinja2.environment import Template

from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.reportv4.extractors.action_notes import (
    action_checklist_extractor,
    notes_assumptions_extractor)
from safe.reportv4.extractors.analysis_detail import analysis_detail_extractor
from safe.reportv4.extractors.analysis_result import analysis_result_extractor
from safe.reportv4.extractors.composer import qgis_composer_extractor
from safe.reportv4.extractors.impact_table import impact_table_extractor
from safe.reportv4.extractors.minimum_needs import minimum_needs_extractor
from safe.reportv4.processors.default import (
    qgis_composer_renderer,
    jinja2_renderer)
from safe.reportv4.report_metadata import ReportMetadata
from safe.test.utilities import get_qgis_app
from safe.utilities.keyword_io import KeywordIO

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from PyQt4.QtCore import QSettings
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry
from safe.definitionsv4.report import report_a3_portrait_blue
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
        # current_directory = os.path.abspath(
        #     os.path.join(
        #         os.path.dirname(__file__), '../../../')
        # )
        current_directory = os.path.abspath('../resources')
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

    @classmethod
    def patch_keywords(cls, layer):
        """Patch keywords shorthand from QgsVectorLayer

        TODO: Delete me once layer is taken from impact_function

        :param layer: QgsVectorLayer to patch
        :type layer: QgsVectorLayer
        """
        try:
            # in case it already contains keywords
            keywords = layer.keywords
        except AttributeError:
            keywords = KeywordIO().read_keywords(layer)
        layer.keywords = keywords

    def test_analysis_result(self):
        """Test generate analysis result"""
        sample_report_metadata_dict = {
            'key': 'analysis-result-html',
            'name': 'analysis-result-html',
            'template_folder': '../resources/report-templates/',
            'components': [
                {
                    'key': 'analysis-result',
                    'type': 'Jinja2',
                    'processor': jinja2_renderer,
                    'extractor': analysis_result_extractor,
                    'output_format': 'file',
                    'output_path': 'analysis-result-output.html',
                    'template': 'standard-template/'
                                'jinja2/'
                                'analysis-result.html',
                },
                {
                    'key': 'analysis-breakdown',
                    'type': 'Jinja2',
                    'processor': jinja2_renderer,
                    'extractor': analysis_detail_extractor,
                    'output_format': 'file',
                    'output_path': 'analysis-detail-output.html',
                    'template': 'standard-template/'
                                'jinja2/'
                                'analysis-detail.html',
                },
                {
                    'key': 'action-checklist',
                    'type': 'Jinja2',
                    'processor': jinja2_renderer,
                    'extractor': action_checklist_extractor,
                    'output_format': 'file',
                    'output_path': 'action-checklist-output.html',
                    'template': 'standard-template/'
                                'jinja2/'
                                'bullet-list-section.html',
                },
                {
                    'key': 'notes-assumptions',
                    'type': 'Jinja2',
                    'processor': jinja2_renderer,
                    'extractor': notes_assumptions_extractor,
                    'output_format': 'file',
                    'output_path': 'notes-assumptions-output.html',
                    'template': 'standard-template/'
                                'jinja2/'
                                'bullet-list-section.html',
                },
                {
                    'key': 'minimum-needs',
                    'type': 'Jinja2',
                    'processor': jinja2_renderer,
                    'extractor': minimum_needs_extractor,
                    'output_format': 'file',
                    'output_path': 'minimum-needs-output.html',
                    'template': 'standard-template/'
                                'jinja2/'
                                'minimum-needs.html',
                },
                {
                    'key': 'impact-report',
                    'type': 'Jinja2',
                    'processor': jinja2_renderer,
                    'extractor': impact_table_extractor,
                    'output_format': 'file',
                    'output_path': 'impact-report-output.html',
                    'template': 'standard-template/'
                                'jinja2/'
                                'impact-report-layout.html',
                }
            ]
        }

        exposure_json = self.fixtures_dir('analysis_sample/1-exposure.geojson')
        exposure_layer = QgsVectorLayer(exposure_json, '', 'ogr')
        self.patch_keywords(exposure_layer)

        hazard_json = self.fixtures_dir('analysis_sample/2-hazard.geojson')
        hazard_layer = QgsVectorLayer(hazard_json, '', 'ogr')
        self.patch_keywords(hazard_layer)

        impact_json = self.fixtures_dir('analysis_sample/14-impact.geojson')
        impact_layer = QgsVectorLayer(impact_json, '', 'ogr')
        self.patch_keywords(impact_layer)

        analysis_json = self.fixtures_dir(
            'analysis_sample/18-analysis.geojson')
        analysis_layer = QgsVectorLayer(analysis_json, '', 'ogr')
        self.patch_keywords(analysis_layer)

        breakdown_csv = self.fixtures_dir(
            'analysis_sample/16-breakdown.csv')
        exposure_breakdown = QgsVectorLayer(breakdown_csv, '', 'ogr')
        self.patch_keywords(exposure_breakdown)

        minimum_needs = NeedsProfile()
        minimum_needs.load()

        report_metadata = ReportMetadata(
            metadata_dict=sample_report_metadata_dict)

        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            exposure_layer=exposure_layer,
            hazard_layer=hazard_layer,
            impact_layer=impact_layer,
            analysis_layer=analysis_layer,
            exposure_breakdown=exposure_breakdown,
            minimum_needs_profile=minimum_needs)
        impact_report.output_folder = self.fixtures_dir('../output')
        impact_report.process_component()

        output_path = os.path.abspath(
            os.path.join(
                impact_report.output_folder, 'impact-report-output.html'))

        self.assertCompareFileControl(
            self.fixtures_dir('controls/impact-report-output.html'),
            output_path)


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

