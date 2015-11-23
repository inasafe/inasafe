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

    def action_checklist(self):
        """The actions to be taken in for the impact on this exposure type.

        :returns: The action checklist.
        :rtype: safe.messaging.Message
        """
        return m.Message()

    def impact_summary(self):
        """The impact summary.

        :returns: The action checklist.
        :rtype: safe.messaging.Message
        """
        return m.Message()

    def notes(self):
        """Additional notes to be used.

        :return: The notes to be added to this report
        :rtype: safe.messaging.Message

        ..Notes:
        Notes are very much specific to IFs so it is expected that this method
        is overwritten in the IF if needed.
        """
        return m.Message()
