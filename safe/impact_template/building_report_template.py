# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Building Template Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'building_report_template'
__date__ = '4/15/16'
__copyright__ = 'imajimatika@gmail.com'


import safe.messaging as m
from safe.common.utilities import format_int
from safe.impact_template.abstract_road_building_report_template import \
    AbstractRoadBuildingReportTemplate


class BuildingReportTemplate(AbstractRoadBuildingReportTemplate):
    """Report Template for Building.

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
        super(BuildingReportTemplate, self).__init__(
            impact_layer_path=impact_layer_path,
            json_file=json_file,
            impact_data=impact_data)
        self.impact_table = self.impact_data.get('impact table')

    def format_impact_summary(self):
        """Format impact summary.

        :returns: The impact impact summary.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None
        for category in self.impact_summary['fields']:
            row = m.Row()
            row.add(m.Cell(category[0], header=True))
            row.add(m.Cell(format_int(category[1]), align='right'))
            # For value field, if existed
            if len(category) > 2:
                row.add(m.Cell(format_int(category[2]), align='right'))
            table.add(row)
        message.add(table)
        return message

    def format_breakdown(self):
        """Breakdown by building type.

        :returns: The buildings breakdown report.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None

        # Table header
        row = m.Row()
        attributes = self.impact_table['attributes']
        # Bold and align left the 1st one.
        row.add(m.Cell(attributes[0], header=True, align='left'))
        for attribute in attributes[1:]:
            # Bold and align right.
            row.add(m.Cell(attribute, header=True, align='right'))
        table.add(row)

        # Fields
        for record in self.impact_table['fields'][:-1]:
            row = m.Row()
            # Bold and align left the 1st one.
            row.add(m.Cell(record[0], header=True, align='left'))
            for content in record[1:-1]:
                # Align right.
                row.add(m.Cell(format_int(content), align='right'))
            # Bold and align right the last one.
            row.add(m.Cell(format_int(record[-1]), header=True, align='right'))
            table.add(row)

        # Total Row
        row = m.Row()
        last_row = self.impact_table['fields'][-1]
        # Bold and align left the 1st one.
        row.add(m.Cell(last_row[0], header=True, align='left'))
        for content in last_row[1:]:
            # Bold and align right.
            row.add(m.Cell(format_int(content), header=True, align='right'))
        table.add(row)

        message.add(table)

        return message
