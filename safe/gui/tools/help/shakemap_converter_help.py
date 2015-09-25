# coding=utf-8
__author__ = 'ismailsunni'

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles

INFO_STYLE = styles.INFO_STYLE


def shakemap_converter_help():
    """Help message for extent selector dialog.

    :returns: A message object containing helpful information.
    :rtype: messaging.message.Message
    """
    heading = m.Heading(tr('Shakemap Converter Help'), **INFO_STYLE)
    body = tr('')

    message = m.Message()
    message.add(m.Brand())
    message.add(heading)
    message.add(body)

    return message
