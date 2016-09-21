# coding=utf-8
import logging

from definitionsv4.definitions_v3 import layer_mode_continuous, layer_geometry_point, \
    layer_geometry_line, layer_geometry_polygon
from safe.common.exceptions import MetadataLayerConstraintError
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.bases.layer_types.continuous_vector_exposure \
    import ContinuousVectorExposureMixin
from safe.impact_functions.bases.layer_types.continuous_vector_hazard import \
    ContinuousVectorHazardMixin
from safe.impact_functions.bases.utilities import check_layer_constraint

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '08/05/15'

LOGGER = logging.getLogger('InaSAFE')


class ContinuousVHContinuousVE(
        ImpactFunction,
        ContinuousVectorHazardMixin,
        ContinuousVectorExposureMixin):
    """Continuous Vector Hazard, Continuous Vector Exposure base class.

    """

    def __init__(self):
        """Constructor"""
        super(ContinuousVHContinuousVE, self).__init__()
        # check constraint
        valid = check_layer_constraint(
            self.metadata(),
            layer_mode_continuous,
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
