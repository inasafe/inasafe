# coding=utf-8
"""Help text for the Field Mapping dialog."""

from safe import messaging as m
from safe.messaging import styles
from safe.utilities.i18n import tr
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

    .. versionadded:: 4.1.0

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

    .. versionadded:: 4.1.0

    :returns: A heading object.
    :rtype: safe.messaging.heading.Heading
    """
    message = m.Heading(tr('Field Mapping Tool Help'), **INFO_STYLE)
    return message


def content():
    """Helper method that returns just the content.

    This method was added so that the text could be reused in the
    dock_help module.

    .. versionadded:: 4.1.0

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
    message.add(field_mapping_help_content())
    return message


def field_mapping_help_content():
    """Helper method that returns just the content in extent mode.

    This method was added so that the text could be reused in the
    wizard.

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
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
        'exposure data, but ratios defined in aggregation layers will be '
        'used when raster exposure population data is used.'
    ))
    message.add(paragraph)

    paragraph = m.Paragraph(
        m.Image(
            'file:///%s/img/screenshots/'
            'demographic-concepts-screenshot.png' % resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)

    paragraph = m.Paragraph(tr(
        'The illustration above shows the principle behind InaSAFE\'s '
        'demographic breakdown reporting system. The idea here is to support '
        'the production of a detailed demographic breakdown when carrying out '
        'an analysis with a population exposure vector dataset. So for '
        'example instead of simply reporting on the total number of people '
        'exposed to a hazard, we want to break down the affected population '
        'into distinct demographic groups. In InaSAFE by default we consider '
        'three groups:'
    ))
    message.add(paragraph)

    bullets = m.BulletedList()
    bullets.add(m.Paragraph(
        m.ImportantText(tr('Gender: ')),
        tr(
            'The gender group reports on gender specific demographics '
            'including things like the number of women of child bearing age, '
            'number of pregnant women, number of lactating women and so on.'
        )
    ))
    bullets.add(m.Paragraph(
        m.ImportantText(tr('Age: ')),
        tr(
            'The age group reports on age specific demographics including '
            'things like the number of infants, children, young adults, '
            'adults elderly people and so on.'
        )
    ))
    bullets.add(m.Paragraph(
        m.ImportantText(tr('Vulnerable people: ')),
        tr(
            'The vulnerable people group reports on specific demographics '
            'relating to vulnerability including things like the number of '
            'infants, elderly people, disabled people and so on.'
        )
    ))
    message.add(bullets)
    paragraph = m.Paragraph(tr(
        'In the diagram above, you can see that we have an "age" group '
        '(column on the right) which, for purposes of illustration, has two '
        'age classes: "infant" and "child" (center column). These age classes '
        'are defined in InaSAFE metadata and there are actually five classes '
        'in a default installation. In the left hand column you can see a '
        'number of columns listed from the attribute table. In this example '
        'our population data contains columns for different age ranges ('
        '0-1, 1-2, 2-4, 4-6). The field mapping tool can be used in order '
        'to combine the data in the "0 - 1" and "1 - 2" columns into a '
        'new column called "infant". In the next section of this document we '
        'enumerate the different groups and concepts that InaSAFE supports '
        'when generating demographic breakdowns.'))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'When the tool is used, it will write additional data to the '
        'exposure or aggregation layer keywords so that your preferred '
        'concept mappings will be used when reports are generated after the '
        'analysis is carried out. You should note the following special '
        'characteristics of the field mapping tool when used for aggregation '
        'datasets versus when used for vector population exposure datasets:'
    ))
    message.add(paragraph)
    paragraph = m.Paragraph(
        m.ImportantText(tr('Aggregation datasets: ')),
        tr(
            'For aggregation datasets, the field mapping tool uses global '
            'defaults (see the InaSAFE Options Dialog documentation for more '
            'details) or dataset level defaults to determine which ratios '
            'should be used to calculate concept values. For example, in the '
            'age group the aggregation dataset may specify that infants '
            'should by calculated as a ratio of 0.1% of the total population. '
            'Note that for aggregation datasets you can only use ratios, '
            'not counts.')
    )
    message.add(paragraph)
    paragraph = m.Paragraph(
        m.ImportantText(tr('Vector population exposure datasets: ')),
        tr(
            'For exposure datasets, ratios are not supported, only counts. '
            'The field mappings carried out here will be used to generate '
            'new columns during a pre-processing step before the actual '
            'analysis is carried out.')
    )
    message.add(paragraph)
    paragraph = m.Paragraph(
        tr(
            'The interplay between default ratios, aggregation layer '
            'provided ratios and population exposure layers is illustrated '
            'in the table below.')
    )
    message.add(paragraph)

    table = m.Table(style_class='table table-condensed table-striped')
    row = m.Row()
    row.add(m.Cell(tr('Aggregation'), header=True))
    row.add(m.Cell(tr('Raster'), header=True))
    row.add(m.Cell(tr('Vector, no counts'), header=True))
    row.add(m.Cell(tr('Vector with counts'), header=True))
    row.add(m.Cell(tr('Notes'), header=True))
    table.add(row)
    row = m.Row([
        tr('No aggregation'),
        tr('Use global default ratio'),
        tr('Use global default ratio'),
        tr('Use count to determine ratio'),
        tr(''),
    ])
    table.add(row)
    row = m.Row([
        tr('Aggregation, ratio not set'),
        tr('Use global default ratio'),
        tr('Do nothing'),
        tr('Use count to determine ratio'),
        tr(''),
    ])
    table.add(row)
    row = m.Row([
        tr('Aggregation, ratio value set'),
        tr('Use aggregation layer ratio'),
        tr('Use aggregation layer ratio'),
        tr('Use count to determine ratio'),
        tr(''),
    ])
    table.add(row)
    row = m.Row([
        tr('Aggregation, ratio field mapping set'),
        tr('Use aggregation layer ratio'),
        tr('Use aggregation layer ratio'),
        tr('Use count to determine ratio'),
        tr(''),
    ])
    table.add(row)
    message.add(table)

    return message
