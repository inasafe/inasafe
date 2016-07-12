__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'message.py'
__date__ = '7/12/16'
__copyright__ = 'imajimatika@gmail.com'

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles
from safe.common.signals import send_static_message
from safe.utilities.resources import resources_path

WARNING_STYLE = styles.WARNING_STYLE
SUGGESTION_STYLE = styles.SUGGESTION_STYLE
DETAILS_STYLE = styles.DETAILS_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE


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
    detail = tr(
        'The missing keyword is <i>%s</i> in your <b>%s</b> layer.' % (
            missing_keyword_exception.keyword,
            missing_keyword_exception.layer_name
        )
    )
    suggestion_heading = m.Heading(
        tr('Suggestion'), **DETAILS_STYLE)
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
