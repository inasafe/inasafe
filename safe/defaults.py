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

from safe.common.utilities import ugettext as tr

DEFAULTS = dict()

# https://www.cia.gov/library/publications/the-world-factbook/geos/xx.html
# total population: 1.01 male(s)/female (2011 est.)
DEFAULTS['FEM_RATIO'] = 0.50

# https://www.cia.gov/library/publications/the-world-factbook/geos/xx.html
# Age structure:
# 0-14 years: 26.3% (male 944,987,919/female 884,268,378)
# 15-64 years: 65.9% (male 2,234,860,865/female 2,187,838,153)
# 65 years and over: 7.9% (male 227,164,176/female 289,048,221) (2011 est.)

# NOTE (MB) CIA can not do maths!!!  this gives 100.1%
# inaSAFE can, thus we remove 0.1% from the elderly
# I wrote them and got this contact confirmation number: CTCU1K2

DEFAULTS['YOUTH_RATIO'] = 0.263
DEFAULTS['ADULT_RATIO'] = 0.659
DEFAULTS['ELDER_RATIO'] = 0.078

#Keywords key names
DEFAULTS['FEM_RATIO_ATTR_KEY'] = 'female ratio attribute'
DEFAULTS['FEM_RATIO_KEY'] = 'female ratio default'
DEFAULTS['AGGR_ATTR_KEY'] = 'aggregation attribute'
DEFAULTS['NO_DATA'] = tr('No data')
