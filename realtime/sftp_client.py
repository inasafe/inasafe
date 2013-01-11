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

import paramiko
import ntpath
from datetime import datetime
from stat import S_ISDIR
from errno import ENOENT
import os

my_host = '118.97.83.243'
my_username = 'geospasial'
my_password = 'geospasial'
download_dir = ''

remote_path = 'shakemaps'

class SFtpClient:
    """A utility class that contains methods to fetch a listings and files
    from an SSH protocol"""
    def __init__(self, the_host=my_host, the_username=my_username,
                 the_password=my_password,):

        self.host = the_host
        self.username = the_username
        self.password = the_password
        self.events = None

        # create transport object
        self.transport=paramiko.Transport(self.host)
        self.transport.connect(username=self.username,password=self.password)

        # create sftp object
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

        # go to remote_path folder, this is the default folder
        self.sftp.chdir(remote_path)

    def get_list_event_ids(self):
        """Get all event id indicated by folder in remote_path
        """
        dirs = self.sftp.listdir()
        event_ids = []
        for my_dir in dirs:
            if self.is_event_id(my_dir):
                event_ids.append(my_dir)
        self.event_ids = event_ids
        if len(self.event_ids) == 0:
            raise Exception('List event is empty')
        return event_ids

    def is_event_id(self, id):
        """Check if an id is event id.
        Event id is in form of yyyymmddHHMMSS or '%Y%m%d%H%M%S'
        i.e. 20130110204706
        """
        if len(id) != 14:
            return False
        try:
            datetime.strptime(id, '%Y%m%d%H%M%S')
        except ValueError:
            return False
        return True

    def get_latest_event_id(self):
        """Return latest event id
        """
        if self.event_ids is None:
            self.get_list_events()
        self.event_ids.sort()
        return self.event_ids[-1]

#    def get_files(self, event_id=None):
#        """Download files related event_id from the host
#        if event_id = None, return the latest one
#        """
#        self.get_list_events()
#        if event_id is None:
#            event_id = self.get_latest_event_id()
#        if event_id not in self.event_ids:
#            raise Exception('Event Id is not found in the host %s' % self.host)
#
#        # create directory for the event in download directory
#        event_dir = os.path.join(download_dir, event_id)
#        if not os.path.isdir(event_dir):
#            os.mkdir(event_dir)
#
#        # create input dir
#        input_dir = os.path.join(event_dir, 'input')
#        if not os.path.isdir(input_dir):
#            os.mkdir(input_dir)
#
#        # create output dir
#            output_dir = os.path.join(event_dir, 'output')
#        if not os.path.isdir(output_dir):
#            os.mkdir(output_dir)
#
#        # download input folder

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
            print 'path %s is a directory' % remote_path
            # get directory name
            dir_name = get_path_tail(remote_path)
            print 'the dir name %s' % dir_name
            # create directory in local machine
            local_dir_path = os.path.join(local_path, dir_name)
            print 'local_dir_path %s' % local_dir_path
            make_dir(local_dir_path)
            # list all directory in remote path
            list_dir = self.sftp.listdir(remote_path)
            # iterate recursive
            for my_dir in list_dir:
                print my_dir
                new_remote_path = os.path.join(remote_path, my_dir)
#                new_local_path = os.path.join(local_path, my_dir)
                self.download_path(new_remote_path, local_dir_path)
        else:
            # download file to local_path
            file_name = get_path_tail(remote_path)
            local_file_path = os.path.join(local_path, file_name)
            print 'file %s will be downloaded to %s' % (remote_path, local_file_path)
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

def make_dir(dir_path):
    """Helper function for creating directory in file system
    """
    if not os.path.isdir(dir_path):
        try:
            os.mkdir(dir_path)
            print 'YAHA'
        except OSError, e:
            print e
            return False
        return True

def get_path_tail(path):
    '''Return tail of a path
    Reference : http://stackoverflow.com/a/8384788/1198772
    '''
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)