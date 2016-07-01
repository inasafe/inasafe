# coding=utf-8
import logging
import threading
import unittest

import os

import shutil

import pyinotify
import time

from realtime.earthquake.notify_new_shake import watch_shakemaps_push, \
    ShakemapPushHandler
from realtime.utilities import realtime_logger_name
from safe.common.utilities import temp_dir
from safe.test.utilities import standard_data_path

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/9/15'


# Shake ID for this test
SHAKE_ID = '20131105060809'


LOGGER = logging.getLogger(realtime_logger_name())


class EventHandler(pyinotify.ProcessEvent):

    def __init__(self, test_object):
        self.test_object = test_object
        self.file_handled = None

    def process_IN_CREATE(self, event):
        LOGGER.info('Event %s' % event)
        if event.pathname.endswith('output/grid.xml'):
            LOGGER.info('Grid xml received : %s' % event.pathname)
            # we know that we have the correct file now
            self.file_handled = os.path.exists(event.pathname)


class TestShakemapMonitoring(unittest.TestCase):

    local_path = os.path.join(temp_dir('realtime-test'))
    shake_data = standard_data_path('hazard', 'shake_data', SHAKE_ID)

    def setUp(self):
        # Delete the files that we make in the init for the shake data
        shutil.rmtree(temp_dir('realtime-test'))

    def tearDown(self):
        """Action after each test is called."""
        # Delete the files that we make in the init for the shake data
        shutil.rmtree(temp_dir('realtime-test'))

    def test_trigger_inotify(self):
        """Trigger inotify job"""

        # Download files (which are local files) to realtime-test temp folder

        shakemap_folder = os.path.join(self.local_path, 'shakemaps')
        os.makedirs(shakemap_folder)

        handler = EventHandler(self)
        notifier = watch_shakemaps_push(
            shakemap_folder, handler=handler, daemon=True)
        notifier.start()

        # sleep to let inotify run first
        time.sleep(5)

        # trigger copy
        LOGGER.info('Copy folders')
        shutil.copytree(
            self.shake_data,
            os.path.join(self.local_path, 'shakemaps', SHAKE_ID))
        LOGGER.info('End of folder copy')
        time.sleep(5)
        self.assertTrue(handler.file_handled)
        notifier.stop()

    def test_execute_shake_processor(self):
        """Trigger shake processing job"""

        # Download files (which are local files) to realtime-test temp folder

        shakemap_folder = os.path.join(self.local_path, 'shakemaps')
        os.makedirs(shakemap_folder)

        def process_shakemap_dummy(*args, **kwargs):
            self.assertTrue('shake_id' in kwargs)
            self.assertEqual(kwargs.get('shake_id'), '20131105060809')

        handler = ShakemapPushHandler(
            shakemap_folder, callback=process_shakemap_dummy)

        notifier = watch_shakemaps_push(
            shakemap_folder, handler=handler, daemon=True)
        notifier.start()

        # sleep to let inotify run first
        time.sleep(5)

        # trigger copy
        LOGGER.info('Copy folders')
        shutil.copytree(
            self.shake_data,
            os.path.join(self.local_path, 'shakemaps', SHAKE_ID))
        LOGGER.info('End of folder copy')

        # sleep to let inotify handles events
        time.sleep(5)
        notifier.stop()
