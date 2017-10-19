# coding=utf-8
"""Help for batch runner dialog."""

from safe import messaging as m
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path

INFO_STYLE = styles.BLUE_LEVEL_4_STYLE

__author__ = 'ismailsunni'


def batch_help():
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
    message = m.Heading(tr('Batch Runner'), **INFO_STYLE)
    return message


def content():
    """Helper method that returns just the content.

    This method was added so that the text could be reused in the
    other contexts.

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
        'With this tool you can set up numerous scenarios and run them all in '
        'one go. A typical use case may be where you define a number of e.g. '
        'flood impact scenarios all using a standard data set e.g. '
        'flood.shp. As new flood data becomes available you replace flood.shp '
        'and rerun the scenarios using the batch runner. Using this approach '
        'you can quickly produce regional contingency plans as your '
        'understanding of hazards changes. When you run the batch of '
        'scenarios, pdf reports are generated automatically and all placed in '
        'a single common directory making it easy for you to browse and '
        'disseminate the reports produced.')))

    message.add(m.Paragraph(tr(
        'When the batch process completes, it will also produce a summary '
        'report like this:')))

    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row(m.Cell(tr('InaSAFE Batch Report File')), header=True)
    table.add(row)
    table.add(m.Row(m.Cell('P: gempa bumi Sumatran fault (Mw7.8)')))
    table.add(m.Row(m.Cell('P: gempa di Yogya tahun 2006')))
    table.add(m.Row(m.Cell('P: banjir jakarta 2007')))
    table.add(m.Row(m.Cell('P: Tsunami di Maumere (Mw 8.1)')))
    table.add(m.Row(m.Cell('P: gempa Mw6.5 Palu-Koro Fault')))
    table.add(m.Row(m.Cell('P: gunung merapi meletus')))
    table.add(m.Row(m.Cell('-----------------------------')))
    table.add(m.Row(m.Cell(tr('Total passed: 6'))))
    table.add(m.Row(m.Cell(tr('Total failed: 0'))))
    table.add(m.Row(m.Cell(tr('Total tasks: 6'))))

    message.add(table)

    # message.add(m.Paragraph(tr(
    #     'For advanced users there is also the ability to batch run python '
    #     'scripts using this tool, but this should be considered an '
    #     'experimental</strong> feature still at this stage.')))

    message.add(m.Paragraph(tr(
        'Before running the Batch Runner you might want to use the \'save '
        'scenario\' tool to first save some scenarios on which you '
        'can let the batch runner do its work. This tool lets you run saved '
        'scenarios in one go. It lets you select scenarios or let run all '
        'scenarios in one go.')))
    return message
