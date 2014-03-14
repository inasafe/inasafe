# coding=utf-8
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
#noinspection PyUnresolvedReferences
from safe.storage.vector import Layer
from safe.storage.vector import Vector
from safe.storage.raster import Raster
from safe.defaults import DEFAULTS
from safe.storage.utilities import (
    bbox_intersection,
    buffered_bounding_box,
    verify,
    write_keywords,
    read_keywords,
    calculate_polygon_centroid)

from safe.storage.core import read_layer

from safe.impact_functions import (
    load_plugins,  # you need to call this to ensure all plugins are loaded TS
    get_plugins,
    get_function_title,
    get_admissible_plugins,
    is_function_enabled,
    get_metadata)
from safe.impact_functions.core import (
    get_doc_string,
    get_unique_values,
    get_plugins_as_table,
    evacuated_population_weekly_needs)

from safe.engine.core import calculate_impact

from safe.common.numerics import nan_allclose
from safe.common.exceptions import (
    InaSAFEError,
    BoundingBoxError,
    ReadLayerError,
    InaSAFEError,
    GetDataError,
    ZeroImpactException,
    PointsInputError,
    PostProcessorError)
from safe.common.utilities import (
    VerificationError,
    temp_dir,
    unique_filename,
    ugettext as safe_tr,
    get_free_memory,
    format_int,
    get_thousand_separator,
    get_decimal_separator,
    get_utm_epsg,
    feature_attributes_as_dict,
    which)
from safe.common.shake_grid_converter import convert_mmi_data
from safe.common.version import get_version
from safe.common.polygon import in_and_outside_polygon
from safe.common.tables import Table, TableCell, TableRow
from safe.postprocessors import (
    get_postprocessors,
    get_postprocessor_human_name)
from safe import messaging
from safe.messaging import styles
from safe.common.signals import (
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    ERROR_MESSAGE_SIGNAL)
from safe.messaging import ErrorMessage

# hack for excluding test-related import in builded package
try:
    from safe.common.testing import (
        HAZDATA, EXPDATA, TESTDATA, UNITDATA, BOUNDDATA)
except ImportError:
    pass
# pylint: enable=W0611
