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

from collections import OrderedDict
from operator import add
from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.impact_reports.report_mixin_base import ReportMixin
import safe.messaging as m
from safe.messaging import styles


class BuildingExposureReportMixin(ReportMixin):
    """Building specific report.

    .. versionadded:: 3.1
    """

    def __init__(self):
        """Building specific report mixin.

        .. versionadded:: 3.1

        ..Notes:
        Expect affected buildings and buildings to be given as following:
            affected_buildings = OrderedDict([
                (category, {building_type: amount}),
            e.g.
                (inundated, {
                    residential: OrderedDict([
                        (Buildings Affected, 1000),
                        (value, ...
                    ]),
                    school: OrderedDict([
                        (Buildings Affected, 0),
                        (value, ...
                    },
                    ...
                }),
                (wet, {
                    residential: OrderedDict([
                        (Buildings Affected, 12),
                        (value, ...
                    },
                    school: OrderedDict([
                        (Buildings Affected, 2),
                        (value, ...
                    }...
                }),
                (dry, {
                    residential: OrderedDict([
                        (Buildings Affected, 1),
                        (value, ...
                    },
                    school: {
                        (Buildings Affected, 5),
                        (value, ...
                    }...
                }),
            ])

            buildings = {residential: 1062, school: 52 ...}
        """
        self.question = ''
        self.buildings = {}
        self.affected_buildings = {}
        self.building_report_threshold = 25

        self.impact_data = {}

    def impact_summary(self):
        """Create impact summary as data.

        :returns: Impact Summary in dictionary format.
        :rtype: dict
        """
        affect_types = self._impact_breakdown
        attributes = ['category', 'value']
        fields = []
        for (category, building_breakdown) in self.affected_buildings.items():
            total_affected = [0] * len(affect_types)
            for affected_breakdown in building_breakdown.values():
                for affect_type, number_affected in affected_breakdown.items():
                    count = affect_types.index(affect_type)
                    total_affected[count] += number_affected
            field = [tr(category)]
            for affected in total_affected:
                field.append(affected)
            fields.append(field)

        if len(self._affected_categories) > 1:
            fields.append(
                [tr('Affected buildings'), self.total_affected_buildings])

        if self._affected_categories == self.affected_buildings.keys():
            fields.append(
                [tr('Not affected buildings'), self.total_unaffected_buildings])

        fields.append([tr('Total'), self.total_buildings])

        return {
            'attributes': attributes,
            'fields': fields
        }

    def buildings_breakdown(self):
        """Create building breakdown as data.

        :returns: Building Breakdown in dictionary format.
        :rtype: dict
        """
        impact_names = self.affected_buildings.keys()  # e.g. flooded, wet, dry
        attributes = ['Building type']
        for name in impact_names:
            attributes.append(tr(name))
        # Only show not affected building row if the IF does not use custom
        # affected categories
        if self._affected_categories == self.affected_buildings.keys():
            attributes.append(tr('Not Affected'))
        attributes.append(tr('Total'))

        fields = []

        # Let's sort alphabetically first
        building_types = [building_type for building_type in self.buildings]
        building_types.sort()
        impact_totals = []  # Used to store the total for each impact name
        # Initialise totals with zeros
        for _ in impact_names:
            impact_totals.append(0)
        # Only show not affected building row if the IF does not use custom
        # affected categories
        if self._affected_categories == self.affected_buildings.keys():
            # And one extra total for the unaffected column
            impact_totals.append(0)
        # And one extra total for the cumulative total column
        impact_totals.append(0)
        # Now build the main table
        for building_type in building_types:
            row = []
            building_type_name = building_type.replace('_', ' ')
            impact_subtotals = []
            for name in impact_names:
                if building_type in self.affected_buildings[name]:
                    impact_subtotals.append(
                        self.affected_buildings[name][
                            building_type].values()[0])
                else:
                    impact_subtotals.append(0)
            row.append(building_type_name.capitalize())
            # Only show not affected building row if the IF does not use custom
            # affected categories
            if self._affected_categories == self.affected_buildings.keys():
                # Add not affected subtotals
                impact_subtotals.append(
                    self.buildings[building_type] - sum(impact_subtotals))
            # list out the subtotals for this category per impact type
            for value in impact_subtotals:
                row.append(value)

            # totals column
            line_total = format_int(self.buildings[building_type])
            impact_subtotals.append(self.buildings[building_type])
            row.append(line_total)
            fields.append(row)
            # add the subtotal to the cumulative total
            # see http://stackoverflow.com/questions/18713321/element
            #     -wise-addition-of-2-lists-in-python
            # pylint: disable=bad-builtin
            impact_totals = map(add, impact_totals, impact_subtotals)

        # list out the TOTALS for this category per impact type
        row = []
        row.append(tr('Total'))
        for value in impact_totals:
            row.append(format_int(value))
        fields.append(row)

        return {
            'attributes': attributes,
            'fields': fields
        }

    def action_checklist(self):
        """Action Checklist Data.

        :returns: An action list in dictionary format.
        :rtype: dict

        """
        title = tr('Action checklist')
        fields = [
            tr('Which structures have warning capacity (eg. sirens, speakers, '
               'etc.)?'),
            tr('Are the water and electricity services still operating?'),
            tr('Are the health centres still open?'),
            tr('Are the other public services accessible?'),
            tr('Which buildings will be evacuation centres?'),
            tr('Where will we locate the operations centre?'),
            tr('Where will we locate warehouse and/or distribution centres?'),
            tr('Are the schools and hospitals still active?'),
        ]
        if self.schools_closed > 0:
            fields.append(tr(
                'Where will the students from the %s closed schools go to '
                'study?') % format_int(self.schools_closed))
        if self.hospitals_closed > 0:
            fields.append(tr(
                'Where will the patients from the %s closed hospitals go '
                'for treatment and how will we transport them?') % format_int(
                self.hospitals_closed))

        return {
            'title': title,
            'fields': fields
        }

    def generate_report(self):
        """Breakdown by building type.

        :returns: The report.
        :rtype: safe.messaging.Message
        """
        message = m.Message()
        message.add(m.Paragraph(self.question))
        message.add(self.format_impact_summary())
        message.add(self.format_buildings_breakdown())
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
        impact_table = self.buildings_breakdown()
        action_checklist = self.action_checklist()
        notes = self.notes()

        return {
            'question': question,
            'impact summary': impact_summary,
            'impact table': impact_table,
            'action check list': action_checklist,
            'notes': notes
        }

    def format_impact_summary(self):
        """The impact summary as per category.

        :returns: The impact summary.
        :rtype: safe.messaging.Message
        """
        impact_summary = self.impact_summary()
        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None
        for category in impact_summary['fields']:
            row = m.Row()
            row.add(m.Cell(category[0], header=True))
            row.add(m.Cell(format_int(category[1]), align='right'))
            # For value field, if existed
            if len(category) > 2:
                row.add(m.Cell(format_int(category[2]), align='right'))
            table.add(row)
        message.add(table)
        return message

    def format_buildings_breakdown(self):
        """Breakdown by building type.

        :returns: The buildings breakdown report.
        :rtype: safe.messaging.Message
        """
        building_breakdowns = self.buildings_breakdown()

        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None

        # Table header
        row = m.Row()
        for attribute in building_breakdowns['attributes']:
            row.add(m.Cell(tr(attribute), header=True, align='right'))
        table.add(row)

        # Fields
        for record in building_breakdowns['fields'][:-1]:
            row = m.Row()
            # Bold the 1st one
            row.add(m.Cell(tr(record[0]), header=True, align='right'))
            for content in record[1:-1]:
                row.add(m.Cell(format_int(content), align='right'))
            row.add(m.Cell(format_int(record[-1]), header=True, align='right'))
            table.add(row)

        # Total Row
        row = m.Row()
        for content in building_breakdowns['fields'][-1]:
            row.add(m.Cell(tr(content), header=True, align='right'))
        table.add(row)

        message.add(table)

        return message

    @property
    def schools_closed(self):
        """Get the number of schools

        :returns: Count of closed schools.
        :rtype: int

        .. note::

            Expect affected buildings to be given as following:

            affected_buildings = OrderedDict([
                (category, {building_type: amount}),
            e.g.
                (inundated, {residential: 1000, school: 0 ...}),
                (wet, {residential: 12, school: 2 ...}),
                (dry, {residential: 50, school: 50})
            ])
        """
        return self._count_usage('school', self._affected_categories)

    @property
    def hospitals_closed(self):
        """Get the number of hospitals.

        :returns: Count of closed hospitals.
        :rtype: int

        ..Notes:
        Expect affected buildings to be given as following:
            affected_buildings = OrderedDict([
                (category, {building_type: amount}),
            e.g.
                (inundated, {residential: 1000, school: 0 ...}),
                (wet, {residential: 12, school: 2 ...}),
                (dry, {residential: 50, school: 50})
            ])
        """
        return self._count_usage('hospital', self._affected_categories)

    def _count_usage(self, usage, categories=None):
        """Obtain the number of usage (building) that in categories.

        If categories is None, get all categories.

        :param usage: Building usage.
        :type usage: str

        :param categories: Categories that's requested.
        :type categories: list

        :returns: Number of building that is usage and fall in categories.
        :rtype: int
        """
        count = 0
        for category, category_breakdown in self.affected_buildings.items():
            if categories and category not in categories:
                continue
            for current_usage in category_breakdown:
                if current_usage.lower() == usage.lower():
                    count += category_breakdown[current_usage].values()[0]
        return count

    @property
    def _impact_breakdown(self):
        """Get the impact breakdown categories.

        For example, on Earthquake Building with nexis true, this will return:
            [tr('Buildings Affected'),
             tr('Buildings value ($M)'),
             tr('Contents value ($M)')]
        """
        if len(self.affected_buildings.values()) == 0:
            return []
        if len(self.affected_buildings.values()[0].values()) == 0:
            return []
        return self.affected_buildings.values()[0].values()[0].keys()

    @property
    def _affected_categories(self):
        return self.affected_buildings.keys()

    @property
    def total_affected_buildings(self):
        """The total number of affected buildings

        :returns: The total number of affected buildings.
        :rtype: int
        """
        total_affected = 0
        for category in self._affected_categories:
            category_breakdown = self.affected_buildings[category]
            for building_breakdown in category_breakdown.values():
                total_affected += building_breakdown.values()[0]
        return total_affected

    @property
    def total_unaffected_buildings(self):
        """The total number of unaffected buildings.

        :returns: The total number of unaffected buildings.
        :rtype: int
        """
        return self.total_buildings - self.total_affected_buildings

    @property
    def total_buildings(self):
        """The total number of buildings.

        :returns: The total number of buildings.
        :rtype: int
        """
        return sum(self.buildings.values())

    def _consolidate_to_other(self):
        """Consolidate small building usage groups within self.threshold.

        Small groups will be grouped together in the "other" group.
        """
        other = tr('Other')
        for (usage, value) in self.buildings.items():
            if value >= self.building_report_threshold:
                continue
            if other not in self.buildings.keys():
                self.buildings[other] = 0
                for category in self.affected_buildings.keys():
                    other_dict = OrderedDict(
                        [(key, 0) for key in self._impact_breakdown])
                    self.affected_buildings[category][other] = other_dict
            self.buildings[other] += value
            del self.buildings[usage]
            for category in self.affected_buildings.keys():
                for key in self._impact_breakdown:
                    old = self.affected_buildings[category][usage][key]
                    self.affected_buildings[category][other][key] += old
                del self.affected_buildings[category][usage]
