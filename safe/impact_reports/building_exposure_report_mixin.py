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
from collections import OrderedDict
from operator import add

from safe.definitionsv4.value_maps import structure_class_order
from safe.common.utilities import format_int
from safe.impact_reports.report_mixin_base import ReportMixin
from safe.utilities.i18n import tr
from safe.utilities.utilities import reorder_dictionary

__author__ = 'Christian Christelis <christian@kartoza.com>'


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
        super(BuildingExposureReportMixin, self).__init__()
        self.exposure_report = 'building'
        self.buildings = {}
        self.categories = None
        self.affected_buildings = {}

        self.impact_data = {}

    @property
    def impact_summary_headings(self):
        """Headings for the impact summary.

        :return: Headings
        :rtype: list
        """
        return [tr('Buildings'), tr('Count')]

    def init_report_var(self, categories):
        """Create tables for the report according to the classes.

        .. versionadded:: 3.4

        :param categories: The list of classes to use.
        :type categories: list
        """
        self.categories = categories
        self.buildings = {}
        self.affected_buildings = {}
        for category in categories:
            self.affected_buildings[category] = {}

    def classify_feature(self, hazard_class, usage, affected):
        """Fill the report variables with the feature.

        :param hazard_class: The hazard class of the building.
        :type hazard_class: str

        :param usage: The main usage of the building.
        :type usage: str

        :param affected: If the building is affected or not.
        :type affected: bool
        """
        building_affected = tr('Buildings Affected')
        if usage not in self.buildings:
            self.buildings[usage] = 0

            for category in self.categories:
                self.affected_buildings[category][usage] = OrderedDict()
                self.affected_buildings[category][usage][building_affected] = 0

        self.buildings[usage] += 1
        if affected:
            self.affected_buildings[hazard_class][usage][building_affected]\
                += 1

    def reorder_dictionaries(self):
        """Reorder every dictionaries so as to generate the report properly."""

        buildings = self.buildings.copy()
        self.buildings = reorder_dictionary(buildings, structure_class_order)

        affected_buildings = self.affected_buildings.copy()
        self.affected_buildings = reorder_dictionary(
            affected_buildings, self.categories)

    def impact_summary(self):
        """Create impact summary as data.

        :returns: Impact Summary in dictionary format.
        :rtype: dict
        """
        affect_types = self._impact_breakdown
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
            fields.append([
                tr('Not affected buildings'), self.total_unaffected_buildings]
            )

        fields.append([tr('Total'), self.total_buildings])

        return {
            'attributes': ['category', 'value'],
            'headings': self.impact_summary_headings,
            'fields': fields
        }

    def impact_table(self):
        """Create building breakdown as data.

        :returns: Building Breakdown in dictionary format.
        :rtype: dict
        """
        impact_names = self.affected_buildings.keys()  # e.g. flooded, wet, dry
        attributes = [tr('Building type')]
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
            row.append(tr(building_type_name.capitalize()))
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
            line_total = self.buildings[building_type]
            impact_subtotals.append(self.buildings[building_type])
            row.append(line_total)
            fields.append(row)
            # add the subtotal to the cumulative total
            # see http://stackoverflow.com/questions/18713321/element
            #     -wise-addition-of-2-lists-in-python
            # pylint: disable=bad-builtin
            impact_totals = map(add, impact_totals, impact_subtotals)

        # list out the TOTALS for this category per impact type
        row = [tr('Total')]
        for value in impact_totals:
            row.append(value)
        fields.append(row)

        return {
            'attributes': attributes,
            'fields': fields
        }

    def extra_actions(self):
        """Get actions specific to building exposure.

        .. note:: Only calculated actions are implemented here, the rest
            are defined in definitions_v3.py.

        .. versionadded:: 3.5

        :returns: An action list in list format.
        :rtype: list

        """
        fields = []
        if self.schools_closed > 0:
            fields.append(tr(
                'Where will the students from the %s closed schools go to '
                'study?') % format_int(self.schools_closed))
        if self.hospitals_closed > 0:
            fields.append(tr(
                'Where will the patients from the %s closed hospitals go '
                'for treatment and how will we transport them?') % format_int(
                self.hospitals_closed))
        return fields

    def generate_data(self):
        """Create a dictionary contains impact data.

        :returns: The impact report data.
        :rtype: dict
        """
        extra_data = {
            'impact table': self.impact_table()
        }
        data = super(BuildingExposureReportMixin, self).generate_data()
        data.update(extra_data)
        return data

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
