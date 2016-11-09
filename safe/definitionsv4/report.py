# coding=utf-8

"""
Definitions for basic report
"""
from safe.common.utilities import safe_dir
from safe.reportv4.extractors.action_notes import action_checklist_extractor, \
    notes_assumptions_extractor
from safe.reportv4.extractors.analysis_detail import analysis_detail_extractor
from safe.reportv4.extractors.analysis_result import analysis_result_extractor
from safe.reportv4.extractors.composer import qgis_composer_extractor
from safe.reportv4.extractors.impact_table import impact_table_extractor
from safe.reportv4.extractors.minimum_needs import minimum_needs_extractor
from safe.reportv4.processors.default import qgis_composer_renderer, \
    jinja2_renderer

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

standard_impact_report_metadata = {
    'key': 'analysis-result-html',
    'name': 'analysis-result-html',
    'template_folder': safe_dir(sub_dir='../resources/report-templates/'),
    'components': [
        {
            'key': 'analysis-result',
            'type': 'Jinja2',
            'processor': jinja2_renderer,
            'extractor': analysis_result_extractor,
            'output_format': 'string',
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
            'output_format': 'string',
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
            'output_format': 'string',
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
            'output_format': 'string',
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
            'output_format': 'string',
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

report_a3_portrait_blue = {
    'key': 'a3-portrait-blue',
    'name': 'a3-portrait-blue',
    'template_folder': '../resources/report-templates/',
    'components': [
        {
            'key': 'analysis-result',
            'type': 'Jinja2',
            'processor': jinja2_renderer,
            'extractor': analysis_result_extractor,
            'output_format': 'string',
            'template': 'standard-template/jinja2/analysis-result.html',
        },
        {
            'key': 'a3-portrait-blue',
            'type': 'QGISComposer',
            'processor': qgis_composer_renderer,
            'extractor': qgis_composer_extractor,
            'output_format': 'pdf',
            'template': 'standard-template/qgis-composer/a3-portrait-blue.qpt',
            'output_path': 'a3-portrait-blue.pdf',
            'extra_args': {
                'page_dpi': 300,
                'page_width': 210,
                'page_height': 297,
            }
        }
    ]
    # 'components': [
    #     {
    #         'key': 'analysis_information',
    #         'type': 'Jinja2',
    #         'processor': jinja2_transformers,
    #         'extractor': 'extractors/analysis_information.py',
    #         'output_format': 'file',
    #         'template': 'component/analysis-information.html',
    #         'output_path': 'analysis-information.html',
    #     },
    #     {
    #         'key': 'disclaimer',
    #         'type': 'Jinja2',
    #         'processor': jinja2_transformers,
    #         'extractor': 'extractors/disclaimer.py',
    #         'output_format': 'file',
    #         'template': 'component/disclaimer.html',
    #         'output_path': 'disclaimer.html',
    #     },
    #     {
    #         'key': 'simple_report',
    #         'type': 'QGISComposer',
    #         'processor': qgis_composer_transformers,
    #         'extractor': 'extractors/composer.py',
    #         'output_format': 'pdf',
    #         'template': 'simple-report.qpt',
    #         'output_path': 'simple-report.pdf',
    #         'extra_args': {
    #             'page_dpi': 300,
    #             'page_width': 210,
    #             'page_height': 297,
    #         }
    #     }
    # ]
}
