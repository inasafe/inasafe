"""SAFE (Scenario Assessment For Emergencies) - API

The purpose of the module is to provide a well defined public API
for the packages that constitute the SAFE engine. Modules using SAFE
should only need to import functions from here.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com, ole.moller.nielsen@gmail.com'
__version__ = '0.4.0'
__revision__ = '$Format:%H$'
__date__ = '01/06/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from storage.utilities import read_keywords, bbox_intersection
from storage.utilities import buffered_bounding_box, verify
from storage.utilities import write_keywords, read_keywords
from storage.core import read_layer

from impact_functions import get_plugins
from impact_functions import get_function_title
from impact_functions import get_admissible_plugins

from engine.core import calculate_impact

from common.dynamic_translations import names as internationalisedNames
from common.numerics import nanallclose

# For testing and demoing
from common.testing import TESTDATA, HAZDATA, EXPDATA
