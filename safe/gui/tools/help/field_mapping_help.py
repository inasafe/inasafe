# coding=utf-8
"""Help text for the Field Mapping dialog."""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles
from safe.utilities.resources import resources_path
SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE
INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE


__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def field_mapping_help():
    """Help message for field mapping Dialog.

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
    message = m.Heading(tr('Field Mapping Tool Help'), **INFO_STYLE)
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
            'field-mapping-tool-screenshot.png' % resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)

    paragraph = m.Paragraph(tr(
        'This tool allows you to define field mappings to use for demographic '
        'breakdowns of your analysis results. You can activate the '
        'tool on the InaSAFE toolbar:'),
        m.Image(
            'file:///%s/img/icons/'
            'show-mapping-tool.svg' % resources_path(),
            **SMALL_ICON_STYLE),

    )
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'Field mapping describes the process of matching one or more fields '
        'in an attribute table to a concept in InaSAFE. The field mappings '
        'tool InaSAFE allows you to match concepts such as "elderly", '
        '"disabled people", "pregnant" and so on to their counterpart fields '
        'in either an aggregation layer or an exposure population vector '
        'layer.'
    ))
    message.add(paragraph)
    paragraph = m.Paragraph(m.ImportantText(
        'Note: It is not possible to use this tool with raster population '
        'exposure data.'
    ))
    message.add(paragraph)


    return message
