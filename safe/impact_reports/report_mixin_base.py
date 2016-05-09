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
