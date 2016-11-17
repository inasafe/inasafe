# coding=utf-8

"""
Definitions for basic report
"""
from safe.common.utilities import safe_dir
from safe.reportv4.extractors.action_notes import (
    action_checklist_extractor,
    notes_assumptions_extractor)
from safe.reportv4.extractors.aggregate_result import (
    aggregation_result_extractor)
from safe.reportv4.extractors.analysis_detail import analysis_detail_extractor
from safe.reportv4.extractors.analysis_result import analysis_result_extractor
from safe.reportv4.extractors.composer import qgis_composer_extractor
from safe.reportv4.extractors.impact_table import (
    impact_table_extractor,
    impact_table_pdf_extractor)
from safe.reportv4.extractors.minimum_needs import minimum_needs_extractor
from safe.reportv4.processors.default import (
    qgis_composer_renderer,
    jinja2_renderer,
    qgis_composer_html_renderer)
from safe.reportv4.report_metadata import (
    ReportComponentsMetadata,
    Jinja2ComponentsMetadata,
    QgisComposerComponentsMetadata)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# Default impact report component for reusability
impact_report_component_metadata = [
    {
        'key': 'analysis-result',
        'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
        'processor': jinja2_renderer,
        'extractor': analysis_result_extractor,
        'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
        'output_path': 'analysis-result-output.html',
        'template': 'standard-template/'
                    'jinja2/'
                    'analysis-result.html',
    },
    {
        'key': 'analysis-breakdown',
        'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
        'processor': jinja2_renderer,
        'extractor': analysis_detail_extractor,
        'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
        'output_path': 'analysis-detail-output.html',
        'template': 'standard-template/'
                    'jinja2/'
                    'analysis-detail.html',
    },
    {
        'key': 'action-checklist',
        'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
        'processor': jinja2_renderer,
        'extractor': action_checklist_extractor,
        'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
        'output_path': 'action-checklist-output.html',
        'template': 'standard-template/'
                    'jinja2/'
                    'bullet-list-section.html',
    },
    {
        'key': 'notes-assumptions',
        'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
        'processor': jinja2_renderer,
        'extractor': notes_assumptions_extractor,
        'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
        'output_path': 'notes-assumptions-output.html',
        'template': 'standard-template/'
                    'jinja2/'
                    'bullet-list-section.html',
    },
    {
        'key': 'minimum-needs',
        'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
        'processor': jinja2_renderer,
        'extractor': minimum_needs_extractor,
        'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
        'output_path': 'minimum-needs-output.html',
        'template': 'standard-template/'
                    'jinja2/'
                    'minimum-needs.html',
    },
    {
        'key': 'aggregation-result',
        'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
        'processor': jinja2_renderer,
        'extractor': aggregation_result_extractor,
        'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
        'output_path': 'aggregation-result-output.html',
        'template': 'standard-template/'
                    'jinja2/'
                    'aggregation-result.html',
    }
]

# Standard HTML output for impact report
standard_impact_report_metadata_html = {
    'key': 'analysis-result-html',
    'name': 'analysis-result-html',
    'template_folder': safe_dir(sub_dir='../resources/report-templates/'),
    'components': impact_report_component_metadata + [
        {
            'key': 'impact-report',
            'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
            'processor': jinja2_renderer,
            'extractor': impact_table_extractor,
            'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
            'output_path': 'impact-report-output.html',
            'template': 'standard-template/'
                        'jinja2/'
                        'impact-report-layout.html',
        }
    ]
}

# Standard PDF Output for impact report
standard_impact_report_metadata_pdf = {
    'key': 'analysis-result-pdf',
    'name': 'analysis-result-pdf',
    'template_folder': safe_dir(sub_dir='../resources/report-templates/'),
    'components': impact_report_component_metadata + [
        {
            'key': 'impact-report',
            'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
            'processor': jinja2_renderer,
            'extractor': impact_table_extractor,
            'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
            'output_path': 'impact-report-output.html',
            'template': 'standard-template/'
                        'jinja2/'
                        'impact-report-layout.html',
        },
        {
            'key': 'impact-report-pdf',
            'type': ReportComponentsMetadata.AvailableComponent.QGISComposer,
            'processor': qgis_composer_html_renderer,
            'extractor': impact_table_pdf_extractor,
            'output_format': QgisComposerComponentsMetadata.OutputFormat.PDF,
            'output_path': 'impact-report-output.pdf',
        }
    ]
}

report_a4_portrait_blue = {
    'key': 'a4-portrait-blue',
    'name': 'a4-portrait-blue',
    'template_folder': safe_dir(sub_dir='../resources/report-templates/'),
    'components': [
        {
            'key': 'a4-portrait-blue',
            'type': ReportComponentsMetadata.AvailableComponent.QGISComposer,
            'processor': qgis_composer_renderer,
            'extractor': qgis_composer_extractor,
            'output_format': QgisComposerComponentsMetadata.OutputFormat.PDF,
            'template': 'standard-template/'
                        'qgis-composer/'
                        'a4-portrait-blue.qpt',
            'output_path': 'a4-portrait-blue.pdf',
        }
    ]
}
