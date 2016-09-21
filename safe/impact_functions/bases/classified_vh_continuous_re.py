# coding=utf-8
from definitionsv4.definitions_v3 import (
    layer_mode_classified,
    layer_geometry_line,
    layer_geometry_point,
    layer_geometry_polygon,
    layer_mode_continuous,
    layer_geometry_raster
)
from safe.common.exceptions import MetadataLayerConstraintError
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.bases.layer_types.classified_vector_hazard import \
    ClassifiedVectorHazardMixin
from safe.impact_functions.bases.layer_types.continuous_raster_exposure \
    import ContinuousRasterExposureMixin
from safe.impact_functions.bases.utilities import check_layer_constraint

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '28/05/15'


class ClassifiedVHContinuousRE(
        ImpactFunction,
        ClassifiedVectorHazardMixin,
        ContinuousRasterExposureMixin):
    """Continuous Vector Hazard Continuous Raster Exposure base class.

    """

    def __init__(self):
        super(ClassifiedVHContinuousRE, self).__init__()
        # checks the metadata
        valid = check_layer_constraint(
            self.metadata(),
            layer_mode_classified,
            [layer_geometry_point,
             layer_geometry_line,
             layer_geometry_polygon],
            layer_mode_continuous,
            [layer_geometry_raster])
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
