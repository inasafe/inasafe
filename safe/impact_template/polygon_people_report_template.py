# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Polygon People Template Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'people_polygon_report_template'
__date__ = '4/28/16'
__copyright__ = 'imajimatika@gmail.com'

import safe.messaging as m
from safe.messaging import styles
from safe.utilities.utilities import tr
from safe.common.utilities import format_int
from safe.impact_template.template_base import TemplateBase
from safe.impact_functions.core import population_rounding


class PolygonPeopleReportTemplate(TemplateBase):
    """Report Template for Polygon People.

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
        super(PolygonPeopleReportTemplate, self).__init__(
            impact_layer_path=impact_layer_path,
            json_file=json_file,
            impact_data=impact_data)
        self.minimum_needs = self.impact_data.get('minimum needs')
        self.breakdown = self.impact_data.get('breakdown')

    def generate_message_report(self):
        """Generate impact report as message object.

        :returns: The report.
        :rtype: safe.messaging.Message
        """
        message = m.Message()
        message.add(m.Paragraph(self.question))
        message.add(self.format_impact_summary())
        message.add(self.format_breakdown())
        message.add(self.format_minimum_needs_breakdown())
        message.add(self.format_action_check_list())
        message.add(self.format_notes())
        if self.postprocessing:
            message.add(self.format_postprocessing())

        return message

    def format_impact_summary(self):
        """The impact summary as per category

        :returns: The impact summary.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')

        table = m.Table(
            style_class='table table-condensed table-striped')
        table.caption = None
        for category in self.impact_summary['fields']:
            row = m.Row()
            row.add(m.Cell(category[0], header=True))
            row.add(m.Cell(
                format_int(population_rounding(category[1])), align='right'))
            # For value field, if existed
            if len(category) > 2:
                row.add(m.Cell(format_int(category[2]), align='right'))
            table.add(row)

        message.add(table)

        return message

    def format_breakdown(self):
        """
        """
        message = m.Message(style_class='container')

        table = m.Table(
            style_class='table table-condensed table-striped')
        table.caption = None

        row = m.Row()
        for attribute in self.breakdown['attributes']:
            row.add(m.Cell(attribute, header=True, align='right'))
        table.add(row)

        affected_area = 0
        total_area = 0
        affected_people = 0
        total_people = 0
        for field in self.breakdown['fields']:
            affected_area += field[1]
            total_area += field[3]
            affected_people += field[4]
            total_people += field[6]
            table.add(self.impact_row(
                field[0],
                field[1],
                field[2],
                field[3],
                field[4],
                field[5],
                field[6],
            ))

        percent_area = 0
        percent_people = 0
        if total_area > 0:
            percent_area = affected_area / total_area * 100.0
        if total_people > 0:
            percent_people = affected_people / total_people * 100.0
        table.add(self.impact_row(
            tr('Total'),
            affected_area,
            percent_area,
            total_area,
            affected_people,
            percent_people,
            total_people)
        )

        message.add(table)

        return message

    def format_minimum_needs_breakdown(self):
        """Breakdown by population.

        :returns: The population breakdown report.
        :rtype: list
        """
        message = m.Message(style_class='container')
        message.add(m.Heading(
            tr('Evacuated population minimum needs'),
            **styles.INFO_STYLE))
        table = m.Table(
            style_class='table table-condensed table-striped')
        table.caption = None
        for frequency, needs in self.minimum_needs.items():
            row = m.Row()
            row.add(m.Cell(
                tr('Relief items to be provided %s' % frequency),
                header=True
            ))
            row.add(m.Cell(tr('Total'), header=True, align='right'))
            table.add(row)
            for resource in needs:
                row = m.Row()
                row.add(m.Cell(tr(resource['table name'])))
                row.add(m.Cell(
                    tr(format_int(resource['amount'])),
                    align='right'
                ))
                table.add(row)

        message.add(table)

        return message

    def impact_row(
            self,
            area_name,
            affected,
            percent_affected,
            single_total_area,
            number_people_affected,
            percent_people_affected,
            area_population):
        """Adds the calculated results into respective impact row

        :param area_name: Area Name
        :type area_name: str

        :param affected: table with first and second row
        :type affected: Table

        :param percent_affected: percentage of affected area
        :type percent_affected: float

        :param single_total_area: total area of the land
        :type single_total_area: float

        :param number_people_affected: number of people affected
        :type number_people_affected: float

        :param percent_people_affected: percentage of people affected
        in the area
        :type percent_people_affected: float

        :param area_population: Population of the area
        :type area_population: float

        :return row: the new impact row
        :rtype row: Row
        """

        row = m.Row()
        row.add(m.Cell(area_name))
        row.add(m.Cell(format_int(int(affected)), align='right'))
        row.add(m.Cell(
            "%.1f%%" % percent_affected, align='right'))
        row.add(m.Cell(
            format_int(int(single_total_area)), align='right'))
        row.add(m.Cell(
            format_int(int(number_people_affected)),
            align='right'))
        row.add(m.Cell("%.1f%%" % percent_people_affected, align='right'))
        row.add(m.Cell(
            format_int(int(area_population)),
            align='right'))

        return row
