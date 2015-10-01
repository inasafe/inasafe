# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Building Exposure Report Mixin Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'Christian Christelis <christian@kartoza.com>'

from safe.utilities.i18n import tr
from safe.common.utilities import format_int
import safe.messaging as m
from safe.impact_reports.report_mixin_base import ReportMixin


class RoadExposureReportMixin(ReportMixin):
    """Building specific report.

    .. versionadded:: 3.2
    """

    def __init__(self):
        """Road specific report mixin.

        .. versionadded:: 3.2
        """
        self.question = ''
        self.road_lengths = {}
        self.affected_road_lengths = {}
        self.affected_road_categories = []

    def generate_report(self):
        """Breakdown by road type.

        :returns: The report.
        :rtype: safe.message.Message
        """
        message = m.Message()
        message.add(m.Paragraph(self.question))
        message.add(self.impact_summary())
        message.add(self.roads_breakdown())
        message.add(self.action_checklist())
        message.add(self.notes())
        return message

    def impact_summary(self):
        """The impact summary as per category

        :returns: The impact summary.
        :rtype: safe.message.Message
        """
        affected_categories = self.affected_road_categories

        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None
        row = m.Row()
        row.add(m.Cell(tr('Road Type'), header=True))
        row.add(m.Cell(affected_categories, header=True))
        row.add(m.Cell(tr('Total (m)'), header=True))
        table.add(row)

        total_affected = [0] * len(affected_categories)
        for (category, road_breakdown) in self.affected_road_lengths.items():
            number_affected = sum(road_breakdown.values())
            count = affected_categories.index(category)
            total_affected[count] = format_int(int(number_affected))

        row = m.Row()
        row.add(m.Cell(tr('All')))
        row.add(m.Cell(total_affected))
        row.add(m.Cell(format_int(int(self.total_road_length))))
        table.add(row)

        message.add(table)

        return message

    def roads_breakdown(self):
        """Breakdown by road type.

        :returns: The roads breakdown report.
        :rtype: list
        """
        category_names = self.affected_road_categories

        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None

        row = m.Row()
        row.add(m.Cell(tr('Breakdown by road type'), header=True))
        table.add(row)

        for road_type in self.road_lengths:
            affected_by_usage = []
            for category in category_names:
                if road_type in self.affected_road_lengths[category]:
                    affected_by_usage.append(
                        self.affected_road_lengths[category][
                            road_type])
                else:
                    affected_by_usage.append(0)
            row = m.Row()
            row.add(m.Cell(road_type.capitalize()))
            row.add(m.Cell(format_int(int(x)) for x in affected_by_usage))
            row.add(m.Cell(format_int(int(self.road_lengths[road_type]))))
            table.add(row)

        message.add(table)

        return message

    @property
    def total_road_length(self):
        """The total road length.

        :returns: The total road length.
        :rtype: float
        """
        return sum(self.road_lengths.values())
