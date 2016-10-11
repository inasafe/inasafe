# coding=utf-8
"""Help text for the dock widget."""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles
from safe.utilities.resources import resources_path
import safe.definitionsv4 as definitions
INFO_STYLE = styles.INFO_STYLE
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
    ##
    #  Hazard definitions
    ##

    hazards = definitions.hazards
    hazard_category = definitions.hazard_category
    header = m.Heading(tr('Hazards'), **INFO_STYLE)
    message = m.Message()
    message.add(header)
    message.add(definition_to_message(hazards))
    header = m.Heading(tr('Hazards scenarios'), **INFO_STYLE)
    message.add(header)
    message.add(definition_to_message(hazard_category))
    header = m.Heading(tr('Hazard fields'), **INFO_STYLE)
    message.add(header)
    hazard_fields = definitions.hazard_fields
    for hazard_field in hazard_fields:
        message.add(definition_to_message(
            hazard_field))

    ##
    #  Exposure definitions
    ##

    header = m.Heading(tr('Exposures'), **INFO_STYLE)
    message = m.Message()
    message.add(header)
    message.add(definition_to_message(hazards))
    header = m.Heading(tr('Exposure scenarios'), **INFO_STYLE)
    message.add(header)
    message.add(definition_to_message(hazard_category))
    header = m.Heading(tr('Exposure fields'), **INFO_STYLE)
    message.add(header)
    hazard_fields = definitions.hazard_fields
    for hazard_field in hazard_fields:
        message.add(definition_to_message(
            hazard_field))


    # paragraph = m.Paragraph(tr(
    #   ''
    # ))
    # message.add(paragraph)
    return message


def definition_to_message(definition):
    """Helper function to render a definition to a message.

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
    'hazard_classifications': list of ,
    'extra_fields': []

    :returns: Message
    :rtype: str
    """

    header = m.ImportantText(definition['name'])
    message = m.Message()
    message.add(m.HorizontalRule())
    message.add(header)
    message.add(m.Paragraph(definition['description']))
    if 'field_name' in definition:
        message.add(
            m.Paragraph(tr('Field name: %s') % definition['field_name']))
    if 'type' in definition:
        # TODO: figure out how to get class names for Qt4 enumerated types
        # For now we just show the enumeration ids

        # Hack for now until we have consistent store of types in a list
        if not isinstance(definition['type'], list):
            message.add(
                m.Paragraph(
                    tr('Field type: %s') % definition['type']))
        else:
            for field_type in definition['type']:
                message.add(
                    m.Paragraph(
                        tr('Field type: %s') % field_type))
    if 'length' in definition:
        message.add(
            m.Paragraph(tr('Field length: %s') % definition['length']))
    if 'precision' in definition:
        message.add(
            m.Paragraph(tr('Field length: %s') % definition['precision']))

    if 'types' in definition:
        for sub_definition in definition['types']:
            message.add(definition_to_message(sub_definition))

    if 'notes' in definition:
        message.add(m.Paragraph(tr('General notes:')))
        bullets = m.BulletedList()
        for note in definition['notes']:
            bullets.add(m.Text(note))
        message.add(bullets)

    if 'continuous_notes' in definition:
        message.add(m.Paragraph(tr('Notes for continuous datasets:')))
        bullets = m.BulletedList()
        for note in definition['continuous_notes']:
            bullets.add(m.Text(note))
        message.add(bullets)

    if 'classified_notes' in definition:
        message.add(m.Paragraph(tr('Notes for classified datasets:')))
        bullets = m.BulletedList()
        for note in definition['classified_notes']:
            bullets.add(m.Text(note))
        message.add(bullets)

    if 'single_event_notes' in definition:
        message.add(m.Paragraph(tr('Notes for single events')))
        bullets = m.BulletedList()
        for note in definition['single_event_notes']:
            bullets.add(m.Text(note))
        message.add(bullets)

    if 'multi_event_notes' in definition:
        message.add(m.Paragraph(tr('Notes for multi events / scenarios:')))
        bullets = m.BulletedList()
        for note in definition['multi_event_notes']:
            bullets.add(m.Text(note))
        message.add(bullets)

    if 'actions' in definition:
        message.add(m.Paragraph(tr('Actions:')))
        bullets = m.BulletedList()
        for note in definition['actions']:
            bullets.add(m.Text(note))
        message.add(bullets)

    if 'continuous_hazard_units' in definition:
        message.add(m.Paragraph(tr('Continuous hazard units:')))
        for unit in definition['continuous_hazard_units']:
            message.add(definition_to_message(unit))

    if 'vector_hazard_classifications' in definition:
        message.add(m.Paragraph(tr('Vector hazard classifications')))
        for hazard_class in definition['vector_hazard_classifications']:
            message.add(definition_to_message(hazard_class))

    if 'raster_hazard_classifications' in definition:
        message.add(m.Paragraph(tr('Raster hazard classifications')))
        for hazard_class in definition['raster_hazard_classifications']:
            message.add(definition_to_message(hazard_class))
    return message
