# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Special Message Sender.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""
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
    suggestion_heading = m.Heading(
        tr('Suggestion'), **DETAILS_STYLE)
    detail = tr(
        'The layer <b>%s</b> is missing the keyword <i>%s</i>.'
         % (
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
