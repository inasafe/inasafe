# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Getting shake data from local storage**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__version__ = '3.0'
__date__ = '14/12/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import shutil
from datetime import datetime
import logging
import filecmp


from realtime.utilities import is_event_id
from realtime.utilities import (
    shakemap_extract_dir,
    make_directory,
    realtime_logger_name)
from realtime.exceptions import (
    FileNotFoundError,
    EventIdError,
    EventValidationError,
    CopyError,
    EmptyShakeDirectoryError)

LOGGER = logging.getLogger(realtime_logger_name())


class ShakeData(object):
    """A class for reading data from shake files.

    The shake files currently located under BASE_PATH directory in a folder
    named by the event id (which represent the timestamp of the event of the
    shake)

    There are numerous files in that directory but there is only really one
    that we are interested in:

        * grid.xml - which contains all the metadata pertaining to the event

    It's located at output/grid.xml under each event directory
    """

    def __init__(self,
                 working_dir,
                 event=None,
                 force_flag=False):
        """Constructor for the LocalShakeData class.

        :param working_dir: The working directory where all the shakemaps are
            located.
        :type working_dir: str

        :param event: A string representing the event id that this raster is
            associated with. e.g. 20110413170148 (Optional).
            **If no event id is supplied, the latest event id will be
            assigned.**
        :type event: str

        :param force_flag: The flag if we want to force move data from
            working_dir to extracted dir.
        :type force_flag: bool
        """
        self.event_id = event
        self.working_dir = working_dir
        self.force_flag = force_flag
        self.input_file_name = 'grid.xml'

        if self.event_id is None:
            try:
                self.get_latest_event_id()
            except (EmptyShakeDirectoryError, EventIdError):
                raise
        else:
            # If we fetched it above using get_latest_event_id we assume it is
            # already validated.
            try:
                self.validate_event()
            except EventValidationError:
                raise
        # If event_id is still None after all the above, moan....
        if self.event_id is None:
            message = ('No id was passed to the constructor and the  latest '
                       'id could not be retrieved from the server.')
            LOGGER.exception('ShakeData initialisation failed')
            raise EventIdError(message)

    def validate_event(self):
        """Check that the event exists in working dir.

        :return: True if valid, False if not.
        :rtype: bool
        """
        event_path = os.path.join(
            self.working_dir, self.event_id)
        return os.path.exists(event_path)

    @staticmethod
    def get_list_event_ids_from_folder(working_dir):
        """Get all event id indicated by folder in working dir."""
        if os.path.exists(working_dir):
            directories = os.listdir(working_dir)
        else:
            LOGGER.debug(
                'Directory %s does not exist, return None' % working_dir)
            return None
        # Filter the dirs to only contain valid event dirs
        valid_dirs = []
        for directory in directories:
            if is_event_id(directory):
                valid_dirs.append(directory)

        if len(valid_dirs) == 0:
            raise EmptyShakeDirectoryError(
                'The directory %s does not contain any shakemaps.' %
                working_dir)
        return valid_dirs

    def get_list_event_ids(self):
        return ShakeData.get_list_event_ids_from_folder(self.working_dir)

    def get_latest_event_id(self):
        """Return latest event id."""
        try:
            event_ids = self.get_list_event_ids()
        except EmptyShakeDirectoryError:
            raise

        now = datetime.now()
        now = int(
            '%04d%02d%02d%02d%02d%02d' %
            (now.year, now.month, now.day, now.hour, now.minute, now.second))

        if event_ids is not None:
            event_ids.sort()

        latest_event_id = now + 1
        while int(latest_event_id) > now:
            if len(event_ids) < 1:
                raise EventIdError('Latest Event Id could not be obtained')
            latest_event_id = event_ids.pop()

        self.event_id = latest_event_id
        return self.event_id

    def extract_dir(self):
        """A helper method to get the path to the extracted datasets.

        :return: A string representing the absolute local filesystem path to
            the unzipped shake event dir. e.g.
            :file:`/tmp/inasafe/realtime/shakemaps-extracted/20131105060809`
        :rtype: str

        :raises: Any exceptions will be propagated.
        """
        return os.path.join(shakemap_extract_dir(), self.event_id)

    def extract(self, force_flag=False):
        """Checking the grid.xml file in the machine, if found use it.

        :param force_flag: force flag to extract.
        :type force_flag: bool

        :return: a string containing the grid.xml paths e.g.::
            grid_xml = local_shake_data.extract()
            print grid_xml
            /tmp/inasafe/realtime/shakemaps-extracted/20131105060809/grid.xml
        """
        final_grid_xml_file = os.path.join(self.extract_dir(), 'grid.xml')

        # move grid.xml from working dir to the extracted dir
        local_path = os.path.join(self.working_dir, self.event_id)
        source_grid_xml = os.path.join(local_path, 'output', 'grid.xml')

        if not os.path.exists(self.extract_dir()):
            make_directory(self.extract_dir())

        if force_flag or self.force_flag:
            self.remove_extracted_files()
        elif os.path.exists(final_grid_xml_file):
            if filecmp.cmp(final_grid_xml_file, source_grid_xml):
                return final_grid_xml_file
            # if it is not identical, copy again

        if not os.path.exists(source_grid_xml):
            raise FileNotFoundError(
                'The output does not contain %s file.' %
                source_grid_xml)

        # move the file we care about to the top of the extract dir
        shutil.copyfile(source_grid_xml, final_grid_xml_file)
        if not os.path.exists(final_grid_xml_file):
            raise CopyError('Error copying grid.xml')
        return final_grid_xml_file

    def remove_extracted_files(self):
        """Tidy up the filesystem by removing all extracted files
        for the given event instance.

        :raises: Any error e.g. file permission error will be raised.
        """
        extracted_dir = self.extract_dir()
        if os.path.isdir(extracted_dir):
            shutil.rmtree(extracted_dir)
