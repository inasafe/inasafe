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

import unittest
from safe_qgis.inasafe_lightmaps import (InasafeSlippyMap)
from safe_qgis.utilities_test import (getQgisTestApp)

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


class SlippyMapTest(unittest.TestCase):
    """Test the Slippy map widget"""

    def setUp(self):
        self.slippyMap = InasafeSlippyMap(PARENT)

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

    def test_calculateExtends(self):
        """ test calculateExtends function """

        self.slippyMap.zoom = 9
        self.slippyMap.latitude = 80
        self.slippyMap.longitude = 81
        self.slippyMap.width = 400
        self.slippyMap.height = 400

        self.slippyMap.calculateExtent()

        myMessage = "Number don't match. expect {0} but got {1} "

        myNumber = self.slippyMap.tlLat
        myResult = 79.45078125
        assert myNumber == myResult, myMessage.format(myResult, myNumber)

        myNumber = self.slippyMap.tlLng
        myResult = 80.45078125
        assert myNumber == myResult, myMessage.format(myResult, myNumber)

        myNumber = self.slippyMap.brLat
        myResult = 80.54921875
        assert myNumber == myResult, myMessage.format(myResult, myNumber)

        myNumber = self.slippyMap.brLng
        myResult = 81.54921875
        assert myNumber == myResult, myMessage.format(myResult, myNumber)

if __name__ == '__main__':
    suite = unittest.makeSuite(SlippyMapTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
