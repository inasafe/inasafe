# coding=utf-8
"""Help text for the dock widget."""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles
import safe.definitionsv4 as definitions
INFO_STYLE = styles.INFO_STYLE
WARNING_STYLE = styles.WARNING_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE

__author__ = 'timlinux'


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
    message = m.Heading(tr('InaSAFE Definitions help'), **INFO_STYLE)
    return message


def content():
    """Helper method that returns just the content.

    This method was added so that the text could be reused in the
    dock_help module.

    .. versionadded:: 4.0.0

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
    ##
    #  Analysis workflow
    ##

    steps = definitions.analysis_steps.values()
    header = m.Heading(tr('Analysis steps'), **INFO_STYLE)
    message.add(header)
    for step in steps:
        message.add(definition_to_message(step))

    ##
    #  Hazard definitions
    ##

    hazards = definitions.hazards
    hazard_category = definitions.hazard_category
    message.add(definition_to_message(hazards, heading_style=INFO_STYLE))
    header = m.Heading(tr('Hazard scenarios'), **INFO_STYLE)
    message.add(header)
    message.add(definition_to_message(hazard_category))

    ##
    #  Exposure definitions
    ##

    exposures = definitions.exposures
    header = m.Heading(tr('Exposures'), **INFO_STYLE)
    message.add(header)
    message.add(definition_to_message(exposures))

    # paragraph = m.Paragraph(tr(
    #   ''
    # ))
    # message.add(paragraph)
    return message


def definition_to_message(definition, heading_style=None):
    """Helper function to render a definition to a message.

    :param definition: A definition dictionary (see definitions package).
    :type definition: dict

    :param heading_style: Optional style to apply to the definition
        heading. See safe.messaging.styles
    :type heading_style: dict

    'key': A String describing the unique name for this definition
    'name': A human readable translated string naming this definition
    'description': A human readable translated detailed description of this
        definition.
    'citations': A list of one or more citation dicts.
    'types': A list of definitions we will recursively call definition to
        get a sub message message on them.
    'field_name': the name of a field,
    'type': the type of a field,
    'length': the length of a field,
    'precision': the precision of a field,

    'notes': a list of strings,
    'continuous_notes': a list of strings
    'classified_notes':  a list of strings
    'single_event_notes':  a list of strings
    'multi_event_notes':  a list of strings
    'actions':  a list of strings

    'continuous_hazard_units': list of ,
    'vector_hazard_classifications': list of,
    'raster_hazard_classifications': list of,
    'classifications': list of ,
    'extra_fields': []

    :returns: Message
    :rtype: str
    """

    if heading_style:
        header = m.Heading(definition['name'], **heading_style)
    else:
        header = m.Heading(definition['name'])
    message = m.Message()
    message.add(m.HorizontalRule())
    message.add(header)
    message.add(m.Paragraph(definition['description']))
    # types containses e.g. hazard_all
    if 'types' in definition:
        for sub_definition in definition['types']:
            message.add(definition_to_message(
                sub_definition, WARNING_STYLE))

    if 'notes' in definition:
        message.add(m.Paragraph(
            m.ImportantText(tr('General notes:'))))
        bullets = m.BulletedList()
        for note in definition['notes']:
            bullets.add(m.Text(note))
        message.add(bullets)

    if 'continuous_notes' in definition:
        message.add(m.Paragraph(
            m.ImportantText(tr('Notes for continuous datasets:'))))
        bullets = m.BulletedList()
        for note in definition['continuous_notes']:
            bullets.add(m.Text(note))
        message.add(bullets)

    if 'classified_notes' in definition:
        message.add(m.Paragraph(
            m.ImportantText(tr('Notes for classified datasets:'))))
        bullets = m.BulletedList()
        for note in definition['classified_notes']:
            bullets.add(m.Text(note))
        message.add(bullets)

    if 'single_event_notes' in definition:
        message.add(
            m.Paragraph(m.ImportantText(tr('Notes for single events'))))
        bullets = m.BulletedList()
        for note in definition['single_event_notes']:
            bullets.add(m.Text(note))
        message.add(bullets)

    if 'multi_event_notes' in definition:
        message.add(m.Paragraph(
            m.ImportantText(tr('Notes for multi events / scenarios:'))))
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
        message.add(m.Paragraph(tr('Fields')))
        table = m.Table(style_class='table table-condensed table-striped')
        row = m.Row()
        row.add(m.Cell(tr('Name')), header_flag=True)
        row.add(m.Cell(tr('Field Name')), header_flag=True)
        row.add(m.Cell(tr('Type')), header_flag=True)
        row.add(m.Cell(tr('Length')), header_flag=True)
        row.add(m.Cell(tr('Precision')), header_flag=True)
        table.add(row)
        all_fields = definition['fields'] + definition['extra_fields']
        for field in all_fields:
            row = m.Row()
            row.add(m.Cell(field['name']))
            row.add(m.Cell(field['field_name']))
            field_types = None
            if not isinstance(field['type'], list):
                field_types = '%s' % field['type']
            else:
                for field_type in field['type']:
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
        message.add(table)

    # TOOD: vector_hazard_classifications should be ignored
    # it is replaced by hazard_classfications in v4
    # We should delete vector_hazard_classifications from
    # definitions
    if 'classifications' in definition:
        message.add(m.Paragraph(tr('Hazard classifications')))
        for inasafe_class in definition['classifications']:
            message.add(definition_to_message(inasafe_class))

    if 'classes' in definition:
        message.add(m.Paragraph(tr('Classes')))
        table = m.Table(style_class='table table-condensed table-striped')
        row = m.Row()
        row.add(m.Cell(tr('Name')), header_flag=True)
        row.add(m.Cell(tr('Affected')), header_flag=True)
        row.add(m.Cell(tr('Default values')), header_flag=True)
        row.add(m.Cell(tr('Default min')), header_flag=True)
        row.add(m.Cell(tr('Default max')), header_flag=True)
        table.add(row)
        for inasafe_class in definition['classes']:
            row = m.Row()
            row.add(m.Cell(inasafe_class['name']))
            if 'affected' in inasafe_class:
                row.add(m.Cell(inasafe_class['affected']))
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
                if 'numeric_default_min' in inasafe_class:
                    row.add(m.Cell(inasafe_class['numeric_default_min']))
                else:
                    row.add(m.Cell(tr('unspecified')))
                if 'numeric_default_min' in inasafe_class:
                    row.add(m.Cell(inasafe_class['numeric_default_max']))
                else:
                    row.add(m.Cell(tr('unspecified')))

                table.add(row)
                # Description goes in its own row with spanning
                row = m.Row()
                row.add(m.Cell(inasafe_class['description'], span=5))
                table.add(row)
            else:
                row.add(m.Cell(tr('unspecified')))
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
