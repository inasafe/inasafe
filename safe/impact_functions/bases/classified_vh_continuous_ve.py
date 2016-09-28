# coding=utf-8
import logging

from safe.definitionsv4.definitions_v3 import (
    layer_mode_classified,
    layer_geometry_line,
    layer_geometry_polygon
)
from safe.definitionsv4.layer_modes import layer_mode_continuous, \
    layer_mode_classified
from safe.definitionsv4.layer_geometry import layer_geometry_point, \
    layer_geometry_line, layer_geometry_polygon
from safe.common.exceptions import MetadataLayerConstraintError
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.bases.layer_types.classified_vector_hazard import \
    ClassifiedVectorHazardMixin
from safe.impact_functions.bases.layer_types.continuous_vector_exposure \
    import ContinuousVectorExposureMixin
from safe.impact_functions.bases.utilities import check_layer_constraint

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '08/05/15'

LOGGER = logging.getLogger('InaSAFE')


class ClassifiedVHContinuousVE(
        ImpactFunction,
        ClassifiedVectorHazardMixin,
        ContinuousVectorExposureMixin):
    """Classified Vector Hazard, Continuous Vector Exposure base class.

    """

    def __init__(self):
        super(ClassifiedVHContinuousVE, self).__init__()
        valid = check_layer_constraint(
            self.metadata(),
            layer_mode_classified,
            [layer_geometry_point,
             layer_geometry_line,
             layer_geometry_polygon],
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
