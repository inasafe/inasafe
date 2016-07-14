# coding=utf-8
import unittest

import os

import shutil

from realtime.ash.ash_event import AshEvent

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/13/16'


class TestAshTemplate(unittest.TestCase):
    """Tests related with Ash Report Template"""

    def setUp(self):
        try:
            shutil.rmtree(self.data_dir('temp'))
        except:
            pass
        os.makedirs(self.data_dir('temp'))

    def test_process_pdf(self):
        event = AshEvent()
        event.impact_exists = True
        event.report_path = self.data_dir('temp')
        event.population_impact_path = self.data_dir('hazard.tif')
        event.map_report_path = self.data_dir('temp/temp.pdf')
        event.nearby_html_path = self.data_dir('nearby_places.html')
        event.impacts_html_path = self.data_dir('table_potential_impact.html')
        event.landcover_html_path = self.data_dir('land_cover_impact.html')
        event.generate_report()

    def data_dir(self, path):
        dirpath = os.path.dirname(__file__)
        return os.path.join(dirpath, 'data', path)
