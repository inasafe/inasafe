# coding=utf-8
"""Help text for needs calculator."""

from safe import messaging as m
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path

SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE


def multi_buffer_help():
    """Help message for multi buffer dialog.

    .. versionadded:: 4.0.0

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

    .. versionadded:: 4.0.0

    :returns: A heading object.
    :rtype: safe.messaging.heading.Heading
    """
    message = m.Heading(tr('Multi buffer tool help'), **SUBSECTION_STYLE)
    return message


def content():
    """Helper method that returns just the content.

    This method was added so that the text could be reused in the
    dock_help module.

    .. versionadded:: 4.0.0

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
    paragraph = m.Paragraph(
        m.Image(
            'file:///%s/img/screenshots/'
            'multi-buffer-screenshot.png' % resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)
    message.add(m.Paragraph(tr(
        'This tool will generate a polygon layer by multi-buffering the input '
        'layer. '
        'To use this tool effectively:'
    )))
    tips = m.BulletedList()
    tips.add(tr(
        'Load a point or line layer in QGIS. Typically, the layer will '
        'represent hazard source such as volcano and river.'
    ))
    tips.add(tr(
        'Choose where to save the output layer to.'
    ))
    tips.add(tr(
        'Create one or more entries in the classes list, and define '
        'the appropriate distances for each buffer. You should give '
        'each buffer distance a corresponding name '
        'e.g. "high", "medium", "low". Click the add (+) button to '
        'record your entries.'
    ))
    tips.add(tr(
        'To remove the classification, select the classification you want to '
        'remove, then click the remove (-) button.'
    ))
    tips.add(tr(
        'Check the "launch keywords wizard" checkbox to launch the keywords '
        'creation wizard after the buffering is complete. If you want assign '
        'keywords later, uncheck the "launch keywords wizard" checkbox.'
    ))
    tips.add(tr(
        'A new layer will be added to QGIS after the buffering is complete. '
        'The layer will contain new buffer polygon(s) and the class name will '
        'be stored as an attribute of each polygon. If you check the '
        'launch keywords wizard checkbox, the keywords creation wizard will '
        'launch right after the buffering process has completed. '
        'You can assign the keywords to the output layer.'
    ))
    message.add(tips)
    return message
