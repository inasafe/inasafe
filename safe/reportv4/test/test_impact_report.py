# coding=utf-8
import unittest

import os

from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.reportv4.extractors.action_notes import action_checklist_extractor, \
    notes_assumptions_extractor
from safe.reportv4.extractors.analysis_result import analysis_result_extractor
from safe.reportv4.extractors.composer import qgis_composer_extractor
from safe.reportv4.extractors.impact_table import impact_table_extractor
from safe.reportv4.extractors.minimum_needs import minimum_needs_extractor
from safe.reportv4.processors.default import qgis_composer_renderer, \
    jinja2_renderer
from safe.reportv4.report_metadata import ReportMetadata
from safe.test.utilities import get_qgis_app, load_test_vector_layer

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from PyQt4.QtCore import QSettings
from PyQt4.QtXml import QDomDocument
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsComposition
from safe.definitionsv4.report import report_a3_portrait_blue
from safe.reportv4.impact_report import ImpactReport

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '10/26/16'


class TestImpactReport(unittest.TestCase):

    @classmethod
    def fixtures_dir(cls, path):
        dirname = os.path.dirname(__file__)
        return os.path.join(dirname, 'fixtures', path)

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
        impact_json = self.fixtures_dir('analysis_sample/13-impact.geojson')
        impact_layer = QgsVectorLayer(impact_json, '', 'ogr')
        analysis_json = self.fixtures_dir('analysis_sample/analysis-summary.geojson')
        analysis_layer = QgsVectorLayer(analysis_json, '', 'ogr')
        minimum_needs = NeedsProfile()
        minimum_needs.load()
        report_metadata = ReportMetadata(
            metadata_dict=sample_report_metadata_dict)
        impact_report = ImpactReport(
            IFACE,
            report_metadata,
            impact_layer,
            analysis_layer,
            minimum_needs_profile=minimum_needs)
        impact_report.output_folder = self.fixtures_dir('../output')
        impact_report.process_component()

    def test_existing_population_json(self):
        layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        print layer.extent().asWktPolygon()
        print layer.extent().width()

    def test_qgis_composer_print(self):
        composition = QgsComposition(CANVAS.mapRenderer())

        template_path = os.path.abspath(
            '../resources/report-templates/standard-template/qgis-composer/blank.qpt')

        with open(template_path) as f:
            template_content = f.read()

        document = QDomDocument()
        document.setContent(template_content)

        # load composition object from template
        result = composition.loadFromTemplate(document, {})
        composition.exportAsPDF(self.fixtures_dir('../output/test.pdf'))

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
        analysis_json = self.fixtures_dir('analysis_sample/analysis-summary.geojson')
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

    def test_generate_default_report(self):
        """Test generate default map report"""
        impact_json = self.fixtures_dir('impact.geojson')
        impact_layer = QgsVectorLayer(impact_json, '', 'ogr')
        analysis_json = self.fixtures_dir('analysis_sample/analysis-summary.geojson')
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

