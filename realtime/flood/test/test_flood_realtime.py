# coding=utf-8
import logging
import unittest

import os
from realtime.flood.peta_jakarta_api import PetaJakartaAPI
from realtime.utilities import realtime_logger_name
from realtime.make_flood_map import process_event

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'

__date__ = '11/24/15'


LOGGER = logging.getLogger(realtime_logger_name())


class TestFloodRealtime(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_peta_jakarta_aggregates(self):
        json_response = PetaJakartaAPI.get_aggregate_report(1, "rw")
        LOGGER.debug('JSON Response %s' % json_response)

    def test_flood_event_calculate(self):
        working_dir = os.environ['FLOODMAPS_DIR']
        process_event(working_dir)
