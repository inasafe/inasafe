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

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'template_base.py'
__date__ = '4/15/16'
__copyright__ = 'imajimatika@gmail.com'

import os
import json
from collections import OrderedDict
import safe.messaging as m
from safe.messaging import styles
from safe.common.exceptions import MissingImpactReport


class TemplateBase(object):
    """Template Base Class.

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
        self.question = impact_data.get('question')
        self.impact_summary = impact_data.get('impact summary')
        self.action_check_list = impact_data.get('action check list')
        self.notes = impact_data.get('notes')

    def generate_message_report(self):
        """Generate impact report as message object.

        :returns: The report.
        :rtype: safe.messaging.Message
        """
        raise NotImplementedError('Need to be implemented in child class')

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
        raise NotImplementedError('Need to be implemented in child class')

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
