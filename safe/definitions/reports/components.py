# coding=utf-8
"""Contains definitions about Report components.

"""
from __future__ import absolute_import

from safe.definitions.concepts import concepts
from safe.definitions.exposure import (
    exposure_structure,
    exposure_road,
    exposure_land_cover,
    exposure_population)
from safe.definitions.reports import (
    jinja2_component_type,
    qgis_composer_component_type,
    qt_renderer_component_type,
    svg_product_tag,
    png_product_tag,
    infographic_product_tag,
    final_product_tag,
    html_product_tag,
    table_product_tag,
    map_product_tag,
    pdf_product_tag,
    template_product_tag,
    qpt_product_tag)

from safe.utilities.resources import resources_path
from safe.definitions.fields import (
    affected_field,
    total_affected_field,
    total_not_affected_field,
    total_not_exposed_field,
    population_exposed_per_mmi_field,
    population_displaced_per_mmi,
    fatalities_per_mmi_field,
    population_count_field,
    displaced_field,
    fatalities_field,
    female_displaced_count_field,
    youth_displaced_count_field,
    adult_displaced_count_field,
    elderly_displaced_count_field,
    exposure_count_field,
    affected_productivity_field,
    affected_production_cost_field,
    affected_production_value_field)
from safe.definitions.styles import charcoal_black
from safe.report.extractors.action_notes import (
    action_checklist_extractor,
    notes_assumptions_extractor,
    action_checklist_report_extractor,
    action_checklist_report_pdf_extractor)
from safe.report.extractors.aggregate_postprocessors import (
    aggregation_postprocessors_extractor)
from safe.report.extractors.aggregate_result import (
    aggregation_result_extractor)
from safe.report.extractors.analysis_detail import analysis_detail_extractor
from safe.report.extractors.analysis_provenance_details import (
    analysis_provenance_details_extractor,
    analysis_provenance_details_simplified_extractor,
    analysis_provenance_details_report_extractor,
    analysis_provenance_details_pdf_extractor)
from safe.report.extractors.analysis_question import (
    analysis_question_extractor)
from safe.report.extractors.general_report import general_report_extractor
from safe.report.extractors.composer import (
    qgis_composer_extractor,
    qgis_composer_infographic_extractor)
from safe.report.extractors.impact_table import (
    impact_table_extractor,
    impact_table_pdf_extractor)
from safe.report.extractors.infographics import (
    population_chart_legend_extractor,
    infographic_people_section_notes_extractor)
from safe.report.extractors.minimum_needs import minimum_needs_extractor
from safe.report.extractors.mmi_detail import mmi_detail_extractor
from safe.report.extractors.population_chart import (
    population_chart_extractor,
    population_chart_to_png_extractor)
from safe.report.processors.default import (
    qgis_composer_renderer,
    jinja2_renderer,
    qgis_composer_html_renderer,
    qt_svg_to_png_renderer)
from safe.report.report_metadata import (
    Jinja2ComponentsMetadata,
    QgisComposerComponentsMetadata)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


# Individual report component
analysis_question_component = {
    'key': 'analysis-question',
    'type': jinja2_component_type,
    'processor': jinja2_renderer,
    'extractor': analysis_question_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'analysis-result-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'analysis-question.html',
    'extra_args': {
        'header': tr('Analysis question')
    }
}

general_report_component = {
    'key': 'general-report',
    'type': jinja2_component_type,
    'processor': jinja2_renderer,
    'extractor': general_report_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'general-report-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'general-report.html',
    'extra_args': {
        'header': tr('General Report'),
        'table_header_format': tr('Estimated {title} affected per {unit}'),
        'hazard_header': tr('Hazard Zone'),
        # Used to customize header.
        # See issue inasafe#3688: remove all 'total' words
        'reported_fields': [
            {
                'header': affected_field['name'],
                'field': total_affected_field
            },
            {
                # specify it directly since there is no field for
                # unaffected only.
                'header': tr('Not Affected'),
                'field': total_not_affected_field
            },
            {
                'header': tr('Not Exposed'),
                'field': total_not_exposed_field
            },
            {
                'header': displaced_field['name'],
                'field': displaced_field
            },
            {
                'header': fatalities_field['name'],
                'field': fatalities_field
            }
        ],
        'concept_notes': {
            'population_concepts': [
                concepts['exposed_people'],
                concepts['affected_people'],
                concepts['displaced_people']
            ],
            'general_concepts': [
                concepts['affected']
            ],
            'note_format': u'{name}: {description}'
        }
    }
}

mmi_detail_component = {
    'key': 'mmi-detail',
    'type': jinja2_component_type,
    'processor': jinja2_renderer,
    'extractor': mmi_detail_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'mmi-detail-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'mmi-detail.html',
    'extra_args': {
        'header': tr('MMI Detail'),
        'mmi_header': tr('MMI'),
        # used to customize header
        'reported_fields': [
            {
                'header': tr('Exposed'),
                'field': population_exposed_per_mmi_field
            },
            {
                'header': tr('Displaced'),
                'field': population_displaced_per_mmi
            },
            {
                'header': tr('Fatalities'),
                'field': fatalities_per_mmi_field
            }
        ],
        'total_fields': [
            # TODO: change to total exposed population field once it is
            # available
            population_count_field,
            displaced_field,
            fatalities_field
        ],
        'total_header': tr('Total'),
    }
}

analysis_detail_component = {
    'key': 'analysis-detail',
    'type': jinja2_component_type,
    'processor': jinja2_renderer,
    'extractor': analysis_detail_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'analysis-detail-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'analysis-detail.html',
    'extra_args': {
        'exposure_type_header_mapping': {
            # In the report, exposure type is usually singular
            # We can also use this to rename exposure name
            exposure_structure['key']: tr('Structure'),
            exposure_road['key']: tr('Road'),
            exposure_land_cover['key']: tr('Land cover')
        },
        'hazard_class_header_mapping': {
            'affected': {
                'header': tr('Affected'),
                # this is color for background in affected column in
                # hex #rgb format. Don't declare this for default bootstrap
                # background
                # 'color': affected_column_background.name()
            },
            'not_affected': {
                'header': tr('Not affected')
            }
        },
        'group_border_color': charcoal_black.name(),
        'breakdown_header_type_format': tr('{exposure} type'),
        'breakdown_header_class_format': tr('{exposure} class'),
        'header': tr('Analysis Detail'),
        'table_header_format': tr(
            'Estimated {title} {unit} by {exposure} type'),
        'notes': [],
        'extra_table_header_format': tr(
            'Estimated loss by affected {exposure} type'),
        'exposure_extra_fields': {
            exposure_land_cover['key']: [
                affected_productivity_field,
                affected_production_cost_field,
                affected_production_value_field,
            ],
        },
    }
}

action_checklist_component = {
    'key': 'action-checklist',
    'type': jinja2_component_type,
    'processor': jinja2_renderer,
    'extractor': action_checklist_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'action-checklist-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'action-note-categorized.html',
    'extra_args': {
        'header': tr('Action Checklist')
    }
}

notes_assumptions_component = {
    'key': 'notes-assumptions',
    'type': jinja2_component_type,
    'processor': jinja2_renderer,
    'extractor': notes_assumptions_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'notes-assumptions-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'action-note-categorized.html',
    'extra_args': {
        'header': tr('Notes and assumptions'),
        'analysis_notes': {
            'item_header': tr('analysis notes'),
            'item_list': [
                tr('Columns and rows containing only 0 or "No data" values '
                   'are excluded from the tables.')
            ]
        },
        'affected_note_format': {
            'item_header': tr('affected notes'),
            'item_list': [
                tr('Exposures in this following hazard classes are considered '
                   'affected: {hazard_classes}')
            ]
        },
        'displacement_rates_note_format': {
            'item_header': tr('displacement rates notes'),
            'item_list': [
                tr('For this analysis, the following displacement rates were '
                   'used: {rate_description}')
            ]
        },
        'hazard_displacement_rates_note_format': tr(
            '{name} - {displacement_rate:.0%}'),
        'fatality_rates_note_format': {
            'item_header': tr('fatality rates notes'),
            'item_list': [
                tr('For this analysis, the following fatality rates were '
                   'used: {rate_description}')
            ]
        },
        'hazard_fatality_rates_note_format': tr(
            '{name} - {fatality_rate}%')
    }
}

minimum_needs_component = {
    'key': 'minimum-needs',
    'type': jinja2_component_type,
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
        'header_additional_needs_format': tr(
            'Additional items to be provided {frequency}'),
        'total_header': tr('Total'),
        'need_header_format': tr('{name} [{unit_abbreviation}]'),
        'zero_displaced_message': tr(
            'Analysis produced 0 displaced count. No calculations produced.')
    }
}

aggregation_result_component = {
    'key': 'aggregation-result',
    'type': jinja2_component_type,
    'processor': jinja2_renderer,
    'extractor': aggregation_result_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'aggregation-result-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'aggregation-result.html',
    'extra_args': {
        'header': tr('Aggregation Result'),
        'notes': [],
        'table_header_format': tr(
            'Estimated {title} {unit} by aggregation area'),
        'aggregation_area_default_header': tr('Aggregation area'),
        'total_header': tr('Total'),
        'total_in_aggregation_header': tr('Total'),
    }
}

aggregation_postprocessors_component = {
    'key': 'aggregation-postprocessors',
    'type': jinja2_component_type,
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
            'minimum_needs': {
                'header': tr('Estimated number of minimum needs per week')
            }
        },
        'defaults': {
            'aggregation_header': tr('Aggregation area'),
            'total_population_header': tr('Total Displaced Population'),
            'total_header': tr('Total'),
            'notes': [],
            'section_header_format': tr(
                'Estimated number of people displaced by {header_name} '
                'per aggregation area'),
            'group_header_format': tr('{header_name} breakdown'),
            'zero_displaced_message': tr(
                'Analysis produced 0 displaced count. '
                'No calculations produced.'),
            'no_gender_rate_message': tr(
                'Gender ratio is not found. '
                'No calculations produced.'),
            'no_age_rate_message': tr(
                'Age ratio is not found. '
                'No calculations produced.'),
            'no_vulnerability_rate_message': tr(
                'Vulnerability ratio is not found. '
                'No calculations produced.')
        }
    }
}

analysis_provenance_details_component = {
    'key': 'analysis-provenance-details',
    'type': jinja2_component_type,
    'processor': jinja2_renderer,
    'extractor': analysis_provenance_details_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'analysis-provenance-details-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'analysis-provenance-details.html',
    'extra_args': {
        'defaults': {
            'source': tr('source not available'),
            'reference': tr('reference unspecified'),
            'aggregation_not_used': tr('not used')
        },
        'header': {
            'analysis_detail': tr('Analysis details')
        },
        'provenance_format': {
            'impact_function_header': tr('Impact Function'),
            'hazard_header': tr('Hazard'),
            'exposure_header': tr('Exposure'),
            'aggregation_header': tr('Aggregation'),
            'analysis_environment_header': tr('Analysis Environment')
        }
    }
}

analysis_provenance_details_simplified_component = {
    'key': 'analysis-provenance-details-simplified',
    'type': jinja2_component_type,
    'processor': jinja2_renderer,
    'extractor': analysis_provenance_details_simplified_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'analysis-provenance-details-simplified-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'analysis-provenance-details-simplified.html',
    'extra_args': {
        'defaults': {
            'source': tr('source not available'),
            'reference': tr('reference unspecified'),
            'aggregation_not_used': tr('not used')
        },
        'header': {
            'analysis_detail': tr('Analysis details')
        },
        'provenance_format': {
            'hazard_header': tr('Hazard source'),
            'hazard_format': u'{layer_name} - {source} - ',

            'exposure_header': tr('Exposure source'),
            'exposure_format': u'{layer_name} - {source} - ',

            'aggregation_header': tr('Aggregation source'),
            'aggregation_format': u'{layer_name} - {source} - ',

            'impact_function_header': tr('Impact Function'),
            'impact_function_format': u'{impact_function_name}',
        }
    }
}

population_chart_svg_component = {
    'key': 'population-chart',
    'type': jinja2_component_type,
    'processor': jinja2_renderer,
    'extractor': population_chart_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
    'output_path': 'population-chart.svg',
    'template': 'standard-template'
                '/jinja2/svg'
                '/donut-chart.svg',
    'tags': [svg_product_tag],
    'extra_args': {
        'chart_title': tr('Estimated total population'),
        'total_header': tr('Affected')
    }
}

population_chart_png_component = {
    # This component depends on population_chart_svg_component
    'key': 'population-chart-png',
    'type': qt_renderer_component_type,
    'processor': qt_svg_to_png_renderer,
    'extractor': population_chart_to_png_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
    'output_path': 'population-chart.png',
    'tags': [png_product_tag],
    'extra_args': {
        'width': 256,
        'height': 256
    }
}

population_chart_legend_component = {
    # This component depends on population_chart_png_component
    'key': 'population-chart-legend',
    'type': jinja2_component_type,
    'processor': jinja2_renderer,
    'extractor': population_chart_legend_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'population-chart-legend-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'population-chart-legend.html',
}

infographic_people_section_notes_component = {
    'key': 'infographic-people-section-notes',
    'type': jinja2_component_type,
    'processor': jinja2_renderer,
    'extractor': infographic_people_section_notes_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.String,
    'output_path': 'infographic-people-section-notes-output.html',
    'template': 'standard-template/'
                'jinja2/'
                'infographic-people-section-notes.html',
    'extra_args': {
        'extra_note': tr(
            'In this analysis, people are considered to be affected if they '
            'are exposed to the hazard, and considered to be displaced if '
            'they exposed to high or medium hazard.'),
        'hazard_displacement_rates_note_format': tr(
            '{displacement_rate:.0%} affected in {name} {classification_unit}')
    }
}

population_infographic_component = {
    # This component depends on population_chart_png_component,
    # population_chart_legend_component, and
    # infographic_people_section_notes_component
    'key': 'population-infographic',
    'type': qgis_composer_component_type,
    'processor': qgis_composer_renderer,
    'extractor': qgis_composer_infographic_extractor,
    'output_format': {
        'map': QgisComposerComponentsMetadata.OutputFormat.PDF,
        'template': QgisComposerComponentsMetadata.OutputFormat.QPT
    },
    'output_path': {
        'map': 'infographic.pdf',
        'template': 'infographic.qpt'
    },
    'orientation': 'landscape',
    'page_dpi': 300,
    'page_width': 297,
    'page_height': 210,
    'template': '../qgis-composer-templates/'
                'infographic.qpt',
    'tags': [
        final_product_tag,
        infographic_product_tag,
        template_product_tag,
        pdf_product_tag,
        qpt_product_tag
    ],
    'extra_args': {
        'components': {
            'population-chart-legend': population_chart_legend_component,
            'infographic-people-section-notes': (
                infographic_people_section_notes_component)
        }
    },
}

# Default impact report component for reusability
impact_report_component_metadata = [
    analysis_question_component,
    general_report_component,
    mmi_detail_component,
    analysis_detail_component,
    action_checklist_component,
    notes_assumptions_component,
    minimum_needs_component,
    aggregation_result_component,
    aggregation_postprocessors_component,
    analysis_provenance_details_simplified_component,
    analysis_provenance_details_component
]

# Standard HTML output for impact report
standard_impact_report_metadata_html = {
    'key': 'analysis-result-html',
    'name': 'analysis-result-html',
    'template_folder': resources_path('report-templates'),
    'components': impact_report_component_metadata + [
        {
            'key': 'impact-report',
            'type': jinja2_component_type,
            'processor': jinja2_renderer,
            'extractor': impact_table_extractor,
            'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
            'output_path': 'impact-report-output.html',
            'resources': [
                resources_path('css'),
                resources_path('js'),
                resources_path('img')],
            'template': 'standard-template/'
                        'jinja2/'
                        'impact-report-layout.html',
            'tags': [
                final_product_tag,
                table_product_tag,
                html_product_tag
            ],
            'extra_args': {
                'components_list': {
                    'analysis_question': analysis_question_component,
                    'general_report': general_report_component,
                    'mmi_detail': mmi_detail_component,
                    'analysis_detail': analysis_detail_component,
                    'action_checklist': action_checklist_component,
                    'notes_assumptions': notes_assumptions_component,
                    'minimum_needs': minimum_needs_component,
                    'aggregation_result': aggregation_result_component,
                    'aggregation_postprocessors': (
                        aggregation_postprocessors_component),
                    'analysis_provenance_details_simplified': (
                        analysis_provenance_details_simplified_component)
                }
            }
        },
        {
            'key': 'action-checklist-report',
            'type': jinja2_component_type,
            'processor': jinja2_renderer,
            'extractor': action_checklist_report_extractor,
            'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
            'output_path': 'action-checklist-output.html',
            'template': 'standard-template/'
                        'jinja2/'
                        'action-checklist-layout.html',
            'tags': [
                final_product_tag,
                table_product_tag,
                html_product_tag
            ],
            'extra_args': {
                'components_list': {
                    'analysis_question': analysis_question_component,
                    'action_checklist': action_checklist_component,
                    'analysis_provenance_details': (
                        analysis_provenance_details_simplified_component)
                }
            }
        },
        {
            'key': 'analysis-provenance-details-report',
            'type': jinja2_component_type,
            'processor': jinja2_renderer,
            'extractor': analysis_provenance_details_report_extractor,
            'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
            'output_path': 'analysis-provenance-details-report-output.html',
            'template': 'standard-template/'
                        'jinja2/'
                        'analysis-provenance-details-layout.html',
            'tags': [
                final_product_tag,
                table_product_tag,
                html_product_tag
            ],
            'extra_args': {
                'components_list': {
                    'analysis_question': analysis_question_component,
                    'analysis_provenance_details': (
                        analysis_provenance_details_component)
                }
            }
        }
    ]
}

# Standard PDF Output for impact report
standard_impact_report_metadata_pdf = {
    'key': 'analysis-result-pdf',
    'name': 'analysis-result-pdf',
    'template_folder': resources_path('report-templates'),
    'components': standard_impact_report_metadata_html['components'] + [
        # Impact Report PDF
        {
            'key': 'impact-report-pdf',
            'type': qgis_composer_component_type,
            'processor': qgis_composer_html_renderer,
            'extractor': impact_table_pdf_extractor,
            'output_format': QgisComposerComponentsMetadata.OutputFormat.PDF,
            'output_path': 'impact-report-output.pdf',
            'tags': [
                final_product_tag,
                table_product_tag,
                pdf_product_tag
            ]
        },
        # Action Checklist Report PDF
        {
            'key': 'action-checklist-pdf',
            'type': qgis_composer_component_type,
            'processor': qgis_composer_html_renderer,
            'extractor': action_checklist_report_pdf_extractor,
            'output_format': QgisComposerComponentsMetadata.OutputFormat.PDF,
            'output_path': 'action-checklist-output.pdf',
            'tags': [
                final_product_tag,
                table_product_tag,
                pdf_product_tag
            ]
        },
        # Analysis Provenance Details Report PDF
        {
            'key': 'analysis-provenance-details-report-pdf',
            'type': qgis_composer_component_type,
            'processor': qgis_composer_html_renderer,
            'extractor': analysis_provenance_details_pdf_extractor,
            'output_format': QgisComposerComponentsMetadata.OutputFormat.PDF,
            'output_path': 'analysis-provenance-details-report-output.pdf',
            'tags': [
                final_product_tag,
                table_product_tag,
                pdf_product_tag
            ]
        },
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

map_report = {
    'key': 'inasafe-map-report',
    'name': 'inasafe-map-report',
    'template_folder': resources_path('report-templates'),
    'components': [
        {
            'key': 'inasafe-map-report-portrait',
            'type': qgis_composer_component_type,
            'processor': qgis_composer_renderer,
            'extractor': qgis_composer_extractor,
            'output_format': {
                'map': QgisComposerComponentsMetadata.OutputFormat.PDF,
                'template': QgisComposerComponentsMetadata.OutputFormat.QPT
            },
            'template': '../qgis-composer-templates/'
                        'inasafe-map-report-portrait.qpt',
            'tags': [
                final_product_tag,
                map_product_tag,
                template_product_tag,
                pdf_product_tag,
                qpt_product_tag
            ],
            'output_path': {
                'map': 'inasafe-map-report-portrait.pdf',
                'template': 'inasafe-map-report-portrait.qpt'
            },
            'extra_args': map_report_extra_args
        },
        {
            'key': 'inasafe-map-report-landscape',
            'type': qgis_composer_component_type,
            'processor': qgis_composer_renderer,
            'extractor': qgis_composer_extractor,
            'output_format': {
                'map': QgisComposerComponentsMetadata.OutputFormat.PDF,
                'template': QgisComposerComponentsMetadata.OutputFormat.QPT
            },
            'template': '../qgis-composer-templates/'
                        'inasafe-map-report-landscape.qpt',
            'tags': [
                final_product_tag,
                map_product_tag,
                template_product_tag,
                pdf_product_tag,
                qpt_product_tag
            ],
            'output_path': {
                'map': 'inasafe-map-report-landscape.pdf',
                'template': 'inasafe-map-report-landscape.qpt'
            },
            'orientation': 'landscape',
            'page_dpi': 300,
            'page_width': 297,
            'page_height': 210,
            'extra_args': map_report_extra_args
        }
    ]
}

map_report_component_boilerplate = {
    'key': 'boilerplate',  # should be updated if this component is used
    'type': qgis_composer_component_type,
    'processor': qgis_composer_renderer,
    'extractor': qgis_composer_extractor,
    'output_format': {
        'map': QgisComposerComponentsMetadata.OutputFormat.PDF,
        'template': QgisComposerComponentsMetadata.OutputFormat.QPT
    },
    'template': 'boilerplate.qpt',  # should be updated
    'tags': [
        final_product_tag,
        map_product_tag,
        template_product_tag,
        pdf_product_tag,
        qpt_product_tag
    ],
    'output_path': {
        'map': 'boilerplate.pdf',  # should be updated
        'template': 'boilerplate.qpt'  # should be updated
    },
    # we set the orientation is landscape by default
    'orientation': 'landscape',
    'page_dpi': 300,
    'page_width': 297,
    'page_height': 210,
    'extra_args': map_report_extra_args
}

infographic_report = {
    'key': 'infographic_report',
    'name': 'infographic_report',
    'template_folder': resources_path('report-templates'),
    'components': [
        population_chart_svg_component,
        population_chart_png_component,
        population_chart_legend_component,
        infographic_people_section_notes_component,
        population_infographic_component
    ]
}
