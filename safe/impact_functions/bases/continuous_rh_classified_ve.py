# coding=utf-8

from definitionsv4.definitions_v3 import layer_mode_continuous, layer_geometry_raster, \
    layer_geometry_point, layer_geometry_line, \
    layer_geometry_polygon, layer_mode_classified
from safe.common.exceptions import (
    MetadataLayerConstraintError)
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.bases.layer_types. \
    classified_vector_exposure import ClassifiedVectorExposureMixin
from safe.impact_functions.bases.layer_types.continuous_raster_hazard import \
    ContinuousRasterHazardMixin
from safe.impact_functions.bases.utilities import (
    check_layer_constraint)

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '28/05/15'


class ContinuousRHClassifiedVE(
        ImpactFunction,
        ContinuousRasterHazardMixin,
        ClassifiedVectorExposureMixin):
    """Continuous Raster Hazard, Classified Vector Exposure base class.

    """

    def __init__(self):
        """Constructor"""
        super(ContinuousRHClassifiedVE, self).__init__()
        # check constraint
        valid = check_layer_constraint(
            self.metadata(),
            layer_mode_continuous,
            [layer_geometry_raster],
            layer_mode_classified,
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
