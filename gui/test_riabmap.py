"""
Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.2.0'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)


from utilities_test import getQgisTestApp
from gui.riabmap import RiabMap

from utilities_test import loadLayer
try:
    from pydevd import *
    print 'Remote debugging is enabled.'
    DEBUG = True
except Exception, e:
    print 'Debugging was disabled'

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


class RiabDockTest(unittest.TestCase):
    """Test the risk in a box GUI"""

    def test_riabMap(self):
        """Test making a pdf using the RiabMap class.

        .. todo:: Move this into its own test class

        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        loadLayer('issue58.tif')
        myMap = RiabMap(IFACE)
        myPdf = '/tmp/out.pdf'
        if os.path.exists(myPdf):
            os.remove(myPdf)
        myMap.makePdf(myPdf)
        assert os.path.exists(myPdf)
        os.remove(myPdf)

if __name__ == '__main__':
    suite = unittest.makeSuite(RiabDockTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
