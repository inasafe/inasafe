# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Polygon People Report Template Test Cases.**

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest
import os
import json

from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.common.utilities import temp_dir

from safe.impact_template.polygon_people_report_template import (
    PolygonPeopleReportTemplate)

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'test_polygon_people_report_template'
__date__ = '4/28/16'
__copyright__ = 'imajimatika@gmail.com'

TEMP_DIR = temp_dir(sub_dir='test/template')
TEST_DIR = os.path.dirname(__file__)

JSON_FILE = os.path.join(TEST_DIR, 'data', 'polygon_people_impact.json')


class TestBuildingReportTemplate(unittest.TestCase):
    def test_population_report_template(self):
        """Test Population Report Template
        """
        with open(JSON_FILE) as json_file:
            impact_data = json.load(json_file)

        population_report_template = PolygonPeopleReportTemplate(
            impact_data=impact_data)
        report = population_report_template.generate_message_report()
        self.assertIn(
            impact_data['question'], report.message[0].to_text())
        text = '''
---
**High Hazard Zone**, 4,600------
**Medium Hazard Zone**, 65,700------
**Low Hazard Zone**, 2,500------
**Total affected people**, 72,600------
**Unaffected people**, 26,400------
**Total people**, 98,900---
'''

        self.assertIn(text, report.message[1].to_text())


if __name__ == '__main__':
    unittest.main()
