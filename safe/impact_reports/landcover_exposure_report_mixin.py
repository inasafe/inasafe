# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Land Cover Exposure Report Mixin Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'Ismail Sunni <ismail@kartoza.com>'

from collections import OrderedDict
from operator import add
from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.impact_reports.report_mixin_base import ReportMixin
import safe.messaging as m
from safe.messaging import styles


class LandCoverExposureReportMixin(ReportMixin):
    """Land Cover specific report.

    .. versionadded:: 3.2
    """

    def __init__(self):
        """Land cover specific report mixin.

        .. versionadded:: 3.2

        """
        self.question = ''
        self.total_affected_area = 0
        self.total_area = 0
        self.all_landcovers = {}
        self.imp_landcovers = {}

    def generate_report(self):
        """Breakdown by building type.

        :returns: The report.
        :rtype: safe.messaging.Message
        """
        message = m.Message()
        message.add(m.Paragraph(self.question))
        message.add(self.impact_summary())
        message.add(self.action_checklist())
        message.add(self.notes())
        return message

    def action_checklist(self):
        """Breakdown by building type.

        :returns: The buildings breakdown report.
        :rtype: safe.messaging.Message
        """

        message = m.Message(style_class='container')
        message.add(m.Heading(tr('Action checklist'), **styles.INFO_STYLE))

        return message

    def impact_summary(self):
        """The impact summary as per category.

        :returns: The impact summary.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None

        row = m.Row()
        row.add(m.Cell(tr('Land Cover Type'), header=True))
        row.add(m.Cell(tr('Affected Area (ha)'), header=True))
        row.add(m.Cell(tr('Affected Area (%)'), header=True))
        row.add(m.Cell(tr('Total (ha)'), header=True))
        table.add(row)

        row = m.Row()
        row.add(m.Cell(tr('All')))
        row.add(m.Cell(self.total_affected_area))
        row.add(m.Cell(
            "%.0f%%" % (self.total_affected_area / self.total_area * 100)))
        row.add(m.Cell(self.total_area))
        table.add(row)

        row = m.Row()
        row.add(m.Cell(tr('Total (ha)'), header=True))
        row.add(m.Cell('', header=True))
        row.add(m.Cell('', header=True))
        row.add(m.Cell('', header=True))
        table.add(row)

        for t, v in self.all_landcovers.iteritems():
            affected = (
                self.imp_landcovers[t] if t in self.imp_landcovers else 0.)
            affected_area = round(affected, 1)
            area = round(v, 1)
            percent_affected = affected_area / area * 100

            row = m.Row()
            row.add(m.Cell(t))
            row.add(m.Cell(affected_area))
            row.add(m.Cell("%.0f%%" % percent_affected))
            row.add(m.Cell(area))
            table.add(row)

        message.add(table)
        return message