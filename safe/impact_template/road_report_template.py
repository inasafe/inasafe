# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Road Template Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'road_report_template'
__date__ = '4/28/16'
__copyright__ = 'imajimatika@gmail.com'


import safe.messaging as m
from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.impact_template.abstract_road_building_report_template import \
    AbstractRoadBuildingReportTemplate


class RoadReportTemplate(AbstractRoadBuildingReportTemplate):
    """Report Template for Road.

    ..versionadded: 3.4
    """
    def __init__(
            self, impact_layer_path=None, json_file=None, impact_data=None):
        """Initialize Template.

        :param impact_layer_path: Path to impact layer.
        :type impact_layer_path: str

        :param json_file: Path to json impact data.
        :type json_file: str

        :param impact_data: Dictionary that represent impact data.
        :type impact_data: dict
        """
        super(RoadReportTemplate, self).__init__(
            impact_layer_path=impact_layer_path,
            json_file=json_file,
            impact_data=impact_data)
        self.roads_breakdown = self.impact_data.get('impact table')

    def format_impact_summary(self):
        """The impact summary as per category

        :returns: The impact summary.
        :rtype: safe.message.Message
        """
        attributes = self.impact_summary['attributes']
        fields = self.impact_summary['fields']

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

    def format_breakdown(self):
        """Breakdown by road type.

        :returns: The roads breakdown report.
        :rtype: safe.message.Message
        """
        road_breakdown = self.roads_breakdown
        attributes = road_breakdown['attributes']
        fields = road_breakdown['fields']

        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None

        row = m.Row()
        row.add(m.Cell(tr('Breakdown by road type'), header=True))
        for _ in attributes:
            # Add empty cell as many as affected_categories
            row.add(m.Cell('', header=True))

        # Add empty cell for total column
        row.add(m.Cell('', header=True))
        table.add(row)

        row = m.Row()
        # We align left the first column, then right.
        row.add(m.Cell(tr(attributes[0]), header=True))
        for attribute in attributes[1:]:
            row.add(m.Cell(tr(attribute), header=True, align='right'))
        table.add(row)

        for field in fields:
            row = m.Row()
            # First column
            # proper format for i186
            row.add(m.Cell(
                tr('%(road_type)s (m)') % {
                    'road_type': field[0].capitalize()}))
            # Start from second column
            for value in field[1:]:
                row.add(m.Cell(
                    format_int(int(value)), align='right'))
            table.add(row)

        impact_summary_fields = self.impact_summary['fields']

        row = m.Row()
        row.add(m.Cell(tr('Total (m)'), header=True))
        for field in impact_summary_fields:
            for value in field:
                row.add(m.Cell(
                    format_int(int(value)),
                    align='right',
                    header=True))

        table.add(row)

        message.add(table)

        return message
