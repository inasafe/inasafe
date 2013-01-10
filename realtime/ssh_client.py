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

my_host = ' 118.97.83.243'
my_username = 'geospasial'
my_password = 'geospasial'

class SSHClient:
    """A utility class that contains methods to fetch a listings and files
    from an SSH protocol"""
    def __init__(self, the_host=my_host,
                 the_username=my_username, the_password=my_password):

        self.host = the_host
        self.username = the_username
        self.password = the_password
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.host, username=self.username, password=self.password)

