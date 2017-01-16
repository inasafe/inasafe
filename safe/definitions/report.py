# coding=utf-8

"""
Definitions for basic report
"""
from __future__ import absolute_import

from qgis.core import QgsComposition

from safe.common.utilities import safe_dir
from safe.report.extractors.action_notes import (
    action_checklist_extractor,
    notes_assumptions_extractor)
from safe.report.extractors.aggregate_postprocessors import \
    aggregation_postprocessors_extractor
from safe.report.extractors.aggregate_result import \
    aggregation_result_extractor
from safe.report.extractors.analysis_detail import analysis_detail_extractor
from safe.report.extractors.analysis_result import analysis_result_extractor
from safe.report.extractors.composer import qgis_composer_extractor
from safe.report.extractors.impact_table import (
    impact_table_extractor,
    impact_table_pdf_extractor)
from safe.report.extractors.infographics import \
    population_infographic_extractor, infographic_layout_extractor, \
    infographic_pdf_extractor
from safe.report.extractors.minimum_needs import minimum_needs_extractor
from safe.report.processors.default import (
    qgis_composer_renderer,
    jinja2_renderer,
    qgis_composer_html_renderer)
from safe.report.report_metadata import (
    ReportComponentsMetadata,
    Jinja2ComponentsMetadata,
    QgisComposerComponentsMetadata)
from safe.utilities.resources import resource_url, resources_path

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# Individual report component
analysis_result_component = {
    'key': 'analysis-result',
    'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
    'processor': jinja2_renderer,
    'extractor': analysis_result_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'analysis-result-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'analysis-result.html',
}

analysis_breakdown_component = {
    'key': 'analysis-breakdown',
    'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
    'processor': jinja2_renderer,
    'extractor': analysis_detail_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'analysis-detail-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'analysis-detail.html',
}

action_checklist_component = {
    'key': 'action-checklist',
    'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
    'processor': jinja2_renderer,
    'extractor': action_checklist_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'action-checklist-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'bullet-list-section.html',
}

notes_assumptions_component = {
    'key': 'notes-assumptions',
    'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
    'processor': jinja2_renderer,
    'extractor': notes_assumptions_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'notes-assumptions-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'bullet-list-section.html',
}

minimum_needs_component = {
    'key': 'minimum-needs',
    'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
    'processor': jinja2_renderer,
    'extractor': minimum_needs_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'minimum-needs-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'minimum-needs.html',
}

aggregation_result_component = {
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

aggregation_postprocessors_component = {
    'key': 'aggregation-postprocessors',
    'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
    'processor': jinja2_renderer,
    'extractor': aggregation_postprocessors_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'aggregation-postprocessors-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'aggregation-postprocessors.html',
}

population_infographic_component = {
    'key': 'population-infographic',
    'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
    'processor': jinja2_renderer,
    'extractor': population_infographic_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'population-infographic-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'population-infographic.html',
    'extra_args': {
        'icons': {
            'total_affected_field': resource_url(resources_path(
                'img/definitions/people.svg')),
            'female_count_field': resource_url(resources_path(
                'img/definitions/female.svg')),
            'youth_count_field': resource_url(resources_path(
                'img/definitions/youth.svg')),
            'adult_count_field': resource_url(resources_path(
                'img/definitions/adult.svg')),
            'elderly_count_field': resource_url(resources_path(
                'img/definitions/elderly.svg')),
            'minimum_needs__rice_count_field': resource_url(resources_path(
                'img/definitions/rice.svg')),
            'minimum_needs__toilets_count_field': resource_url(resources_path(
                'img/definitions/toilets.svg')),
            'minimum_needs__drinking_water_count_field': resource_url(
                resources_path('img/definitions/drinking_water.svg')),
            'minimum_needs__clean_water_count_field': resource_url(
                resources_path('img/definitions/clean_water.svg')),
            'minimum_needs__family_kits_count_field': resource_url(
                resources_path('img/definitions/family_kits.svg')),
        }
    }
}

# Default impact report component for reusability
impact_report_component_metadata = [
    analysis_result_component,
    analysis_breakdown_component,
    action_checklist_component,
    notes_assumptions_component,
    minimum_needs_component,
    aggregation_result_component,
    aggregation_postprocessors_component,
]

# Standard HTML output for impact report
standard_impact_report_metadata_html = {
    'key': 'analysis-result-html',
    'name': 'analysis-result-html',
    'template_folder': safe_dir(sub_dir='../resources/report-templates/'),
    'components': impact_report_component_metadata + [
        population_infographic_component,
        # Infographic Layout HTML
        {
            'key': 'infographic-layout',
            'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
            'processor': jinja2_renderer,
            'extractor': infographic_layout_extractor,
            'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
            'output_path': 'infographic.html',
            'extra_args': {
                'infographics': [population_infographic_component['key']]
            },
            'template': 'standard-template/'
                        'jinja2/'
                        'infographic-layout.html',
        },
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
        # Impact Report HTML
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
        # Impact Report PDF
        {
            'key': 'impact-report-pdf',
            'type': ReportComponentsMetadata.AvailableComponent.QGISComposer,
            'processor': qgis_composer_html_renderer,
            'extractor': impact_table_pdf_extractor,
            'output_format': QgisComposerComponentsMetadata.OutputFormat.PDF,
            'output_path': 'impact-report-output.pdf',
        },
        population_infographic_component,
        # Infographic Layout HTML
        {
            'key': 'infographic-layout',
            'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
            'processor': jinja2_renderer,
            'extractor': infographic_layout_extractor,
            'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
            'output_path': 'infographic.html',
            'extra_args': {
                'infographics': [population_infographic_component['key']]
            },
            'template': 'standard-template/'
                        'jinja2/'
                        'infographic-layout.html',
        },
        # Infographic Layout PDF
        {
            'key': 'infographic-pdf',
            'type': ReportComponentsMetadata.AvailableComponent.QGISComposer,
            'processor': qgis_composer_html_renderer,
            'extractor': infographic_pdf_extractor,
            'output_format': QgisComposerComponentsMetadata.OutputFormat.PDF,
            'output_path': 'infographic.pdf',
            'page_dpi': 300,
            'page_width': 297,
            'page_height': 210,
        }
    ]
}

# Standard PDF Output for infographic report
standard_infographic_report_metadata_pdf = {
    'key': 'infographic-result-pdf',
    'name': 'infographic-result-pdf',
    'template_folder': safe_dir(sub_dir='../resources/report-templates/'),
    'components': [
        population_infographic_component,
        {
            'key': 'infographic-layout',
            'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
            'processor': jinja2_renderer,
            'extractor': infographic_layout_extractor,
            'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
            'output_path': 'infographic.html',
            'extra_args': {
                'infographics': [population_infographic_component['key']]
            },
        },
        {
            'key': 'infographic-pdf',
            'type': ReportComponentsMetadata.AvailableComponent.QGISComposer,
            'processor': qgis_composer_html_renderer,
            'extractor': infographic_pdf_extractor,
            'output_format': QgisComposerComponentsMetadata.OutputFormat.PDF,
            'output_path': 'infographic.pdf',
            'page_dpi': 300,
            'page_width': 297,
            'page_height': 210,
        }
    ]
}

report_a4_blue = {
    'key': 'a4-blue',
    'name': 'a4-blue',
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
        },
        {
            'key': 'a4-landscape-blue',
            'type': ReportComponentsMetadata.AvailableComponent.QGISComposer,
            'processor': qgis_composer_renderer,
            'extractor': qgis_composer_extractor,
            'output_format': QgisComposerComponentsMetadata.OutputFormat.PDF,
            'template': 'standard-template/'
                        'qgis-composer/'
                        'a4-landscape-blue.qpt',
            'output_path': 'a4-landscape-blue.pdf',
            'orientation': 'landscape',
            'page_dpi': 300,
            'page_width': 297,
            'page_height': 210,
        }
    ]
}
