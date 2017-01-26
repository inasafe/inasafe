# coding=utf-8
"""Help text for needs calculator."""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles

SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE


def multi_buffer_help():
    """Help message for hazar layer generator dialog.

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
    message = m.Heading(tr('Multi buffer tool help'), **SUBSECTION_STYLE)
    return message


def content():
    """Helper method that returns just the content.

    This method was added so that the text could be reused in the
    dock_help module.

    .. versionadded:: 3.2.2

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
    message.add(m.Paragraph(tr(
        'This tool will generate polygon layer by multi-buffering input layer.'
        ' To use this tool effectively:'
    )))
    tips = m.BulletedList()
    tips.add(tr(
        'Load a point or multiline layer in QGIS. Typically the layer will '
        'represent hazard source such as volcano and river.'
    ))
    tips.add(tr(
        'Choose where to put the ouput layer to.'
    ))
    tips.add(tr(
        'Create a classification for every buffer distance you fill in radius '
        'form, for example: high, medium, and low. Click add (+) button to '
        'record your classification.'
    ))
    tips.add(tr(
        'To remove the classification, select the classification you want to '
        'remove, then click remove (-) button.'
    ))
    tips.add(tr(
        'A new layer will be added to QGIS after the buffering is complete. '
        'The layer will contain new buffer polygon(s) and the class name.'
    ))
    message.add(tips)
    return message
