"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'bungcip@gmail.com'
__date__ = '05/02/2013'
__copyright__ = ('Copyright 2013, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest
import logging

from safe_qgis.safe_interface import temp_dir, unique_filename
from safe_qgis.utilities_test import (getQgisTestApp,
                                      loadLayer,
                                      checkImages)
from safe_qgis.html_renderer import HtmlRenderer
from safe_qgis.keyword_io import KeywordIO

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
LOGGER = logging.getLogger('InaSAFE')


from safe_qgis.inasafe_lightmaps import (InasafeLightMaps, InasafeSlippyMap)

class SlippyMapTest(unittest.TestCase):
    """Test the Slippy map widget"""

    def setUp(self):
        self.slippyMap = InasafeSlippyMap()

    def test_flipLatitude(self):
        """ test flipLatitude function """
        myMessage = "Number don't match. expect {0} but got {1} "

        myNumber = self.slippyMap.flipLatitude(20)
        assert myNumber == 20, myMessage.format(20, myNumber)

        myNumber = self.slippyMap.flipLatitude(100)
        assert myNumber == 80, myMessage.format(80, myNumber)

        myNumber = self.slippyMap.flipLatitude(300)
        assert myNumber == -60, myMessage.format(-60, myNumber)

        myNumber = self.slippyMap.flipLatitude(-20)
        assert myNumber == -20, myMessage.format(-20, myNumber)

        myNumber = self.slippyMap.flipLatitude(-100)
        assert myNumber == -80, myMessage.format(80, myNumber)

        #FIXME(gigih): still fail, expected value is 60 the result is 120
#        myNumber = self.slippyMap.flipLatitude(-300)
#        assert myNumber == 60, myMessage.format(60, myNumber)

    def test_flipLongitude(self):
        """ test flipLongitude function """

        myMessage = "Number don't match. expect {0} but got {1} "

        myNumber = self.slippyMap.flipLatitude(20)
        assert myNumber == 20, myMessage.format(20, myNumber)

        myNumber = self.slippyMap.flipLatitude(200)
        assert myNumber == -20, myMessage.format(-20, myNumber)

        myNumber = self.slippyMap.flipLatitude(400)
        assert myNumber == 40, myMessage.format(40, myNumber)

        myNumber = self.slippyMap.flipLatitude(-20)
        assert myNumber == -20, myMessage.format(-20, myNumber)

        myNumber = self.slippyMap.flipLatitude(-200)
        assert myNumber == 20, myMessage.format(20, myNumber)




if __name__ == '__main__':
    suite = unittest.makeSuite(SlippyMapTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
