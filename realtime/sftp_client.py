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

import sys
import paramiko
import ntpath
from stat import S_ISDIR
from errno import ENOENT
import os
import logging
from utils import mkDir

# The logger is intialised in utils.py by init
LOGGER = logging.getLogger('InaSAFE')

my_host = '118.97.83.243'
my_username = 'geospasial'
try:
    my_password = os.environ['QUAKE_SERVER_PASSWORD']
except KeyError:
    LOGGER.exception('QUAKE_SERVER_PASSWORD not set!')
    sys.exit()

my_remote_path = 'shakemaps'


class SFtpClient:
    """A utility class that contains methods to fetch a listings and files
    from an SSH protocol"""
    def __init__(self, the_host=my_host, the_username=my_username,
                 the_password=my_password, the_working_dir=my_remote_path):

        self.host = the_host
        self.username = the_username
        self.password = the_password
        self.working_dir = the_working_dir

        # create transport object
        self.transport = paramiko.Transport(self.host)
        self.transport.connect(username=self.username, password=self.password)

        # create sftp object
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

        # go to remote_path folder, this is the default folder
        if not self.working_dir is None:
            self.sftp.chdir(self.working_dir)
        self.workdir_path = self.sftp.getcwd()

    def download_path(self, remote_path, local_path):
        """ Download remote_dir to local_dir.
        for example : remote_path = '20130111133900' will be download to
        local_dir/remote_path
        Must be in the parent directory of remote dir.
        """
        # Check if remote_dir is exist
        if not self.is_path_exist(remote_path):
            print 'remote path is not exist %s' % remote_path
            return False
        if self.is_dir(remote_path):
            # get directory name
            dir_name = get_path_tail(remote_path)
            # create directory in local machine
            local_dir_path = os.path.join(local_path, dir_name)
            mkDir(local_dir_path)
            # list all directory in remote path
            list_dir = self.sftp.listdir(remote_path)
            # iterate recursive
            for my_dir in list_dir:
                new_remote_path = os.path.join(remote_path, my_dir)
                self.download_path(new_remote_path, local_dir_path)
        else:
            # download file to local_path
            file_name = get_path_tail(remote_path)
            local_file_path = os.path.join(local_path, file_name)

            LOGGER.info('file %s will be downloaded to %s' % (remote_path,
                                                        local_file_path))
            self.sftp.get(remote_path, local_file_path)

    def is_dir(self, path):
        """Check if a path is a directory or not in sftp
        Reference: http://stackoverflow.com/a/8307575/1198772
        """
        try:
            return S_ISDIR(self.sftp.stat(path).st_mode)
        except IOError:
            #Path does not exist, so by definition not a directory
            return False

    def is_path_exist(self, path):
        """os.path.exists for paramiko's SCP object
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

    def getListing(self, remote_dir=None, my_func=None):
        """Return list of files and directories name under a remote_dir
        and return true when it is input to my_func
        """
        if remote_dir is None:
            remote_dir = self.workdir_path
        if self.is_path_exist(remote_dir):
            temp_list = self.sftp.listdir(remote_dir)
        else:
            LOGGER.debug('Directory %s is not exist, return None' % remote_dir)
            return None
        retval = []
        for my_temp in temp_list:
            if my_func(my_temp):
                retval.append(my_temp)
        return retval


def get_path_tail(path):
    '''Return tail of a path
    Reference : http://stackoverflow.com/a/8384788/1198772
    '''
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
