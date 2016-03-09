# coding=utf-8
import logging

import os

from realtime.celery_app import app
from realtime.celeryconfig import FLOOD_WORKING_DIRECTORY
from realtime.flood.make_map import process_event
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/16/16'


# Initialized in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


@app.task(
    name='realtime.tasks.flood.process_flood', queue='inasafe-realtime')
def process_flood(event_folder=None):
    LOGGER.info('-------------------------------------------')

    if 'INASAFE_LOCALE' in os.environ:
        locale_option = os.environ['INASAFE_LOCALE']
    else:
        locale_option = 'en'

    working_directory = FLOOD_WORKING_DIRECTORY
    try:
        process_event(
            working_directory, locale_option, dummy_folder=event_folder)
        LOGGER.info('Process event end.')
        return True
    except Exception as e:
        LOGGER.exception(e)

    return False
