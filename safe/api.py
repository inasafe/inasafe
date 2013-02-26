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

__author__ = 'tim@linfiniti.com, ole.moller.nielsen@gmail.com'
__version__ = '0.4.0'
__revision__ = '$Format:%H$'
__date__ = '01/06/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# pylint: disable=W0611
from safe.storage.utilities import (bbox_intersection,
                                    buffered_bounding_box,
                                    verify,
                                    write_keywords,
                                    read_keywords,
                                    calculate_polygon_centroid)

from safe.storage.core import read_layer

from safe.impact_functions import (get_plugins,
                                    get_function_title,
                                    get_admissible_plugins,
                                    is_function_enabled,
                                    get_documentation)

from safe.engine.core import calculate_impact

from safe.common.numerics import nanallclose
from safe.common.exceptions import (InaSAFEError,
                                    BoundingBoxError,
                                    ReadLayerError,
                                    InaSAFEError)
from safe.common.utilities import (VerificationError,
                                   temp_dir,
                                   unique_filename,
                                   ugettext as safe_tr,
                                   get_free_memory,
                                   format_int)
from safe.common.version import get_version
from safe.common.polygon import in_and_outside_polygon
from safe.common.tables import Table, TableCell, TableRow
from safe.postprocessors import (get_postprocessors,
                                 get_postprocessor_human_name)
# pylint: enable=W0611
