# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Road Report Template Test Cases.**

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'test_road_report_template'
__date__ = '4/28/16'
__copyright__ = 'imajimatika@gmail.com'

import unittest
import os
import json
from safe.common.utilities import temp_dir

from safe.impact_template.road_building_report_template import (
    RoadBuildingReportTemplate)

TEMP_DIR = temp_dir(sub_dir='test/template')
TEST_DIR = os.path.dirname(__file__)

ROAD_JSON_FILE = os.path.join(TEST_DIR, 'data', 'road_impact.json')
BUILDING_JSON_FILE = os.path.join(TEST_DIR, 'data', 'building_impact.json')


class TestRoadReportTemplate(unittest.TestCase):

    def test_road_report_template(self):
        """Test Road Report Template
        """
        with open(ROAD_JSON_FILE) as json_file:
            impact_data = json.load(json_file)

        road_report_template = RoadBuildingReportTemplate(
            impact_data=impact_data)
        report = road_report_template.generate_message_report()
        self.assertIn(
            impact_data['question'], report.message[0].to_text())

        expected = '''
---
**17459.7365945 (m)**, 41,116, 58,576---
'''
        result = report.message[1].to_text()
        self.assertIn(expected, result)

    def test_building_report_template(self):
        """Test Building Report Template
        """
        with open(BUILDING_JSON_FILE) as json_file:
            impact_data = json.load(json_file)

        building_report_template = RoadBuildingReportTemplate(
            impact_data=impact_data)
        report = building_report_template.generate_message_report()
        self.assertIn(
            impact_data['question'], report.message[0].to_text())
        text = '''
---
**High**, 0------
**Medium**, 181------
**Low**, 0------
**Affected buildings**, 181------
**Not affected buildings**, 0------
**Total**, 181---
'''

        self.assertIn(text, report.message[1].to_text())

if __name__ == '__main__':
    unittest.main()
