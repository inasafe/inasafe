# coding=utf-8
"""Help text for needs calculator."""

from safe import messaging as m
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path

SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE

__author__ = 'ismailsunni'


def needs_calculator_help():
    """Help message for needs calculator dialog.

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
    message = m.Heading(tr('Needs calculator help'), **SUBSECTION_STYLE)
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
    paragraph = m.Paragraph(
        m.Image(
            'file:///%s/img/screenshots/'
            'needs-calculator-screenshot.png' % resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)
    message.add(m.Paragraph(tr(
        'This tool will calculated minimum needs for evacuated people. To '
        'use this tool effectively:'
    )))
    tips = m.BulletedList()
    tips.add(tr(
        'Load a point or polygon layer in QGIS. Typically the layer will '
        'represent administrative districts where people have gone to an '
        'evacuation center.'))
    tips.add(tr(
        'Ensure that the layer has an INTEGER attribute for the number of '
        'displaced people associated with each feature.'
    ))
    tips.add(tr(
        'Use the pick lists to select the layer and the population '
        'field and then press \'OK\'.'
    ))
    tips.add(tr(
        'A new layer will be added to QGIS after the calculation is '
        'complete. The layer will contain the minimum needs per district '
        '/ administrative boundary.'))
    message.add(tips)
    return message
