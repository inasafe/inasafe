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

__author__ = 'etiennetrimaille'
__project_name__ = 'inasafe-dev'
__filename__ = 'abstract_road_building_report_template'
__date__ = '09/05/16'
__copyright__ = 'etienne@kartoza.com'


import safe.messaging as m
from safe.common.utilities import format_int
from safe.impact_template.template_base import TemplateBase


class AbstractRoadBuildingReportTemplate(TemplateBase):
    """Abstract Report Template for Road and Building.

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
        super(AbstractRoadBuildingReportTemplate, self).__init__(
            impact_layer_path=impact_layer_path,
            json_file=json_file,
            impact_data=impact_data)

    def format_breakdown(self):
        """Breakdown by road/building type."""
        raise NotImplementedError

    def generate_message_report(self):
        """Generate impact report as message object.

        :returns: The report.
        :rtype: safe.messaging.Message
        """
        message = m.Message()
        message.add(self.format_question())
        message.add(self.format_impact_summary())
        message.add(self.format_breakdown())
        message.add(self.format_action_check_list())
        message.add(self.format_notes())
        if self.postprocessing:
            message.add(self.format_postprocessing())
        return message

    def format_postprocessing(self):
        """Format postprocessing.

        :returns: The postprocessing.
        :rtype: safe.messaging.Message
        """
        if not self.postprocessing:
            return False
        message = m.Message()
        for k, v in self.postprocessing.items():
            table = m.Table(
                style_class='table table-condensed table-striped')
            table.caption = v['caption']
            attributes = v['attributes']

            header = m.Row()
            # Bold and align left the 1st one.
            header.add(m.Cell(attributes[0], header=True, align='left'))
            for attribute in attributes[1:]:
                # Bold and align right.
                header.add(m.Cell(attribute, header=True, align='right'))
            header.add(m.Cell('Total', header=True, align='right'))
            table.add(header)

            for field in v['fields']:
                row = m.Row()
                # First column is string
                row.add(m.Cell(field[0]))
                total = 0
                for value in field[1:]:
                    try:
                        val = int(value)
                        total += val
                        # Align right integers.
                        row.add(m.Cell(format_int(val), align='right'))
                    except ValueError:
                        # Catch no data value. Align left strings.
                        row.add(m.Cell(value, align='left'))

                row.add(m.Cell(format_int(int(round(total))), align='right'))
                table.add(row)
            message.add(table)

        return message
