# coding=utf-8
"""Help text for Population Downloader."""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles

INFO_STYLE = styles.INFO_STYLE


def population_downloader_help():
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
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
    )
    tips = m.BulletedList()
    tips.add(tr(
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'))
    tips.add(tr(
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
    ))
    tips.add(tr(
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
    ))
    tips.add(tr(
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
    ))
    tips.add(tr(
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'
        'HELP GOES HERE HELP GOES HERE HELP GOES HERE HELP GOES HERE'))
    tips.add(m.Link(
        'http://www.worldpop.org.uk/copyright',
        text=tr(
            'Downloaded data is copyright Worldpop'
            ' (click for more info).')
    ))
    message.add(body)
    message.add(tips)
    return message