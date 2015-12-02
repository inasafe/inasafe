# coding=utf-8
import json
import logging

import os

import sys

# noinspection PyPackageRequirements

from datetime import datetime

from realtime.flood.flood_event import FloodEvent
from realtime.utilities import realtime_logger_name, data_dir

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '11/24/15'


LOGGER = logging.getLogger(realtime_logger_name())


def process_event(working_directory):
    """Process floodmap event

    :param working_dir:
    :return:
    """
    # population_path = os.path.join(
    #     os.environ['INASAFE_POPULATION_PATH'],
    #     'exposure',
    #     'population.tif')
    population_path = os.environ['INASAFE_FLOOD_POPULATION_PATH']

    # check settings file
    settings_file = os.path.join(
        data_dir(), 'settings', 'flood-settings.json')
    if not os.path.exists(settings_file):
        default_settings = {
            'duration': 6,
            'level': 'rw'
        }
        with open(settings_file, 'w+') as f:
            f.write(json.dumps(default_settings))

    with open(settings_file) as f:
        settings = json.loads(f.read())

    duration = settings['duration']
    level = settings['level']

    allowed_duration = [1, 3, 6]
    try:
        duration = int(duration)
        if duration not in allowed_duration:
            raise Exception()
    except Exception as e:
        sys.exit(
            'Valid duration are: %s' % (
                ','.join([str(i) for i in allowed_duration]),
            )
        )

    allowed_level = ['subdistrict', 'village', 'rw']
    if level not in allowed_level:
        sys.exit(
            'Valid level are: %s' % ','.join(allowed_level)
        )

    LOGGER.info('Creating Flood Event.')
    now = datetime.utcnow()
    event = FloodEvent(
        working_dir=working_directory,
        population_raster_path=population_path,
        duration=duration,
        level=level,
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour
        )

    event.calculate_impact()
    event.generate_report()


if __name__ == '__main__':
    LOGGER.info('-------------------------------------------')

    if 'INASAFE_LOCALE' in os.environ:
        locale_option = os.environ['INASAFE_LOCALE']
    else:
        locale_option = 'en'

    if len(sys.argv) > 2:
        sys.exit(
            'Usage:\n%s [working_dir]'
        )
    working_directory = sys.argv[1]
    process_event(working_directory)
