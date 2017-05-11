# coding=utf-8
"""Help text for options dialog."""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles
from safe.utilities.resources import resources_path

SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE
INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def options_help():
    """Help message for options dialog.

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
    message = m.Heading(tr('InaSAFE options help'), **SUBSECTION_STYLE)
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
            'inasafe-options-screenshot.png' % resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)
    message.add(m.Paragraph(tr(
        'The InaSAFE options dialog is used to control various aspects of '
        'the InaSAFE analysis and reporting environment. Here are brief '
        'descriptions of all the options available, grouped by the tab '
        'page on which they occur.'
    )))

    header = m.Heading(tr('Basic options tab'), **INFO_STYLE)
    message.add(header)

    message.add(m.Paragraph(tr(
        'The basic options tab provides several general settings:'
    )))

    bullets = m.BulletedList()
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Show organisation logo in InaSAFE dock')),
        tr(
            ' - When this option is enabled, a logo will be displayed at the '
            'bottom of the InaSAFE dock widget. By default the logo used '
            'is the InaSAFE supporters logo, but you can alter this by '
            'setting the \'Use custom organisation logo\' option in '
            'the template options tab (see below).')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Show only visible layers in the InaSAFE dock')),
        tr(
            ' - When this option is enabled layers that are not visible '
            'in the QGIS layers panel will not be shown in the hazard, '
            'exposure and aggregation combo boxes in the dock area.')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Set QGIS layer name from title in keywords')),
        tr(' - If this option is enabled, the InaSAFE keywords title '
           'attribute will be used for the layer name in the QGIS Layers list '
           'when adding a layer.')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Zoom to impact layer on scenario estimate completion')),
        tr(' - When this option is enabled, the map view extents will '
           'be updated to match the extents of the generated impact layer '
           'once the analysis completes.')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Hide exposure on scenario estimate completion')),
        tr(' - Use this option if you prefer to not show the exposure '
           'layer as an underlay behind the generated impact layer.')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Show only impact layer on report map')),
        tr('When this option is enabled, the map report created after an '
           'analysis completes will not show any other layers in your '
           'current project except for the impact layer. ')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Use selected features only with the aggregation layer')),
        tr('If enabled, running an analysis with some features of the '
           'aggregation layer selected will constrain the analysis to only '
           'those selected aggregation areas, all others will be ignored.')))
    bullets.add(m.Text(
        m.ImportantText(tr('Location for results')),
        tr(' - By default, InaSAFE will write impact layer and intermediate '
           'outputs to the system temporary directory. On some operating '
           'systems, these temporary files will be deleted on each reboot. '
           'If you wish to, you can specify an alternative directory '
           'to use for storing these temporary files.')))
    message.add(bullets)

    header = m.Heading(tr('Earthquake options tab'), **INFO_STYLE)
    message.add(header)
    paragraph = m.Paragraph(
        m.Image(
            'file:///%s/img/screenshots/'
            'inasafe-options-earthquake-screenshot.png' %
            resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'In this tab you can select which model to use when calculating '
        'earthquake fatalities and displacements. This option is global - '
        'it will affect all subsequent earthquake analyses carried out in '
        'InaSAFE.'
    ))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'When selecting an earthquake analysis model, its details will be '
        'shown below in the text box area.'
    ))
    message.add(paragraph)

    header = m.Heading(tr('Template options tab'), **INFO_STYLE)
    message.add(header)
    paragraph = m.Paragraph(
        m.Image(
            'file:///%s/img/screenshots/'
            'inasafe-options-template-options-screenshot.png' %
            resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)

    message.add(m.Paragraph(tr(
        'This tab has options relating to the printing of reports and the '
        'generation of map composer templates.'
    )))

    bullets = m.BulletedList()
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Use custom organisation logo')),
        tr(' - By default, InaSAFE will add the supporters logo to each '
           'map template. The supporters logo is also used at tbe bottom '
           'of the dock panel if the \'show organisation logo in dock\' '
           'option is enabled. You can use this option to replace the '
           'organisation logo with that of your own organisation. The logo '
           'will be rescaled automatically to fill the space provided.')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Use custom north arrow image')),
        tr(' - InaSAFE provides a basic north arrow which is placed on '
           'generated map compositions and rendered PDF reports. You can '
           'replace this north arrow with one of your own choosing using '
           'this option.')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Additional template directory')),
        tr(' - When generating a print report, InaSAFE will offer a number '
           'of pre-defined templates for you to use. For example there '
           'is an A4 variant, an A3 variant and so on. You can use this '
           'option to specify additional search directories to be used '
           'when presenting a list of available templates. This is useful '
           'in cases where you have created your own custom map templates '
           'and you wish to use them for report production.')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Use custom disclaimer text')),
        tr(' - By default, InaSAFE will display a disclaimer on reports '
           'advising readers of the report to exercise caution when '
           'interpreting the outputs presented. You can override this '
           'text using this option, though we do advise that you include '
           'a similar statement of caution in your overridden text.')))
    message.add(bullets)

    header = m.Heading(tr('ISO 19115 metadata tab'), **INFO_STYLE)
    message.add(header)
    paragraph = m.Paragraph(
        m.Image(
            'file:///%s/img/screenshots/'
            'inasafe-options-metadata-screenshot.png' %
            resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)

    message.add(m.Paragraph(tr(
        'This tab is used to define various options related to the '
        'automated generation of ISO 19115 metadata which is associated with '
        'hazard, exposure, aggregation and impact layers.'
    )))

    bullets = m.BulletedList()
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Organisation')),
        tr(' - Use this option to specify the name of your organisation.')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Contact email')),
        tr(' - Use this option to specify the contact person\'s email '
           'address to use in the generated metadata document.')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Website')),
        tr(' - Use this option to set the website address to be used in '
           'the generated metadata document.')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Analysis title')),
        tr(' - Use this to set the title value for the generated metadata '
           'document.')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Analysis license')),
        tr(' - Use this to set the usage and redistribution license for the '
           'generated impact layer.')))
    message.add(bullets)

    header = m.Heading(tr('Demographic Defaults tab'), **INFO_STYLE)
    message.add(header)
    paragraph = m.Paragraph(
        m.Image(
            'file:///%s/img/screenshots/'
            'inasafe-options-demographic-screenshot.png' %
            resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'In this tab you will find options for setting the default ratios '
        'for demographic groups. There is more detailed help on demographic '
        'groups within the main help page for InaSAFE in the Field Mapping '
        'Tool section. Essentially default ratios for demographic groups '
        'determine what proportion of the population are within a each '
        'population segment (e.g. infants versus children etc.). The options '
        'defined in this tab be used in cases where you choose to use the '
        'global default ratios while configuring the keywords for an '
        'aggregation layer as shown below.'
    ))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'Note that the contents of this tab may changed depending on what '
        'groups have been defined for demographic breakdowns.'
    ))
    message.add(paragraph)
    paragraph = m.Paragraph(
        m.Image(
            'file:///%s/img/screenshots/'
            'field-mapping-tool-default-ratios-screenshot.png' %
            resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)

    header = m.Heading(tr('Advanced tab'), **INFO_STYLE)
    message.add(header)
    paragraph = m.Paragraph(
        m.Image(
            'file:///%s/img/screenshots/'
            'inasafe-options-advanced-screenshot.png' %
            resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)

    message.add(m.Paragraph(tr(
        'This tab contains options intended for advanced users only.'
    )))

    bullets = m.BulletedList()
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Keyword cache for remote databases')),
        tr(' - When InaSAFE is used with remote layers (for example a '
           'database layer or a WFS layer), it is not possible to store the '
           'keywords for the layer with the layer itself. To accommodate for '
           'these types of layers, InaSAFE writes the keywords to a small '
           'file based database (using sqlite) and then retrieves them based '
           'on unique connection details used for that layer. You can '
           'specify a custom path to be used for storing the keywords '
           'database using this option.')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'Help to improve InaSAFE by submitting errors to a '
            'remote server')),
        tr(' - With this option enabled, InaSAFE will post any errors that '
           'occur to an online server for analysis by our development team. '
           'This option is disabled by default as some may consider some of '
           'the data submitted (IP Address, logged in user name) to be '
           'sensitive.')))
    bullets.add(m.Text(
        m.ImportantText(tr('Enable developer mode')),
        tr(' - When this option is enabled, right clicking on the webview '
           'widget in the dock will allow you to debug the generated HTML. '
           'In addition, if the metadata.txt for the running InaSAFE is '
           'set to \'alpha\', an additional icon will be added to the '
           'toolbar to add test layers to the QGIS project.'),
        m.Image(
            'file:///%s/img/icons/'
            'add-test-layers.svg' % resources_path(),
            **SMALL_ICON_STYLE)))
    message.add(bullets)

    return message
