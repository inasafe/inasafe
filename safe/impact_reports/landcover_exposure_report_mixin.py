# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Land cover Exposure Report Mixin Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'Martin Dobias'

from safe.utilities.i18n import tr
from safe.common.utilities import format_decimal
from safe.impact_reports.report_mixin_base import ReportMixin
import safe.messaging as m


class LandcoverExposureReportMixin(ReportMixin):
    """Land cover specific report.

    .. versionadded:: 3.3
    """

    def __init__(self):
        """Building specific report mixin.

        .. versionadded:: 3.3
        """
        self.question = ''

    def generate_report(self):
        """Breakdown by building type.

        :returns: The report.
        :rtype: safe.messaging.Message
        """
        message = m.Message()
        message.add(m.Paragraph(self.question))
        message.add(self.impact_summary())
        return message

    def impact_summary(self):
        """The impact summary as per category.

        :returns: The impact summary.
        :rtype: safe.messaging.Message
        """

        total_affected_area = round(sum(self.imp_landcovers.values()), 1)
        total_area = round(sum(self.all_landcovers.values()), 1)

        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None
        row = m.Row()
        row.add(m.Cell(tr('Land Cover Type'), header=True))  # intentionally empty top left cell
        row.add(m.Cell(tr('Affected Area (ha)'), header=True))
        row.add(m.Cell(tr('Affected Area (%)'), header=True))
        row.add(m.Cell(tr('Total (ha)'), header=True))
        table.add(row)

        row = m.Row()
        row.add(m.Cell(tr('All')))
        row.add(m.Cell(format_decimal(0.1, total_affected_area), align='right'))
        row.add(m.Cell(format_decimal(1, round(total_affected_area / total_area * 100))+"%", align='right'))
        row.add(m.Cell(format_decimal(0.1, total_area), align='right'))
        table.add(row)

        row = m.Row()
        row.add(m.Cell(tr('Breakdown by land cover type'), header=True))
        row.add(m.Cell(tr('Affected Area (ha)'), header=True))
        row.add(m.Cell(tr('Affected Area (%)'), header=True))
        row.add(m.Cell(tr('Total (ha)'), header=True))
        table.add(row)

        for t, v in self.all_landcovers.iteritems():
            affected = self.imp_landcovers[t] if t in self.imp_landcovers else 0.
            affected_area = round(affected, 1)
            area = round(v, 1)
            percent_affected = affected_area / area * 100
            row = m.Row()
            row.add(m.Cell(t))
            row.add(m.Cell(format_decimal(0.1, affected_area), align='right'))
            row.add(m.Cell(format_decimal(1, percent_affected)+"%", align='right'))
            row.add(m.Cell(format_decimal(0.1, area), align='right'))
            table.add(row)

        message.add(table)
        return message
