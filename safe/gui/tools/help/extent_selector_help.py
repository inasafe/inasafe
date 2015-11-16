# coding=utf-8
"""Help text for the extent selector dialog."""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles

INFO_STYLE = styles.INFO_STYLE

__author__ = 'ismailsunni'


def extent_selector_help():
    """Help message for extent selector dialog.

    .. versionadded:: 3.2.1

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

    .. versionadded:: 3.2.2

    :returns: A heading object.
    :rtype: safe.messaging.heading.Heading
    """
    message = m.Heading(tr('Extent selector help'), **INFO_STYLE)
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
    paragraph = m.Paragraph(tr(
        'This tool allows you to specify exactly which geographical '
        'region should be used for your analysis. You can either '
        'enter the coordinates directly into the input boxes below '
        '(using the same CRS as the canvas is currently set to), or '
        'you can interactively select the area by using the \'select '
        'on map\' button - which will temporarily hide this window and '
        'allow you to drag a rectangle on the map. After you have '
        'finished dragging the rectangle, this window will reappear. '))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'You can also use one of your bookmarks to set the region. '
        'If you enable the \'Toggle scenario outlines\' tool on the '
        'InaSAFE toolbar, your user defined extent will be shown on '
        'the map as a blue rectangle. Please note that when running '
        'your analysis, the effective analysis extent will be the '
        'intersection of the hazard extent, exposure extent and user '
        'extent - thus the entire user extent area may not be used for '
        'analysis.'))
    message.add(paragraph)

    return message
