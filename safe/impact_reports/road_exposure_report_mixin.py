# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Road Exposure Report Mixin Class**

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
        self.add_unaffected_column = True

    def generate_report(self):
        """Breakdown by road type.

        :returns: The report.
        :rtype: safe.message.Message
        """
        message = m.Message()
        message.add(m.Paragraph(self.question))
        message.add(self.format_impact_summary())
        message.add(self.format_roads_breakdown())
        message.add(self.format_action_checklist())
        message.add(self.format_notes())
        return message

    def generate_data(self):
        """Create a dictionary contains impact data.

        :returns: The impact report data.
        :rtype: dict
        """
        question = self.question
        impact_summary = self.impact_summary()
        impact_table = self.roads_breakdown()
        action_checklist = self.action_checklist()
        notes = self.notes()

        return {
            'exposure': 'road',
            'question': question,
            'impact summary': impact_summary,
            'impact table': impact_table,
            'action check list': action_checklist,
            'notes': notes
        }

    def impact_summary(self):
        """Create impact summary as data.

        :returns: Impact Summary in dictionary format.
        :rtype: dict
        """
        attributes = []
        fields = []

        for affected_category in self.affected_road_categories:
            attributes.append(affected_category)
        attributes.append('Unaffected')
        attributes.append('Total')

        all_field = [0] * len(self.affected_road_lengths)
        for (category, road_breakdown) in self.affected_road_lengths.items():
            number_affected = sum(road_breakdown.values())
            count = self.affected_road_categories.index(category)
            all_field[count] = number_affected
        all_field.append(self.total_road_length - sum(all_field))
        all_field.append(self.total_road_length)

        fields.append(all_field)

        return {
            'attributes': attributes,
            'fields': fields
        }

    def format_impact_summary(self):
        """The impact summary as per category

        :returns: The impact summary.
        :rtype: safe.message.Message
        """
        impact_summary = self.impact_summary()
        attributes = impact_summary['attributes']
        fields = impact_summary['fields']

        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None

        row = m.Row()
        row.add(m.Cell(tr('Summary by road type'), header=True))
        for _ in attributes:
            row.add(m.Cell('', header=True))

        row = m.Row()
        row.add(m.Cell(tr('Road Type'), header=True))
        for affected_category in attributes:
            row.add(m.Cell(tr(affected_category), header=True, align='right'))
        table.add(row)

        row = m.Row()
        row.add(m.Cell(tr('All (m)')))
        for total_affected_value in fields[0]:
            row.add(m.Cell(
                format_int(int(total_affected_value)), align='right'))

        table.add(row)

        message.add(table)

        return message

    def roads_breakdown(self):
        """Create road breakdown as data.

        :returns: Road Breakdown in dictionary format.
        :rtype: dict
        """
        attributes = ['Road Type']
        fields = []

        for affected_category in self.affected_road_categories:
            attributes.append(affected_category)
        attributes.append('Unaffected')
        attributes.append('Total')

        for road_type in self.road_lengths:
            affected_by_usage = []
            for category in self.affected_road_categories:
                if road_type in self.affected_road_lengths[category]:
                    affected_by_usage.append(
                        self.affected_road_lengths[category][
                            road_type])
                else:
                    affected_by_usage.append(0)
            row = []

            row.append(road_type)
            for affected_by_usage_value in affected_by_usage:
                row.append(affected_by_usage_value)

            # Unaffected
            row.append(self.road_lengths[road_type] - sum(affected_by_usage))

            # Total for the road type
            row.append(self.road_lengths[road_type])

            fields.append(row)

        return {
            'attributes': attributes,
            'fields': fields
        }

    def format_roads_breakdown(self):
        """Breakdown by road type.

        :returns: The roads breakdown report.
        :rtype: safe.message.Message
        """

        road_breakdown = self.roads_breakdown()
        attributes = road_breakdown['attributes']
        fields = road_breakdown['fields']

        category_names = self.affected_road_categories
        affected_categories = self.affected_road_categories

        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None

        row = m.Row()
        row.add(m.Cell(tr('Breakdown by road type'), header=True))
        for _ in affected_categories:
            # Add empty cell as many as affected_categories
            row.add(m.Cell('', header=True))

        if self.add_unaffected_column:
            # Add empty cell for un-affected road
            row.add(m.Cell('', header=True))

        # Add empty cell for total column
        row.add(m.Cell('', header=True))
        table.add(row)

        row = m.Row()
        for attribute in attributes:
            row.add(m.Cell(tr(attribute), header=True))
        table.add(row)

        for field in fields:
            row = m.Row()
            # First column
            row.add(m.Cell(tr('%(road_type)s (m)' % {
                'road_type': field[0].capitalize()})))
            # Start from second column
            for value in field[1:]:
                row.add(m.Cell(
                    format_int(int(value)), align='right'))
            table.add(row)

        impact_summary_fields = self.impact_summary()['fields']

        row = m.Row()
        row.add(m.Cell(tr('Total (m)'), header=True))
        for field in impact_summary_fields:
            for value in field[1:]:
                row.add(m.Cell(
                    format_int(int(value)),
                    align='right',
                    header=True))

        table.add(row)

        message.add(table)

        return message

    def action_checklist(self):
        """Return the action check list section of the report.

        :return: The action check list as dict.
        :rtype: dict
        """
        title = tr('Action checklist')
        fields = [
            tr('Which roads can be used to evacuate people or to distribute '
               'logistics?'),
            tr('What type of vehicles can use the unaffected roads?'),
            tr('What sort of equipment will be needed to reopen roads & where '
               'will we get it?'),
            tr('Which government department is responsible for supplying '
               'equipment ?')
        ]

        return {
            'title': title,
            'fields': fields
        }

    @property
    def total_road_length(self):
        """The total road length.

        :returns: The total road length.
        :rtype: float
        """
        return sum(self.road_lengths.values())
