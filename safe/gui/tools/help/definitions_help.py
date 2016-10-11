# coding=utf-8
"""Help text for the dock widget."""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles
from safe.utilities.resources import resources_path
from safe.gui.tools.help.function_options_help import content as options
from safe.gui.tools.help.impact_report_help import content as report
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

    hazard_category = definitions.hazard_category
    header = m.Heading(tr('Hazard Fields'), **INFO_STYLE)
    message = m.Message()
    message.add(header)



    paragraph = m.Paragraph(tr(
      ''
    ))
    message.add(paragraph)

    hazard_fields = definitions.hazard_fields
    # This adds the help content of the print dialog
    message.add(report())
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

    :returns: Message
    """
    header = m.Heading(definition['name'], **INFO_STYLE)
    message = m.Message()
    message.add(header)
    message.add(m.Paragraph(definition['description']))
    for sub_definition in definition['types']:
        message.add(definition_to_message(sub_definition))
    return message
