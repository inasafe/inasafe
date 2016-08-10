# coding=utf-8
import json
import logging
import os
import sys

from dateutil.parser import parse

from realtime.ash.ash_event import AshEvent
from realtime.ash.push_ash import push_ash_event_to_rest
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/13/16'

# Initialized in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


def process_event(
        working_dir,
        locale_option='en',
        event_time=None,
        volcano_name=None,
        volcano_location=None,
        eruption_height=None,
        region=None,
        alert_level=None,
        hazard_url=None):
    """

    :param working_dir: The working directory of floodmaps report
    :param locale_option: the locale of the report
    :param event_time:
    :param volcano_name:
    :param volcano_location:
    :param eruption_height:
    :param region:
    :param alert_level:
    :param hazard_url:
    :return:
    """
    population_path = os.environ['INASAFE_ASH_POPULATION_PATH']
    landcover_path = os.environ['INASAFE_ASH_LANDCOVER_PATH']
    cities_path = os.environ['INASAFE_ASH_CITIES_PATH']
    airport_path = os.environ['INASAFE_ASH_AIRPORT_PATH']
    volcano_path = os.environ['INASAFE_ASH_VOLCANO_PATH']
    highlight_base_path = os.environ['INASAFE_ASH_HIGHLIGHT_BASE_PATH']
    overview_path = os.environ['INASAFE_ASH_OVERVIEW_PATH']

    # We always want to generate en products too so we manipulate the locale
    # list and loop through them:
    locale_list = [locale_option]
    if 'en' not in locale_list:
        locale_list.append('en')

    for locale in locale_list:
        LOGGER.info('Creating Ash Event for locale %s.' % locale)
        event = AshEvent(
            working_dir=working_dir,
            locale='en',
            event_time=event_time,
            volcano_name=volcano_name,
            volcano_location=volcano_location,
            eruption_height=eruption_height,
            region=region,
            alert_level=alert_level,
            overview_path=overview_path,
            population_path=population_path,
            highlight_base_path=highlight_base_path,
            volcano_path=volcano_path,
            landcover_path=landcover_path,
            cities_path=cities_path,
            airport_path=airport_path,
            # It will be processed either if it is a file or a url
            hazard_path=hazard_url)

        event.calculate_impact()
        event.generate_report()
        ret = push_ash_event_to_rest(ash_event=event)
        LOGGER.info('Is Push successful? %s.' % bool(ret))


def extract_folder_metadata(event_folder):
    """Parse ash event folder metadata to python dict

    example of event folder

    20160720112233-Sinabung

    example metadata json:
    {
        'volcano_name': 'Sinabung',
        'volcano_location': [107, 6],
        'alert_level': 'Siaga',
        'eruption_height': 7000, # eruption height in meters
        'event_time': '2016-07-20 11:22:33 +0700',
        'region': 'North Sumatra'
    }

    :param event_folder:
    :return:
    """
    # check folder exists
    if not os.path.exists(event_folder):
        raise IOError("%s doesn't exists" % event_folder)

    # check metadata file exists
    metadata_path = os.path.join(event_folder, 'metadata.json')
    if not os.path.exists(metadata_path):
        raise IOError("Metadata file doesn't exists")

    # extract volcano name
    with open(metadata_path) as f:
        metadata = json.loads(f.read())
    # parse date
    metadata['event_time'] = parse(metadata['event_time'])
    return metadata

if __name__ == '__main__':
    LOGGER.info('-------------------------------------------')

    print sys.argv

    # if 'INASAFE_LOCALE' in os.environ:
    #     locale_op = os.environ['INASAFE_LOCALE']
    # else:
    #     locale_op = 'en'
    locale_op = 'en'

    if len(sys.argv) > 3:
        sys.exit(
            'Usage:\n%s [working_dir] [event_folder]')
    working_directory = sys.argv[1]
    event_fold = None
    if len(sys.argv) == 3:
        event_fold = sys.argv[2]
        event_fold = os.path.join(working_directory, event_fold)

    event_metadata = extract_folder_metadata(event_fold)
    try:
        process_event(
            working_directory,
            locale_option=locale_op,
            event_time=event_metadata['event_time'],
            volcano_name=event_metadata['volcano_name'],
            volcano_location=event_metadata['volcano_location'],
            eruption_height=event_metadata['eruption_height'],
            region=event_metadata['region'],
            alert_level=event_metadata['alert_level'])
        LOGGER.info('Process event end.')
    except Exception as e:
        LOGGER.exception(e)
