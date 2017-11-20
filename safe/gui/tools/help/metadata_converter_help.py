# coding=utf-8
"""Help text for the Metadata Converter dialog."""

from safe import messaging as m
from safe.messaging import styles
from safe.utilities.i18n import tr

SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE
INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE


__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def metadata_converter_help():
    """Help message for metadata converter Dialog.

    .. versionadded:: 4.3

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

    .. versionadded:: 4.3

    :returns: A heading object.
    :rtype: safe.messaging.heading.Heading
    """
    message = m.Heading(tr('Metadata Converter Help'), **INFO_STYLE)
    return message


def content():
    """Helper method that returns just the content.

    This method was added so that the text could be reused in the
    dock_help module.

    .. versionadded:: 4.3

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
    message.add(metadata_converter_help_content())
    return message


def metadata_converter_help_content():
    """Helper method that returns just the content in extent mode.

    This method was added so that the text could be reused in the
    wizard.

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
    paragraph = m.Paragraph(tr(
        'This tool will convert InaSAFE 4.x keyword metadata into the '
        'metadata format used by InaSAFE 3.5. The primary reason for doing '
        'this is to prepare data for use in GeoSAFE - the online version of '
        'InaSAFE.'
    ))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'You should note that this tool will not touch the original data or '
        'metadata associated with a layer. Instead it will make a copy of the '
        'original layer to the place that you nominate, and create a new '
        'keywords XML file to accompany that data. This new keywords file '
        'will contain InaSAFE keywords in the 3.5 format.'
    ))
    message.add(paragraph)
    return message
