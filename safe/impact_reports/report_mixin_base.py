# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Function Report Mixin Base Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'Christian Christelis <christian@kartoza.com>'

import safe.messaging as m
from safe.messaging import styles


class ReportMixin(object):
    """Report Mixin Interface.

    .. versionadded:: 3.1
    """

    def html_report(self):
        """Generate an HTML report.

        :returns: The report in html format.
        :rtype: basestring
        """
        return self.generate_report().to_html(suppress_newlines=True)

    def generate_report(self):
        """Defining the interface.

        :returns: An itemized breakdown of the report.
        :rtype: safe.messaging.Message
        """
        return m.Message()

    def format_impact_summary(self):
        """The impact summary.

        :returns: The action checklist.
        :rtype: safe.messaging.Message
        """
        return m.Message()

    def format_action_checklist(self):
        """Breakdown by building type.

        :returns: The buildings breakdown report.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        message.add(m.Heading(
            self.action_checklist()['title'], **styles.INFO_STYLE))
        checklist = m.BulletedList()
        for text in self.action_checklist()['fields']:
            checklist.add(text)
        message.add(checklist)
        return message

    def format_notes(self):
        """Format notes to be shown to the user.

        :returns: Message object that will be rendered.
        :rtype: safe.messaging.Message
        """
        notes = self.notes()

        message = m.Message(style_class='container')
        message.add(
            m.Heading(notes['title'], **styles.INFO_STYLE))
        checklist = m.BulletedList()

        for field in notes['fields']:
            checklist.add(field)

        message.add(checklist)
        return message

    def notes(self):
        """
        """
        return {
            'title': '',
            'fields': []
        }
