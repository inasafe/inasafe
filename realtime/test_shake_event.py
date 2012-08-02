"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Shake Event Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '2/08/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
from realtime.utils import shakemapExtractDir
from realtime.shake_data import ShakeData
from realtime.shake_event import (eventFilePath)

class TestShakeEvent(unittest.TestCase):
    def test_eventFilePath(self):
        """Test eventFilePath works"""
        myShakeEvent = '20120726022003'

        myExpectedPath = os.path.join(shakemapExtractDir(), 'event.xml')
        myShakeData = ShakeData(myShakeEvent)
        myShakeData.extract()
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
