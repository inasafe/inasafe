# coding=utf-8
"""Help text for Raster Reclassify Tool."""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles

INFO_STYLE = styles.INFO_STYLE


def raster_reclassify_help():
    """Help message for Raster Reclassify Tool.

    .. versionadded:: 3.4

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

    .. versionadded:: 3.4

    :returns: A heading object.
    :rtype: safe.messaging.heading.Heading
    """
    message = m.Heading(tr('Raster reclassify help'), **INFO_STYLE)
    return message


def content():
    """Helper method that returns just the content.

    This method was added so that the text could be reused in the
    dock_help module.

    .. versionadded:: 3.4

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
    body = m.Paragraph(tr(
        'This tool will reclassify a given raster layer to vector layer with '
        'specified thresholds used for classifications.'))
    message.add(body)
    return message
