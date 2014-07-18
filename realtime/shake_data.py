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
import shutil
from datetime import datetime
from zipfile import ZipFile
import logging

from realtime.exceptions import (
    EventUndefinedError,
    EventIdError,
    NetworkError,
    EventValidationError,
    InvalidInputZipError,
    ExtractionError)
from realtime.ftp_client import FtpClient
from realtime.utilities import (
    shakemap_zip_dir,
    shakemap_extract_dir,
    realtime_logger_name)
from realtime.sftp_configuration.base_config import BASE_URL


# The logger is initialised in realtime/__init__
LOGGER = logging.getLogger(realtime_logger_name())


class ShakeData:
    """A class for retrieving, reading, converting and extracting
       data from shakefiles.

    Shake files are provided on an ftp server. There are two files for every
    event:

       * an 'inp' file
       * an 'out' file

    These files are provided on the ftp server as zip files. For example:
        * `<ftp://118.97.83.243/20110413170148.inp.zip>`_
        * `<ftp://118.97.83.243/20110413170148.out.zip>`_

    There are numerous files provided within these two zip files, but there
    is only really one that we are interested in:

        * grid.xml - which contains all the metadata pertaining to the event

    The remaining files are fetched for completeness and possibly use in the
    future.

    This class provides a high level interface for retrieving this data and
    then extracting various by products from it.
    """

    def __init__(self, event=None, host=BASE_URL):
        """Constructor for the ShakeData class.

        :param event: (Optional) a string representing the event id
                that this raster is associated with. e.g. 20110413170148.
                **If no event id is supplied, a query will be made to the
                  ftp server, and the latest event id assigned.**

        :param host: (Optional) a string representing the ip address
                  or host name of the server from which the data should be
                  retrieved. It assumes that the data is in the root directory.
                  Defaults to BASE_URL

        :returns: None

        :raises: None
        """
        self.event_id = event
        self.host = host
        # private Shake event instance associated with this shake dataset
        self._shakeEvent = None
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
                       'latest id could not be retrieved from the server.')
            LOGGER.exception('ShakeData initialisation failed')
            raise EventIdError(message)

    def get_latest_event_id(self):
        """Query the ftp server and determine the latest event id.

        :return: A string containing a valid event id.

        :raises: NetworkError
        """
        ftp_client = FtpClient()
        try:
            ftp_client_list = ftp_client.get_listing()
            ftp_client_list.sort(key=lambda x: x.lower())
        except NetworkError:
            raise
        now = datetime.now()
        now = int(
            '%04d%02d%02d%02d%02d%02d' % (
                now.year, now.month, now.day, now.hour, now.minute, now.second
            ))
        event_id = now + 1
        while int(event_id) > now:
            if len(ftp_client_list) < 1:
                raise EventIdError('Latest Event Id could not be obtained')
            event_id = ftp_client_list.pop().split('/')[-1].split('.')[0]

        if event_id is None:
            raise EventIdError('Latest Event Id could not be obtained')
        self.event_id = event_id

    def is_on_server(self):
        """Check the event associated with this instance exists on the server.

        :return: True if valid, False if not

        :raises: NetworkError
        """
        input_file_name, output_file_name = self.file_names()
        file_list = [input_file_name, output_file_name]
        ftp_client = FtpClient()
        return ftp_client.has_files(file_list)

    def file_names(self):
        """Return file names for the inp and out files based on the event id.

        e.g. 20131105060809.inp.zip, 20131105060809.out.zip

        :return: Tuple Consisting of inp and out local cache paths.
        :rtype: tuple (str, str)

        :raises: None
        """
        input_file_name = '%s.inp.zip' % self.event_id
        output_file_name = '%s.out.zip' % self.event_id
        return input_file_name, output_file_name

    def cache_paths(self):
        """Return the paths to the inp and out files as expected locally.

        :return: Tuple consisting of inp and out local cache paths.
        :rtype: tuple (str, str)

        :raises: None
        """
        input_file_name, output_file_name = self.file_names()
        input_file_path = os.path.join(shakemap_zip_dir(), input_file_name)
        output_file_path = os.path.join(shakemap_zip_dir(), output_file_name)
        return input_file_path, output_file_path

    def is_cached(self):
        """Check the event associated with this instance exists in cache.

        :return: True if locally cached, False if not

        :raises: None
        """
        input_file_path, output_file_path = self.cache_paths()
        if os.path.exists(input_file_path) and \
                os.path.exists(output_file_path):
            # TODO: we should actually try to unpack them for deeper validation
            return True
        else:
            LOGGER.debug('%s is not cached' % input_file_path)
            LOGGER.debug('%s is not cached' % output_file_path)
            return False

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

    #noinspection PyMethodMayBeStatic
    def _fetch_file(self, event_file, retries=3):
        """Private helper to fetch a file from the ftp site.

          e.g. for event 20110413170148 this file would be fetched::

              ftp://118.97.83.243/20110413170148.inp.zip

          and this local file created::

              /tmp/realtime/20110413170148.inp.zip

        .. note:: If a cached copy of the file exits, the path to the cache
           copy will simply be returned without invoking any network requests.

        :param event_file: Filename on server e.g.20110413170148.inp.zip
        :type event_file: str

        :param retries: Number of reattempts that should be made in
                in case of network error etc.
        :type retries: int

        :return: A string for the dataset path on the local storage system.
        :rtype: str

        :raises: EventUndefinedError, NetworkError
        """
        # Return the cache copy if it exists
        local_path = os.path.join(shakemap_zip_dir(), event_file)
        if os.path.exists(local_path):
            return local_path

        #Otherwise try to fetch it using ftp
        for counter in range(retries):
            last_error = None
            try:
                client = FtpClient()
                client.get_file(event_file, local_path)
            except NetworkError, e:
                last_error = e
            except:
                LOGGER.exception(
                    'Could not fetch shake event from server %s'
                    % event_file)
                raise

            if last_error is None:
                return local_path

            LOGGER.info('Fetching failed, attempt %s' % counter)

        LOGGER.exception('Could not fetch shake event from server %s'
                         % event_file)
        raise Exception('Could not fetch shake event from server %s'
                        % event_file)

    def fetch_input(self):
        """Fetch the input file for the event id associated with this class
           e.g. for event 20110413170148 this file would be fetched::

              ftp://118.97.83.243/20110413170148.inp.zip

          and this local file created::

              /tmp/realtime/20110413170148.inp.zip


        :return: A string for the 'inp' dataset path on the local storage
            system.

        :raises: EventUndefinedError, NetworkError
        """
        if self.event_id is None:
            raise EventUndefinedError('Event is none')

        event_file = '%s.inp.zip' % self.event_id
        try:
            return self._fetch_file(event_file)
        except (EventUndefinedError, NetworkError):
            raise

    def fetch_output(self):
        """Fetch the output file for the event id associated with this class.
          e.g. for event 20110413170148 this file would be fetched::

              ftp://118.97.83.243/20110413170148.out.zip

          and this local file created::

              /tmp/realtime/20110413170148.out.zip

        :return: A string for the 'out' dataset path on the local storage
            system.

        :raises: EventUndefinedError, NetworkError
        """
        if self.event_id is None:
            raise EventUndefinedError('Event is none')

        event_file = '%s.out.zip' % self.event_id
        try:
            return self._fetch_file(event_file)
        except (EventUndefinedError, NetworkError):
            raise

    def fetch_event(self):
        """Fetch both the input and output shake data from the server for
        the event id associated with this class.

        :return: A two tuple where the first item is the inp dataset path and
         the second the out dataset path on the local storage system.

        :raises: EventUndefinedError, NetworkError
        """
        if self.event_id is None:
            raise EventUndefinedError('Event is none')

        try:
            input_file = self.fetch_input()
            output_file = self.fetch_output()
        except (EventUndefinedError, NetworkError):
            raise
        return input_file, output_file

    def extract(self, force_flag=False):
        """Extract the zipped resources. The two zips associated with this
        shakemap will be extracted to e.g.

        :file:`/tmp/inasafe/realtime/shakemaps-extracted/20131105060809`

        After extraction, under that directory, there will be directory that
        appears something like this:

        :file:`/usr/local/smap/data/20131105060809`

        with input and output directories appearing beneath that.

        This method will then move the grid.xml file up to the root of
        the extract dir and recursively remove the extracted dirs.

        After this final step, :file:`grid.xml` will be present under:

        :file:`/tmp/inasafe/realtime/shakemaps-extracted/20131105060809/`

        If the zips have not already been retrieved from the ftp server,
        they will be fetched first automatically.

        If the zips have previously been extracted, the extract dir will
        be completely removed and the dataset re-extracted.

        .. note:: You should not store any of your own working data in the
           extract dir - it should be treated as transient.

        .. note:: the grid.xml also contains MMI point data that
           we care about and will extract as a matrix (MMI in the 5th column).


        :param force_flag: (Optional) Whether to force re-extraction. If the
                files were previously extracted, you can force them to be
                extracted again. If False, grid.xml local file is used if
                it is cached. Default False.

        :return: a string containing the grid.xml paths e.g.::
            myGridXml = myShakeData.extract()
            print myGridXml
            /tmp/inasafe/realtime/shakemaps-extracted/20131105060809/grid.xml

        :raises: InvalidInputZipError, InvalidOutputZipError
        """

        final_grid_xml_file = os.path.join(self.extract_dir(), 'grid.xml')

        if force_flag:
            self.remove_extracted_files()
        elif os.path.exists(final_grid_xml_file):
            return final_grid_xml_file

        event_input, event_output = self.fetch_event()
        input_zip = ZipFile(event_input)
        output_zip = ZipFile(event_output)

        expected_grid_xml_file = (
            'usr/local/smap/data/%s/output/grid.xml' %
            self.event_id)

        output_name_list = output_zip.namelist()
        if expected_grid_xml_file not in output_name_list:
            raise InvalidInputZipError(
                'The output zip does not contain an '
                '%s file.' % expected_grid_xml_file)

        extract_dir = self.extract_dir()
        input_zip.extractall(extract_dir)
        output_zip.extractall(extract_dir)

        # move the file we care about to the top of the extract dir
        shutil.copyfile(os.path.join(self.extract_dir(),
                                     expected_grid_xml_file),
                        final_grid_xml_file)
        # Get rid of all the other extracted stuff
        user_dir = os.path.join(self.extract_dir(), 'usr')
        if os.path.isdir(user_dir):
            shutil.rmtree(user_dir)

        if not os.path.exists(final_grid_xml_file):
            raise ExtractionError('Error copying grid.xml')
        return final_grid_xml_file

    def extract_dir(self):
        """A helper method to get the path to the extracted datasets.

        :return: A string representing the absolute local filesystem path to
            the unzipped shake event dir. e.g.
            :file:`/tmp/inasafe/realtime/shakemaps-extracted/20131105060809`

        :raises: Any exceptions will be propogated
        """
        return os.path.join(shakemap_extract_dir(), self.event_id)

    def remove_extracted_files(self):
        """Tidy up the filesystem by removing all extracted files
        for the given event instance.

        Args: None

        Returns: None

        Raises: Any error e.g. file permission error will be raised.
        """
        extracted_dir = self.extract_dir()
        if os.path.isdir(extracted_dir):
            shutil.rmtree(extracted_dir)
