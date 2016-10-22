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

from collections import OrderedDict

from safe.definitionsv4.value_maps import road_class_order
from safe.impact_reports.report_mixin_base import ReportMixin
from safe.utilities.i18n import tr
from safe.utilities.utilities import reorder_dictionary

__author__ = 'Christian Christelis <christian@kartoza.com>'


class RoadExposureReportMixin(ReportMixin):
    """Building specific report.

    .. versionadded:: 3.2
    """

    def __init__(self):
        """Road specific report mixin.

        .. versionadded:: 3.2
        """
        super(RoadExposureReportMixin, self).__init__()
        self.exposure_report = 'road'
        self.attribute = 'Road Type'
        self.order = road_class_order
        self.road_lengths = {}
        self.affected_road_lengths = {}
        self.affected_road_categories = {}
        # By default it's true.
        # But for the Tsunami raster on Roads, we already have the dry column.
        self.add_unaffected_column = True

    @property
    def impact_summary_headings(self):
        """Headings for the impact summary.

        :return: Headings
        :rtype: list
        """
        return [tr('Roads'), tr('Length')]

    @staticmethod
    def label_with_unit(label):
        """Get the label with the correct unit.

        :param label: The label.
        :type label: str

        :return: The label with the unit.
        :rtype: str
        """
        return '%s (m)' % label

    def init_report_var(self, categories):
        """Create tables for the report according to the classes.

        .. versionadded:: 3.4

        :param categories: The list of classes to use.
        :type categories: list
        """
        self.road_lengths = {}
        self.affected_road_categories = categories

        self.affected_road_lengths = OrderedDict()
        for category in categories:
            self.affected_road_lengths[category] = {}

    def classify_feature(self, hazard_class, usage, length, affected):
        """Fill the report variables with the feature.

        :param hazard_class: The hazard class of the road.
        :type hazard_class: str

        :param usage: The main usage of the road.
        :type usage: str

        :param length: The length of the road, in meters.
        :type length: float

        :param affected: If the road is affected or not.
        :type affected: bool
        """
        if usage not in self.road_lengths:
            self.road_lengths[usage] = 0

        if hazard_class not in self.affected_road_categories:
            self.affected_road_lengths[hazard_class] = {}

        if usage not in self.affected_road_lengths[hazard_class]:
            self.affected_road_lengths[hazard_class][usage] = 0

        self.road_lengths[usage] += length

        if affected:
            self.affected_road_lengths[hazard_class][usage] += length

    def reorder_dictionaries(self):
        """Reorder every dictionaries so as to generate the report properly."""
        road_lengths = self.road_lengths.copy()
        self.road_lengths = reorder_dictionary(road_lengths, self.order)

        affected_road_lengths = self.affected_road_lengths.copy()
        self.affected_road_lengths = OrderedDict()
        for key in affected_road_lengths:
            item = affected_road_lengths[key]
            self.affected_road_lengths[key] = reorder_dictionary(
                item, self.order)

    def generate_data(self):
        """Create a dictionary contains impact data.

        :returns: The impact report data.
        :rtype: dict
        """
        extra_data = {
            'impact table': self.impact_table(),
        }
        data = super(RoadExposureReportMixin, self).generate_data()
        data.update(extra_data)
        return data

    def impact_summary(self):
        """Create impact summary as data.

        :returns: Impact Summary in dictionary format.
        :rtype: dict
        """
        fields = []

        sum_affected = 0
        for (category, road_breakdown) in self.affected_road_lengths.items():
            number_affected = sum(road_breakdown.values())
            fields.append([self.label_with_unit(category), number_affected])
            sum_affected += number_affected
        if self.add_unaffected_column:
            fields.append([
                self.label_with_unit(tr('Unaffected')),
                self.total_road_length - sum_affected])
        fields.append([
            self.label_with_unit(tr('Total')),
            self.total_road_length])

        return {
            'attributes': ['category', 'value'],
            'headings': self.impact_summary_headings,
            'fields': fields
        }

    def impact_table(self):
        """Create road breakdown as data.

        :returns: Road Breakdown in dictionary format.
        :rtype: dict
        """
        attributes = [self.attribute]
        fields = []

        for affected_category in self.affected_road_categories:
            attributes.append(affected_category)
        if self.add_unaffected_column:
            attributes.append('Unaffected')
        attributes.append('Total')

        for road_type in self.road_lengths:
            affected_by_usage = []
            for category in self.affected_road_categories:
                if road_type in self.affected_road_lengths[category]:
                    affected_by_usage.append(
                        self.affected_road_lengths[category][road_type])
                else:
                    affected_by_usage.append(0)

            row = [self.label_with_unit(road_type.capitalize())]
            for affected_by_usage_value in affected_by_usage:
                row.append(affected_by_usage_value)

            # Unaffected
            if self.add_unaffected_column:
                row.append(
                    self.road_lengths[road_type] - sum(affected_by_usage))

            # Total for the road type
            row.append(self.road_lengths[road_type])

            fields.append(row)

        impact_summary = self.impact_summary()['fields']
        row = [self.label_with_unit(tr('Total'))]
        for value in impact_summary:
            row.append(value[1])
        fields.append(row)

        return {
            'attributes': attributes,
            'fields': fields
        }

    def extra_actions(self):
        """Return the extra exposure specific actions.

        .. note:: Only calculated actions are implemented here, the rest
            are defined in definitions.

        .. versionadded:: 3.5

        :return: The action check list as list.
        :rtype: list
        """
        fields = []
        return fields

    @property
    def total_road_length(self):
        """The total road length.

        :returns: The total road length.
        :rtype: float
        """
        return sum(self.road_lengths.values())
