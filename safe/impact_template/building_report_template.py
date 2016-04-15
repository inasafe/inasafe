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
from safe.impact_template.template_base import TemplateBase

class BuildingReportTemplate(TemplateBase):
    """Report Template for Building.

    ..versionadded: 3.4
    """
    def __init__(self, impact_data):
        """Initialize Template.

        :param impact_data: Dictionary that represent impact data.
        :type impact_data: dict
        """
        super(BuildingReportTemplate, self).__init__(impact_data)
        self.impact_table = self.impact_data.get('impact table')

    def generate_message_report(self):
        """Generate impact report as message object.

        :returns: The report.
        :rtype: safe.messaging.Message
        """
        message = m.Message()
        message.add(self.format_question())
        message.add(self.format_impact_summary())
        message.add(self.format_building_break_down())
        message.add(self.format_action_check_list())
        message.add(self.format_notes())
        return message

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

    def format_building_break_down(self):
        """Breakdown by building type.

        :returns: The buildings breakdown report.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None

        # Table header
        row = m.Row()
        for attribute in self.impact_table['attributes']:
            row.add(m.Cell(attribute, header=True, align='right'))
        table.add(row)

        # Fields
        for record in self.impact_table['fields'][:-1]:
            row = m.Row()
            # Bold the 1st one
            row.add(m.Cell(record[0], header=True, align='right'))
            for content in record[1:-1]:
                row.add(m.Cell(format_int(content), align='right'))
            row.add(m.Cell(format_int(record[-1]), header=True, align='right'))
            table.add(row)

        # Total Row
        row = m.Row()
        for content in self.impact_table['fields'][-1]:
            row.add(m.Cell(content, header=True, align='right'))
        table.add(row)

        message.add(table)

        return message
