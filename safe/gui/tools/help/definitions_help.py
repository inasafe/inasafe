# coding=utf-8
"""Help text for the dock widget."""


import copy
import logging
import re
from os.path import exists

from qgis.PyQt import QtCore

import safe.definitions as definitions
import safe.processors
from safe import messaging as m
from safe.common.version import get_version
from safe.definitions.earthquake import current_earthquake_model_name
from safe.definitions.exposure import exposure_all
from safe.definitions.field_groups import (
    population_field_groups, aggregation_field_groups)
from safe.definitions.hazard_classifications import hazard_classification_type
from safe.definitions.hazard_exposure_specifications import (
    specific_notes, specific_actions)
from safe.definitions.reports.infographic import html_frame_elements
from safe.definitions.reports.report_descriptions import all_reports
from safe.gui.tools.help.batch_help import content as batch_help
from safe.gui.tools.help.developer_help import content as developer_help
from safe.gui.tools.help.dock_help import content as dock_help
from safe.gui.tools.help.extent_selector_help import content as extent_help
from safe.gui.tools.help.field_mapping_help import content as \
    field_mapping_tool_help
from safe.gui.tools.help.impact_report_help import content as report_help
from safe.gui.tools.help.multi_buffer_help import content as multi_buffer_help
from safe.gui.tools.help.needs_calculator_help import content as needs_help
from safe.gui.tools.help.needs_manager_help import content as \
    needs_manager_help
from safe.gui.tools.help.options_help import content as options_help
from safe.gui.tools.help.osm_downloader_help import content as osm_help
from safe.gui.tools.help.peta_bencana_help import content as petabencana_help
from safe.gui.tools.help.shakemap_converter_help \
    import content as shakemap_help
from safe.messaging import styles
from safe.processors import (
    post_processor_input_types,
    post_processor_input_values)
from safe.utilities.expressions import qgis_expressions
from safe.utilities.i18n import tr
from safe.utilities.resources import resource_url, resources_path
from safe.utilities.rounding import html_scientific_notation_rate

LOGGER = logging.getLogger('InaSAFE')
# For chapter sections
# Items marked as numbered below will show section numbering in HTML render
TITLE_STYLE = styles.TITLE_LEVEL_1_STYLE  # h1 Not numbered
SECTION_STYLE = styles.SECTION_LEVEL_2_STYLE  # h2 numbered
SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE  # h3 numbered
BLUE_CHAPTER_STYLE = styles.BLUE_LEVEL_4_STYLE  # h4 numbered
RED_CHAPTER_STYLE = styles.RED_LEVEL_4_STYLE  # h4 numbered
DETAILS_STYLE = styles.ORANGE_LEVEL_5_STYLE  # h5 numbered
DETAILS_SUBGROUP_STYLE = styles.GREY_LEVEL_6_STYLE  # h5 numbered
# For images
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE
MEDIUM_ICON_STYLE = styles.MEDIUM_ICON_STYLE
HEADING_LOOKUPS = {
    1: SECTION_STYLE,
    2: SUBSECTION_STYLE,
    3: BLUE_CHAPTER_STYLE,
    4: DETAILS_STYLE,
    5: DETAILS_SUBGROUP_STYLE,
}
HEADING_COUNTS = {
    1: 1,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
}

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def definitions_help():
    """Help message for Definitions.

    .. versionadded:: 4.0.0

    :returns: A message object containing helpful information.
    :rtype: messaging.message.Message
    """
    message = m.Message()
    message.add(m.Brand())
    message.add(heading())
    message.add(content())
    return message


def heading():
    """Helper method that returns just the header.

    This method was added so that the text could be reused in the
    other contexts.

    .. versionadded:: 4.0.0

    :returns: A heading object.
    :rtype: safe.messaging.heading.Heading
    """
    message = m.Heading(
        '{} {}'.format(tr('InaSAFE help'), get_version()), **TITLE_STYLE)
    return message


def content():
    """Helper method that returns just the content.

    This method was added so that the text could be reused in the
    dock_help module.

    .. versionadded:: 4.0.0

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    # We will store a contents section at the top for easy navigation
    table_of_contents = m.Message()
    # and this will be the main message that we create
    message = m.Message()

    _create_section_header(
        message,
        table_of_contents,
        'overview',
        tr('Overview'),
        heading_level=1)
    ##
    # Credits and disclaimers ...
    ##
    _create_section_header(
        message,
        table_of_contents,
        'disclaimer',
        tr('Disclaimer'),
        heading_level=2)
    message.add(m.Paragraph(definitions.messages.disclaimer()))

    _create_section_header(
        message,
        table_of_contents,
        'limitations',
        tr('Limitations and License'),
        heading_level=2)
    bullets = m.BulletedList()
    for item in definitions.limitations():
        bullets.add(item)
    message.add(bullets)

    ##
    # Basic concepts ...
    ##
    ##
    # Help dialog contents ...
    ##
    _create_section_header(
        message,
        table_of_contents,
        'glossary',
        tr('Glossary of terms'),
        heading_level=1)

    last_group = None
    table = None
    for key, value in list(definitions.concepts.items()):
        current_group = value['group']
        if current_group != last_group:
            if last_group is not None:
                message.add(table)
            _create_section_header(
                message,
                table_of_contents,
                current_group.replace(' ', '-'),
                current_group,
                heading_level=2)
            table = _start_glossary_table(current_group)
            last_group = current_group
        row = m.Row()
        term = value['key'].replace('_', ' ').title()
        description = m.Message(value['description'])
        for citation in value['citations']:
            if citation['text'] in [None, '']:
                continue
            if citation['link'] in [None, '']:
                description.add(m.Paragraph(citation['text']))
            else:
                description.add(m.Paragraph(
                    m.Link(citation['link'], citation['text'])))
        row.add(m.Cell(term))
        row.add(m.Cell(description))
        url = _definition_icon_url(value)
        if url:
            row.add(m.Cell(m.Image(url, **MEDIUM_ICON_STYLE)))
        else:
            row.add(m.Cell(''))
        table.add(row)
    # ensure the last group's table is added
    message.add(table)

    ##
    # Help dialog contents ...
    ##
    _create_section_header(
        message,
        table_of_contents,
        'core-functionality',
        tr('Core functionality and tools'),
        heading_level=1)

    _create_section_header(
        message,
        table_of_contents,
        'dock',
        tr('The InaSAFE Dock'),
        heading_level=2)
    message.add(dock_help())

    _create_section_header(
        message,
        table_of_contents,
        'reports',
        tr('InaSAFE Reports'),
        heading_level=2)
    message.add(report_help())

    _create_section_header(
        message,
        table_of_contents,
        'extents',
        tr('Managing analysis extents with the extents selector'),
        heading_level=2)
    message.add(extent_help())

    _create_section_header(
        message,
        table_of_contents,
        'options',
        tr('InaSAFE Options'),
        heading_level=2)
    message.add(options_help())

    _create_section_header(
        message,
        table_of_contents,
        'batch-runner',
        tr('The Batch Runner'),
        heading_level=2)
    message.add(batch_help())

    _create_section_header(
        message,
        table_of_contents,
        'osm-downloader',
        tr('The OpenStreetmap Downloader'),
        heading_level=2)
    message.add(osm_help())

    _create_section_header(
        message,
        table_of_contents,
        'petabencana-downloader',
        tr('The PetaBencana Downloader'),
        heading_level=2)
    message.add(petabencana_help())

    _create_section_header(
        message,
        table_of_contents,
        'shakemap-converter',
        tr('The Shakemap Converter'),
        heading_level=2)
    message.add(shakemap_help())

    _create_section_header(
        message,
        table_of_contents,
        'multi-buffer-tool',
        tr('The Multi Buffer Tool'),
        heading_level=2)
    message.add(multi_buffer_help())

    # Field mapping tool has a few added bits to enumerate the groups
    _create_section_header(
        message,
        table_of_contents,
        'field-mapping-tool',
        tr('The Field Mapping Tool'),
        heading_level=2)
    message.add(field_mapping_tool_help())

    _create_section_header(
        message,
        table_of_contents,
        'exposure-groups',
        tr('Exposure Groups'),
        heading_level=3)
    message.add(m.Paragraph(
        'The following demographic groups apply only to vector population '
        'exposure layers:'
    ))
    for group in population_field_groups:
        definition_to_message(
            group, message, table_of_contents, heading_level=4)

    _create_section_header(
        message,
        table_of_contents,
        'aggregation-groups',
        tr('Aggregation Groups'),
        heading_level=3)
    message.add(m.Paragraph(
        'The following demographic groups apply only to aggregation layers:'
    ))
    for group in aggregation_field_groups:
        definition_to_message(
            group, message, table_of_contents, heading_level=4)

    # End of field mapping tool help

    # Keep this last in the tool section please as it has subsections
    # and so uses the top level section style
    _create_section_header(
        message,
        table_of_contents,
        'minimum-needs',
        tr('Minimum Needs'),
        heading_level=2)
    _create_section_header(
        message,
        table_of_contents,
        'minimum-needs-tool',
        tr('The minimum needs tool'),
        heading_level=3)
    message.add(needs_help())
    _create_section_header(
        message,
        table_of_contents,
        'minimum-manager',
        tr('The minimum needs manager'),
        heading_level=3)
    message.add(needs_manager_help())

    ##
    #  Analysis workflow
    ##

    _create_section_header(
        message,
        table_of_contents,
        'analysis-steps',
        tr('Analysis steps'),
        heading_level=1)
    _create_section_header(
        message,
        table_of_contents,
        'analysis-internal-process',
        tr('Analysis internal process'),
        heading_level=2)
    analysis = definitions.concepts['analysis']
    message.add(analysis['description'])
    url = _definition_screenshot_url(analysis)
    if url:
        message.add(m.Paragraph(m.Image(url), style_class='text-center'))

    _create_section_header(
        message,
        table_of_contents,
        'analysis-progress-reporting',
        tr('Progress reporting steps'),
        heading_level=2)
    steps = list(definitions.analysis_steps.values())
    for step in steps:
        definition_to_message(
            step, message, table_of_contents, heading_level=3)

    ##
    #  Hazard definitions
    ##

    _create_section_header(
        message,
        table_of_contents,
        'hazards',
        tr('Hazard Concepts'),
        heading_level=1)

    hazard_category = definitions.hazard_category
    definition_to_message(
        hazard_category,
        message,
        table_of_contents,
        heading_level=2)

    hazards = definitions.hazards
    definition_to_message(
        hazards,
        message,
        table_of_contents,
        heading_level=2)

    ##
    #  Exposure definitions
    ##

    _create_section_header(
        message,
        table_of_contents,
        'exposures',
        tr('Exposure Concepts'),
        heading_level=1)
    exposures = definitions.exposures

    definition_to_message(
        exposures,
        message,
        table_of_contents,
        heading_level=2)

    ##
    #  Defaults
    ##

    _create_section_header(
        message,
        table_of_contents,
        'defaults',
        tr('InaSAFE Defaults'),
        heading_level=1)
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('Name'), header=True))
    row.add(m.Cell(tr('Default value'), header=True))
    row.add(m.Cell(tr('Default min'), header=True))
    row.add(m.Cell(tr('Default max'), header=True))
    row.add(m.Cell(tr('Description'), header=True))
    table.add(row)
    defaults = [
        definitions.youth_ratio_default_value,
        definitions.adult_ratio_default_value,
        definitions.elderly_ratio_default_value,
        definitions.female_ratio_default_value,
        definitions.feature_rate_default_value
    ]
    for default in defaults:
        row = m.Row()
        row.add(m.Cell(default['name']))
        row.add(m.Cell(default['default_value']))
        row.add(m.Cell(default['min_value']))
        row.add(m.Cell(default['max_value']))
        row.add(m.Cell(default['description']))
        table.add(row)
    message.add(table)

    ##
    #  All Fields
    ##

    _create_section_header(
        message,
        table_of_contents,
        'all-fields',
        tr('Fields'),
        heading_level=1)
    _create_section_header(
        message,
        table_of_contents,
        'input-fields',
        tr('Input dataset fields'),
        heading_level=2)
    _create_fields_section(
        message,
        table_of_contents,
        tr('Exposure fields'),
        definitions.exposure_fields)
    _create_fields_section(
        message,
        table_of_contents,
        tr('Hazard fields'),
        definitions.hazard_fields)
    _create_fields_section(
        message,
        table_of_contents,
        tr('Aggregation fields'),
        definitions.aggregation_fields)
    _create_section_header(
        message,
        table_of_contents,
        'output-fields',
        tr('Output dataset fields'),
        heading_level=2)
    _create_fields_section(
        message,
        table_of_contents,
        tr('Impact fields'),
        definitions.impact_fields)
    _create_fields_section(
        message,
        table_of_contents,
        tr('Aggregate hazard fields'),
        definitions.aggregate_hazard_fields)
    _create_fields_section(
        message,
        table_of_contents,
        tr('Aggregation summary fields'),
        definitions.aggregation_summary_fields)
    _create_fields_section(
        message,
        table_of_contents,
        tr('Exposure summary table fields'),
        definitions.exposure_summary_table_fields)
    _create_fields_section(
        message,
        table_of_contents,
        tr('Analysis fields'),
        definitions.analysis_fields)

    ##
    #  Geometries
    ##

    _create_section_header(
        message,
        table_of_contents,
        'geometries',
        tr('Layer Geometry Types'),
        heading_level=1)
    _create_section_header(
        message,
        table_of_contents,
        'vector-geometries',
        tr('Vector'),
        heading_level=2)
    definition_to_message(
        definitions.layer_geometry_point,
        message,
        table_of_contents,
        heading_level=3)
    definition_to_message(
        definitions.layer_geometry_line,
        message,
        table_of_contents,
        heading_level=3)
    definition_to_message(
        definitions.layer_geometry_polygon,
        message,
        table_of_contents,
        heading_level=3)
    _create_section_header(
        message,
        table_of_contents,
        'raster-geometries',
        tr('Raster'),
        heading_level=2)
    definition_to_message(
        definitions.layer_geometry_raster,
        message,
        table_of_contents,
        heading_level=3)

    ##
    #  Layer Modes
    ##

    _create_section_header(
        message,
        table_of_contents,
        'layer-modes',
        tr('Layer Modes'),
        heading_level=1)
    definition_to_message(
        definitions.layer_mode,
        message,
        table_of_contents,
        heading_level=2)

    ##
    #  Layer Purposes
    ##

    _create_section_header(
        message,
        table_of_contents,
        'layer-purposes',
        tr('Layer Purposes'),
        heading_level=1)
    definition_to_message(
        definitions.layer_purpose_hazard,
        message,
        table_of_contents,
        heading_level=2)
    definition_to_message(
        definitions.layer_purpose_exposure,
        message,
        table_of_contents,
        heading_level=2)
    definition_to_message(
        definitions.layer_purpose_aggregation,
        message,
        table_of_contents,
        heading_level=2)
    definition_to_message(
        definitions.layer_purpose_exposure_summary,
        message,
        table_of_contents,
        heading_level=2)
    definition_to_message(
        definitions.layer_purpose_aggregate_hazard_impacted,
        message,
        table_of_contents,
        heading_level=2)
    definition_to_message(
        definitions.layer_purpose_aggregation_summary,
        message,
        table_of_contents,
        heading_level=2)
    definition_to_message(
        definitions.layer_purpose_exposure_summary_table,
        message,
        table_of_contents,
        heading_level=2)
    definition_to_message(
        definitions.layer_purpose_profiling,
        message,
        table_of_contents,
        heading_level=2)

    ##
    # All units
    ##

    _create_section_header(
        message,
        table_of_contents,
        'all-units',
        tr('All Units'),
        heading_level=1)
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('Name'), header=True))
    row.add(m.Cell(tr('Plural'), header=True))
    row.add(m.Cell(tr('Abbreviation'), header=True))
    row.add(m.Cell(tr('Details'), header=True))
    table.add(row)
    for unit in definitions.units_all:
        row = m.Row()
        row.add(m.Cell(unit['name']))
        row.add(m.Cell(unit['plural_name']))
        row.add(m.Cell(unit['abbreviation']))
        row.add(m.Cell(unit['description']))
        table.add(row)
    message.add(table)

    ##
    #  Post processors
    ##

    _create_section_header(
        message,
        table_of_contents,
        'post-processors',
        tr('Post Processors'),
        heading_level=1)
    _create_section_header(
        message,
        table_of_contents,
        'post-processor-input-types',
        tr('Post Processor Input Types'),
        heading_level=2)
    table = _create_post_processor_subtable(
        post_processor_input_types
    )
    message.add(table)

    _create_section_header(
        message,
        table_of_contents,
        'post-processor-input-values',
        tr('Post Processor Input Values'),
        heading_level=2)
    table = _create_post_processor_subtable(
        post_processor_input_values
    )
    message.add(table)

    _create_section_header(
        message,
        table_of_contents,
        'post-processor-process-values',
        tr('Post Processor Process Types'),
        heading_level=2)
    table = _create_post_processor_subtable(
        safe.processors.post_processor_process_types
    )
    message.add(table)

    _create_section_header(
        message,
        table_of_contents,
        'post-processors',
        tr('Post Processors'),
        heading_level=2)
    post_processors = safe.processors.post_processors
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('Name'), header=True))
    row.add(m.Cell(tr('Input Fields'), header=True))
    row.add(m.Cell(tr('Output Fields'), header=True))
    table.add(row)
    for post_processor in post_processors:
        row = m.Row()
        row.add(m.Cell(post_processor['name']))
        # Input fields
        bullets = m.BulletedList()
        for key, value in sorted(post_processor['input'].items()):
            bullets.add(key)
        row.add(m.Cell(bullets))
        # Output fields
        bullets = m.BulletedList()
        for key, value in sorted(post_processor['output'].items()):
            name = value['value']['name']
            formula_type = value['type']['key']
            if formula_type == 'formula':
                formula = value['formula']
            else:
                # We use python introspection because the processor
                # uses a python function for calculations
                formula = value['function'].__name__
                formula += ' ('
                formula += value['function'].__doc__
                formula += ')'
            bullets.add('%s  %s. : %s' % (
                name, formula_type, formula))

        row.add(m.Cell(bullets))
        table.add(row)
        # Add the descriptions
        row = m.Row()
        row.add(m.Cell(''))
        row.add(m.Cell(post_processor['description'], span=2))
        table.add(row)
    message.add(table)

    ##
    # Reporting
    ##
    _create_section_header(
        message,
        table_of_contents,
        'reporting',
        tr('Reporting'),
        heading_level=1)

    paragraph = m.Paragraph(
        m.ImportantText(tr('Note: ')),
        m.Text(tr(
            'This section of the help documentation is intended for advanced '
            'users who want to modify reports which are produced by InaSAFE.'
        )))
    message.add(paragraph)
    _create_section_header(
        message,
        table_of_contents,
        'reporting-overview',
        tr('Overview'),
        heading_level=2)
    message.add(m.Paragraph(tr(
        'Whenever InaSAFE completes an analysis, it will automatically '
        'generate a number of reports. Some of these reports are based on '
        'templates that are shipped with InaSAFE, and can be customised or '
        'over-ridden by creating your own templates. The following '
        'reports are produced in InaSAFE:'
    )))
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('Name'), header=True))
    row.add(m.Cell(tr('Customisable?'), header=True))
    row.add(m.Cell(tr('Example'), header=True))
    row.add(m.Cell(tr('Description'), header=True))
    table.add(row)

    for report in all_reports:
        row = m.Row()
        row.add(m.Cell(report['name']))
        if report['customisable']:
            row.add(m.Cell(tr('Yes')))
        else:
            row.add(m.Cell(tr('No')))
        png_image_path = resources_path(
            'img', 'screenshots', report['thumbnail'])
        row.add(m.Image(png_image_path, style_class='text-center'))
        row.add(m.Cell(report['description']))
        table.add(row)

    message.add(table)

    message.add(m.Paragraph(tr(
        'In the sections that follow, we provide more technical information '
        'about the custom QGIS Expressions and special template elements '
        'that can be used to customise your templates.'
    )))

    _create_section_header(
        message,
        table_of_contents,
        'reporting-expressions',
        tr('QGIS Expressions'),
        heading_level=2)
    message.add(m.Paragraph(tr(
        'InaSAFE adds a number of expressions that can be used to '
        'conveniently obtain provenance data to the active analysis results. '
        'The expressions can also be used elsewhere in QGIS as needed.'
        '.'
    )))

    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('Name'), header=True))
    row.add(m.Cell(tr('Description'), header=True))
    table.add(row)
    for expression_name, expression in sorted(qgis_expressions().items()):
        row = m.Row()
        row.add(m.Cell(expression_name))
        help = expression.helptext()
        # This pattern comes from python/qgis/core/__init__.py ≈ L79
        pattern = r'<h3>(.*) function</h3><br>'
        help = re.sub(pattern, '', help)
        help = re.sub(r'\n', '<br>', help)
        row.add(m.Cell(help))
        table.add(row)
    message.add(table)

    _create_section_header(
        message,
        table_of_contents,
        'reporting-composer-elements',
        tr('Composer Elements'),
        heading_level=2)
    message.add(m.Paragraph(tr(
        'InaSAFE looks for elements with specific id\'s on the composer '
        'page and replaces them with InaSAFE specific content.'
    )))
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('ID'), header=True))
    row.add(m.Cell(tr('Description'), header=True))
    table.add(row)
    for item in html_frame_elements:
        row = m.Row()
        row.add(m.Cell(item['id']))
        row.add(m.Cell(item['description']))
        table.add(row)
    message.add(table)

    ##
    # Developer documentation
    ##
    _create_section_header(
        message,
        table_of_contents,
        'developer-guide',
        tr('Developer Guide'),
        heading_level=1)
    message.add(developer_help())

    # Finally we add the table of contents at the top
    full_message = m.Message()
    # Contents is not a link so reset style
    style = SECTION_STYLE
    style['element_id'] = ''
    header = m.Heading(tr('Contents'), **style)
    full_message.add(header)
    full_message.add(table_of_contents)
    full_message.add(message)
    return full_message


def _start_glossary_table(group):
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    # first col for icons if present
    row.add(m.Cell(tr('Term'), header=True))
    row.add(m.Cell(tr('Description'), header=True))
    row.add(m.Cell(tr(''), header=True))
    table.add(row)
    return table


def _create_section_header(
        message,
        table_of_contents,
        element_id,
        text,
        heading_level=1):
    # Warning a side effect here is that the SECTION_STYLE is updated
    # when setting style as we modify the id so we have to make a deep copy
    style = copy.deepcopy(HEADING_LOOKUPS[heading_level])
    style['element_id'] = element_id

    HEADING_COUNTS[heading_level] += 1
    # Reset the heading counts for headings below this level
    # Also calculate the index of the TOC entry
    index_number = ''
    for key in list(HEADING_COUNTS.keys()):
        if key > heading_level:
            HEADING_COUNTS[key] = 0
        else:
            index_number += str(HEADING_COUNTS[key]) + '.'

    header = m.Heading(text, **style)
    link = m.Link('#%s' % element_id, index_number + ' ' + text)
    # See bootstrap docs for ml-1 explanation
    # https://v4-alpha.getbootstrap.com/utilities/spacing/#examples
    paragraph = m.Paragraph(
        link,
        style_class='ml-%i' % heading_level)
    table_of_contents.add(paragraph)
    message.add(header)


def _create_post_processor_subtable(item_list):
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('Name'), header=True))
    row.add(m.Cell(tr('Description'), header=True))
    table.add(row)
    for item in item_list:
        row = m.Row()
        row.add(m.Cell(item['key']))
        row.add(m.Cell(item['description']))
        table.add(row)
    return table


def _create_fields_section(message, table_of_contents, title, fields):
    _create_section_header(
        message,
        table_of_contents,
        title.replace(' ', '-'),
        title,
        heading_level=3)
    table = _create_fields_table()
    for field in fields:
        _add_field_to_table(field, table)
    message.add(table)


def definition_to_message(
        definition, message=None, table_of_contents=None, heading_level=None):
    """Helper function to render a definition to a message.

    :param definition: A definition dictionary (see definitions package).
    :type definition: dict

    :param message: The message that the definition should be appended to.
    :type message: parameters.message.Message

    :param table_of_contents: Table of contents that the headings should be
        included in.
    :type message: parameters.message.Message

    :param heading_level: Optional style to apply to the definition
        heading. See HEADING_LOOKUPS
    :type heading_level: int

    :returns: Message
    :rtype: str
    """

    if message is None:
        message = m.Message()

    if table_of_contents is None:
        table_of_contents = m.Message()

    if heading_level:
        _create_section_header(
            message,
            table_of_contents,
            definition['name'].replace(' ', '-'),
            definition['name'],
            heading_level=heading_level)
    else:
        header = m.Paragraph(m.ImportantText(definition['name']))
        message.add(header)

    # If the definition has an icon, we put the icon and description side by
    # side in a table otherwise just show the description as a paragraph
    url = _definition_icon_url(definition)
    if url is None:
        message.add(m.Paragraph(definition['description']))
        if 'citations' in definition:
            _citations_to_message(message, definition)
    else:
        LOGGER.info('Creating mini table for definition description: ' + url)
        table = m.Table(style_class='table table-condensed')
        row = m.Row()
        row.add(m.Cell(m.Image(url, **MEDIUM_ICON_STYLE)))
        row.add(m.Cell(definition['description']))
        table.add(row)
        for citation in definition['citations']:
            if citation['text'] in [None, '']:
                continue
            row = m.Row()
            row.add(m.Cell(''))
            if citation['link'] in [None, '']:
                row.add(m.Cell(citation['text']))
            else:
                row.add(m.Cell(m.Link(citation['link'], citation['text'])))
            table.add(row)
        message.add(table)

    url = _definition_screenshot_url(definition)
    if url:
        message.add(m.Paragraph(m.Image(url), style_class='text-center'))

    # types contains e.g. hazard_all
    if 'types' in definition:
        for sub_definition in definition['types']:
            definition_to_message(
                sub_definition,
                message,
                table_of_contents,
                heading_level=3)

    #
    # Notes section if available
    #

    if 'notes' in definition:
        # Start a notes details group too since we have an exposure
        message.add(m.Heading(
            tr('Notes:'), **DETAILS_STYLE))
        message.add(m.Heading(
            tr('General notes:'), **DETAILS_SUBGROUP_STYLE))
        bullets = m.BulletedList()
        for note in definition['notes']:
            if isinstance(note, dict):
                bullets = _add_dict_to_bullets(bullets, note)
            elif note:
                bullets.add(m.Text(note))
        message.add(bullets)
        if 'citations' in definition:
            _citations_to_message(message, definition)

    # This only for EQ
    if 'earthquake_fatality_models' in definition:
        current_function = current_earthquake_model_name()
        paragraph = m.Paragraph(tr(
            'The following earthquake fatality models are available in '
            'InaSAFE. Note that you need to set one of these as the '
            'active model in InaSAFE Options. The currently active model '
            'is: '),
            m.ImportantText(current_function)
        )
        message.add(paragraph)

        models_definition = definition['earthquake_fatality_models']
        for model in models_definition:
            message.add(m.Heading(model['name'], **DETAILS_SUBGROUP_STYLE))
            if 'description' in model:
                paragraph = m.Paragraph(model['description'])
                message.add(paragraph)
            for note in model['notes']:
                paragraph = m.Paragraph(note)
                message.add(paragraph)
            _citations_to_message(message, model)

    for exposure in exposure_all:
        extra_exposure_notes = specific_notes(definition, exposure)
        if extra_exposure_notes:
            title = tr('Notes for exposure : {exposure_name}').format(
                exposure_name=exposure['name'])
            message.add(m.Heading(title, **DETAILS_SUBGROUP_STYLE))
            bullets = m.BulletedList()
            for note in extra_exposure_notes:
                if isinstance(note, dict):
                    bullets = _add_dict_to_bullets(bullets, note)
                elif note:
                    bullets.add(m.Text(note))
            message.add(bullets)

    if 'continuous_notes' in definition:
        message.add(m.Heading(
            tr('Notes for continuous datasets:'),
            **DETAILS_SUBGROUP_STYLE))
        bullets = m.BulletedList()
        for note in definition['continuous_notes']:
            bullets.add(m.Text(note))
        message.add(bullets)

    if 'classified_notes' in definition:
        message.add(m.Heading(
            tr('Notes for classified datasets:'),
            **DETAILS_SUBGROUP_STYLE))
        bullets = m.BulletedList()
        for note in definition['classified_notes']:
            bullets.add(m.Text(note))
        message.add(bullets)

    if 'single_event_notes' in definition:
        message.add(
            m.Heading(tr('Notes for single events'), **DETAILS_STYLE))
        if len(definition['single_event_notes']) < 1:
            message.add(m.Paragraph(tr('No single event notes defined.')))
        else:
            bullets = m.BulletedList()
            for note in definition['single_event_notes']:
                bullets.add(m.Text(note))
            message.add(bullets)

    if 'multi_event_notes' in definition:
        message.add(
            m.Heading(
                tr('Notes for multi events / scenarios:'),
                **DETAILS_STYLE))
        if len(definition['multi_event_notes']) < 1:
            message.add(m.Paragraph(tr('No multi-event notes defined.')))
        else:
            bullets = m.BulletedList()
            for note in definition['multi_event_notes']:
                bullets.add(m.Text(note))
            message.add(bullets)

    if 'actions' in definition:
        message.add(m.Paragraph(m.ImportantText(tr('Actions:'))))
        bullets = m.BulletedList()
        for note in definition['actions']:
            if isinstance(note, dict):
                bullets = _add_dict_to_bullets(bullets, note)
            elif note:
                bullets.add(m.Text(note))
        message.add(bullets)

    for exposure in exposure_all:
        extra_exposure_actions = specific_actions(definition, exposure)
        if extra_exposure_actions:
            title = tr('Actions for exposure : {exposure_name}').format(
                exposure_name=exposure['name'])
            message.add(m.Heading(title, **DETAILS_SUBGROUP_STYLE))
            bullets = m.BulletedList()
            for note in extra_exposure_actions:
                if isinstance(note, dict):
                    bullets = _add_dict_to_bullets(bullets, note)
                elif note:
                    bullets.add(m.Text(note))
            message.add(bullets)

    if 'continuous_hazard_units' in definition:
        message.add(m.Paragraph(m.ImportantText(tr('Units:'))))
        table = m.Table(style_class='table table-condensed table-striped')
        row = m.Row()
        row.add(m.Cell(tr('Name'), header=True))
        row.add(m.Cell(tr('Plural'), header=True))
        row.add(m.Cell(tr('Abbreviation'), header=True))
        row.add(m.Cell(tr('Details'), header=True))
        table.add(row)
        for unit in definition['continuous_hazard_units']:
            row = m.Row()
            row.add(m.Cell(unit['name']))
            row.add(m.Cell(unit['plural_name']))
            row.add(m.Cell(unit['abbreviation']))
            row.add(m.Cell(unit['description']))
            table.add(row)
        message.add(table)

    if 'fields' in definition:
        message.add(m.Paragraph(m.ImportantText(tr('Fields:'))))
        table = _create_fields_table()

        if 'extra_fields' in definition:
            all_fields = definition['fields'] + definition['extra_fields']
        else:
            all_fields = definition['fields']

        for field in all_fields:
            _add_field_to_table(field, table)
        message.add(table)

    if 'classifications' in definition:
        message.add(m.Heading(
            tr('Hazard classifications'),
            **DETAILS_STYLE))
        message.add(m.Paragraph(
            definitions.hazard_classification['description']))
        for inasafe_class in definition['classifications']:
            definition_to_message(
                inasafe_class,
                message,
                table_of_contents,
                heading_level=3)

    if 'classes' in definition:
        message.add(m.Paragraph(m.ImportantText(tr('Classes:'))))
        is_hazard = definition['type'] == hazard_classification_type
        if is_hazard:
            table = _make_defaults_hazard_table()
        else:
            table = _make_defaults_exposure_table()

        for inasafe_class in definition['classes']:
            row = m.Row()
            if is_hazard:
                # name() on QColor returns its hex code
                if 'color' in inasafe_class:
                    colour = inasafe_class['color'].name()
                    row.add(m.Cell(
                        '', attributes='style="background: %s;"' % colour))
                else:
                    row.add(m.Cell(' '))

            row.add(m.Cell(inasafe_class['name']))

            if is_hazard:
                if 'affected' in inasafe_class:
                    row.add(m.Cell(tr(inasafe_class['affected'])))
                else:
                    row.add(m.Cell(tr('unspecified')))

            if is_hazard:
                if inasafe_class.get('fatality_rate') > 0:
                    # we want to show the rate as a scientific notation
                    rate = html_scientific_notation_rate(
                        inasafe_class['fatality_rate'])
                    rate = '%s%%' % rate
                    row.add(m.Cell(rate))
                elif inasafe_class.get('fatality_rate') == 0:
                    row.add(m.Cell('0%'))
                else:
                    row.add(m.Cell(tr('unspecified')))

            if is_hazard:
                if 'displacement_rate' in inasafe_class:
                    rate = inasafe_class['displacement_rate'] * 100
                    rate = '%.0f%%' % rate
                    row.add(m.Cell(rate))
                else:
                    row.add(m.Cell(tr('unspecified')))

            if 'string_defaults' in inasafe_class:
                defaults = None
                for default in inasafe_class['string_defaults']:
                    if defaults:
                        defaults += ',%s' % default
                    else:
                        defaults = default
                row.add(m.Cell(defaults))
            else:
                row.add(m.Cell(tr('unspecified')))

            if is_hazard:
                # Min may be a single value or a dict of values so we need
                # to check type and deal with it accordingly
                if 'numeric_default_min' in inasafe_class:
                    if isinstance(inasafe_class['numeric_default_min'], dict):
                        bullets = m.BulletedList()
                        minima = inasafe_class['numeric_default_min']
                        for key, value in sorted(minima.items()):
                            bullets.add('%s : %s' % (key, value))
                        row.add(m.Cell(bullets))
                    else:
                        row.add(m.Cell(inasafe_class['numeric_default_min']))
                else:
                    row.add(m.Cell(tr('unspecified')))

            if is_hazard:
                # Max may be a single value or a dict of values so we need
                # to check type and deal with it accordingly
                if 'numeric_default_max' in inasafe_class:
                    if isinstance(inasafe_class['numeric_default_max'], dict):
                        bullets = m.BulletedList()
                        maxima = inasafe_class['numeric_default_max']
                        for key, value in sorted(maxima.items()):
                            bullets.add('%s : %s' % (key, value))
                        row.add(m.Cell(bullets))
                    else:
                        row.add(m.Cell(inasafe_class['numeric_default_max']))
                else:
                    row.add(m.Cell(tr('unspecified')))

            table.add(row)
            # Description goes in its own row with spanning
            row = m.Row()
            row.add(m.Cell(''))
            row.add(m.Cell(inasafe_class['description'], span=7))
            table.add(row)

        # For hazard classes we also add the 'not affected' class manually:
        if definition['type'] == definitions.hazard_classification_type:
            row = m.Row()
            colour = definitions.not_exposed_class['color'].name()
            row.add(m.Cell(
                '', attributes='style="background: %s;"' % colour))
            description = definitions.not_exposed_class['description']
            row.add(m.Cell(description, span=7))
            table.add(row)

        message.add(table)

    if 'affected' in definition:
        if definition['affected']:
            message.add(m.Paragraph(tr(
                'Exposure entities in this class ARE considered affected')))
        else:
            message.add(m.Paragraph(tr(
                'Exposure entities in this class are NOT considered '
                'affected')))

    if 'optional' in definition:
        if definition['optional']:
            message.add(m.Paragraph(tr(
                'This class is NOT required in the hazard keywords.')))
        else:
            message.add(m.Paragraph(tr(
                'This class IS required in the hazard keywords.')))

    return message


def _citations_to_message(message, definition):
    citations = m.Message()
    bullets = m.BulletedList()
    for citation in definition['citations']:
        if citation['text'] in [None, '']:
            continue
        if citation['link'] in [None, '']:
            bullets.add(m.Paragraph(citation['text']))
        else:
            bullets.add(m.Paragraph(
                m.Link(citation['link'], citation['text'])))
    if not bullets.is_empty():
        citations.add(m.Paragraph(m.ImportantText(
            tr('Citations:')
        )))
        citations.add(bullets)
        message.add(citations)


def _definition_icon_url(definition):
    if 'key' not in definition:
        return None
    svg_image_path = resources_path(
        'img', 'definitions', definition['key'] + '.svg')
    png_image_path = resources_path(
        'img', 'definitions', definition['key'] + '.png')
    if exists(svg_image_path):
        url = resource_url(svg_image_path)
    elif exists(png_image_path):
        url = resource_url(png_image_path)
    else:
        url = None
    return url


def _definition_screenshot_url(definition):
    jpg_image_path = resources_path(
        'img', 'definitions', definition['key'] + '_screenshot.jpg')
    png_image_path = resources_path(
        'img', 'definitions', definition['key'] + '_screenshot.png')
    if exists(jpg_image_path):
        url = resource_url(jpg_image_path)
    elif exists(png_image_path):
        url = resource_url(png_image_path)
    else:
        url = None
    return url


def _create_fields_table():
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('Name'), header=True))
    row.add(m.Cell(tr('Field Name'), header=True))
    row.add(m.Cell(tr('Type'), header=True))
    row.add(m.Cell(tr('Length'), header=True))
    row.add(m.Cell(tr('Precision'), header=True))
    table.add(row)
    return table


def _add_field_to_table(field, table):
    row = m.Row()
    row.add(m.Cell(field['name']))
    row.add(m.Cell(field['field_name']))
    field_types = None
    if not isinstance(field['type'], list):
        field_types = '%s' % _type_to_string(field['type'])
    else:
        # List of field types are supported but the user will only care
        # about the simple types so we turn them into simple names (whole
        # number, decimal number etc. and then strip out the duplicates
        unique_list = []
        # First iterate the types found in the definition to get english names
        for field_type in field['type']:
            field_type_string = _type_to_string(field_type)
            if field_type_string not in unique_list:
                unique_list.append(field_type_string)
        # now iterate the unque list and write to a sentence
        for field_type in unique_list:
            if field_types:
                field_types += ', %s' % str(field_type)
            else:
                field_types = str(field_type)
    row.add(m.Cell(field_types))
    row.add(m.Cell(field['precision']))
    table.add(row)
    # Description goes in its own row with spanning
    row = m.Row()
    row.add(m.Cell(field['description'] + ' ' + field['help_text'], span=6))
    table.add(row)


def _type_to_string(value):
    type_map = {
        QtCore.QVariant.Double: tr('Decimal number'),
        QtCore.QVariant.String: tr('Text'),
        QtCore.QVariant.Int: tr('Whole number'),
        QtCore.QVariant.UInt: tr('Whole number'),
        QtCore.QVariant.LongLong: tr('Whole number'),
        QtCore.QVariant.ULongLong: tr('Whole number'),
        6: tr('Decimal number'),
        10: tr('Text'),
        2: tr('Whole number')
    }
    return type_map[value]


def _make_defaults_hazard_table():
    """Build headers for a table related to hazard classes.

    :return: A table with headers.
    :rtype: m.Table
    """
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    # first row is for colour - we dont use a header here as some tables
    # do not have colour...
    row.add(m.Cell(tr(''), header=True))
    row.add(m.Cell(tr('Name'), header=True))
    row.add(m.Cell(tr('Affected'), header=True))
    row.add(m.Cell(tr('Fatality rate'), header=True))
    row.add(m.Cell(tr('Displacement rate'), header=True))
    row.add(m.Cell(tr('Default values'), header=True))
    row.add(m.Cell(tr('Default min'), header=True))
    row.add(m.Cell(tr('Default max'), header=True))
    table.add(row)
    return table


def _make_defaults_exposure_table():
    """Build headers for a table related to exposure classes.

    :return: A table with headers.
    :rtype: m.Table
    """
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('Name'), header=True))
    row.add(m.Cell(tr('Default values'), header=True))
    table.add(row)
    return table


def _add_dict_to_bullets(target, value):
    """Add notes and actions in dictionary to the bullets

    :param target: Target bullets
    :type target: Bullets

    :param value: Dictionary that contains actions or notes
    :type value: dict

    :return: Updated bullets
    :rtype: Bullets
    """
    actions = value.get('action_list')
    notes = value.get('item_list')
    items_tobe_added = []
    if actions:
        items_tobe_added = actions
    elif notes:
        items_tobe_added = notes

    if items_tobe_added:
        for item in items_tobe_added:
            target.add(m.Text(item))
    return target
