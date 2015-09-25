# coding=utf-8

__author__ = 'ismailsunni'


from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles

INFO_STYLE = styles.INFO_STYLE


def needs_manager_helps():
    """Help message for Batch Dialog.

    .. versionadded:: 3.2.1

    :returns: A message object containing helpful information.
    :rtype: messaging.message.Message
    """
    heading = m.Heading(tr('Minimum Needs Manager Help'), **INFO_STYLE)
    body = tr('')

    message = m.Message()
    message.add(m.Brand())
    message.add(heading)
    message.add(body)

    return message
