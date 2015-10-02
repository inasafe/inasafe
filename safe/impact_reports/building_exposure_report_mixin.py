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

from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.impact_reports.report_mixin_base import ReportMixin


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
        :rtype: list
        """
        report = [{'content': self.question}]
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.impact_summary()
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.buildings_breakdown()
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.action_checklist()
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.notes()
        return report

    def action_checklist(self):
        """Breakdown by building type.

        :returns: The buildings breakdown report.
        :rtype: list
        """
        schools_closed = self.schools_closed
        hospitals_closed = self.hospitals_closed
        return [
            {
                'content': tr('Action checklist'),
                'header': True
            },
            {
                'content': tr('Are the critical facilities still open?')
            },
            {
                'content': tr(
                    'Which structures have warning capacity '
                    '(eg. sirens, speakers, etc.)?')},
            {
                'content': tr('Which buildings will be evacuation centres?')
            },
            {
                'content': tr('Where will we locate the operations centre?')
            },
            {
                'content': tr(
                    'Where will we locate warehouse and/or distribution '
                    'centres?')
            },
            {
                'content': tr(
                    'Where will the students from the %s closed schools go to '
                    'study?'),
                'arguments': (format_int(schools_closed),),
                'condition': schools_closed > 0
            },
            {
                'content': tr(
                    'Where will the patients from the %s closed hospitals go '
                    'for treatment and how will we transport them?'),
                'arguments': (format_int(hospitals_closed),),
                'condition': hospitals_closed > 0
            }
        ]

    def impact_summary(self):
        """The impact summary as per category

        :returns: The impact summary.
        :rtype: list
        """
        affect_types = self._impact_breakdown
        impact_summary_report = [
            {
                # We leave the top left cell blank in the summary table
                'content': [tr('')] + affect_types,
                'header': True
            }]
        for (category, building_breakdown) in self.affected_buildings.items():
            total_affected = [0] * len(affect_types)
            for affected_breakdown in building_breakdown.values():
                for affect_type, number_affected in affected_breakdown.items():
                    count = affect_types.index(affect_type)
                    total_affected[count] += number_affected
            total_affected_formatted = [
                format_int(affected) for affected in total_affected]
            impact_summary_report.append(
                {
                    'content': [tr(category)] + total_affected_formatted
                })
        if len(self._affected_categories) > 1:
            impact_summary_report.append(
                {
                    'content': [
                        tr(tr('Total affected buildings')),
                        format_int(self.total_affected_buildings)],
                    'header': True
                })
        impact_summary_report.append(
            {
                'content': [
                    tr('Unaffected buildings'),
                    format_int(self.total_unaffected_buildings)],
                'header': True
            })
        impact_summary_report.append(
            {
                'content': [
                    tr('All buildings'),
                    format_int(self.total_buildings)],
                'header': True
            })
        return impact_summary_report

    def buildings_breakdown(self):
        """Breakdown by building type.

        :returns: The buildings breakdown report.
        :rtype: list
        """
        buildings_breakdown_report = []
        category_names = self.affected_buildings.keys()
        table_headers = [tr('Building type')]
        table_headers += [tr(category) for category in category_names]
        table_headers += [tr('Total')]
        buildings_breakdown_report.append(
            {
                'content': table_headers,
                'header': True
            })
        # Let's sort alphabetically first
        building_types = [building_type for building_type in self.buildings]
        building_types.sort()
        for building_type in building_types:
            building_type_name = building_type.replace('_', ' ')
            affected_by_usage = []
            for category in category_names:
                if building_type in self.affected_buildings[category]:
                    affected_by_usage.append(
                        self.affected_buildings[category][
                            building_type].values()[0])
                else:
                    affected_by_usage.append(0)
            building_detail = (
                # building type
                [building_type_name.capitalize()] +
                # categories
                [format_int(x) for x in affected_by_usage] +
                # total
                [format_int(self.buildings[building_type])])
            buildings_breakdown_report.append(
                {
                    'content': building_detail
                })

        return buildings_breakdown_report

    @property
    def schools_closed(self):
        """Get the number of schools

        :returns: The buildings breakdown report.
        :rtype: list

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
        """Get the number of schools

        :returns: The buildings breakdown report.
        :rtype: list

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
