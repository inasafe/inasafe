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
from safe.messaging import styles


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
        row.add(m.Cell(tr('Breakdown by road type'), header=True))
        row.add(m.Cell('', header=True))  # intentionally empty top left cell
        row.add(m.Cell('', header=True))  # intentionally empty top left cell
        table.add(row)

        row = m.Row()
        row.add(m.Cell(tr('Road Type'), header=True))
        for affected_category in affected_categories:
            row.add(m.Cell(affected_category, header=True, align='right'))
        row.add(m.Cell(tr('Total (m)'), header=True, align='right'))
        table.add(row)

        total_affected = [0] * len(affected_categories)
        for (category, road_breakdown) in self.affected_road_lengths.items():
            number_affected = sum(road_breakdown.values())
            count = affected_categories.index(category)
            total_affected[count] = format_int(int(number_affected))

        row = m.Row()
        row.add(m.Cell(tr('All')))
        for total_affected_value in total_affected:
            row.add(m.Cell(total_affected_value, align='right'))
        row.add(m.Cell(format_int(int(self.total_road_length)), align='right'))
        table.add(row)

        message.add(table)

        return message

    def roads_breakdown(self):
        """Breakdown by road type.

        :returns: The roads breakdown report.
        :rtype: safe.message.Message
        """
        category_names = self.affected_road_categories
        affected_categories = self.affected_road_categories

        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None

        row = m.Row()
        row.add(m.Cell(tr('Breakdown by road type'), header=True))
        row.add(m.Cell('', header=True))  # intentionally empty top left cell
        row.add(m.Cell('', header=True))  # intentionally empty top left cell
        table.add(row)

        row = m.Row()
        row.add(m.Cell(tr('Road Type'), header=True))
        for affected_category in affected_categories:
            row.add(m.Cell(affected_category, header=True, align='right'))
        row.add(m.Cell(tr('Total (m)'), header=True, align='right'))
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
            for affected_by_usage_value in affected_by_usage:
                row.add(m.Cell(
                    format_int(int(affected_by_usage_value)), align='right'))
            row.add(m.Cell(
                format_int(int(self.road_lengths[road_type])), align='right'))
            table.add(row)

        # adding total (copied from impact summary
        total_affected = [0] * len(affected_categories)
        for (category, road_breakdown) in self.affected_road_lengths.items():
            number_affected = sum(road_breakdown.values())
            count = affected_categories.index(category)
            total_affected[count] = format_int(int(number_affected))

        row = m.Row()
        row.add(m.Cell(tr('Total'), header=True))
        for total_affected_value in total_affected:
            row.add(m.Cell(total_affected_value, align='right', header=True))
        row.add(m.Cell(
            format_int(int(self.total_road_length)),
            align='right',
            header=True))
        table.add(row)

        message.add(table)

        return message

    def action_checklist(self):
        """Action checklist for the itb earthquake fatality report.

        .. versionadded:: 3.2.1

        :returns: The action checklist
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        message.add(m.Heading(tr('Action checklist'), **styles.INFO_STYLE))
        checklist = m.BulletedList()
        checklist.add(tr(
            'Try to Identify which potential roads that able to '
            'access for evacuation and logistic distribution purpose. '
            'What type of transportation reliable to use in that order?'))
        checklist.add(tr(
            'Identify what equipment needed to open access of '
            'affected roads. Where the resources or equipment to open '
            'access affected roads located? who/what department '
            'responsible to mobilize?'))
        checklist.add(tr(
            'Which roads can be used to evacuate people or to '
            'distribute logistics?'))
        checklist.add(tr(
            'What type of vehicles can use the unaffected roads?'))
        checklist.add(tr(
            'What sort of equipment will be needed to reopen roads & '
            'where will we get it?'))
        checklist.add(tr(
            'Which government department is responsible for supplying '
            'equipment ?'))
        message.add(checklist)
        return message

    @property
    def total_road_length(self):
        """The total road length.

        :returns: The total road length.
        :rtype: float
        """
        return sum(self.road_lengths.values())
