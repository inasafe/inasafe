# coding=utf-8
"""Help text for the dock widget."""

from os.path import exists
import logging
from PyQt4 import QtCore
from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles
import safe.definitions as definitions
from safe.gui.tools.help.dock_help import content as dock_help
from safe.gui.tools.help.extent_selector_help import content as extent_help
from safe.gui.tools.help.impact_report_help import content as report_help
from safe.gui.tools.help.needs_calculator_help import content as needs_help
from safe.gui.tools.help.batch_help import content as batch_help
from safe.gui.tools.help.needs_manager_help import content as \
    needs_manager_help
from safe.gui.tools.help.options_help import content as options_help
from safe.gui.tools.help.osm_downloader_help import content as osm_help
from safe.gui.tools.help.peta_bencana_help import content as petabencana_help
from safe.gui.tools.help.shakemap_converter_help \
    import content as shakemap_help
from safe.gui.tools.help.multi_buffer_help import content as multi_buffer_help
from safe.utilities.resources import resource_url, resources_path
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
    message = m.Heading(tr('InaSAFE help'), **TITLE_STYLE)
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
        tr('Overview'))
    ##
    # Credits and disclaimers ...
    ##
    header = m.Heading(tr('Disclaimer'), **BLUE_CHAPTER_STYLE)
    message.add(header)
    message.add(m.Paragraph(definitions.messages.disclaimer()))

    header = m.Heading(tr('Limitations and License'), **BLUE_CHAPTER_STYLE)
    message.add(header)
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
        tr('Glossary of terms'))

    last_group = None
    table = None
    for key, value in definitions.concepts.iteritems():
        current_group = value['group']
        if current_group != last_group:
            if last_group is not None:
                message.add(table)
            header = m.Heading(current_group, **SUBSECTION_STYLE)
            message.add(header)
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
        tr('Core functionality and tools'))

    header = m.Heading(tr('The InaSAFE Dock'), **SUBSECTION_STYLE)
    message.add(header)
    message.add(dock_help())

    header = m.Heading(tr('InaSAFE Reports'), **SUBSECTION_STYLE)
    message.add(header)
    message.add(report_help())

    header = m.Heading(tr(
        'Managing analysis extents with the extents selector'),
        **SUBSECTION_STYLE)
    message.add(header)
    message.add(extent_help())

    header = m.Heading(tr('InaSAFE Options'), **SUBSECTION_STYLE)
    message.add(header)
    message.add(options_help())

    header = m.Heading(tr('The Batch Runner'), **SUBSECTION_STYLE)
    message.add(header)
    message.add(batch_help())

    header = m.Heading(tr('The OpenStreetMap Downloader'), **SUBSECTION_STYLE)
    message.add(header)
    message.add(osm_help())

    header = m.Heading(tr('The PetaBencana Downloader'), **SUBSECTION_STYLE)
    message.add(header)
    message.add(petabencana_help())

    header = m.Heading(tr('The Shakemap Converter'), **SUBSECTION_STYLE)
    message.add(header)
    message.add(shakemap_help())

    header = m.Heading(tr('The Multi Buffer Tool'), **SUBSECTION_STYLE)
    message.add(header)
    message.add(multi_buffer_help())

    # Keep this last in the tool section please as it has subsections
    # and so uses the top level section style
    _create_section_header(
        message,
        table_of_contents,
        'minimum-needs',
        tr('Minimum Needs'))
    header = m.Heading(tr('The minimum needs tool'), **SUBSECTION_STYLE)
    message.add(header)
    message.add(needs_help())
    header = m.Heading(tr('The minimum needs manager'), **SUBSECTION_STYLE)
    message.add(header)
    message.add(needs_manager_help())

    ##
    #  Analysis workflow
    ##

    _create_section_header(
        message,
        table_of_contents,
        'analysis-steps',
        tr('Analysis steps'))
    header = m.Heading(tr('Analysis internal process'), **SUBSECTION_STYLE)
    message.add(header)
    analysis = definitions.concepts['analysis']
    message.add(analysis['description'])
    url = _definition_screenshot_url(analysis)
    if url:
        message.add(m.Image(url))
    header = m.Heading(tr('Progress reporting steps'), **SUBSECTION_STYLE)
    message.add(header)
    steps = definitions.analysis_steps.values()
    for step in steps:
        message.add(definition_to_message(step, BLUE_CHAPTER_STYLE))

    ##
    #  Hazard definitions
    ##

    _create_section_header(
        message,
        table_of_contents,
        'hazards',
        tr('Hazard Concepts'))

    hazard_category = definitions.hazard_category
    message.add(definition_to_message(
        hazard_category, heading_style=SUBSECTION_STYLE))

    hazards = definitions.hazards
    message.add(definition_to_message(
        hazards, heading_style=SUBSECTION_STYLE))

    ##
    #  Exposure definitions
    ##

    _create_section_header(
        message,
        table_of_contents,
        'exposures',
        tr('Exposure Concepts'))
    exposures = definitions.exposures
    message.add(
        definition_to_message(exposures, heading_style=SUBSECTION_STYLE))

    ##
    #  Defaults
    ##

    _create_section_header(
        message,
        table_of_contents,
        'defaults',
        tr('InaSAFE Defaults'))
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('Name')), header_flag=True)
    row.add(m.Cell(tr('Default value')), header_flag=True)
    row.add(m.Cell(tr('Default min')), header_flag=True)
    row.add(m.Cell(tr('Default max')), header_flag=True)
    row.add(m.Cell(tr('Description')), header_flag=True)
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
        tr('Fields'))
    header = m.Heading(tr('Input dataset fields'), **SUBSECTION_STYLE)
    message.add(header)
    _create_fields_section(
        message,
        tr('Exposure fields'),
        definitions.exposure_fields)
    _create_fields_section(
        message,
        tr('Hazard fields'),
        definitions.hazard_fields)
    _create_fields_section(
        message,
        tr('Aggregation fields'),
        definitions.aggregation_fields)
    header = m.Heading(tr('Output dataset fields'), **SUBSECTION_STYLE)
    message.add(header)
    _create_fields_section(
        message,
        tr('Impact fields'),
        definitions.impact_fields)
    _create_fields_section(
        message,
        tr('Aggregate hazard fields'),
        definitions.aggregate_hazard_fields)
    _create_fields_section(
        message,
        tr('Aggregation impacted fields'),
        definitions.aggregation_impacted_fields)
    _create_fields_section(
        message,
        tr('Exposure breakdown fields'),
        definitions.exposure_breakdown_fields)
    _create_fields_section(
        message,
        tr('Analysis fields'),
        definitions.analysis_fields)

    ##
    #  Geometries
    ##

    _create_section_header(
        message,
        table_of_contents,
        'geometries',
        tr('Layer Geometry Types'))
    header = m.Heading(tr('Vector'), **SUBSECTION_STYLE)
    message.add(header)
    message.add(definition_to_message(
        definitions.layer_geometry_point, BLUE_CHAPTER_STYLE))
    message.add(definition_to_message(
        definitions.layer_geometry_line, BLUE_CHAPTER_STYLE))
    message.add(definition_to_message(
        definitions.layer_geometry_polygon, BLUE_CHAPTER_STYLE))
    header = m.Heading(tr('Raster'), **SUBSECTION_STYLE)
    message.add(header)
    message.add(definition_to_message(
        definitions.layer_geometry_raster, BLUE_CHAPTER_STYLE))

    ##
    #  Layer Modes
    ##

    _create_section_header(
        message,
        table_of_contents,
        'layer-modes',
        tr('Layer Modes'))
    message.add(definition_to_message(
        definitions.layer_mode, SUBSECTION_STYLE))

    ##
    #  Layer Purposes
    ##

    _create_section_header(
        message,
        table_of_contents,
        'layer-purposes',
        tr('Layer Purposes'))
    message.add(definition_to_message(
        definitions.layer_purpose_hazard, SUBSECTION_STYLE))
    message.add(definition_to_message(
        definitions.layer_purpose_exposure, SUBSECTION_STYLE))
    message.add(definition_to_message(
        definitions.layer_purpose_aggregation, SUBSECTION_STYLE))
    message.add(definition_to_message(
        definitions.layer_purpose_exposure_summary, SUBSECTION_STYLE))
    message.add(definition_to_message(
        definitions.layer_purpose_exposure_breakdown, SUBSECTION_STYLE))
    message.add(definition_to_message(
        definitions.layer_purpose_aggregation_impacted, SUBSECTION_STYLE))
    message.add(definition_to_message(
        definitions.layer_purpose_aggregate_hazard_impacted,
        SUBSECTION_STYLE))
    message.add(definition_to_message(
        definitions.layer_purpose_profiling, SUBSECTION_STYLE))

    ##
    # All units
    ##

    _create_section_header(
        message,
        table_of_contents,
        'all-units',
        tr('All Units'))
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('Name')), header_flag=True)
    row.add(m.Cell(tr('Plural')), header_flag=True)
    row.add(m.Cell(tr('Abbreviation')), header_flag=True)
    row.add(m.Cell(tr('Details')), header_flag=True)
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
        tr('Post Processors'))
    header = m.Heading(tr('Post Processor Input Types'), **SUBSECTION_STYLE)
    message.add(header)
    table = _create_post_processor_subtable(
        definitions.post_processor_input_types
    )
    message.add(table)

    header = m.Heading(tr('Post Processor Input Values'), **SUBSECTION_STYLE)
    message.add(header)
    table = _create_post_processor_subtable(
        definitions.post_processor_input_values
    )
    message.add(table)

    header = m.Heading(tr('Post Processor Process Types'), **SUBSECTION_STYLE)
    message.add(header)
    table = _create_post_processor_subtable(
        definitions.post_processor_process_types
    )
    message.add(table)

    header = m.Heading(tr('Post Processors'), **SUBSECTION_STYLE)
    message.add(header)
    post_processors = definitions.post_processors
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('Name')), header_flag=True)
    row.add(m.Cell(tr('Input Fields')), header_flag=True)
    row.add(m.Cell(tr('Output Fields')), header_flag=True)
    table.add(row)
    for post_processor in post_processors:
        row = m.Row()
        row.add(m.Cell(post_processor['name']))
        # Input fields
        bullets = m.BulletedList()
        for key, value in post_processor['input'].iteritems():
            bullets.add(key)
        row.add(m.Cell(bullets))
        # Output fields
        bullets = m.BulletedList()
        for key, value in post_processor['output'].iteritems():
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
    row.add(m.Cell(tr('Term')), header_flag=True)
    row.add(m.Cell(tr('Description')), header_flag=True)
    table.add(row)
    return table


def _create_section_header(message, table_of_contents, id, text):
    # Warning a side effect here is that the SECTION_STYLE is updated
    # when setting style as we don't have a deep copy
    style = SECTION_STYLE
    style['element_id'] = id
    header = m.Heading(text, **style)
    link = m.Link('#%s' % id, text)
    paragraph = m.Paragraph(link)
    table_of_contents.add(paragraph)
    message.add(header)


def _create_post_processor_subtable(item_list):
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('Name')), header_flag=True)
    row.add(m.Cell(tr('Description')), header_flag=True)
    table.add(row)
    for item in item_list:
        row = m.Row()
        row.add(m.Cell(item['key']))
        row.add(m.Cell(item['description']))
        table.add(row)
    return table


def _create_fields_section(message, title, fields):
    header = m.Heading(title, **BLUE_CHAPTER_STYLE)
    message.add(header)
    table = _create_fields_table()
    for field in fields:
        _add_field_to_table(field, table)
    message.add(table)


def definition_to_message(definition, heading_style=None):
    """Helper function to render a definition to a message.

    :param definition: A definition dictionary (see definitions package).
    :type definition: dict

    :param heading_style: Optional style to apply to the definition
        heading. See safe.messaging.styles
    :type heading_style: dict


    :returns: Message
    :rtype: str
    """

    if heading_style:
        header = m.Heading(definition['name'], **heading_style)
    else:
        header = m.Paragraph(m.ImportantText(definition['name']))
    message = m.Message()
    message.add(header)
    # If the definition has an icon, we put the icon and description side by
    # side in a table otherwise just show the description as a paragraph
    url = _definition_icon_url(definition)
    if url is None:
        LOGGER.info('No URL for definition icon')
        message.add(m.Paragraph(definition['description']))
        for citation in definition['citations']:
            if citation['text'] in [None, '']:
                continue
            if citation['link'] in [None, '']:
                message.add(m.Paragraph(citation['text']))
            else:
                message.add(m.Paragraph(
                    m.Link(citation['link'], citation['text'])))
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
        message.add(m.Image(url))

    # types contains e.g. hazard_all
    if 'types' in definition:
        for sub_definition in definition['types']:
            message.add(definition_to_message(
                sub_definition, RED_CHAPTER_STYLE))

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
            bullets.add(m.Text(note))
        message.add(bullets)

    # This is a bit hacky but we want to be sure that extra notes
    # also show up in the help. See issue #3906 and
    # https://github.com/inasafe/inasafe/pull/3891#issuecomment-281034766
    extra_notes = {
        'earthquake_notes': tr('Earthquake notes:'),
        'earthquake_pager_notes': tr('Earthquake Pager notes:'),
        'earthquake_itb_notes': tr('Earthquake ITB notes:'),
        'earthquake_fatality_model_limitations':
            tr('Earthquake fatality model limitations')}
    for extra_note, title in extra_notes.iteritems():
        if extra_note in definition:
            message.add(m.Heading(
                title, **DETAILS_SUBGROUP_STYLE))
            bullets = m.BulletedList()
            for note in definition[extra_note]:
                bullets.add(m.Text(note))
            message.add(bullets)
    # end of

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
            bullets.add(m.Text(note))
        message.add(bullets)

    if 'continuous_hazard_units' in definition:
        message.add(m.Paragraph(m.ImportantText(tr('Units:'))))
        table = m.Table(style_class='table table-condensed table-striped')
        row = m.Row()
        row.add(m.Cell(tr('Name')), header_flag=True)
        row.add(m.Cell(tr('Plural')), header_flag=True)
        row.add(m.Cell(tr('Abbreviation')), header_flag=True)
        row.add(m.Cell(tr('Details')), header_flag=True)
        table.add(row)
        for unit in definition['continuous_hazard_units']:
            row = m.Row()
            row.add(m.Cell(unit['name']))
            row.add(m.Cell(unit['plural_name']))
            row.add(m.Cell(unit['abbreviation']))
            row.add(m.Cell(unit['description']))
            table.add(row)
        message.add(table)

    if 'extra_fields' and 'fields' in definition:
        message.add(m.Paragraph(m.ImportantText(tr('Fields:'))))
        table = _create_fields_table()
        all_fields = definition['fields'] + definition['extra_fields']
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
            message.add(definition_to_message(
                inasafe_class,
                DETAILS_SUBGROUP_STYLE))

    if 'classes' in definition:
        message.add(m.Paragraph(m.ImportantText(tr('Classes:'))))
        table = _make_defaults_table()
        for inasafe_class in definition['classes']:
            row = m.Row()
            # name() on QColor returns its hex code
            if 'color' in inasafe_class:
                colour = inasafe_class['color'].name()
                row.add(m.Cell(
                    u'', attributes='style="background: %s;"' % colour))
            else:
                row.add(m.Cell(u' '))

            row.add(m.Cell(inasafe_class['name']))
            if 'affected' in inasafe_class:
                row.add(m.Cell(inasafe_class['affected']))
            else:
                row.add(m.Cell(tr('unspecified')))

            if 'displacement_rate' in inasafe_class:
                rate = inasafe_class['displacement_rate'] * 100
                rate = u'%s%%' % rate
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
            # Min may be a single value or a dict of values so we need
            # to check type and deal with it accordingly
            if 'numeric_default_min' in inasafe_class:
                if isinstance(inasafe_class['numeric_default_min'], dict):
                    bullets = m.BulletedList()
                    minima = inasafe_class['numeric_default_min']
                    for key, value in minima.iteritems():
                        bullets.add(u'%s : %s' % (key, value))
                    row.add(m.Cell(bullets))
                else:
                    row.add(m.Cell(inasafe_class['numeric_default_min']))
            else:
                row.add(m.Cell(tr('unspecified')))

            # Max may be a single value or a dict of values so we need
            # to check type and deal with it accordingly
            if 'numeric_default_max' in inasafe_class:
                if isinstance(inasafe_class['numeric_default_max'], dict):
                    bullets = m.BulletedList()
                    maxima = inasafe_class['numeric_default_max']
                    for key, value in maxima.iteritems():
                        bullets.add(u'%s : %s' % (key, value))
                    row.add(m.Cell(bullets))
                else:
                    row.add(m.Cell(inasafe_class['numeric_default_max']))
            else:
                row.add(m.Cell(tr('unspecified')))

            table.add(row)
            # Description goes in its own row with spanning
            row = m.Row()
            row.add(m.Cell(''))
            row.add(m.Cell(inasafe_class['description'], span=6))
            table.add(row)
        # For hazard classes we also add the 'not affected' class manually:
        if definition['type'] == definitions.hazard_classification_type:
            row = m.Row()
            colour = definitions.not_exposed_class['color'].name()
            row.add(m.Cell(
                u'', attributes='style="background: %s;"' % colour))
            description = definitions.not_exposed_class['description']
            row.add(m.Cell(description, span=5))
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


def _definition_icon_url(definition):
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
    row.add(m.Cell(tr('Name')), header_flag=True)
    row.add(m.Cell(tr('Field Name')), header_flag=True)
    row.add(m.Cell(tr('Type')), header_flag=True)
    row.add(m.Cell(tr('Length')), header_flag=True)
    row.add(m.Cell(tr('Precision')), header_flag=True)
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
                field_types += ', %s' % unicode(field_type)
            else:
                field_types = unicode(field_type)
    row.add(m.Cell(field_types))
    row.add(m.Cell(field['precision']))
    table.add(row)
    # Description goes in its own row with spanning
    row = m.Row()
    row.add(m.Cell(field['description'], span=5))
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


def _make_defaults_table():
    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    # first row is for colour - we dont use a header here as some tables
    # do not have colour...
    row.add(m.Cell(tr('')), header_flag=True)
    row.add(m.Cell(tr('Name')), header_flag=True)
    row.add(m.Cell(tr('Affected')), header_flag=True)
    row.add(m.Cell(tr('Displacement rate')), header_flag=True)
    row.add(m.Cell(tr('Default values')), header_flag=True)
    row.add(m.Cell(tr('Default min')), header_flag=True)
    row.add(m.Cell(tr('Default max')), header_flag=True)
    table.add(row)
    return table
