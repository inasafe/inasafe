# coding=utf-8
"""Help text for OSM Downloader."""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles

INFO_STYLE = styles.INFO_STYLE


def osm_downloader_help():
    """Help message for OSM Downloader dialog.

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
    message = m.Heading(tr('OSM downloader help'), **INFO_STYLE)
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
    body = tr(
        'This tool will fetch building (\'structure\') or road ('
        '\'highway\') data from the OpenStreetMap project for you. '
        'The downloaded data will have InaSAFE keywords defined and a '
        'default QGIS style applied. To use this tool effectively:'
    )
    tips = m.BulletedList()
    tips.add(tr(
        'Your current extent, when opening this window, will be used to '
        'determine the area for which you want data to be retrieved. '
        'You can interactively select the area by using the '
        '\'select on map\' button - which will temporarily hide this '
        'window and allow you to drag a rectangle on the map. After you '
        'have finished dragging the rectangle, this window will '
        'reappear.'))
    tips.add(tr(
        'Check the output directory is correct. Note that the saved '
        'dataset will be called either roads.shp or buildings.shp (and '
        'associated files).'
    ))
    tips.add(tr(
        'By default simple file names will be used (e.g. roads.shp, '
        'buildings.shp). If you wish you can specify a prefix to '
        'add in front of this default name. For example using a prefix '
        'of \'padang-\' will cause the downloaded files to be saved as '
        '\'padang-roads.shp\' and \'padang-buildings.shp\'. Note that '
        'the only allowed prefix characters are A-Z, a-z, 0-9 and the '
        'characters \'-\' and \'_\'. You can leave this blank if you '
        'prefer.'
    ))
    tips.add(tr(
        'If a dataset already exists in the output directory it will be '
        'overwritten.'
    ))
    tips.add(tr(
        'This tool requires a working internet connection and fetching '
        'buildings or roads will consume your bandwidth.'))
    tips.add(m.Link(
        'http://www.openstreetmap.org/copyright',
        text=tr(
            'Downloaded data is copyright OpenStreetMap contributors'
            ' (click for more info).')
    ))
    message.add(body)
    message.add(tips)
    return message
