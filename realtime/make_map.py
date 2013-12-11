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
import sys
import logging
from urllib2 import URLError
from zipfile import BadZipfile

from ftp_client import FtpClient
from sftp_client import SFtpClient
from utils import setup_logger, data_dir, is_event_id
from shake_event import ShakeEvent
# Loading from package __init__ not working in this context so manually doing
setup_logger()
LOGGER = logging.getLogger('InaSAFE')


def process_event(event_id=None, locale='en'):
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
        'IDN_mosaic',
        'popmap10_all.tif')

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
                    event_id=event_id,
                    locale=locale,
                    force_flag=force_flag,
                    population_raster_path=population_path)
            else:
                shake_event = ShakeEvent(
                    event_id=event_id,
                    locale=locale,
                    force_flag=force_flag)
        except (BadZipfile, URLError):
            # retry with force flag true
            if os.path.exists(population_path):
                shake_event = ShakeEvent(
                    event_id=event_id,
                    locale=locale,
                    force_flag=True,
                    population_raster_path=population_path)
            else:
                shake_event = ShakeEvent(
                    event_id=event_id,
                    locale=locale,
                    force_flag=True)
        except:
            LOGGER.exception('An error occurred setting up the shake event.')
            return

        LOGGER.info('Event Id: %s', shake_event)
        LOGGER.info('-------------------------------------------')

        shake_event.render_map(force_flag)

LOGGER.info('-------------------------------------------')

if 'INASAFE_LOCALE' in os.environ:
    my_locale = os.environ['INASAFE_LOCALE']
else:
    my_locale = 'en'

if len(sys.argv) > 2:
    sys.exit('Usage:\n%s [optional shakeid]\nor\n%s --list' % (
        sys.argv[0], sys.argv[0]))
elif len(sys.argv) == 2:
    print('Processing shakemap %s' % sys.argv[1])

    my_event_id = sys.argv[1]
    if my_event_id in '--list':
#        myFtpClient = FtpClient()
        sftp_client = SFtpClient()
#        myListing = myFtpClient.get_listing()
        dir_listing = sftp_client.get_listing(my_func=is_event_id)
        for event in dir_listing:
            print event
        sys.exit(0)
    elif my_event_id in '--run-all':
        #
        # Caution, this code path gets memory leaks, use the
        # batch file approach rather!
        #
        myFtpClient = FtpClient()
        dir_listing = myFtpClient.get_listing()
        for event in dir_listing:
            if 'out' not in event:
                continue
            event = event.replace('ftp://118.97.83.243/', '')
            event = event.replace('.out.zip', '')
            print 'Processing %s' % event
            # noinspection PyBroadException
            try:
                process_event(event, my_locale)
            except:  # pylint: disable=W0702
                LOGGER.exception('Failed to process %s' % event)
        sys.exit(0)
    else:
        process_event(my_event_id, my_locale)

else:
    my_event_id = None
    print('Processing latest shakemap')
    # noinspection PyBroadException
    try:
        process_event(locale=my_locale)
    except:  # pylint: disable=W0702
        LOGGER.exception('Process event failed')
