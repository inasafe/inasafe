# coding=utf-8
"""Help text for the IF options dialog."""

from safe import messaging as m
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path

INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def function_options_help():
    """Help message for Function options Dialog.

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
    message = m.Heading(tr('Function Options Help'), **INFO_STYLE)
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
            'batch-calculator-screenshot.png' % resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)
    message.add(m.Paragraph(tr(
        'Depending on which Impact Function you have chosen you have '
        'different options available for adjusting the parameters of the '
        'question you are asking. Some Impact Functions have more '
        'configurable Options than others. To open the Impact Function '
        'Configuration Dialog you need to click on the "Options ..." '
        'button next to the selected impact function paragraph in the '
        'InaSAFE dock. You can have up to 3 tabs visible:'
    )))

    bullets = m.BulletedList()
    bullets.add(m.Text(
        m.ImportantText(tr('Options')),
        tr(
            '- Depending in the Impact function you selected, you can '
            'influence the result of your question here (the Impact Function) '
            'by setting different values to the defaults that will be loaded. '
            'The options available will depend on the Impact Function you '
            'choose (some Impact Functions do not allow users to change the '
            'default parameters).')))
    bullets.add(m.Text(
        m.ImportantText(tr('Post-processors')),
        tr(
            '- Takes the results from the Impact Function and calculates '
            'derivative indicators, for example if you have an affected '
            'population total, the Gender postprocessor will calculate gender '
            'specific indicators such as additional nutritional requirements '
            'for pregnant women.')))
    bullets.add(m.Text(
        m.ImportantText(tr('Minimum Needs')),
        tr(
            '- If the analysis uses population exposure, InaSAFE calculates '
            'the minimum needs of the people affected by the impact scenario. '
            'You should refer to the minimum needs tool for configuring the '
            'global defaults used in these calculations. '),
        m.Image(
            'file:///%s/img/icons/'
            'show-minimum-needs.svg' % resources_path(),
            **SMALL_ICON_STYLE),
        tr(
            ' This panel will let you override global defaults for a specific '
            'analysis run.')))
    message.add(bullets)
    return message
