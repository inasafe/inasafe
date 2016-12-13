# coding=utf-8

import logging

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles
from safe.common.signals import send_static_message
from safe.utilities.resources import resources_path
from safe.defaults import limitations, disclaimer

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

INFO_STYLE = styles.INFO_STYLE
PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
KEYWORD_STYLE = styles.KEYWORD_STYLE
WARNING_STYLE = styles.WARNING_STYLE
SUGGESTION_STYLE = styles.SUGGESTION_STYLE
DETAILS_STYLE = styles.DETAILS_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE
LOGO_ELEMENT = m.Brand()

LOGGER = logging.getLogger('InaSAFE')


def missing_keyword_message(sender, missing_keyword_exception):
    """Display an error when there is missing keyword.

    :param sender: The sender.
    :type sender: object

    :param missing_keyword_exception: A KeywordNotFoundError exception.
    :type missing_keyword_exception: KeywordNotFoundError

    """
    warning_heading = m.Heading(
        tr('Missing Keyword'), **WARNING_STYLE)
    warning_message = tr(
        'There is missing keyword that needed for this analysis.')
    detail_heading = m.Heading(
        tr('Detail'), **DETAILS_STYLE)
    suggestion_heading = m.Heading(
        tr('Suggestion'), **DETAILS_STYLE)
    detail = tr(
        'The layer <b>%s</b> is missing the keyword <i>%s</i>.' % (
            missing_keyword_exception.layer_name,
            missing_keyword_exception.keyword
        )
    )
    suggestion = m.Paragraph(
            tr('Please use the keyword wizard to update the keywords. You '
               'can open the wizard by clicking on the '),
            m.Image(
                'file:///%s/img/icons/'
                'show-keyword-wizard.svg' % resources_path(),
                **SMALL_ICON_STYLE),
            tr(
                ' icon in the toolbar.'))

    message = m.Message()
    message.add(warning_heading)
    message.add(warning_message)
    message.add(detail_heading)
    message.add(detail)
    message.add(suggestion_heading)
    message.add(suggestion)
    send_static_message(sender, message)


def getting_started_message():
    """Generate a message for initial application state.

    :returns: Information for the user on how to get started.
    :rtype: safe.messaging.Message
    """
    message = m.Message()
    message.add(LOGO_ELEMENT)
    message.add(m.Heading(tr('Getting started'), **INFO_STYLE))
    notes = m.Paragraph(
        tr(
            'These are the minimum steps you need to follow in order '
            'to use InaSAFE:'))
    message.add(notes)
    basics_list = m.NumberedList()
    basics_list.add(m.Paragraph(
        tr('Add at least one '),
        m.ImportantText(tr('hazard'), **KEYWORD_STYLE),
        tr(' layer (e.g. earthquake MMI) to QGIS.')))
    basics_list.add(m.Paragraph(
        tr('Add at least one '),
        m.ImportantText(tr('exposure'), **KEYWORD_STYLE),
        tr(' layer (e.g. structures) to QGIS.')))
    basics_list.add(m.Paragraph(
        tr(
            'Make sure you have defined keywords for your hazard and '
            'exposure layers. You can do this using the '
            'keywords creation wizard '),
        m.Image(
            'file:///%s/img/icons/show-keyword-wizard.svg' %
            (resources_path()), **SMALL_ICON_STYLE),
        tr(' in the toolbar.')))
    basics_list.add(m.Paragraph(
        tr('Click on the '),
        m.ImportantText(tr('Run'), **KEYWORD_STYLE),
        tr(' button below.')))
    message.add(basics_list)

    message.add(m.Heading(tr('Limitations'), **WARNING_STYLE))
    caveat_list = m.NumberedList()
    for limitation in limitations():
        caveat_list.add(limitation)
    message.add(caveat_list)

    message.add(m.Heading(tr('Disclaimer'), **WARNING_STYLE))
    message.add(m.Paragraph(disclaimer()))

    return message


def no_overlap_message():
    """Helper which returns a message indicating no valid overlap."""
    return tr(
        'Currently there are no overlapping extents between '
        'the hazard layer, the exposure layer and the user '
        'defined analysis area. Try zooming to the analysis '
        'area, clearing the analysis area or defining a new '
        'one using the analysis area definition tool.')


def ready_message():
    """Helper to create a message indicating inasafe is ready.

    :returns Message: A localised message indicating we are ready to run.
    """
    title = m.Heading(tr('Ready'), **PROGRESS_UPDATE_STYLE)
    notes = m.Paragraph(
        tr('You can now proceed to run your analysis by clicking the '),
        m.EmphasizedText(tr('Run'), **KEYWORD_STYLE),
        tr('button.'))
    message = m.Message(LOGO_ELEMENT, title, notes)
    return message


def show_keyword_version_message(sender, keyword_version, inasafe_version):
    """Show a message indicating that the keywords version is mismatch

    .. versionadded: 3.2

    :param keyword_version: The version of the layer's keywords
    :type keyword_version: str

    :param inasafe_version: The version of the InaSAFE
    :type inasafe_version: str

    .. note:: The print button will be disabled if this method is called.
    """
    LOGGER.debug('Showing Mismatch Version Message')
    report = m.Message()
    report.add(LOGO_ELEMENT)
    report.add(m.Heading(tr(
        'Layer Keyword\'s Version Mismatch:'), **WARNING_STYLE))
    context = m.Paragraph(
        tr(
            'Your layer\'s keyword\'s version (%s) does not match with '
            'your InaSAFE version (%s). If you wish to use it as an '
            'exposure, hazard, or aggregation layer in an analysis, '
            'please use the keyword wizard to update the keywords. You '
            'can open the wizard by clicking on the ' % (
                keyword_version, inasafe_version)),
        m.Image(
            'file:///%s/img/icons/'
            'show-keyword-wizard.svg' % resources_path(),
            **SMALL_ICON_STYLE),
        tr(
            ' icon in the toolbar.'))
    report.add(context)
    send_static_message(sender, report)


# Fixme, this code is not called.
def show_keywords_need_review_message(sender, message=None):
    """Show a message keywords are not adequate to run an analysis.

    .. versionadded: 4.0

    :param message: Additional message to display.
    :type message: str

    .. note:: The print button will be disabled if this method is called.
    """
    LOGGER.debug('Showing incorrect keywords for v4 message')
    report = m.Message()
    report.add(LOGO_ELEMENT)
    report.add(m.Heading(tr(
        'Layer Keywords Outdated:'), **WARNING_STYLE))
    context = m.Paragraph(
        tr(
            'Please update the keywords for your layers and then '
            'try to run the analysis again. Use the keyword wizard '),
        m.Image(
            'file:///%s/img/icons/'
            'show-keyword-wizard.svg' % resources_path(),
            **SMALL_ICON_STYLE),
        tr(
            ' icon in the toolbar to update your layer\'s keywords.'),
        message)
    report.add(context)
    send_static_message(sender, report)


def show_no_keywords_message(sender):
    """Show a message indicating that no keywords are defined.

    .. note:: The print button will be disabled if this method is called.
    """
    LOGGER.debug('Showing No Keywords Message')
    report = m.Message()
    report.add(LOGO_ELEMENT)
    report.add(m.Heading(tr(
        'Layer keywords missing:'), **WARNING_STYLE))
    context = m.Paragraph(
        tr(
            'No keywords have been defined for this layer yet or there is '
            'an issue with the currently defined keywords and they need '
            'to be reviewed. If you wish to use this layer as an '
            'exposure, hazard, or aggregation layer in an analysis, '
            'please use the keyword wizard to update the keywords. You '
            'can open the wizard by clicking on the '),
        m.Image(
            'file:///%s/img/icons/'
            'show-keyword-wizard.svg' % resources_path(),
            **SMALL_ICON_STYLE),
        tr(
            ' icon in the toolbar.'))
    report.add(context)
    send_static_message(sender, report)
