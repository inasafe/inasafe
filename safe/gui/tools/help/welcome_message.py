# coding=utf-8
"""Welcome text for InaSAFE."""

import logging

from safe import messaging as m
from safe.messaging import styles
from safe.utilities.i18n import tr

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

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def welcome_message():
    """Welcome message for first running users.

    .. versionadded:: 4.3.0

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

    .. versionadded:: 4.3.0

    :returns: A heading object.
    :rtype: safe.messaging.heading.Heading
    """
    message = m.Heading(tr('Welcome'), **TITLE_STYLE)
    return message


def content():
    """Helper method that returns just the content.

    This method was added so that the text could be reused in the
    dock_help module.

    .. versionadded:: 4.3.0

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
    message.add(m.Paragraph(tr(
        'Welcome to InaSAFE. Before you begin using InaSAFE, we would '
        'like to encourage you to review some options that will by InaSAFE. '
        'On the "Organisation Profile" tab you can set the name of your '
        'organisation, your organisation logo and other options related to '
        'your organisation.'
    )))
    message.add(m.Paragraph(tr(
        'The "parameters" tab is used to determine '
        'whether people are affected and the displacement rates that apply '
        'to people exposed to different types of hazards and at different '
        'hazard intensities. We really encourage you to consider these '
        'parameters carefully and to choose appropriate values for your '
        'local situation based on past events and expert knowledge.')))
    message.add(m.Paragraph(tr(
        'You can return to these options any time by using the Plugins -> '
        'InaSAFE -> Options menu.'
    )))

    return message
