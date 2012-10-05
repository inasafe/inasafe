"""**SAFE (Scenario Assessment For Emergencies) - API**

The purpose of the module is to provide a well defined public API
for the packages that constitute the SAFE engine. Modules using SAFE
should only need to import functions from here.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'marco@opengis.ch'
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '05/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# https://www.cia.gov/library/publications/the-world-factbook/geos/xx.html
# total population: 1.01 male(s)/female (2011 est.)
DEFAULT_FEMALE_RATIO = 0.50

#Keywords key names
FEMALE_RATIO_ATTRIBUTE_KEY = 'female ratio attribute'
FEMALE_RATIO_DEFAULT_KEY = 'female ratio default'
AGGREGATION_ATTRIBUTE_KEY = 'aggregation attribute'
