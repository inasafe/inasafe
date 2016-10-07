# coding=utf-8
import json
import logging

import os

import sys

# noinspection PyPackageRequirements
from datetime import datetime

from realtime.flood.flood_event import FloodEvent
from realtime.flood.push_flood import push_flood_event_to_rest
from realtime.utilities import realtime_logger_name, data_dir

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '11/24/15'

# Initialized in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


def process_event(working_directory, locale_option='en', dummy_folder=None):
    """Process floodmap event

    :param working_dir: The working directory of floodmaps report
    :param locale_option: the locale of the report
    :param dummy_folder: the location of dummy_folder in the working dir.
        this dummy folder should have flood_data.json on it, and the folder
        should be named like the id of the event.
    :return:
    """
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

    # We always want to generate en products too so we manipulate the locale
    # list and loop through them:
    locale_list = [locale_option]
    if 'en' not in locale_list:
        locale_list.append('en')

    for locale in locale_list:
        LOGGER.info('Creating Flood Event for locale %s.' % locale)
        now = datetime.utcnow()
        try:
            event = FloodEvent(
                working_dir=working_directory,
                locale=locale,
                population_path=population_path,
                duration=duration,
                level=level,
                year=now.year,
                month=now.month,
                day=now.day,
                hour=now.hour,
                dummy_report_folder=dummy_folder)

            event.calculate_impact()
            event.generate_report()
            ret = push_flood_event_to_rest(flood_event=event)
        except Exception as e:
            LOGGER.error(e)
            ret = False
        LOGGER.info('Is Push successful? %s.' % bool(ret))


if __name__ == '__main__':
    LOGGER.info('-------------------------------------------')

    print sys.argv

    if 'INASAFE_LOCALE' in os.environ:
        locale_option = os.environ['INASAFE_LOCALE']
    else:
        locale_option = 'en'

    if len(sys.argv) > 3:
        sys.exit(
            'Usage:\n%s [working_dir] [dummy_folder]'
        )
    working_directory = sys.argv[1]
    dummy_folder = None
    if len(sys.argv) == 3:
        dummy_folder = sys.argv[2]
    try:
        process_event(
            working_directory, locale_option, dummy_folder=dummy_folder)
        LOGGER.info('Process event end.')
    except Exception as e:
        LOGGER.exception(e)
