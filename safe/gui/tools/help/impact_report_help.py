# coding=utf-8
"""Impact report help text."""

from os.path import join

from qgis.core import QgsApplication

from safe import messaging as m
from safe.messaging import styles
from safe.utilities.i18n import tr

SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE

__author__ = 'ismailsunni'


def impact_report_help():
    """Help message for Batch Dialog.

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
    message = m.Heading(tr('Impact report help'), **SUBSECTION_STYLE)
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

    message.add(m.Paragraph(tr(
        'To start report generation you need to click on the Print '
        'button in the buttons area. This will open the Impact report '
        'dialog which has three main areas.')))

    bullets = m.BulletedList()
    bullets.add(m.Text(
        m.ImportantText(tr('InaSAFE reports')),
        tr(
            ' - There are four checkboxes available which are representing '
            'the type of report component that will be generated.'
        )))
    text = tr(
        ' - Here you can select desired template for your report. All '
        'templates bundled with InaSAFE are available here, plus '
        'templates from user-defined template directory (see Options '
        'for information how to set templates directory) and from qgis '
        'setting directory ({qgis_directory}). It is also '
        'possible to select custom template from any location: just '
        'activate radiobutton under combobox and provide path to template '
        'using the "..." button.')
    qgis_directory = join(QgsApplication.qgisSettingsDirPath(), 'inasafe')
    bullets.add(m.Text(
        m.ImportantText(
            tr('Map reports')),
        text.format(qgis_directory=qgis_directory)))
    bullets.add(m.Text(
        m.ImportantText(tr('Buttons area')),
        tr(
            ' - In this area you will find buttons to open the report as '
            'a PDF or in the QGIS print composer. You can also get help by '
            'clicking on the help button or using the close button to close '
            'the print dialog.'
        )))
    message.add(bullets)

    message.add(m.Paragraph(tr(
        'There are four options on which template would you use to generate '
        'a map report.')))

    bullets = m.BulletedList()
    bullets.add(m.Text(
        m.ImportantText(tr('InaSAFE default templates')),
        tr(
            ' - The map report will be generated using InaSAFE default '
            'landscape and portrait map templates. Override template will '
            'not be used.')))

    bullets.add(m.Text(
        m.ImportantText(tr('Override template')),
        tr(
            ' - The map report will be generated using override template '
            'found from qgis setting directory. InaSAFE default map templates '
            'will not be printed.'
        )))

    bullets.add(m.Text(
        m.ImportantText(tr('Template from search directory')),
        tr(
            ' - The map report will be generated using selected template on '
            'template dropdown selector. InaSAFE default map templates will '
            'not be printed and override template will not be used.'
        )))

    bullets.add(m.Text(
        m.ImportantText(tr('Template from file system')),
        tr(
            ' - The map report will be generated using selected template on '
            'file system. InaSAFE default map templates will not be printed '
            'and override template will not be used.'
        )))

    message.add(bullets)

    return message
