# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Ftp Client for Retrieving ftp data.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'imajimatika@gmail.com'
__version__ = '0.5.0'
__date__ = '14/01/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import shutil
from datetime import datetime
from rt_exceptions import (FileNotFoundError,
                           EventIdError,
                           NetworkError,
                           EventValidationError,
                           CopyError
                           )
from sftp_client import SFtpClient
from utils import is_event_id
import logging
LOGGER = logging.getLogger('InaSAFE')
from utils import shakemap_cache_dir, shakemap_extract_dir, mk_dir


default_host = '118.97.83.243'
def_user_name = 'geospasial'
def_password = os.environ['QUAKE_SERVER_PASSWORD']
def_work_dir = 'shakemaps'


class SftpShakeData:
    """A class for retrieving, reading data from shakefiles.
    Shake files are provide on server and can be accessed using SSH protocol.

    The shape files currently located under shakemaps directory in a folder
    named by the event id (which represent the timestamp of the event of the
    shake)

    There are numerous files in that directory but there is only really one
    that we are interested in:

        * grid.xml - which contains all the metadata pertaining to the event

    It's located in under output/grid.xml under each event directory

    The remaining files are fetched for completeness and possibly use in the
    future.

    This class provides a high level interface for retrieving this data and
    then extracting various by products from it

    Note :
        * inspired by shake_data.py but modified according to SSH protocol

    """

    def __init__(self,
                 event=None,
                 host=default_host,
                 user_name=def_user_name,
                 password=def_password,
                 working_dir=def_work_dir,
                 force_flag=False):
        """Constructor for the SftpShakeData class
        :param event: (Optional) a string representing the event id
                  that this raster is associated with. e.g. 20110413170148.
                  **If no event id is supplied, a query will be made to the
                  ftp server, and the latest event id assigned.**
        :param host: (Optional) a string representing the ip address
                  or host name of the server from which the data should be
                  retrieved. It assumes that the data is in the root directory.
        """
        self.event_id = event
        self.host = host
        self.username = user_name
        self.password = password
        self.workdir = working_dir
        self.force_flag = force_flag
        self.sftpclient = SFtpClient(
            self.host, self.username, self.password, self.workdir)

        if self.event_id is None:
            try:
                self.get_latest_event_id()
            except NetworkError:
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
            message = ('No id was passed to the constructor and the '
                       'latest id could not be retrieved from the'
                       'server.')
            LOGGER.exception('ShakeData initialisation failed')
            raise EventIdError(message)

    def reconnect_sftp(self):
        """Reconnect to the server."""
        self.sftpclient = SFtpClient(self.host,
                                     self.username,
                                     self.password,
                                     self.workdir)

    def validate_event(self):
        """Check that the event associated with this instance exists either
        in the local event cache, or on the remote ftp site.

        :return: True if valid, False if not

        :raises: NetworkError
        """
        # First check local cache
        if self.is_cached():
            return True
        else:
            return self.is_on_server()

    def is_cached(self):
        """Check the event associated with this instance exists in cache.

        Args: None

        Returns: True if locally cached, False if not

        Raises: None
        """
        xml_file_path = self.cache_paths()
        if os.path.exists(xml_file_path):
            return True
        else:
            LOGGER.debug('%s is not cached' % xml_file_path)
            return False

    def cache_paths(self):
        """Return the paths to the inp and out files as expected locally.

        :return: grid.xml local cache paths.
        :rtype: str
        """

        xml_file_name = self.file_name()
        xml_file_path = os.path.join(
            shakemap_cache_dir(), self.event_id, xml_file_name)
        return xml_file_path

    #noinspection PyMethodMayBeStatic
    def file_name(self):
        """Return file names for the inp and out files based on the event id.

        For this class, only the grid.xml that is used.

        :return: grid.xml
        :rtype: str
        """
        return 'grid.xml'

    def is_on_server(self):
        """Check the event associated with this instance exists on the server.

        :return: True if valid, False if not

        :raises: NetworkError
        """
        remote_xml_path = os.path.join(
            self.sftpclient.workdir_path, self.event_id)
        return self.sftpclient.is_path_exist(remote_xml_path)

    def get_list_event_ids(self):
        """Get all event id indicated by folder in remote_path
        """
        dirs = self.sftpclient.get_listing(my_func=is_event_id)
        if len(dirs) == 0:
            raise Exception('List event is empty')
        return dirs

    def get_latest_event_id(self):
        """Return latest event id.
        """
        event_ids = self.get_list_event_ids()

        now = datetime.now()
        now = int(
            '%04d%02d%02d%02d%02d%02d' % (
                now.year, now.month, now.day, now.hour, now.minute,
                now.second
            ))

        if event_ids is not None:
            event_ids.sort()

        latest_event_id = now + 1
        while int(latest_event_id) > now:
            if len(event_ids) < 1:
                raise EventIdError('Latest Event Id could not be obtained')
            latest_event_id = event_ids.pop()

        self.event_id = latest_event_id
        return self.event_id

    def fetch_file(self, retries=3):
        """Private helper to fetch a file from the sftp site.

        :param retries: int - number of reattempts that should be made in
                in case of network error etc.
          e.g. for event 20110413170148 this file would be fetched::
                20110413170148 directory

        .. note:: If a cached copy of the file exits, the path to the cache
           copy will simply be returned without invoking any network requests.

        :return: A string for the dataset path on the local storage system.
        :rtype: str

        :raises: EventUndefinedError, NetworkError
        """
        local_path = os.path.join(shakemap_cache_dir(), self.event_id)
        local_parent_path = os.path.join(local_path, 'output')
        xml_file = os.path.join(local_parent_path, self.file_name())
        if os.path.exists(xml_file):
            return local_path

        # fetch from sftp
        trials = [i + 1 for i in xrange(retries)]
        remote_path = os.path.join(self.sftpclient.workdir_path, self.event_id)
        xml_remote_path = os.path.join(remote_path, 'output', self.file_name())
        for my_counter in trials:
            last_error = None
            try:
                mk_dir(local_path)
                mk_dir(os.path.join(local_path, 'output'))
                self.sftpclient.download_path(
                    xml_remote_path, local_parent_path)
            except NetworkError, e:
                last_error = e
            except:
                LOGGER.exception('Could not fetch shake event from server %s'
                                 % remote_path)
                raise
            if last_error is None:
                return local_path
            else:
                self.reconnect_sftp()

            LOGGER.info('Fetching failed, attempt %s' % my_counter)
        LOGGER.exception('Could not fetch shake event from server %s'
                         % remote_path)
        raise Exception('Could not fetch shake event from server %s'
                        % remote_path)

    def extract_dir(self):
        """A helper method to get the path to the extracted datasets.

        :return: A string representing the absolute local filesystem path to
            the unzipped shake event dir. e.g.
            :file:`/tmp/inasafe/realtime/shakemaps-extracted/20120726022003`

        :raises: Any exceptions will be propagated
        """
        return os.path.join(shakemap_extract_dir(), self.event_id)

    def extract(self, force_flag=False):
        """Checking the grid.xml file in the machine, if found use it.
        Else, download from the server
        :param force_flag: force flag to extract.
        """
        final_grid_xml_file = os.path.join(self.extract_dir(), 'grid.xml')
        if not os.path.exists(self.extract_dir()):
            mk_dir(self.extract_dir())
        if force_flag or self.force_flag:
            self.remove_extracted_files()
        elif os.path.exists(final_grid_xml_file):
            return final_grid_xml_file

        # download data
        local_path = self.fetch_file()
        # move grid.xml to the correct directory
        expected_grid_xml_file = os.path.join(local_path, 'output', 'grid.xml')
        if not os.path.exists(expected_grid_xml_file):
            raise FileNotFoundError(
                'The output does not contain an ''%s file.' %
                expected_grid_xml_file)

        # move the file we care about to the top of the extract dir
        shutil.copyfile(os.path.join(
            self.extract_dir(), expected_grid_xml_file), final_grid_xml_file)
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
