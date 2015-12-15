# coding=utf-8
"""Help text for the dock widget."""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles
from safe.utilities.resources import resources_path
from safe.gui.tools.help.function_options_help import content as options
from safe.gui.tools.help.impact_report_help import content as report
INFO_STYLE = styles.INFO_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE

__author__ = 'ismailsunni'


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
    message = m.Heading(tr('InaSAFE dock help'), **INFO_STYLE)
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
        'This document describes the usage of the InaSAFE \'dock panel\''
        '- which is an interface for running hazard scenarios within the QGIS '
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

    header = m.Heading(tr('The questions area'), **INFO_STYLE)
    message.add(header)
    message.add(m.Paragraph(tr(
        'The intention of InaSAFE is to make it really simple and easy to '
        'perform your impact analysis. The question area provides a simple '
        'way for you to formulate what it is you want to find out? All '
        'questions are formulated in the form:'),
        m.EmphasizedText(tr(
            'In the event of a [hazard], how many [exposure] might be '
            'affected?'))))
    message.add(m.Paragraph(tr(
        'For example: "If there is a flood, how many buildings might be '
        'affected?"')))
    message.add(m.Paragraph(tr(
        'In order to answer such questions, the InaSAFE developers have '
        'built a number of Impact Functions that cover scenarios such as '
        'flood, tsunami, volcanic fall, earthquake and so on.')))
    message.add(m.Paragraph(tr(
        'The formulation of these questions if carried out by loading layers '
        'into QGIS that represent either hazard scenarios or exposure data. '
        'A hazard, for example, may be represented as, a raster layer in '
        'QGIS where each pixel in the raster represents the current flood '
        'depth following an inundation event. An exposure layer could be '
        'represented, for example, as vector polygon data representing '
        'building outlines, or a raster outline where each pixel represents '
        'the number of people thought to be resident in that cell.')))
    message.add(m.Paragraph(tr(
        'The impact function will combine these two input layers in a '
        'mathematical model in order to derive what the impacts of the '
        'hazard will be on the exposed infrastructure or people. By '
        'selecting a combination from the hazard and exposure combo boxes, '
        'an appropriate set of impact functions will be listed in the '
        'combo box. You may be wondering how the InaSAFE plugin determines '
        'whether a layer should be listed in the hazard or exposure combo '
        'boxes? The plugin relies on simple keyword metadata to be associated '
        'with each layer. You can define these keywords by selecting a layer '
        'and then clicking the InaSAFE Keywords Wizard icon on the toolbar: '),
        m.Image(
            'file:///%s/img/icons/'
            'show-keyword-wizard.svg' % resources_path(),
            **SMALL_ICON_STYLE),
        tr(
            'The wizard will guide you through the process of defining the '
            'keywords for that layer.')))
    message.add(m.Paragraph(tr(
        'Based on the combination of hazard and exposure layers that are '
        'selected, the Impact Function list (shown in the combo box under '
        '"Might" in the InaSAFE dock panel)  will be updated. Each impact '
        'function can only work with specific combinations of hazard and '
        'exposure types, so the options shown here will be limited '
        'accordingly. The chosen impact function can be configured (if '
        'applicable) by pressing the small ellipses (...) button next to '
        'the chosen impact function. This is explained in more detail below '
        'under the heading "Setting Analysis Parameters".')))
    message.add(m.Paragraph(tr(
        'Aggregation is the process whereby we group the analysis results '
        'by district so that you can see how many people, roads or '
        'buildings were affected in each area. This will help you to '
        'understand where the most critical needs are.  Aggregation is '
        'optional in InaSAFE - if you do not use aggregation, the entire '
        'analysis area will be used for the data summaries. Typically '
        'aggregation layers in InaSAFE have as attributes the name of the '
        'district or reporting area. It is also possible to use extended '
        'attributes to indicate the ratio of men and women; youth, adults '
        'and elderly living in each area. Where these are provided and the '
        'exposure layer is population, InaSAFE will provide a demographic '
        'breakdown per aggregation area indicating how many men, women etc. '
        'were probably affected in that area.'
    )))

    header = m.Heading(tr('The results area'), **INFO_STYLE)
    message.add(header)

    message.add(m.Paragraph(tr(
        'After running an analysis, the question area is hidden to maximise '
        'the amount of space allocated to the results area. You can '
        're-open the question area at any time by pressing the "show question '
        'form" button.')))

    message.add(m.Paragraph(tr(
        'The Results area is used to display various useful feedback items to '
        'the user. Once an impact scenario has been run, a summary table will '
        'be shown.')))

    message.add(m.Paragraph(tr(
        'If you select an impact layer (i.e. a layer that was produced using '
        'an InaSAFE impact function), in the QGIS layers list, this summary '
        'will also be displayed in the results area. When you select a hazard '
        'or exposure layer in the QGIS layers list, the keywords for that '
        'layer will be shown in the Results area, making it easy to '
        'understand what metadata exists for that layer.')))

    message.add(m.Paragraph(tr(
        'The Results area is also used to display status information. For '
        'example, when a suitable combination of hazard, exposure and impact '
        'function are selected, the results area will be updated to indicate '
        'that you can proceed to run the impact scenario calculation. The Run '
        'Button will be activated.'
    )))

    message.add(m.Paragraph(tr(
        'Finally, the Results area is also used to display any error messages '
        'so that the user is informed as to what went wrong and why. You '
        'might want to scroll down a bit in the messaging window to view the '
        'message completely.'
    )))

    message.add(m.Paragraph(tr(
        'To have more space for the results available your Question is '
        'automatically hidden to make the results area as large as possible '
        'to display the results. If you want to have a look again what the '
        'question was that you formulated click on the Show question form '
        'button on top of the result area.'
    )))

    message.add(m.Paragraph(tr(
        'If you want to hide the question area again to have more space to '
        'display the results again, just make the Layer you just calculated '
        'with InaSAFE active again in the Layers list of QGIS.'
    )))

    header = m.Heading(tr('The Buttons Area'), **INFO_STYLE)
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
            'impact scenario project or just generate a report and open it in '
            'composer for further tuning. An impact layer must be active '
            'before the Print button will be enabled.')))
    bullets.add(m.Text(
        m.ImportantText(tr('Run')),
        tr(
            '- if the combination of options in the Questions area\'s '
            'combo boxes will allow you to run a scenario, this button is '
            'enabled.')))
    message.add(bullets)

    header = m.Heading(tr('Data conversions'), **INFO_STYLE)
    message.add(header)

    message.add(m.Paragraph(tr(
        'When running a scenario, the data being used needs to be processed '
        'into a state where it is acceptable for use by the impact function. '
        'In particular it should be noted that:')))

    bullets = m.BulletedList()
    bullets.add(tr(
        'Remote datasets will be copied locally before processing.'))
    bullets.add(m.Text(
        tr(
            'All datasets will be clipped to the intersection of the hazard '
            'layer, exposure layer and the current view extents unless '
            'you have specified a different clipping behaviour in the '
            'extents selector dialog.'),
        m.Image(
            'file:///%s/img/icons/'
            'set-extents-tool.svg' % resources_path(),
            **SMALL_ICON_STYLE)
    ))
    bullets.add(tr(
        'All clipped datasets will be converted (reprojected) to Geographic '
        '(EPSG:4326) coordinate reference system before analysis.'))
    message.add(bullets)

    header = m.Heading(tr('Analysis parameters'), **INFO_STYLE)
    message.add(header)
    # this adds the help content from the IF options help dialog
    message.add(options())

    header = m.Heading(tr('Generating impact reports'), **INFO_STYLE)
    message.add(header)

    message.add(m.Paragraph(tr(
        'When the impact analysis has completed you may want to generate a '
        'report. Usually the "Print..."  button will be enabled immediately '
        'after analysis. Selecting an InaSAFE impact layer in QGIS Layers '
        'panel will also enable it.'
    )))

    # This adds the help content of the print dialog
    message.add(report())
    return message
