# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Functionality related to shake data files.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '30/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import os
import unittest
from datetime import date

from realtime.utils import (
    base_data_dir,
    shakemap_zip_dir,
    shakemap_extract_dir,
    shakemap_data_dir,
    report_data_dir,
    log_dir,
    is_event_id,
    purge_working_data)

# Clear away working dirs so we can be sure they
# are actually created
purge_working_data()
# The logger is intiailsed in utils.py by init
import logging
LOGGER = logging.getLogger('InaSAFE')


class Test(unittest.TestCase):

    def test_base_data_dir(self):
        """Test we can get the realtime data dir"""
        data_dir = base_data_dir()
        expected_dir = '/tmp/inasafe/realtime'
        assert os.path.exists(expected_dir)
        self.assertEqual(data_dir, expected_dir)

    def test_shakemap_zip_dir(self):
        """Test we can get the shakemap zip dir"""
        data_dir = shakemap_zip_dir()
        expected_dir = '/tmp/inasafe/realtime/shakemaps-zipped'
        assert os.path.exists(expected_dir)
        self.assertEqual(data_dir, expected_dir)

    def test_shakemap_extract_dir(self):
        """Test we can get the shakemap extracted data dir"""
        data_dir = shakemap_extract_dir()
        expected_dir = '/tmp/inasafe/realtime/shakemaps-extracted'
        assert os.path.exists(expected_dir)
        self.assertEqual(data_dir, expected_dir)

    def test_shakemap_data_dir(self):
        """Test we can get the shakemap post processed data dir"""
        data_dir = shakemap_data_dir()
        expected_dir = '/tmp/inasafe/realtime/shakemaps-processed'
        assert os.path.exists(expected_dir)
        self.assertEqual(data_dir, expected_dir)

    def test_report_data_dir(self):
        """Test we can get the report data dir"""
        data_dir = report_data_dir()
        expected_dir = '/tmp/inasafe/realtime/reports'
        assert os.path.exists(expected_dir)
        self.assertEqual(data_dir, expected_dir)

    def test_logging(self):
        path = os.path.join(log_dir(), 'realtime.log')
        current_date = date.today()
        date_string = current_date.strftime('%d-%m-%Y-%s')
        message = 'Testing logger %s' % date_string
        LOGGER.info(message)
        log_file = open(path, 'rt')
        log_lines = log_file.readlines()
        if message not in log_lines:
            assert 'Error, expected log message not shown in logs'
        log_file.close()

    def test_is_event_id(self):
        """Test to check if a event is in server
        """
        assert is_event_id('20130110041009'), 'should be event id'
        assert not is_event_id('20130110041090'), 'should not be event id'
        assert not is_event_id('2013'), 'should not be event id'
        assert not is_event_id('AAA'), 'should not be event id'

if __name__ == '__main__':
    unittest.main()
