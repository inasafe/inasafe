# coding=utf-8
import logging
import os

from realtime.ash.make_map import process_event
from realtime.celery_app import app
from realtime.celeryconfig import ASH_WORKING_DIRECTORY
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/15/16'


# Initialized in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


@app.task(
    name='realtime.tasks.ash.process_ash', queue='inasafe-realtime')
def process_ash(
        event_time=None,
        volcano_name=None,
        volcano_location=None,
        eruption_height=None,
        region=None,
        alert_level=None,
        hazard_url=None):
    LOGGER.info('-------------------------------------------')

    # if 'INASAFE_LOCALE' in os.environ:
    #     locale_option = os.environ['INASAFE_LOCALE']
    # else:
    #     locale_option = 'en'
    locale_option = 'en'

    working_directory = ASH_WORKING_DIRECTORY
    try:
        process_event(
            working_directory,
            locale_option=locale_option,
            event_time=event_time,
            volcano_name=volcano_name,
            volcano_location=volcano_location,
            eruption_height=eruption_height,
            region=region,
            alert_level=alert_level,
            hazard_url=hazard_url)
        LOGGER.info('Process event end.')
        return True
    except Exception as e:
        LOGGER.exception(e)

    return False
