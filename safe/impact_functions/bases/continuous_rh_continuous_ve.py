# coding=utf-8

from safe.definitionsv4.definitions_v3 import (
    layer_geometry_raster,
    layer_geometry_line,
    layer_geometry_polygon
)
from safe.definitionsv4.layer_modes import layer_mode_continuous
from safe.definitionsv4.layer_geometry import layer_geometry_point, \
    layer_geometry_line, layer_geometry_polygon, layer_geometry_raster
from safe.common.exceptions import (
    MetadataLayerConstraintError)
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.bases.layer_types.continuous_raster_hazard import \
    ContinuousRasterHazardMixin
from safe.impact_functions.bases.layer_types.continuous_vector_exposure \
    import ContinuousVectorExposureMixin
from safe.impact_functions.bases.utilities import (
    check_layer_constraint)

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '28/05/15'


class ContinuousRHContinuousVE(
        ImpactFunction,
        ContinuousRasterHazardMixin,
        ContinuousVectorExposureMixin):
    """Continuous Raster Hazard, Continuous Vector Exposure base class.

    """

    def __init__(self):
        """Constructor"""
        super(ContinuousRHContinuousVE, self).__init__()
        # check constraint
        valid = check_layer_constraint(
            self.metadata(),
            layer_mode_continuous,
            [layer_geometry_raster],
            layer_mode_continuous,
            [layer_geometry_point,
             layer_geometry_line,
             layer_geometry_polygon])
        if not valid:
            raise MetadataLayerConstraintError()

    @ImpactFunction.hazard.setter
    # pylint: disable=W0221
    def hazard(self, value):
        ImpactFunction.hazard.fset(self, value)

    @ImpactFunction.exposure.setter
    # pylint: disable=W0221
    def exposure(self, value):
        ImpactFunction.exposure.fset(self, value)
