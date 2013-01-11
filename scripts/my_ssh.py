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

import os
import paramiko

my_host = '118.97.83.243'
my_username = 'geospasial'
my_password = 'geospasial'

transport=paramiko.Transport(my_host)
transport.connect(username=my_username,password=my_password)
sftp=paramiko.SFTPClient.from_transport(transport)

# download
filename = 'shakemaps/20130110041009/about_formats.html'
localname = 'ab.html'

#sftp.chdir('shakemaps/20130110041009/')
print os.getcwd()

sftp.get(filename, localname)
print 'saved to ', os.path.join(os.getcwd(), localname)

print 'fin'