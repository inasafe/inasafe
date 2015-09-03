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
        :rtype: list
        """
        report = [{'content': self.question}]
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.impact_summary()
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.roads_breakdown()
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.action_checklist()
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.notes()
        return report

    def impact_summary(self):
        """The impact summary as per category

        :returns: The impact summary.
        :rtype: list
        """
        affected_categories = self.affected_road_categories
        impact_summary_report = [
            {
                'content':
                    [tr('Road Type')] +
                    affected_categories +
                    [tr('Total (m)')],
                'header': True
            }]
        total_affected = [0] * len(affected_categories)
        for (category, road_breakdown) in self.affected_road_lengths.items():
            number_affected = sum(road_breakdown.values())
            count = affected_categories.index(category)
            total_affected[count] = format_int(int(number_affected))
        impact_summary_report.append(
            {
                'content':
                    [tr('All')] +
                    total_affected +
                    [format_int(int(self.total_road_length))]
            })
        return impact_summary_report

    def roads_breakdown(self):
        """Breakdown by road type.

        :returns: The roads breakdown report.
        :rtype: list
        """
        category_names = self.affected_road_categories
        roads_breakdown_report = [(
            {
                'content': (tr('Breakdown by road type')),
                'header': True
            })]
        for road_type in self.road_lengths:
            affected_by_usage = []
            for category in category_names:
                if road_type in self.affected_road_lengths[category]:
                    affected_by_usage.append(
                        self.affected_road_lengths[category][
                            road_type])
                else:
                    affected_by_usage.append(0)
            road_detail = (
                # building type
                [road_type.capitalize()] +
                # categories
                [format_int(int(x)) for x in affected_by_usage] +
                # total
                [format_int(int(self.road_lengths[road_type]))])
            roads_breakdown_report.append(
                {
                    'content': road_detail
                })

        return roads_breakdown_report

    @property
    def total_road_length(self):
        """The total road length.

        :returns: The total road length.
        :rtype: float
        """
        return sum(self.road_lengths.values())
