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
from safe.utilities.i18n import tr

__author__ = 'Christian Christelis <christian@kartoza.com>'


class ReportMixin(object):
    """Report Mixin Interface.

    .. versionadded:: 3.1
    """
    def __init__(self):
        super(ReportMixin, self).__init__()
        self.exposure_report = None

    def notes(self):
        """Return the notes section of the report.

        Sub classes should implement this.

        :return: The notes that should be attached to this impact report.
        :rtype: dict
        """
        return []

    def action_checklist(self):
        """Return the action checklist section of the report.

        .. note:: This is also implemented in the ImpactFunction base class
            - I think its a bit ugly to have it here too ... TS

        Sub classes should implement this.

        :return: The actions that should be attached to this impact report.
        :rtype: dict
        """
        return []

    def extra_actions(self):
        """Provide exposure specific actions.

        .. note:: Only calculated actions are implemented here, the rest
            are defined in definitions.

        .. versionadded:: 3.5

        Sub classes should implement this.

        :return: The action check list as list.
        :rtype: list
        """
        return []

    def impact_summary(self):
        """Create impact summary as data."""
        raise NotImplementedError

    def generate_data(self):
        """Create a dictionary contains impact data.

        :returns: The impact report data.
        :rtype: dict
        """
        actions = {
            'title': tr('Action checklist'),
            'fields': self.action_checklist()
        }
        notes = {
            'title': tr('Notes and assumptions'),
            'fields': self.notes()
        }
        return {
            'exposure': self.exposure_report,
            'question': self.question,  # The question is defined in the IF.
            'impact summary': self.impact_summary(),
            'action check list': actions,
            'notes': notes
        }
