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
from realtime.push_shake import push_shake_event_to_rest

__author__ = 'tim@kartoza.com'
__version__ = '0.5.0'
__date__ = '30/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import sys
import logging
from urllib2 import URLError
from zipfile import BadZipfile

from realtime.utilities import data_dir, is_event_id, realtime_logger_name
from realtime.shake_event import ShakeEvent
from realtime.exceptions import EmptyShakeDirectoryError

# Initialised in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


def process_event(working_dir=None, event_id=None, locale='en'):
    """Launcher that actually runs the event processing.

    :param event_id: The event id to process. If None the latest event will
       be downloaded and processed.
    :type event_id: str

    :param locale: The locale that will be used. Default to en.
    :type locale: str
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
            if os.path.exists(population_path):
                shake_event = ShakeEvent(
                    working_dir=working_dir,
                    event_id=event_id,
                    locale=locale,
                    force_flag=force_flag,
                    population_raster_path=population_path)
            else:
                shake_event = ShakeEvent(
                    working_dir=working_dir,
                    event_id=event_id,
                    locale=locale,
                    force_flag=force_flag)
        except (BadZipfile, URLError):
            # retry with force flag true
            if os.path.exists(population_path):
                shake_event = ShakeEvent(
                    working_dir=working_dir,
                    event_id=event_id,
                    locale=locale,
                    force_flag=True,
                    population_raster_path=population_path)
            else:
                shake_event = ShakeEvent(
                    working_dir=working_dir,
                    event_id=event_id,
                    locale=locale,
                    force_flag=True)
        except EmptyShakeDirectoryError as ex:
            LOGGER.info(ex)
            return
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception('An error occurred setting up the shake event.')
            return

        LOGGER.info('Event Id: %s', shake_event)
        LOGGER.info('-------------------------------------------')

        shake_event.render_map(force_flag)
        # push the shakemap to realtime server
        push_shake_event_to_rest(shake_event)


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
        except:  # pylint: disable=W0702
            LOGGER.exception('Process event failed')
