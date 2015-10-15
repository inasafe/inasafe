# coding=utf-8

__author__ = 'ismailsunni'


from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles
from safe.utilities.resources import resources_path

INFO_STYLE = styles.INFO_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE


def dock_help():
    """Help message for Batch Dialog.

    .. versionadded:: 3.2.1

    :returns: A message object containing helpful information.
    :rtype: messaging.message.Message
    """
    heading = m.Heading(tr('InaSAFE dock help'), **INFO_STYLE)
    message = m.Message()
    message.add(m.Brand())
    message.add(heading)

    paragraph = m.Paragraph(tr(
        'This document describes the usage of the InaSAFE \'dock panel\''
        '- which is an interface for running risk scenarios within the QGIS '
        'environment. If you are a new user, you may also consider using the '
        '\'Impact Function Centric Wizard\' to run the analysis. You can '
        'launch the wizard by clicking on this icon in the toolbar:'),
        m.Image(
            'file:///%s/img/icons/'
            'show-wizard.svg' % resources_path(),
            **SMALL_ICON_STYLE),

    )
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'You can drag and drop the dock panel to reposition it in the user '
        'interface. For example, dragging the panel towards the right margin '
        'of the QGIS application will dock it to the right side of the screen.'
    ))
    message.add(paragraph)

    message.add(m.Paragraph(tr(
        'There are three main areas to the dock panel:')))
    bullets = m.BulletedList()
    bullets.add(tr('the Questions area'))
    bullets.add(tr('the Results area'))
    bullets.add(tr('the Buttons area'))
    message.add(bullets)
    message.add(m.Paragraph(tr(
        'At any time you can obtain help in InaSAFE by clicking on the '
        'help buttons provided on each dock and dialog.')))

    return message
