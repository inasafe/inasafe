# coding=utf-8
"""Help text for shakemap convertor."""

from safe import messaging as m
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path

SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE

__author__ = 'ismailsunni'


def shakemap_converter_help():
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
    message = m.Heading(tr('Shakemap convertor help'), **SUBSECTION_STYLE)
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
            'shakemap-converter-screenshot.png' % resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)
    body = tr(
        'This tool will convert an earthquake \'shakemap\' that is in '
        'grid xml format into a GeoTIFF file. The imported file can be used '
        'in InaSAFE as an input for impact functions that require an '
        'earthquake layer.  To use this tool effectively:')
    message.add(body)
    tips = m.BulletedList()
    tips.add(tr(
        'Select a grid.xml for the input layer.'))
    tips.add(tr(
        'Choose where to write the output layer to.'
    ))
    tips.add(tr(
        'Choose the interpolation algorithm that should be used when '
        'converting the xml grid to a raster. If unsure keep the default.'
    ))
    tips.add(tr(
        'If you want to obtain shake data you can get download it free from '
        'the USGS shakemap site: '
        'http://earthquake.usgs.gov/earthquakes/shakemap/list.php?y=2013'))

    message.add(tips)
    return message
