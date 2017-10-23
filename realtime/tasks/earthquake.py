# coding=utf-8

import logging

import os
import re

from realtime.celery_app import app
from realtime.celeryconfig import EARTHQUAKE_WORKING_DIRECTORY
from realtime.earthquake.make_map import process_event
from realtime.earthquake.notify_new_shake import GRID_FILE_PATTERN
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/16/16'


# Initialized in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


@app.task(
    name='realtime.tasks.earthquake.process_shake', queue='inasafe-realtime')
def process_shake(event_id=None):
    LOGGER.info('-------------------------------------------')

    if 'INASAFE_LOCALE' in os.environ:
        locale_option = os.environ['INASAFE_LOCALE']
    else:
        locale_option = 'en'

    working_directory = EARTHQUAKE_WORKING_DIRECTORY

    if not check_event_exists(event_id):
        LOGGER.info('Shake grid not exists')
        return False

    try:
        process_event(working_directory, event_id, locale_option)
        LOGGER.info('Process event end.')
        return True
    except Exception as e:
        LOGGER.exception(e)

    return False


@app.task(
    name='realtime.tasks.earthquake.check_event_exists',
    queue='inasafe-realtime')
def check_event_exists(event_id=None):
    LOGGER.info('-------------------------------------------')

    working_directory = EARTHQUAKE_WORKING_DIRECTORY

    pattern = re.compile(GRID_FILE_PATTERN)
    shake_dir = os.path.join(working_directory, event_id)
    for root, dirs, files in os.walk(shake_dir):
        for name in files:
            pathname = os.path.join(root, name)
            if pattern.search(pathname):
                return True
    return False


@app.task(
    name='realtime.tasks.earthquake.shake_folder_list',
    queue='inasafe-realtime')
def shake_folder_list():
    LOGGER.info('-------------------------------------------')
    LOGGER.info('Check Shake Folder List')

    working_directory = EARTHQUAKE_WORKING_DIRECTORY

    # iterate directory
    dirlist = []
    for dir in os.listdir(working_directory):
        if check_event_exists(dir):
            # collect dir name
            dirlist.append(dir)

    return dirlist
