# coding=utf-8
import unittest

from safe.report.extractors.action_notes import action_checklist_extractor
from safe.report.extractors.analysis_result import analysis_result_extractor
from safe.report.processors.default import jinja2_renderer
from safe.report.report_metadata import ReportMetadata

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = ':%H$'


class TestReportMetadata(unittest.TestCase):

    def test_metadata_parsing(self):
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
                }
            ]
        }

        report_metadata = ReportMetadata(
            metadata_dict=sample_report_metadata_dict)

        self.assertEqual(
            sample_report_metadata_dict['key'], report_metadata.key)
        self.assertEqual(
            sample_report_metadata_dict['name'], report_metadata.name)
        self.assertEqual(
            len(sample_report_metadata_dict['components']),
            len(report_metadata.components))
