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

from safe.utilities.i18n import tr


class ReportMixin(object):
    """Report Mixin Interface.

    .. versionadded:: 3.1
    """
    def __init__(self):
        super(ReportMixin, self).__init__()
        self.exposure_report = None
        self.question_report = None

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: dict
        """
        return {
            'title': tr('Notes'),
            'fields': []
        }

    def action_checklist(self):
        """Return the action check list section of the report.

        :return: The action check list as dict.
        :rtype: dict
        """
        return {
            'title': tr('Action checklist'),
            'fields': []
        }

    def impact_summary(self):
        """Create impact summary as data."""
        raise NotImplementedError

    def generate_data(self):
        """Create a dictionary contains impact data.

        :returns: The impact report data.
        :rtype: dict
        """
        return {
            'exposure': self.exposure_report,
            'question': self.question_report,
            'impact summary': self.impact_summary(),
            'action check list': self.action_checklist(),
            'notes': self.notes()
        }
