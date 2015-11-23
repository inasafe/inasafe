# coding=utf-8
"""Help text for Peta Jakarta Downloader."""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles

INFO_STYLE = styles.INFO_STYLE


def peta_jakarta_help():
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
    message = m.Heading(tr('Peta Jakarta downloader help'), **INFO_STYLE)
    return message


def content():
    """Helper method that returns just the content.

    This method was added so that the text could be reused in the
    dock_help module.

    .. versionadded:: 3.2.3

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
    link = m.Link('https://petajakarta.org', 'PetaJakarta.org')
    body = m.Paragraph(tr(
        'This tool will fetch current flood data for Jakarta from '), link)
    tips = m.BulletedList()
    tips.add(tr(
        'Choose the reporting period - either 6, 3 or 1 hours.'))
    tips.add(tr(
        'Choose the reporting area size - either subdistrict, village '
        'or RW boundaries.'))
    tips.add(tr(
        'Check the output directory is correct. Note that the saved '
        'dataset will be called jakarta_flood.shp (and '
        'associated files).'
    ))
    tips.add(tr(
        'If you wish you can specify a prefix to '
        'add in front of this default name. For example using a prefix '
        'of \'23Nov-\' will cause the downloaded files to be saved as '
        '\'23Nov-jakarta-flood.shp\'. Note that the only allowed prefix '
        'characters are A-Z, a-z, 0-9 and the characters \'-\' and \'_\'. '
        'You can leave this blank if you prefer.'
    ))
    tips.add(tr(
        'If a dataset already exists in the output directory it will be '
        'overwritten.'
    ))
    tips.add(tr(
        'This tool requires a working internet connection and fetching '
        'data will consume your bandwidth.'))
    tips.add(m.Link(
        'https://petajakarta.org/banjir/en/data/',
        text=tr(
            'Downloaded data is copyright the PetaJarta contributors'
            ' (click for more info).')
    ))
    message.add(body)
    message.add(tips)
    return message
