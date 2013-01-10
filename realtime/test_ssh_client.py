"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Ftp Client Test Cases.**

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
import unittest
from ssh_client import SSHClient

class SSHClientTest(unittest.TestCase):
    def test_ssh_connect(self):
        my_ssh_client = SSHClient()
        assert(my_ssh_client is not None)

if __name__ == '__main__':
    suite = unittest.makeSuite(SSHClientTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

