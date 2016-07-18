# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Template Base Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

import os
import json
import logging
from collections import OrderedDict
import safe.messaging as m
from safe.messaging import styles
from safe.common.exceptions import MissingImpactReport
from safe.common.utilities import format_int

LOGGER = logging.getLogger('InaSAFE')

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'generic_report_template.py'
__date__ = '4/15/16'
__copyright__ = 'imajimatika@gmail.com'


class GenericReportTemplate(object):
    """Generic Template Class.
    This class is used by Roads and Buildings.
    Land Cover, Polygon People and Population have a child class.

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
        # Check for impact layer path first
        if impact_layer_path:
            impact_data_path = os.path.splitext(impact_layer_path)[0] + '.json'
            json_file = impact_data_path
        if json_file:
            if os.path.exists(json_file):
                with open(json_file) as json_file:
                    impact_data = json.load(
                        json_file, object_pairs_hook=OrderedDict)

        if not impact_data:
            raise MissingImpactReport


        self.impact_data = impact_data
        self.exposure = impact_data.get('exposure')
        self.question = impact_data.get('question')
        self.impact_summary = impact_data.get('impact summary')
        self.action_check_list = impact_data.get('action check list')
        self.notes = impact_data.get('notes')
        self.postprocessing = impact_data.get('post processing')
        self.impact_table = self.impact_data.get('impact table')

    def generate_message_report(self):
        """Generate impact report as message object.

        :returns: The report.
        :rtype: safe.messaging.Message
        """
        message = m.Message()
        message.add(self.format_question())
        message.add(self.format_impact_summary())
        message.add(self.format_impact_table())
        message.add(self.format_action_check_list())
        message.add(self.format_notes())
        if self.postprocessing:
            message.add(self.format_postprocessing())
        return message

    def generate_html_report(self):
        """Generate HTML impact report.

        :returns: The report as HTML string.
        :rtype: unicode
        """
        return self.generate_message_report().to_html()

    def format_question(self):
        """Format question.

        :returns: The impact question.
        :rtype: safe.messaging.Message
        """
        return m.Paragraph(self.question)

    def format_impact_summary(self):
        """Format impact summary.

        :returns: The impact summary.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None
        for category in self.impact_summary['fields']:
            row = m.Row()
            row.add(m.Cell(category[0], header=True))
            row.add(m.Cell(self.format_int(category[1]), align='right'))
            # For value field, if existed
            if len(category) > 2:
                row.add(m.Cell(self.format_int(category[2]), align='right'))
            table.add(row)
        message.add(table)
        return message

    def format_impact_table(self):
        """Impact detailed report.

        :returns: The detailed report.
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
                row.add(m.Cell(format_int(int(content)), align='right'))
            # Bold and align right the last one.
            row.add(
                m.Cell(
                    format_int(int(record[-1])), header=True, align='right'))
            table.add(row)

        # Total Row
        row = m.Row()
        last_row = self.impact_table['fields'][-1]
        # Bold and align left the 1st one.
        row.add(m.Cell(last_row[0], header=True, align='left'))
        for content in last_row[1:]:
            # Bold and align right.
            row.add(
                m.Cell(format_int(int(content)), header=True, align='right'))
        table.add(row)

        message.add(table)

        return message

    def format_action_check_list(self):
        """Format action check list.

        :returns: The action check list.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        message.add(m.Heading(
            self.action_check_list['title'], **styles.INFO_STYLE))

        checklist = m.BulletedList()
        for text in self.action_check_list['fields']:
            checklist.add(text)

        message.add(checklist)
        return message

    def format_notes(self):
        """Format notes..

        :returns: The notes.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        message.add(m.Heading(self.notes['title'], **styles.INFO_STYLE))

        checklist = m.BulletedList()
        for field in self.notes['fields']:
            checklist.add(field)

        message.add(checklist)
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

            if attributes:
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
                            row.add(m.Cell(
                                self.format_int(val), align='right'))
                        except ValueError:
                            # Catch no data value. Align left strings.
                            row.add(m.Cell(value, align='left'))

                    row.add(m.Cell(
                        self.format_int(round(total)), align='right'))
                    table.add(row)

            message.add(table)

            for note in v['notes']:
                message.add(m.EmphasizedText(note))

        return message

    @staticmethod
    def format_int(number):
        """Get the correct integer format.

        :param number: The number to format
        :type number: float or integer
        """
        return format_int(int(number))
