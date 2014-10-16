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
__date__ = '10/01/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from stat import S_ISDIR
from errno import ENOENT
import os
import logging

# noinspection PyPackageRequirements
import paramiko

from realtime.utilities import (
    make_directory,
    get_path_tail,
    realtime_logger_name)
from realtime.sftp_configuration.configuration import (
    get_sftp_base_url,
    get_sftp_port,
    get_sftp_user_name,
    get_sftp_user_password,
    get_sftp_base_path)

# The logger is initialised in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


class SFtpClient:
    """A class to fetch directory listings and files using SSH protocol"""
    def __init__(self,
                 host=get_sftp_base_url(),
                 port=get_sftp_port(),
                 username=get_sftp_user_name(),
                 password=get_sftp_user_password(),
                 working_dir=get_sftp_base_path()):

        """Class constructor.

        :param host: The remote host.
        :type host: str

        :param port: The port of the remote host.
        :type port: int

        :param username: The username for the host.
        :type username: str

        :param password: The password for given username.
        :type password: str

        :param working_dir: The base path to fetch the files.
        :type working_dir: str
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.working_dir = working_dir

        # create transport object
        # noinspection PyTypeChecker
        self.transport = paramiko.Transport((self.host, self.port))
        self.transport.connect(username=self.username, password=self.password)

        # create sftp object
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

        # go to working directory, this is the default folder
        if not self.working_dir is None:
            self.sftp.chdir(self.working_dir)
        self.working_dir_path = self.sftp.getcwd()

    def download_path(self, remote_path, local_path):
        """Download all files recursively in remote_path to local_path.

        :param remote_path: The remote path that will be downloaded to local.
        :type remote_path: str

        :param local_path: The target path on local.
        :type local_path: str

        EXAMPLE :
        remote_path = 'remote_head_path/20130111133900' will be downloaded to
        local_path/20130111133900.
        """
        # Check if remote_path is exist
        if not self.path_exists(remote_path):
            print 'Remote path %s does not exist.' % remote_path
            return False

        # If the remote_path is a dir, download all files on that dir
        if self.is_dir(remote_path):
            # get directory name
            dir_name = get_path_tail(remote_path)
            # create directory in local machine
            local_dir_path = os.path.join(local_path, dir_name)
            make_directory(local_dir_path)
            # list all directories in remote path
            directories = self.sftp.listdir(remote_path)
            # iterate recursive
            for directory in directories:
                directory_path = os.path.join(remote_path, directory)
                self.download_path(directory_path, local_dir_path)
        else:
            # download file to local_path
            file_name = get_path_tail(remote_path)
            local_file_path = os.path.join(local_path, file_name)

            LOGGER.info('File %s will be downloaded to %s' %
                        (remote_path, local_file_path))
            self.sftp.get(remote_path, local_file_path)

    def is_dir(self, path):
        """Check if a path is a directory or not in sftp.

        :param path: The target path that will be tested.
        :type path: str

        Reference: http://stackoverflow.com/a/8307575/1198772
        """
        try:
            return S_ISDIR(self.sftp.stat(path).st_mode)
        except IOError:
            #Path does not exist, so by definition not a directory
            return False

    def path_exists(self, path):
        """An implementation of os.path.exists for paramiko's SCP object.

        :param path: The target path that will be tested.
        :type path: str

        Reference: http://stackoverflow.com/q/850749/1198772
        """
        try:
            self.sftp.stat(path)
        except IOError, e:
            if e.errno == ENOENT:
                return False
            raise
        else:
            return True

    def get_listing(self, remote_dir=None, function=None):
        """Return list of files and directories name under a remote_dir if
        the directory/file is valid for a function.

        :param remote_dir: The remote directory that we want to get the list
            of directory inside it.
        :type remote_dir: str

        :param function: The function that use the directory.
        :type function: object
        """
        if remote_dir is None:
            remote_dir = self.working_dir_path
        if self.path_exists(remote_dir):
            directories = self.sftp.listdir(remote_dir)
        else:
            LOGGER.debug('Directory %s is not exist, return None' % remote_dir)
            return None
        valid_list = []
        for directory in directories:
            if function(directory):
                valid_list.append(directory)
        return valid_list
