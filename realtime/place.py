"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Place related functionality.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '1/08/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

class Place:
    """This class is used to represent a place (e.g. a city).

    :example:

    myPlace = Place(theName='Jakarta',
                    theLongitude=12.12,
                    theLatitude=-1.2,
                    thePopulation=4000000,
                    theFeatureCode='PPL)
    myEpicenter = Place(
    myPlace.distanceTo(theOtherPlace)
