# coding=utf-8
"""Help text for the dock widget."""

from safe import messaging as m
from safe.gui.tools.help.impact_report_help import content as report
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path

SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE
INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE

__copyright__ = "Copyright 2015, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def dock_help():
    """Help message for Dock Widget.

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
    message = m.Heading(tr('InaSAFE dock help'), **SUBSECTION_STYLE)
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
    paragraph = m.Paragraph(tr(
        'InaSAFE is free software that produces realistic natural hazard '
        'impact scenarios for better planning, preparedness and response '
        'activities. It provides a simple but rigourous way to combine data '
        'from scientists, local governments and communities to provide '
        'insights into the likely impacts of future disaster events.'
    ))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'The InaSAFE \'dock panel\' helps you to run hazard impact analysis '
        'within the QGIS environment. It helps you create your hazard impact '
        'analysis question and shows the results of this analysis. If you are '
        'a new user, you may also consider using the \'Impact Function '
        'Centric Wizard\' to run the analysis. This wizard will guide you '
        'through the process of running an InaSAFE assessment, with '
        'interactive step by step instructions. You can launch the wizard '
        'by clicking on this icon in the toolbar:'),
        m.Image(
            'file:///%s/img/icons/'
            'show-wizard.svg' % resources_path(),
            **SMALL_ICON_STYLE),

    )
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'You can drag and drop the dock panel to reposition it on the screen. '
        'For example, dragging the panel towards the right margin of the QGIS '
        'application will dock it to the right side of the screen.'
    ))
    message.add(paragraph)

    message.add(m.Paragraph(tr(
        'There are three main areas to the dock panel:')))
    bullets = m.BulletedList()
    bullets.add(m.Text(
        # format 'the __questions__ area' for proper i18n
        tr('the %s area') % (
            m.ImportantText(tr(
                'questions')).to_html(),
        )))
    bullets.add(m.Text(
        # format 'the __results__ area' for proper i18n
        tr('the %s area') % (
            m.ImportantText(tr(
                'results')).to_html(),
        )))
    bullets.add(m.Text(
        # format 'the __buttons__ area' for proper i18n
        tr('the %s area') % (
            m.ImportantText(tr(
                'buttons')).to_html(),
        )))
    message.add(bullets)
    message.add(m.Paragraph(tr(
        'You can get help at any time in InaSAFE by clicking on the '
        'help buttons provided on each dock and dialog.')))

    header = m.Heading(tr('The questions area'), **INFO_STYLE)
    message.add(header)
    message.add(m.Paragraph(tr(
        'The intention of InaSAFE is to make it easy to perform your impact '
        'analysis. We start the analysis in the questions area. This area '
        'contains three drop down menus. You create your question by using '
        'these drop down menus to select the hazard and exposure data you '
        'wish to perform the analysis on. '
        'All questions follow this form:'),
        m.EmphasizedText(tr(
            'In the event of a [hazard], how many [exposure] might be '
            '[impacted]?'))))
    message.add(m.Paragraph(tr(
        'For example: "If there is a flood, how many buildings might be '
        'flooded?"')))
    message.add(m.Paragraph(tr(
        'InaSAFE can be used to answer such questions for hazards such as '
        'flood, tsunami, volcanic ash fall and earthquake and exposures '
        'such as population, roads, structures, land cover etc.')))
    message.add(m.Paragraph(tr(
        'The first step in answering these questions is to load layers that '
        'represent either hazard scenarios or exposure data into QGIS. '
        'A hazard, for example, may be represented as a raster layer in '
        'QGIS where each pixel in the raster represents the flood depth '
        'following an inundation event. An exposure layer could be '
        'represented, for example, as vector polygon data representing '
        'building outlines, or a raster outline where each pixel represents '
        'the number of people thought to be living in that cell.')))
    message.add(m.Paragraph(tr(
        'InaSAFE will combine these two layers in a '
        'mathematical model. The results of this model will show what the '
        'effect of the hazard will be on the exposed infrastructure or '
        'people. The plugin relies on simple keyword metadata '
        'associated with each layer to determine what kind of information the '
        'layer represents. You can define these keywords by '
        'selecting a layer and then clicking the InaSAFE Keywords Wizard icon '
        'on the toolbar: '),
        m.Image(
            'file:///%s/img/icons/'
            'show-keyword-wizard.svg' % resources_path(),
            **SMALL_ICON_STYLE),
        tr(
            'The wizard will guide you through the process of defining the '
            'keywords for that layer.')))
    message.add(m.Paragraph(tr(
        'Aggregation is the process whereby we group the analysis results '
        'by district so that you can see how many people, roads or '
        'buildings were affected in each area. This will help you to '
        'understand where the most critical needs are.  Aggregation is '
        'optional in InaSAFE - if you do not use aggregation, the entire '
        'analysis area will be used for the data summaries. Typically '
        'aggregation layers in InaSAFE have the name of the district or '
        'reporting area as attributes. It is also possible to use extended '
        'attributes to indicate the ratio of men and women; youth, adults '
        'and elderly living in each area. Where these are provided and the '
        'exposure layer is population, InaSAFE will provide a demographic '
        'breakdown per aggregation area indicating how many men, women, etc. '
        'were probably affected in that area.'
    )))

    header = m.Heading(tr('The results area'), **INFO_STYLE)
    message.add(header)

    message.add(m.Paragraph(tr(
        'After running an analysis, the question area is hidden to maximise '
        'the amount of space allocated to the results area. You can '
        're-open the question area at any time by pressing the \'show '
        'question form\' button.')))

    message.add(m.Paragraph(tr(
        'The results area is used to display various useful feedback items to '
        'the user. Once an impact scenario has been run, a summary table will '
        'be shown.')))

    message.add(m.Paragraph(tr(
        'If you select an impact layer (i.e. a layer that was produced using '
        'an InaSAFE Impact Function), in the QGIS layers list, this summary '
        'will also be displayed in the results area. When you select a hazard '
        'or exposure layer in the QGIS layers list, the keywords for that '
        'layer will be shown in the results area, making it easy to '
        'understand what metadata exists for that layer.')))

    message.add(m.Paragraph(tr(
        'The results area is also used to display status information. For '
        'example, during the analysis process, the status area will display '
        'notes about each step in the analysis process. The \'Run\' '
        'button will be activated when both a valid hazard and valid exposure '
        'layer have been added in QGIS.'
    )))

    message.add(m.Paragraph(tr(
        'Finally, the results area is also used to display any error messages '
        'so that you can see what went wrong and why. You may need to '
        'scroll down to view the message completely to see all of the error '
        'message details.'
    )))

    message.add(m.Paragraph(tr(
        'After running the impact scenario calculation, the question is '
        'automatically hidden to make the results area as large as possible. '
        'If you want to see what the question used in the analysis was, click '
        'on the \'Show question form\' button at the top of the results area.'
    )))

    message.add(m.Paragraph(tr(
        'If you want to hide the question area again to have more space to '
        'display the results, click on the layer you just calculated '
        'with InaSAFE in the Layers list of QGIS to make it active.'
    )))

    header = m.Heading(tr('The buttons area'), **INFO_STYLE)
    message.add(header)

    message.add(m.Paragraph(tr(
        'The buttons area contains four buttons:')))
    bullets = m.BulletedList()
    bullets.add(m.Text(
        m.ImportantText(tr('Help')),
        tr(
            '- click on this if you need context help, such as the document '
            'you are reading right now!')))
    bullets.add(m.Text(
        m.ImportantText(tr('About')),
        tr(
            '- click on this to see short credits for the InaSAFE project.')))
    bullets.add(m.Text(
        m.ImportantText(tr('Print')),
        tr(
            '... - click on this if you wish to create a pdf of your '
            'impact scenario project or generate a report to open in '
            'composer for further tuning. An impact layer must be active '
            'before the \'Print\' button will be enabled.')))
    bullets.add(m.Text(
        m.ImportantText(tr('Run')),
        tr(
            '- this button is enabled when the combination of hazard and '
            'exposure selected in the questions area\'s drop down menus will '
            'allow you to run a scenario.')))
    message.add(bullets)

    header = m.Heading(tr('Data conversions'), **INFO_STYLE)
    message.add(header)

    message.add(m.Paragraph(tr(
        'When running a scenario, the data being used needs to be processed '
        'into a state where it is acceptable for use by InaSAFE. '
        'In particular it should be noted that:')))

    bullets = m.BulletedList()
    bullets.add(tr(
        'Remote datasets will be copied locally before processing.'))
    bullets.add(m.Text(
        tr(
            'All datasets will be clipped to the behaviours defined in the '
            'analysis extents dialog if you do not use an aggregation layer.'),
        m.Image(
            'file:///%s/img/icons/'
            'set-extents-tool.svg' % resources_path(),
            **SMALL_ICON_STYLE)
    ))
    bullets.add(m.Text(
        tr(
            'You can visualise the area that will be used for the analysis '
            'by enabling the "Toggle Scenario Outlines" tool. When this tool '
            'is enabled, a line (green by default) will be drawn around the '
            'outermost boundary of the analysis area.'),
        m.Image(
            'file:///%s/img/icons/'
            'toggle-rubber-bands.svg' % resources_path(),
            **SMALL_ICON_STYLE)
    ))
    bullets.add(m.Text(
        tr(
            'When you have selected an aggregation layer the analysis area '
            'will be the outline of the aggregation layer. If you select one '
            'or more polygons in the aggregation layer (by using the QGIS '
            'feature selection tools), the analysis boundary will be reduced '
            'to just the outline of these selected polygons. If the "Toggle '
            'Scenario Outlines" tool is enabled, the preview of the effective '
            'analysis area will be updated to reflect the selected features.'),
    ))
    bullets.add(tr(
        'All clipped datasets will be converted (reprojected) to the '
        'Coordinate Reference System of the exposure layer '
        'before analysis.'))
    message.add(bullets)

    header = m.Heading(tr('Generating impact reports'), **INFO_STYLE)
    message.add(header)

    message.add(m.Paragraph(tr(
        'When the impact analysis has completed you may want to generate a '
        'report. Usually the \'Print...\'  button will be enabled immediately '
        'after analysis. Selecting an InaSAFE impact layer in QGIS Layers '
        'panel will also enable it.'
    )))

    # This adds the help content of the print dialog
    message.add(report())
    return message
