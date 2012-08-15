"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Functionality related to shake data files.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '30/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from shake_data import ShakeData
from safe_qgis.utilities_test import getQgisTestApp
QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
# Used cached data where available
myForceFlag = False
# Get the latest dataset
myShakeData = ShakeData()
# Extract the event
myShakeEvent = myShakeData.shakeEvent(theForceFlag=myForceFlag)
print 'Latest Event Id: %s' % myShakeEvent
print '-------------------------------------------'
# Make contours
for myAlgorithm in ['average', 'invdist', 'nearest']:
    myFile = myShakeEvent.mmiDataToContours(theForceFlag=myForceFlag,
                                   theAlgorithm=myAlgorithm)
    print 'Created: %s' % myFile
try:
    myFile = myShakeEvent.citiesToShape()
    print 'Created: %s' % myFile
except:
    print 'No nearby cities found!'
myFile = myShakeEvent.mmiDataToShapefile(theForceFlag=myForceFlag)
print 'Created: %s' % myFile
print '-------------------------------------------'
