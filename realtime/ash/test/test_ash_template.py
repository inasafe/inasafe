# coding=utf-8
import unittest

import os

import shutil

import datetime

from pytz import timezone

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
        event = AshEvent(
            working_dir=self.data_dir('temp'),
            volcano_name='Nama Gunung',
            volcano_location=[124.2, 6.9],
            eruption_height=7000,
            event_time=datetime.datetime.now().replace(
                tzinfo=timezone('Asia/Jakarta')),
            region='East Java',
            alert_level='Siaga',
            hazard_path=self.data_dir('hazard.tif'))
        event.impact_exists = True
        event.hazard_path = self.data_dir('hazard.tif')
        event.map_report_path = self.data_dir('temp/temp.pdf')
        event.nearby_html_path = self.data_dir('nearby-table.html')
        event.population_html_path = self.data_dir('population-table.html')
        event.landcover_html_path = self.data_dir('landcover-table.html')
        event.calculate_impact()
        event.generate_report()

    def data_dir(self, path):
        dirpath = os.path.dirname(__file__)
        return os.path.join(dirpath, 'data', path)
