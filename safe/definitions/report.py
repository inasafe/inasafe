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
from safe.report.extractors.infographics import (
    population_infographic_extractor,
    infographic_layout_extractor,
    infographic_pdf_extractor)
from safe.report.extractors.minimum_needs import minimum_needs_extractor
from safe.report.extractors.population_chart import (
    population_chart_extractor,
    population_chart_to_png_extractor)
from safe.report.processors.default import (
    qgis_composer_renderer,
    jinja2_renderer,
    qgis_composer_html_renderer,
    qt_svg_to_png_renderer)
from safe.report.report_metadata import (
    ReportComponentsMetadata,
    Jinja2ComponentsMetadata,
    QgisComposerComponentsMetadata)
from safe.utilities.i18n import tr
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
    'extra_args': {
        'header': tr('Analysis Results'),
        'hazard_header': tr('Hazard Zone'),
        'value_header': tr('Count'),
    }
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
    'extra_args': {
        'breakdown_header_type_format': tr('{exposure} type'),
        'breakdown_header_class_format': tr('{exposure} class'),
        'header': tr('Estimated number of {exposure} by type'),
        'notes': tr(
            'Columns and rows containing only 0 or "No data" values are '
            'excluded from the tables.')
    }
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
    'extra_args': {
        'header': tr('Action Checklist')
    }
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
    'extra_args': {
        'header': tr('Notes and assumptions')
    }
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
    'extra_args': {
        'header': tr('Minimum needs'),
        'header_frequency_format': tr(
            'Relief items to be provided {frequency}'),
        'total_header': tr('Total'),
        'need_header_format': tr('{name} [{unit_abbreviation}]')
    }
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
    'extra_args': {
        'header': tr('Aggregation Result'),
        'notes': tr(
            'Columns and rows containing only 0 or "No data" values are '
            'excluded from the tables.'),
        'aggregation_area_default_header': tr('Aggregation area'),
        'total_header': tr('Total'),
        'total_in_aggregation_header': tr('Total'),
    }
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
    'extra_args': {
        'header': tr('Detailed demographic breakdown'),
        'sections': {
            'age': {
                'header': tr('Detailed Age Report')
            },
            'gender': {
                'header': tr('Detailed Gender Report')
            },
            'minimum_needs': {
                'header': tr('Detailed Minimum Needs Report')
            }
        },
        'defaults': {
            'aggregation_header': tr('Aggregation area'),
            'total_population_header': tr('Total Population'),
            'total_header': tr('Total'),
            'notes': tr(
                'Columns and rows containing only 0 or "No data" values are '
                'excluded from the tables.'),
        }
    }
}

population_chart_svg_component = {
    'key': 'population-chart',
    'type': ReportComponentsMetadata.AvailableComponent.Jinja2,
    'processor': jinja2_renderer,
    'extractor': population_chart_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
    'output_path': 'population-chart.svg',
    'template': 'standard-template'
                '/jinja2/svg'
                '/donut-chart.svg',
    'extra_args': {
        'chart_title': tr('Estimated total population'),
        'total_header': tr('Population')
    }
}

population_chart_png_component = {
    # This component depends on population_chart_svg_component
    'key': 'population-chart-png',
    'type': ReportComponentsMetadata.AvailableComponent.QtRenderer,
    'processor': qt_svg_to_png_renderer,
    'extractor': population_chart_to_png_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
    'output_path': 'population-chart.png',
    'extra_args': {
        'width': 256,
        'height': 256
    }
}

population_infographic_component = {
    # This component depends on population_chart_png_component
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
        # definitions for texts
        'sections': {
            'people': {
                'header': tr('People'),
                'sub_header': tr('Affected')
            },
            'vulnerability': {
                'header': tr('Vulnerability'),
                'sub_header_format': tr('from {number_affected:,d} affected'),
                'items': {
                    'headers': [
                        tr('Female'),
                        tr('Youth'),
                        tr('Adult'),
                        tr('Elderly')
                    ]
                }
            },
            'minimum_needs': {
                'header': tr('Minimum needs'),
                'empty_unit_string': tr('units')
            }
        },
        # definitions for icons
        'icons': {
            'total_affected_field': resource_url(resources_path(
                'img/definitions/people.png')),
            'female_count_field': resource_url(resources_path(
                'img/definitions/female.png')),
            'youth_count_field': resource_url(resources_path(
                'img/definitions/youth.png')),
            'adult_count_field': resource_url(resources_path(
                'img/definitions/adult.png')),
            'elderly_count_field': resource_url(resources_path(
                'img/definitions/elderly.png')),
            'minimum_needs__rice_count_field': resource_url(resources_path(
                'img/definitions/rice.png')),
            'minimum_needs__toilets_count_field': resource_url(resources_path(
                'img/definitions/toilets.png')),
            'minimum_needs__drinking_water_count_field': resource_url(
                resources_path('img/definitions/drinking_water.png')),
            'minimum_needs__clean_water_count_field': resource_url(
                resources_path('img/definitions/clean_water.png')),
            'minimum_needs__family_kits_count_field': resource_url(
                resources_path('img/definitions/family_kits.png')),
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
        population_chart_svg_component,
        population_chart_png_component,
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
                'infographics': [population_infographic_component['key']],
                'footer_format': tr(
                    'InaSAFE {version} | {analysis_date} | {analysis_time} | '
                    'info@inasafe.org | Indonesian Government-'
                    'Australian Government-World Bank-GFDRR')
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
            'extra_args': {
                'defaults': {
                    'provenance_source': tr('an unknown source')
                },
                'provenance_format': tr(
                    'Hazard details'
                    '<p>{hazard_provenance}</p>'
                    'Exposure details'
                    '<p>{exposure_provenance}</p>')
            }
        }
    ]
}

# Standard PDF Output for impact report
standard_impact_report_metadata_pdf = {
    'key': 'analysis-result-pdf',
    'name': 'analysis-result-pdf',
    'template_folder': safe_dir(sub_dir='../resources/report-templates/'),
    'components': standard_impact_report_metadata_html['components'] + [
        # Impact Report PDF
        {
            'key': 'impact-report-pdf',
            'type': ReportComponentsMetadata.AvailableComponent.QGISComposer,
            'processor': qgis_composer_html_renderer,
            'extractor': impact_table_pdf_extractor,
            'output_format': QgisComposerComponentsMetadata.OutputFormat.PDF,
            'output_path': 'impact-report-output.pdf',
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
        population_chart_svg_component,
        population_chart_png_component,
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

map_report_extra_args = {
    'defaults': {
        'unknown_source': tr('Unknown'),
        'aggregation_not_used': tr('Not used')
    },
    'version-title': tr('Software'),
    'disclaimer-title': tr('Disclaimer'),
    'date-title': tr('Date'),
    'date-format': '%Y-%m-%d',
    'time-title': tr('Time'),
    'time-format': '%H:%M',
    'caution-title': tr('Note'),
    'caution-text': tr(
        'This assessment is a guide - we strongly recommend that '
        'you ground truth the results shown here before '
        'deploying resources and / or personnel.'),
    'version-text': tr('InaSAFE {version}'),
    'legend-title': tr('Legend'),
    'information-title': tr('Analysis information'),
    'supporters-title': tr('Report produced by'),
    'source-title': tr('Data Source'),
    'analysis-title': tr('Analysis Name'),
    'spatial-reference-title': tr('Reference'),
    'spatial-reference-format': tr(
        'Geographic Coordinates - {crs}')
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
            'template': '../qgis-composer-templates/'
                        'a4-portrait-blue.qpt',
            'output_path': 'a4-portrait-blue.pdf',
            'extra_args': map_report_extra_args
        },
        {
            'key': 'a4-landscape-blue',
            'type': ReportComponentsMetadata.AvailableComponent.QGISComposer,
            'processor': qgis_composer_renderer,
            'extractor': qgis_composer_extractor,
            'output_format': QgisComposerComponentsMetadata.OutputFormat.PDF,
            'template': '../qgis-composer-templates/'
                        'a4-landscape-blue.qpt',
            'output_path': 'a4-landscape-blue.pdf',
            'orientation': 'landscape',
            'page_dpi': 300,
            'page_width': 297,
            'page_height': 210,
            'extra_args': map_report_extra_args
        }
    ]
}
