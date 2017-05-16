# coding=utf-8
"""Contains definitions about Report components.

"""
from __future__ import absolute_import

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

from safe.common.utilities import safe_dir
from safe.definitions.fields import (
    affected_field,
    total_affected_field,
    total_not_affected_field,
    total_not_exposed_field,
    total_field,
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
    exposure_count_field)
from safe.definitions.styles import charcoal_black
from safe.report.extractors.action_notes import (
    action_checklist_extractor,
    notes_assumptions_extractor,
    action_notes_extractor,
    action_notes_pdf_extractor)
from safe.report.extractors.aggregate_postprocessors import \
    aggregation_postprocessors_extractor
from safe.report.extractors.aggregate_result import \
    aggregation_result_extractor
from safe.report.extractors.analysis_detail import analysis_detail_extractor
from safe.report.extractors.analysis_provenance_details import \
    analysis_provenance_details_extractor
from safe.report.extractors.analysis_question import \
    analysis_question_extractor
from safe.report.extractors.general_report import general_report_extractor
from safe.report.extractors.composer import qgis_composer_extractor
from safe.report.extractors.impact_table import (
    impact_table_extractor,
    impact_table_pdf_extractor)
from safe.report.extractors.infographics import (
    population_infographic_extractor,
    infographic_layout_extractor,
    infographic_pdf_extractor)
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
from safe.utilities.resources import resource_url, resources_path

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
        ]
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
        'notes': tr(
            'Columns and rows containing only 0 or "No data" values are '
            'excluded from the tables.')
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
            '{name} - {displacement_rate:.2%}')
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
        'notes': tr(
            'Columns and rows containing only 0 or "No data" values are '
            'excluded from the tables.'),
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
            'age': {
                'header': tr('Detailed Age Report')
            },
            'gender': {
                'header': tr('Detailed Gender Report')
            },
            'vulnerability': {
                'header': tr('Detailed Vulnerability Report')
            },
            'minimum_needs': {
                'header': tr('Detailed Minimum Needs Report')
            }
        },
        'defaults': {
            'aggregation_header': tr('Aggregation area'),
            'total_population_header': tr('Total Displaced Population'),
            'total_header': tr('Total'),
            'notes': tr(
                'Columns and rows containing only 0 or "No data" values are '
                'excluded from the tables.'),
            'zero_displaced_message': tr(
                'Analysis produced 0 displaced count. '
                'No calculations produced.'),
            'no_gender_rate_message': tr(
                'Gender ratio not found. '
                'No calculations produced.'),
            'no_age_rate_message': tr(
                'Age ratio not found. '
                'No calculations produced.'),
            'no_vulnerability_rate_message': tr(
                'Vulnerability ratio not exists. '
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
        'total_header': tr('Population')
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

population_infographic_component = {
    # This component depends on population_chart_png_component
    'key': 'population-infographic',
    'type': jinja2_component_type,
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
                'items': [
                    {
                        'sub_header': {
                            total_affected_field['key']: tr('Affected'),
                            population_count_field['key']: tr('Population'),
                            exposure_count_field['key'] % (
                                exposure_population['key'], ): tr(
                                'Population')
                        }
                    },
                    {
                        'sub_header': tr('Displaced<sup>*</sup>'),
                        'sub_header_note_format': tr(
                            '<sup>*</sup> Displacement rate: '
                            '{rate_description}'),
                        'rate_description_format': tr(
                            '{displacement_rate:.2%} of affected {name}')
                    },
                ]
            },
            'vulnerability': {
                'header': tr('Vulnerability'),
                'sub_header_format': tr('from {number_displaced} displaced'),
                'items': [
                    {
                        'sub_group_header': tr('Gender group'),
                        # used to specify group column width in css
                        'bootstrap_column': 'col-xs-3',
                        # used to specify each element column in css
                        'element_column': 'col-xs-12',
                        'fields': [
                            female_displaced_count_field,
                        ],
                        'headers': [
                            tr('Female'),
                        ]
                    },
                    {
                        'sub_group_header': tr('Age group'),
                        # used to specify group column width in css
                        'bootstrap_column': 'col-xs-9',
                        # used to specify each element column in css
                        'element_column': 'col-xs-4',
                        'fields': [
                            youth_displaced_count_field,
                            adult_displaced_count_field,
                            elderly_displaced_count_field
                        ],
                        'headers': [
                            tr('Youth'),
                            tr('Adult'),
                            tr('Elderly')
                        ]
                    }
                ]
            },
            'minimum_needs': {
                'header': tr('Minimum needs'),
                'empty_unit_string': tr('units')
            }
        },
        # definitions for icons
        'icons': {
            'total_affected_field': resource_url(resources_path(
                'img/definitions/people.svg')),
            'displaced_field': resource_url(resources_path(
                'img/definitions/displaced.svg')),
            'female_displaced_count_field': resource_url(resources_path(
                'img/definitions/female.svg')),
            'youth_displaced_count_field': resource_url(resources_path(
                'img/definitions/youth.svg')),
            'adult_displaced_count_field': resource_url(resources_path(
                'img/definitions/adult.svg')),
            'elderly_displaced_count_field': resource_url(resources_path(
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
    analysis_question_component,
    general_report_component,
    mmi_detail_component,
    analysis_detail_component,
    action_checklist_component,
    notes_assumptions_component,
    minimum_needs_component,
    aggregation_result_component,
    aggregation_postprocessors_component,
    analysis_provenance_details_component
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
            'type': jinja2_component_type,
            'processor': jinja2_renderer,
            'extractor': infographic_layout_extractor,
            'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
            'output_path': 'infographic.html',
            'extra_args': {
                'infographics': [population_infographic_component['key']],
                'footer_format': tr(
                    'InaSAFE {version} | {analysis_date} | {analysis_time} | '
                    'info@inasafe.org | Icons source: OCHA | '
                    'Indonesian Government-'
                    'Australian Government-World Bank-GFDRR')
            },
            'template': 'standard-template/'
                        'jinja2/'
                        'infographic-layout.html',
            'tags': [
                final_product_tag,
                infographic_product_tag,
                html_product_tag
            ]
        },
        {
            'key': 'impact-report',
            'type': jinja2_component_type,
            'processor': jinja2_renderer,
            'extractor': impact_table_extractor,
            'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
            'output_path': 'impact-report-output.html',
            'resources': [
                safe_dir(sub_dir='../resources/css'),
                safe_dir(sub_dir='../resources/js'),
                safe_dir(sub_dir='../resources/img')],
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
                    'analysis_provenance_details': (
                        analysis_provenance_details_component)
                }
            }
        },
        {
            'key': 'action-checklist-report',
            'type': jinja2_component_type,
            'processor': jinja2_renderer,
            'extractor': action_notes_extractor,
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
                    'action_checklist': action_checklist_component,
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
    'template_folder': safe_dir(sub_dir='../resources/report-templates/'),
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
        # Action Checklist and Notes Report PDF
        {
            'key': 'action-checklist-pdf',
            'type': qgis_composer_component_type,
            'processor': qgis_composer_html_renderer,
            'extractor': action_notes_pdf_extractor,
            'output_format': QgisComposerComponentsMetadata.OutputFormat.PDF,
            'output_path': 'action-checklist-output.pdf',
            'tags': [
                final_product_tag,
                table_product_tag,
                pdf_product_tag
            ]
        },
        # Infographic Layout PDF
        {
            'key': 'infographic-pdf',
            'type': qgis_composer_component_type,
            'processor': qgis_composer_html_renderer,
            'extractor': infographic_pdf_extractor,
            'output_format': {
                'doc': QgisComposerComponentsMetadata.OutputFormat.PDF,
                'template': QgisComposerComponentsMetadata.OutputFormat.QPT
            },
            'output_path': {
                'doc': 'infographic.pdf',
                'template': 'infographic.qpt'
            },
            'page_dpi': 300,
            'page_width': 297,
            'page_height': 210,
            'tags': [
                # untag this from final product until donut png were
                # rendered correctly by qgis
                final_product_tag,
                infographic_product_tag,
                pdf_product_tag,
                qpt_product_tag
            ]
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
            'type': qgis_composer_component_type,
            'processor': qgis_composer_renderer,
            'extractor': qgis_composer_extractor,
            'output_format': {
                'map': QgisComposerComponentsMetadata.OutputFormat.PDF,
                'template': QgisComposerComponentsMetadata.OutputFormat.QPT
            },
            'template': '../qgis-composer-templates/'
                        'a4-portrait-blue.qpt',
            'tags': [
                final_product_tag,
                map_product_tag,
                template_product_tag,
                pdf_product_tag,
                qpt_product_tag
            ],
            'output_path': {
                'map': 'a4-portrait-blue.pdf',
                'template': 'a4-portrait-blue.qpt'
            },
            'extra_args': map_report_extra_args
        },
        {
            'key': 'a4-landscape-blue',
            'type': qgis_composer_component_type,
            'processor': qgis_composer_renderer,
            'extractor': qgis_composer_extractor,
            'output_format': {
                'map': QgisComposerComponentsMetadata.OutputFormat.PDF,
                'template': QgisComposerComponentsMetadata.OutputFormat.QPT
            },
            'template': '../qgis-composer-templates/'
                        'a4-landscape-blue.qpt',
            'tags': [
                final_product_tag,
                map_product_tag,
                template_product_tag,
                pdf_product_tag,
                qpt_product_tag
            ],
            'output_path': {
                'map': 'a4-landscape-blue.pdf',
                'template': 'a4-landscape-blue.qpt'
            },
            'orientation': 'landscape',
            'page_dpi': 300,
            'page_width': 297,
            'page_height': 210,
            'extra_args': map_report_extra_args
        }
    ]
}
