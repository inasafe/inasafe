# coding=utf-8
"""This script will tell InaSAFE Realtime the newest shakemap available.

This will make new shakemap processed after a user is pushing a shakemap.
"""
import logging
import os
import re
import sys

import datetime
import pyinotify
from tzlocal import get_localzone

from realtime.earthquake.make_map import process_event
from realtime.earthquake.push_shake import notify_realtime_rest
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '03/09/15'


LOGGER = logging.getLogger(realtime_logger_name())


class ShakemapPushHandler(pyinotify.ProcessEvent):

    def __init__(self, working_dir, callback=None):
        """

        :param working_dir: location of shakemaps folder
        :param callback: function which receives a shake_id
        :return:
        """
        self.working_dir = working_dir
        self.callback = callback

    def process_IN_CREATE(self, event):
        """Handle created event of grid.xml.

        :param event: Inotify event
        """
        # we only listen to pushed output/grid.xml files
        rel_path = os.path.relpath(event.pathname, self.working_dir)
        pattern = re.compile('^(?P<shake_id>\d{14})/output/grid\.xml$')
        if os.path.exists(event.pathname) and pattern.search(rel_path):
            # if we got grid.xml
            LOGGER.info('Got grid.xml: %s' % rel_path)
            if self.callback:
                shake_id = pattern.match(rel_path).group('shake_id')
                self.callback(shake_id=shake_id)

    def process_IN_MOVED_TO(self, event):
        """Handle rename event of grid.xml.

        Should be the same with Create event

        :param event: Inotify event
        """
        self.process_IN_CREATE(event)

    def process_IN_MODIFY(self, event):
        """Handle modify event of grid.xml.

        Should be the same with Create event

        :param event: Inotify event
        """
        self.process_IN_CREATE(event)


def watch_shakemaps_push(
        working_dir, timeout=None, handler=None, daemon=False):
    wm = pyinotify.WatchManager()
    if daemon:
        notifier = pyinotify.ThreadedNotifier(wm, handler, timeout=timeout)
    else:
        notifier = pyinotify.Notifier(wm, handler, timeout=timeout)
    flags = pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_MOVED_TO
    wm.add_watch(working_dir, flags, rec=True, auto_add=True)

    return notifier


if __name__ == '__main__':
    working_dir = sys.argv[1]

    if 'INASAFE_LOCALE' in os.environ:
        locale_option = os.environ['INASAFE_LOCALE']
    else:
        locale_option = 'en'

    def process_shakemap(shake_id=None):
        """Process a given shake_id for realtime shake"""
        LOGGER.info('Inotify received new shakemap')
        tz = get_localzone()
        notify_realtime_rest(datetime.datetime.now(tz=tz))
        done = False
        while not done:
            try:
                done = process_event(
                    working_dir=working_dir,
                    event_id=shake_id,
                    locale=locale_option)
            except Exception as e:  # pylint: disable=W0702
                LOGGER.info('Process event failed')
                LOGGER.exception(e)
                LOGGER.info('Retrying to process event')
        LOGGER.info('Shakemap %s handled' % (shake_id, ))

    handler = ShakemapPushHandler(working_dir, callback=process_shakemap)
    notifier = watch_shakemaps_push(working_dir, daemon=True, handler=handler)
    LOGGER.info('Monitoring %s' % working_dir)
    notifier.loop()
