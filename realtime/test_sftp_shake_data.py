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
from sftp_shake_data import SftpShakeData
import os

sftp_data = SftpShakeData()


class SFtpShakeDataTest(unittest.TestCase):

    def test_create_event(self):
        """Test create shake data
        """
        try:
            event_one = SftpShakeData()
            event_two = SftpShakeData(theEvent='20130110041009')
            event_three = SftpShakeData(theEvent='20130110041009',
                theForceFlag=True)
            assert event_one is not None
            assert event_two is not None
            assert event_three is not None
        except:
            raise

    def test_download_data(self):
        """Test downloading data from server.
        """
        print sftp_data.fetchFile()

    def test_get_latest_event_id(self):
        """Test get latest event id
        """
        latest_id = sftp_data.getLatestEventId()
        print latest_id
        assert latest_id is not None, 'There is not latest event, please check'

    def test_get_list_event_ids(self):
        """Test get list event id
        """
        list_id = sftp_data.get_list_event_ids()
        print list_id
        assert len(list_id) > 0, 'num of list event is zero, please check'

    def test_reconnectSFTP(self):
        """Test to reconnect SFTP
        """
        sftp_client = sftp_data.sftpclient
        sftp_data.reconnectSFTP()
        new_sftp_client = sftp_data.sftpclient
        assert sftp_client != new_sftp_client, 'message'
        assert new_sftp_client is not None, 'new sftp is none'

    def test_filename(self):
        """Test filename
        """
        filename = sftp_data.fileName()
        assert filename == 'grid.xml', 'File name is not same'

    def test_onServer(self):
        """Test to check if a event is in server
        """
        assert sftp_data.isOnServer(), 'Event is not in server'

    def test_extract(self):
        """Test extracting data to be used in earth quake realtime
        """
        sftp_data.extract()
        myFinalGridXmlFile = os.path.join(sftp_data.extractDir(), 'grid.xml')
        assert os.path.exists(myFinalGridXmlFile), 'grid.xml not found'

if __name__ == '__main__':
    suite = unittest.makeSuite(SFtpShakeDataTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
