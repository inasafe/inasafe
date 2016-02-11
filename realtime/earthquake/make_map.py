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

__author__ = 'tim@kartoza.com'
__version__ = '0.5.0'
__date__ = '30/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import logging
import os
import sys
from urllib2 import URLError
from zipfile import BadZipfile

from realtime.earthquake.shake_event import ShakeEvent

from realtime.earthquake.push_shake import push_shake_event_to_rest
from realtime.earthquake.shake_data import ShakeData
from realtime.exceptions import EmptyShakeDirectoryError
from realtime.utilities import data_dir, is_event_id, realtime_logger_name

# Initialised in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


def process_event(working_dir=None, event_id=None, locale='en'):
    """Launcher that actually runs the event processing.

    :param event_id: The event id to process. If None the latest event will
       be downloaded and processed.
    :type event_id: str

    :param locale: The locale that will be used. Default to en.
    :type locale: str

    :return: Return True if succeeded
    :rtype: bool
    """
    population_path = os.path.join(
        data_dir(),
        'exposure',
        'population.tif')

    # Use cached data where available
    # Whether we should always regenerate the products
    force_flag = False
    if 'INASAFE_FORCE' in os.environ:
        force_string = os.environ['INASAFE_FORCE']
        if str(force_string).capitalize() == 'Y':
            force_flag = True

    # We always want to generate en products too so we manipulate the locale
    # list and loop through them:
    locale_list = [locale]
    if 'en' not in locale_list:
        locale_list.append('en')

    # Now generate the products
    for locale in locale_list:
        # Extract the event
        # noinspection PyBroadException
        try:
            shake_events = create_shake_events(
                event_id=event_id,
                force_flag=force_flag,
                locale=locale,
                population_path=population_path,
                working_dir=working_dir)
        except (BadZipfile, URLError):
            # retry with force flag true
            shake_events = create_shake_events(
                event_id=event_id,
                force_flag=True,
                locale=locale,
                population_path=population_path,
                working_dir=working_dir)
        except EmptyShakeDirectoryError as ex:
            LOGGER.info(ex)
            return
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception('An error occurred setting up the shake event.')
            return

        LOGGER.info('Event Id: %s', [s.event_id for s in shake_events])
        LOGGER.info('-------------------------------------------')

        for shake_event in shake_events:
            shake_event.render_map(force_flag)
            # push the shakemap to realtime server
            ret = push_shake_event_to_rest(shake_event)
            LOGGER.info('Is Push successful? %s' % bool(ret))

    return True


def create_shake_events(
        event_id=None,
        population_path=None,
        working_dir=None,
        locale='en',
        force_flag=False):
    """

    :param working_dir: The locale working dir where all the shakemaps are
            located.
    :type working_dir: str

    :param event_id: (Optional) Id of the event. Will be used to
        fetch the ShakeData for this event. The grid.xml file in the
        unpacked event will be used to initialise the state of the a
        ShakeGrid instance. If no event id is supplied, the most recent
        event recorded on working dir will be used.
    :type event_id: str

    :param locale:(Optional) string for iso locale to use for outputs.
        Defaults to en. Can also use 'id' or possibly more as translations
        are added.
    :type locale: str

    :param force_flag: Whether to force retrieval of the dataset.
    :type force_flag: bool

    :return: Shake Events to process
    :rtype: list[ShakeEvent]
    """
    shake_events = []

    if not os.path.exists(population_path):
        population_path = None

    # cron job executed this script minutely, so it is possible in one
    # minute that we have more than one shake_event. We can resolve this
    # by only retrieveng the shake id for that particular minute.

    # retrieve all the shake ids
    shake_ids = ShakeData.get_list_event_ids_from_folder(working_dir)
    shake_ids.sort()
    shake_ids.reverse()
    if not shake_ids:
        return []

    if event_id:
        shake_events.append(
            ShakeEvent(
                working_dir=working_dir,
                event_id=event_id,
                locale=locale,
                force_flag=force_flag,
                population_raster_path=population_path)
        )
    else:
        last_int = int(shake_ids[0])
        # sort descending
        for shake_id in shake_ids:
            if last_int - int(shake_id) < 100:
                shake_event = ShakeEvent(
                    working_dir=working_dir,
                    event_id=shake_id,
                    locale=locale,
                    force_flag=force_flag,
                    population_raster_path=population_path)
                shake_events.append(shake_event)
            else:
                break

    return shake_events


if __name__ == '__main__':
    LOGGER.info('-------------------------------------------')

    if 'INASAFE_LOCALE' in os.environ:
        locale_option = os.environ['INASAFE_LOCALE']
    else:
        locale_option = 'en'

    if len(sys.argv) > 3:
        sys.exit(
            'Usage:\n%s [working_dir] \nor\n%s [working_dir] --list\nor%s '
            '[working_dir] --run-all\nor%s '
            '[working_dir] [event_id]' % (
                sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0]))
    elif len(sys.argv) == 3:
        print('The events in the working dir:')
        working_directory = sys.argv[1]
        event_option = sys.argv[2]
        if event_option in '--list':
            dir_listing = os.listdir(working_directory)
            for event in dir_listing:
                print event
            sys.exit(0)
        else:
            print('Processing shakemap %s' % event_option)
            if is_event_id(event_option):
                process_event(
                    working_dir=working_directory,
                    event_id=event_option,
                    locale=locale_option)
            else:
                print('%s is not a valid event ID' % event_option)
    else:
        working_directory = sys.argv[1]
        event_option = None
        print('Processing latest shakemap')
        # noinspection PyBroadException
        try:
            process_event(working_dir=working_directory, locale=locale_option)
            LOGGER.info('Process event end.')
            sys.exit(0)
        except Exception as e:  # pylint: disable=W0702
            LOGGER.info('Process event failed')
            LOGGER.exception(e)
