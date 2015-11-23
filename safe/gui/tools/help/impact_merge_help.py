# coding=utf-8
"""Help text for impact merge tool"""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles
INFO_STYLE = styles.INFO_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE

__author__ = 'ismailsunni'


def impact_merge_help():
    """Help message for Layer merge dialog.

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
    message = m.Heading(tr('Layer merge tool help'), **INFO_STYLE)
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
        'In some cases you may wish to create a report containing the '
        'combined output of two impact functions for the same area for the '
        'same hazard, different exposures. For example You may carry out an '
        'assessment of the impact of a flood on population and on buildings '
        'and combine the results into a single report. The impact layer '
        'merge tool allows you to do this.'
    )))

    header = m.Heading(tr('Prerequisites'), **INFO_STYLE)
    message.add(header)

    message.add(m.Paragraph(tr(
        'In order to use this tool, please bear in mind the following '
        'requirements:'
    )))
    bullets = m.BulletedList()
    bullets.add(tr(
        'Both impact layers should be loaded in your current project.'))
    bullets.add(tr(
        'Both impact layers should have been created for the same '
        'geographic region.'))
    bullets.add(tr(
        'The same aggregation area should be used for both assessments.'
    ))
    message.add(bullets)

    header = m.Heading(tr('Procedure'), **INFO_STYLE)
    message.add(header)

    message.add(m.Paragraph(tr(
        'To use this tool, follow this procedure:'
    )))

    bullets = m.BulletedList()
    bullets.add(tr(
        'Run an impact assessment for an area using aggregation. e.g. '
        'Flood Impact on Buildings aggregated by municipal boundaries.'
    ))
    bullets.add(tr(
        'Run a second impact assessment for the same area using the same '
        'aggregation. e.g. Flood Impact on People aggregated by municipal '
        'boundaries.'))
    bullets.add(tr(
        'Open impact merge tool and select each impact layer from the pick '
        'lists provided.'
    ))
    bullets.add(tr(
        'Select the aggregation layer that was used to generate the first '
        'and second impact layer.'
    ))
    bullets.add(tr(
        'Select an output directory.'
    ))
    bullets.add(tr(
        'Check "Use customized report template" checkbox and select the '
        'report template file if you want to use your own template. Note '
        'that all the map composer components that are needed must be '
        'fulfilled.'
    ))
    bullets.add(tr(
        'Click OK to generate the per aggregation area combined summaries.'
    ))
    message.add(bullets)

    header = m.Heading(tr('Generated outputs'), **INFO_STYLE)
    message.add(header)

    message.add(m.Paragraph(tr(
        'The tool will generate a PDF per aggregation area. The PDFs will be '
        'placed in the designated output directory after completion of the '
        'merge process.'
    )))

    message.add(m.Paragraph(tr(
        'In the case of impact assessments where no aggregation has been '
        'used, only a single pdf report is generated. In the case of impact '
        'assessments where aggregation has been used, one pdf is generated '
        'per aggregation area.')))

    message.add(m.Paragraph(
        m.ImportantText(tr('Note:')),
        m.Text(tr(
            'After report generation completes, the output directory will '
            'be opened automatically.'))
    ))

    header = m.Heading(tr('Using Customized Template'), **INFO_STYLE)
    message.add(header)

    message.add(m.Paragraph(tr(
        'The default template report is located in '
        '/resources/qgis-composer-templates/merged-report.qpt. If that '
        'template does not satisfy your needs, you can use your own report '
        'template. Before using your own report template, make sure that '
        'your template contains all of these elements with id:'
    )))

    bullets = m.BulletedList()
    bullets.add(m.Text(
        m.ImportantText(tr('impact-map')),
        tr('- a QgsComposerMap')))
    bullets.add(m.Text(
        m.ImportantText(tr('safe-logo')),
        tr('- a QgsComposerPicture')))
    bullets.add(m.Text(
        m.ImportantText(tr('summary-report')),
        tr('- a QgsComposerLabel')))
    bullets.add(m.Text(
        m.ImportantText(tr('aggregation-area')),
        tr('- a QgsComposerLabel')))
    bullets.add(m.Text(
        m.ImportantText(tr('map-scale')),
        tr('- a QgsComposerScaleBar')))
    bullets.add(m.Text(
        m.ImportantText(tr('map-legend')),
        tr('- a QgsComposerLegend')))
    bullets.add(m.Text(
        m.ImportantText(tr('organisation-logo')),
        tr('- a QgsComposerPicture')))
    bullets.add(m.Text(
        m.ImportantText(tr('merged-report-table')),
        tr('- a QgsComposerHTML')))
    message.add(bullets)

    message.add(m.Paragraph(
        m.ImportantText(tr('Note:')),
        m.Text(tr(
            'You can arrange those elements in any position you want.'))
    ))

    message.add(m.Paragraph(tr(
        'If any of those elements does not exist on the report template, the '
        'tools will give you the information of what element is missing on '
        'the template.'
    )))

    header = m.Heading(tr('Map Template Elements'), **INFO_STYLE)
    message.add(header)

    message.add(m.Paragraph(tr(
        'In terms of value replacement, there are three groups of elements '
        'on the template:')))

    message.add(m.Paragraph(
        m.ImportantText(tr('Options driven elements')),
        tr(
            '- Elements that can be changed on InaSAFE Options tool. To '
            'change the value of these elements, please go to InaSAFE '
            'Option tools and change the value of the related field. '
            'Those elements are:')))

    bullets = m.BulletedList()
    bullets.add(m.Text(
        m.ImportantText(tr('organisation-logo')),
        tr(
            'This corresponds to the Organisation logo field in InaSAFE '
            'Option tools. If you do not fill this field, then the default '
            'one, supporters logo, will be used.')))
    bullets.add(m.Text(
        m.ImportantText(tr('disclaimer')),
        tr(
            'It corresponds to Disclaimer text field on InaSAFE Option '
            'tools. If you do not fill this field, then the default one will '
            'be used.')))

    message.add(m.Paragraph(
        m.ImportantText(tr('Elements containing tokens')),
        tr(
            '- the id of these element is not significant, only the token it '
            'contains. At render time, any of these tokens will be replaced. '
            'If you want to have a label containing value of these elements, '
            'enclose these elements with [] on a label i.e [impact-title] '
            'or [hazard-title]. Those elements are listed below:')))

    bullets = m.BulletedList()
    bullets.add(m.Text(
        m.ImportantText('impact-title'),
        tr(
            'It indicates the title of two impacts. The value will be '
            '"first_impact_title and second_impact_title"')))
    bullets.add(m.Text(
        m.ImportantText('hazard-title'),
        tr(
            'It indicates the hazard title used to generate the '
            'impact layer.')))

    message.add(m.Paragraph(
        m.ImportantText(tr(
            'Elements that are directly updated by the renderer')),
        tr(
            '- all of these elements below are generated automatically by '
            'the tool.')))

    bullets = m.BulletedList()
    bullets.add(m.Text(
        m.ImportantText('impact-map'),
        tr(
            ' - contains the map of two impact layers.')))
    bullets.add(m.Text(
        m.ImportantText('summary-report'),
        tr(
            ' - contains the summary of the impact from two impact layers.')))
    bullets.add(m.Text(
        m.ImportantText('aggregation-area'),
        tr(
            ' - contains the name of the aggregation area.')))
    bullets.add(m.Text(
        m.ImportantText('map-scale'),
        tr(
            ' - indicates the scale of the map. To work with any layer '
            'projection preferences, we encourage you to use a numeric '
            'scale bar.')))
    bullets.add(m.Text(
        m.ImportantText('map-legend'),
        tr(
            ' - shows the legend of merged impact layers. The map legend '
            'on default template is set to have two columns showing each '
            'impact layer legend.')))
    bullets.add(m.Text(
        m.ImportantText('merged-report-table'),
        tr(
            '- contains the detailed information of each impact.')))
    message.add(bullets)

    return message
