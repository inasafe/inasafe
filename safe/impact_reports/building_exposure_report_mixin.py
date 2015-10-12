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

    def generate_report(self):
        """Breakdown by building type.

        :returns: The report.
        :rtype: safe.messaging.Message
        """
        message = m.Message()
        message.add(m.Paragraph(self.question))
        message.add(self.impact_summary())
        message.add(self.buildings_breakdown())
        message.add(self.action_checklist())
        message.add(self.notes())
        return message

    def action_checklist(self):
        """Breakdown by building type.

        :returns: The buildings breakdown report.
        :rtype: safe.messaging.Message
        """
        schools_closed = self.schools_closed
        hospitals_closed = self.hospitals_closed

        message = m.Message(style_class='container')
        message.add(m.Heading(tr('Action checklist'), **styles.INFO_STYLE))
        checklist = m.BulletedList()
        checklist.add(tr('Are the critical facilities still open?'))
        checklist.add(tr(
            'Which structures have warning capacity (eg. sirens, speakers, '
            'etc.)?'))
        checklist.add(tr('Which buildings will be evacuation centres?'))
        checklist.add(tr('Where will we locate the operations centre?'))
        checklist.add(
            tr('Where will we locate warehouse and/or distribution centres?'))
        if schools_closed > 0:
            checklist.add(tr(
                'Where will the students from the %s closed schools '
                'go to study?') % format_int(schools_closed))
        if hospitals_closed > 0:
            checklist.add(tr(
                'Where will the patients from the %s closed hospitals go '
                'for treatment and how will we transport them?') % format_int(
                    hospitals_closed))
        message.add(checklist)
        return message

    def impact_summary(self):
        """The impact summary as per category.

        :returns: The impact summary.
        :rtype: safe.messaging.Message
        """
        affect_types = self._impact_breakdown
        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None
        row = m.Row()
        row.add(m.Cell('', header=True))  # intentionally empty top left cell
        row.add(m.Cell('Buildings affected', header=True))
        for (category, building_breakdown) in self.affected_buildings.items():
            total_affected = [0] * len(affect_types)
            for affected_breakdown in building_breakdown.values():
                for affect_type, number_affected in affected_breakdown.items():
                    count = affect_types.index(affect_type)
                    total_affected[count] += number_affected
            row = m.Row()
            row.add(m.Cell(tr(category), header=True))
            for affected in total_affected:
                row.add(m.Cell(format_int(affected), align='right'))
            table.add(row)

        if len(self._affected_categories) > 1:
            row = m.Row()
            row.add(m.Cell(tr('Affected buildings'), header=True))
            row.add(m.Cell(
                format_int(self.total_affected_buildings), align='right'))
            table.add(row)

        row = m.Row()
        row.add(m.Cell(tr('Unaffected buildings'), header=True))
        row.add(m.Cell(
            format_int(self.total_unaffected_buildings), align='right'))
        table.add(row)

        row = m.Row()
        row.add(m.Cell(tr('Total'), header=True))
        row.add(m.Cell(
            format_int(self.total_buildings), align='right'))
        table.add(row)
        message.add(table)
        return message

    def buildings_breakdown(self):
        """Breakdown by building type.

        :returns: The buildings breakdown report.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None
        impact_names = self.affected_buildings.keys()  # e.g. flooded, wet, dry

        row = m.Row()
        row.add(m.Cell('Building type', header=True))
        for name in impact_names:
            row.add(m.Cell(tr(name), header=True, align='right'))
        row.add(m.Cell(tr('Total'), header=True, align='right'))
        table.add(row)

        # Let's sort alphabetically first
        building_types = [building_type for building_type in self.buildings]
        building_types.sort()
        impact_totals = []  # Used to store the total for each impact name
        # Initialise totals with zeros
        for _ in impact_names:
            impact_totals.append(0)
        # And one extra total for the cumuluative total column
        impact_totals.append(0)
        # Now build the main table
        for building_type in building_types:
            row = m.Row()
            building_type_name = building_type.replace('_', ' ')
            impact_subtotals = []
            for name in impact_names:
                if building_type in self.affected_buildings[name]:
                    impact_subtotals.append(
                        self.affected_buildings[name][
                            building_type].values()[0])
                else:
                    impact_subtotals.append(0)
            row.add(m.Cell(building_type_name.capitalize(), header=True))
            # list out the subtotals for this category per impact type
            for value in impact_subtotals:
                row.add(m.Cell(format_int(value), align='right'))
            # totals column
            line_total = format_int(self.buildings[building_type])
            impact_subtotals.append(self.buildings[building_type])
            row.add(m.Cell(
                line_total,
                header=True,
                align='right'))
            table.add(row)
            # add the subtotal to the cumulative total
            # see http://stackoverflow.com/questions/18713321/element
            #     -wise-addition-of-2-lists-in-python
            # pylint: disable=bad-builtin
            impact_totals = map(add, impact_totals, impact_subtotals)

        # list out the TOTALS for this category per impact type
        row = m.Row()
        row.add(m.Cell(tr('Total'), header=True))
        for value in impact_totals:
            row.add(m.Cell(format_int(value), align='right', header=True))
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
        return self._count_usage('school')

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
        return self._count_usage('hospital')

    def _count_usage(self, usage):
        count = 0
        for category_breakdown in self.affected_buildings.values():
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
        """Consolidate the small building usage groups < 25 to other."""
        cutoff = 25
        other = tr('Other')
        for (usage, value) in self.buildings.items():
            if value >= cutoff:
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
