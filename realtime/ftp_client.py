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
__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '19/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import socket
import urllib2
import logging

from realtime.sftp_configuration.base_config import BASE_URL
from realtime.utilities import realtime_logger_name


# The logger is initialised in realtime/__init__
LOGGER = logging.getLogger(realtime_logger_name())


class FtpClient:
    """A utility class that contains methods to fetch a listings and files
        from an FTP server"""
    def __init__(self,
                 base_url=BASE_URL,
                 pasv_mode=True):
        """Constructor for the FtpClient class.

        :param base_url: (Optional) an ftp server to connect to. If omitted
              it will default to BASE_URL.
        :type base_url: str

        :param pasv_mode - (Optional) whether passive connections should be
              made. Defaults to True.
        :type pasv_mode: bool
        """
        self.base_url = base_url
        self.pasv = pasv_mode

    def get_listing(self, extension='zip'):
        """Get a listing of the available files.

        Adapted from Ole's original shake library.

        :param extension: (Optional) Filename suffix to filter the listing by.
            Defaults to zip.

        :returns: A list containing the unique filenames (if any) that match
            the supplied extension suffix.

        :raises: URLError on failure
        """
        LOGGER.debug('Getting ftp listing for %s', self.base_url)
        base_url = 'ftp://%s' % self.base_url
        request = urllib2.Request(base_url)
        try:
            file_id = urllib2.urlopen(request, timeout=60)
        except urllib2.URLError:
            LOGGER.exception('Error opening url for directory listing.')
            raise

        file_list = []
        try:
            for line in file_id.readlines():
                fields = line.strip().split()
                if fields[-1].endswith('.%s' % extension):
                    file_list.append(base_url + '/' + fields[-1])
        except urllib2.URLError, e:
            if isinstance(e.reason, socket.timeout):
                LOGGER.exception('Timed out getting directory listing')
            else:
                LOGGER.exception('Exception getting directory listing')
            raise

        return file_list

    def ftp_url_for_file(self, url_path):
        """Get a file from the ftp server.

        :param url_path: (Mandatory) The path (relative to the ftp root)
              from which the file should be retrieved.

        :return: An ftp url e.g. ftp://118.97.83.243/20131105060809.inp.zip
        :rtype: str

        :raises: None
        """
        return 'ftp://%s/%s' % (self.base_url, url_path)

    def get_file(self, url_path, file_path):
        """Get a file from the ftp server.

         :param url_path: (Mandatory) The path (relative to the ftp root)
              from which the file should be retrieved.

         :param file_path: (Mandatory). The path on the filesystem to which
              the file should be saved.

         :return: The path to the downloaded file.
        """
        LOGGER.debug('Getting ftp file: %s', file_path)
        url = self.ftp_url_for_file(url_path)
        request = urllib2.Request(url)
        try:
            url_handle = urllib2.urlopen(request, timeout=60)
            saved_file = file(file_path, 'wb')
            saved_file.write(url_handle.read())
            saved_file.close()
        except urllib2.URLError:
            LOGGER.exception('Bad Url or Timeout')
            raise

    def has_file(self, checked_file):
        """Check if a file is on the ftp server.

         :param checked_file: (Mandatory) The paths (relative to the ftp
          root) to be checked. e.g. '20131105060809.inp.zip',

         :return: True if the file exists on the server, otherwise False.
         :rtype: bool
        """
        LOGGER.debug('Checking for ftp file: %s', checked_file)
        file_list = self.get_listing()
        url = self.ftp_url_for_file(checked_file)
        return url in file_list

    def has_files(self, checked_files):
        """Check if a list files is on the ftp server.

        .. seealso: func:`has_file`

        :param checked_files: The paths (relative to the ftp root) to be
            checked. e.g.
            ['20131105060809.inp.zip', '20131105060809.inp.zip']

         :type checked_files: list

        :return: True if **all** files exists on the server, otherwise False.
        :rtype: bool
        """
        LOGGER.debug('Checking for ftp file: %s', checked_files)
        # Note we don't delegate to has_file as we want to limit network IO
        file_list = self.get_listing()
        for input_file in checked_files:
            url = self.ftp_url_for_file(input_file)
            if not url in file_list:
                LOGGER.debug('** %s NOT found on server**' % url)
                return False
            LOGGER.debug('%s found on server' % url)
        return True
