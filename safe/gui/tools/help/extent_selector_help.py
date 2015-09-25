# coding=utf-8
__author__ = 'ismailsunni'

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles

INFO_STYLE = styles.INFO_STYLE


def extent_selector_help():
    """Help message for extent selector dialog.

    :returns: A message object containing helpful information.
    :rtype: messaging.message.Message
    """
    heading = m.Heading(tr('User Extents Tool'), **INFO_STYLE)
    body = tr(
        'This tool allows you to specify exactly which geographical '
        'region should be used for your analysis. You can either '
        'enter the coordinates directly into the input boxes below '
        '(using the same CRS as the canvas is currently set to), or '
        'you can interactively select the area by using the \'select '
        'on map\' button - which will temporarily hide this window and '
        'allow you to drag a rectangle on the map. After you have '
        'finished dragging the rectangle, this window will reappear. '
        'You can also use one of your bookmarks to set the region. '
        'If you enable the \'Toggle scenario outlines\' tool on the '
        'InaSAFE toolbar, your user defined extent will be shown on '
        'the map as a blue rectangle. Please note that when running '
        'your analysis, the effective analysis extent will be the '
        'intersection of the hazard extent, exposure extent and user '
        'extent - thus the entire user extent area may not be used for '
        'analysis.'

    )

    message = m.Message()
    message.add(m.Brand())
    message.add(heading)
    message.add(body)

    return message
