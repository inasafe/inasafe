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
import logging

from realtime.sftp_client import SFtpClient
from realtime.utilities import is_event_id
from realtime.utilities import (
    shakemap_cache_dir,
    shakemap_extract_dir,
    make_directory,
    realtime_logger_name)
from realtime.exceptions import (
    FileNotFoundError,
    EventIdError,
    NetworkError,
    EventValidationError,
    CopyError,
    SFTPEmptyError)
from realtime.sftp_configuration.configuration import (
    get_sftp_base_url,
    get_sftp_port,
    get_sftp_user_name,
    get_sftp_user_password,
    get_sftp_base_path)


LOGGER = logging.getLogger(realtime_logger_name())


class SftpShakeData:
    """A class for retrieving, reading data from shake files.
    Shake files are provided on server and can be accessed using SSH protocol.

    The shake files currently located under BASE_PATH directory in a folder
    named by the event id (which represent the timestamp of the event of the
    shake)

    There are numerous files in that directory but there is only really one
    that we are interested in:

        * grid.xml - which contains all the metadata pertaining to the event

    It's located at output/grid.xml under each event directory

    The remaining files are fetched for completeness and possibly use in the
    future.

    This class provides a high level interface for retrieving this data and
    then extracting various by products from it

    Note :
        * inspired by shake_data.py but modified according to SSH protocol

    """

    def __init__(self,
                 event=None,
                 host=get_sftp_base_url(),
                 port=get_sftp_port(),
                 user_name=get_sftp_user_name(),
                 password=get_sftp_user_password(),
                 working_dir=get_sftp_base_path(),
                 force_flag=False):
        """Constructor for the SftpShakeData class.

        :param event: A string representing the event id that this raster is
            associated with. e.g. 20110413170148 (Optional).
            **If no event id is supplied, a query will be made to the ftp
            server, and the latest event id assigned.**
        :type event: str

        :param host: A string representing the ip address or host name of the
            server from which the data should be retrieved. It assumes that
            the data is in the root directory (Optional).
        :type host: str

        :param port: The port of the host.
        :type port: int
        """
        self.event_id = event
        self.host = host
        self.port = port
        self.username = user_name
        self.password = password
        self.working_dir = working_dir
        self.force_flag = force_flag
        self.input_file_name = 'grid.xml'

        self.sftp_client = SFtpClient(
            self.host,
            self.port,
            self.username,
            self.password,
            self.working_dir)

        if self.event_id is None:
            try:
                self.get_latest_event_id()
            except (SFTPEmptyError, NetworkError, EventIdError):
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

    def reconnect_sftp(self):
        """Reconnect to the server."""
        self.sftp_client = SFtpClient(
            self.host, self.username, self.password, self.working_dir)

    def validate_event(self):
        """Check that the event associated with this instance exists.

         This will check either in the local event cache or on the remote ftp
         site.

        :return: True if valid, False if not.
        :rtype: bool

        :raises: NetworkError
        """
        # First check local cache
        if self.is_cached():
            return True
        else:
            return self.is_on_server()

    def is_cached(self):
        """Check the event associated with this instance exists in cache.

        :return: True if locally cached, otherwise False.
        :rtype: bool

        :raises: None
        """
        xml_file_path = self.cache_paths()
        if os.path.exists(xml_file_path):
            return True
        else:
            LOGGER.debug('%s is not cached' % xml_file_path)
            return False

    def cache_paths(self):
        """Return the paths to the inp and out files as expected locally.

        :return: The grid.xml local cache path.
        :rtype: str
        """

        xml_file_name = self.input_file_name
        xml_file_path = os.path.join(
            shakemap_cache_dir(), self.event_id, xml_file_name)
        return xml_file_path

    def is_on_server(self):
        """Check the event associated with this instance exists on the server.

        :return: True if valid, False if not.

        :raises: NetworkError
        """
        remote_xml_path = os.path.join(
            self.sftp_client.working_dir_path, self.event_id)
        return self.sftp_client.path_exists(remote_xml_path)

    def get_list_event_ids(self):
        """Get all event id indicated by folder in remote_path."""
        dirs = self.sftp_client.get_listing(function=is_event_id)
        if len(dirs) == 0:
            raise SFTPEmptyError(
                'The SFTP directory does not contain any shakemaps.')
        return dirs

    def get_latest_event_id(self):
        """Return latest event id."""
        try:
            event_ids = self.get_list_event_ids()
        except SFTPEmptyError:
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

    def fetch_file(self, retries=3):
        """Private helper to fetch a file from the sftp site.

        .. note:: If a cached copy of the file exits, the path to the cache
           copy will simply be returned without invoking any network requests.

        :param retries: The number of reattempts that should be made in
            case of e.g network error.
            e.g. for event 20110413170148 this file would be fetched::
            20110413170148 directory
        :type retries: int

        :return: A string for the dataset path on the local storage system.
        :rtype: str

        :raises: EventUndefinedError, NetworkError
        """
        local_path = os.path.join(shakemap_cache_dir(), self.event_id)
        local_parent_path = os.path.join(local_path, 'output')
        xml_file = os.path.join(local_parent_path, self.input_file_name)
        if os.path.exists(xml_file):
            return local_path

        # fetch from sftp
        trials = [i + 1 for i in xrange(retries)]
        remote_path = os.path.join(
            self.sftp_client.working_dir_path, self.event_id)
        xml_remote_path = os.path.join(
            remote_path, 'output', self.input_file_name)

        for counter in trials:
            last_error = None
            try:
                make_directory(local_path)
                make_directory(os.path.join(local_path, 'output'))
                self.sftp_client.download_path(
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
            LOGGER.info('Fetching failed, attempt %s' % counter)

        LOGGER.exception('Could not fetch shake event from server %s'
                         % remote_path)
        raise Exception('Could not fetch shake event from server %s'
                        % remote_path)

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
        Else, download from the server.

        :param force_flag: force flag to extract.
        :type force_flag: bool

        :return: a string containing the grid.xml paths e.g.::
            grid_xml = myShakeData.extract()
            print grid_xml
            /tmp/inasafe/realtime/shakemaps-extracted/20131105060809/grid.xml
        """
        final_grid_xml_file = os.path.join(self.extract_dir(), 'grid.xml')
        if not os.path.exists(self.extract_dir()):
            make_directory(self.extract_dir())
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
