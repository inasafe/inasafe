# coding=utf-8

"""
Definitions for basic report
"""
from safe.reportv4.extractors.analysis_result import analysis_result_extractor
from safe.reportv4.extractors.composer import qgis_composer_extractor
from safe.reportv4.processors.default import qgis_composer_renderer, \
    jinja2_renderer

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '10/19/16'


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
