# coding=utf-8
import unittest

import os

from realtime.ash.ash_event import AshEvent

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/13/16'


class TestAshTemplate(unittest.TestCase):
    """Tests related with Ash Report Template"""

    def test_process_pdf(self):
        event = AshEvent()
        event.impacts_html_path = self.data_dir('IDN_Volcano_WGS84.shp')
        event.map_report_path = self.data_dir('temp')
        event.nearby_html_path = self.data_dir('nearby_places.html')
        event.table_potential_impact = self.data_dir('table_potential_impact.html')
        event.landcover_html_path = self.data_dir('land_cover_impact.html')
        event.generate_report()

    def data_dir(self, path):
        data_path = os.path.join('data', path)
        return os.path.abspath(data_path)
