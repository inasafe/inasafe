# coding=utf-8
"""Help text for PetaBencana Downloader."""

from safe import messaging as m
from safe.definitions.peta_bencana import production_api
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path

SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE


def peta_bencana_help():
    """Help message for PetaBencana dialog.

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
    message = m.Heading(tr('PetaBencana downloader help'), **SUBSECTION_STYLE)
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
    paragraph = m.Paragraph(
        m.Image(
            'file:///%s/img/screenshots/'
            'petabencana-screenshot.png' % resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)
    link = m.Link('https://petabencana.id', 'PetaBencana.id')
    body = m.Paragraph(tr(
        'This tool will fetch current flood data for Jakarta from '), link)
    tips = m.BulletedList()
    tips.add(tr(
        'Check the output directory is correct. Note that the saved '
        'dataset will be called jakarta_flood.shp (and associated files).'
    ))
    tips.add(tr(
        'If you wish you can specify a prefix to '
        'add in front of this default name. For example using a prefix '
        'of \'foo-\' will cause the downloaded files to be saved as e.g. '
        '\'foo-rw-jakarta-flood.shp\'. Note that the only allowed prefix '
        'characters are A-Z, a-z, 0-9 and the characters \'-\' and \'_\'. '
        'You can leave this blank if you prefer.'
    ))
    tips.add(tr(
        'If a dataset already exists in the output directory it will be '
        'overwritten if the "overwrite existing files" checkbox is ticked.'
    ))
    tips.add(tr(
        'If the "include date/time in output filename" option is ticked, '
        'the filename will be prefixed with a time stamp e.g. '
        '\'foo-22-Mar-2015-08-01-2015-rw-jakarta-flood.shp\' where the date '
        'timestamp is in the form DD-MMM-YYYY.'
    ))
    tips.add(tr(
        'This tool requires a working internet connection and fetching '
        'data will consume your bandwidth.'))
    tips.add(m.Link(
        production_api['help_url'],
        text=tr(
            'Downloaded data is copyright the PetaBencana contributors'
            ' (click for more info).')
    ))
    message.add(body)
    message.add(tips)
    return message
