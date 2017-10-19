# coding=utf-8
"""Help text for the extent selector dialog."""

from safe import messaging as m
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path

SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE
INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE

__author__ = 'ismailsunni'


def extent_selector_help():
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
    message = m.Heading(
        tr('Analysis extent selector help'), **SUBSECTION_STYLE)
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
            'analysis-area-screenshot.png' % resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)

    paragraph = m.Paragraph(tr(
        'This tool allows you to specify which geographical region should be '
        'used for your analysis. If you want to check what area will be '
        'included in your analysis, enable the \'Toggle scenario outlines\' '
        'tool on the InaSAFE toolbar:'),
        m.Image(
            'file:///%s/img/icons/'
            'toggle-rubber-bands.svg' % resources_path(),
            **SMALL_ICON_STYLE),

    )
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'Your user defined extent will be shown on the map as a rectangle. '
        'There are a number of different modes that can be used which are '
        'described below:'))
    message.add(paragraph)

    message.add(extent_mode_content())

    return message


def extent_mode_content():
    """Helper method that returns just the content in extent mode.

    This method was added so that the text could be reused in the
    wizard.

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
    header = m.Heading(tr(
        'Use intersection of hazard and exposure layers'), **INFO_STYLE)
    message.add(header)
    paragraph = m.Paragraph(tr(
        'The largest area that can be analysed is the intersection of the '
        'hazard and exposure layers you have added. To choose this option, '
        'click \'Use intersection of hazard and exposure layers\'. '))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'Sometimes it is more useful to analyse a smaller area. This could be '
        'to reduce processing time (smaller areas with process faster) or '
        'because information is only needed in a certain area (e.g. if a '
        'district only wants information for their district, not for the '
        'entire city). If you want to analyse a smaller area, there are a few '
        'different ways to do this.'))
    message.add(paragraph)
    header = m.Heading(tr(
        'Use intersection of hazard, exposure and current view extent'),
        **INFO_STYLE)
    message.add(header)
    paragraph = m.Paragraph(tr(
        'If you wish to conduct the analysis on the area currently shown in '
        'the window, you can set the analysis area to \'Use intersection of '
        'hazard, exposure and current view extent\'. If the extents of the '
        'datasets are smaller than the view extent, the analysis area will be '
        'reduced to the extents of the datasets.'))
    message.add(paragraph)
    header = m.Heading(tr(
        'Use intersection of hazard, exposure and this bookmark'),
        **INFO_STYLE)
    message.add(header)
    paragraph = m.Paragraph(tr(
        'You can also use one of your QGIS bookmarks to set the analysis '
        'area.'),
        m.ImportantText(tr(
            'This option will be greyed out if you have no bookmarks.')))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'To create a bookmark, zoom to the area you want to create a bookmark '
        'for. When you are happy with the extent, click the \'New bookmark\' '
        'button in the QGIS toolbar.'))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'The drop down menu in the InaSAFE Analysis Area window should now be '
        'activated. When you choose a bookmark from the drop down menu it '
        'will zoom to the analysis area selected by the bookmark.'))
    message.add(paragraph)
    header = m.Heading(tr(
        'Use intersection of hazard, exposure and this bounding box'),
        **INFO_STYLE)
    message.add(header)
    paragraph = m.Paragraph(tr(
        'You can also choose the analysis area interactively by clicking '
        '\'Use intersection of hazard, exposure and this bounding box\'. This '
        'will allow you to click \'Drag on map\' which will temporarily hide '
        'this window and allow you to drag a rectangle on the map. After you '
        'have finished dragging the rectangle, this window will reappear with '
        'values in the North, South, East and West boxes. If the extents of '
        'the datasets are smaller than the user defined analysis area, the '
        'analysis area will be reduced to the extents of the datasets.'))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'Alternatively, you can enter the coordinates directly into the '
        'N/S/E/W boxes once the \'Use intersection of hazard, exposure and '
        'this bounding box\' option is selected (using the same coordinate '
        'reference system, or CRS, as the map is currently set).'))
    message.add(paragraph)

    return message
