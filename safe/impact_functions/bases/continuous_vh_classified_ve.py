# coding=utf-8
import logging

from safe.common.exceptions import (
    MetadataLayerConstraintError)
from safe.definitions import layer_mode_continuous, layer_geometry_point, \
    layer_geometry_line, layer_geometry_polygon, layer_mode_none
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.bases.layer_types. \
    classified_vector_exposure import ClassifiedVectorExposureMixin
from safe.impact_functions.bases.layer_types.continuous_vector_hazard import \
    ContinuousVectorHazardMixin
from safe.impact_functions.bases.utilities import (
    check_layer_constraint)

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '05/05/15'

LOGGER = logging.getLogger('InaSAFE')


class ContinuousVHClassifiedVE(
    ImpactFunction,
    ContinuousVectorHazardMixin,
    ClassifiedVectorExposureMixin):
    """Continuous Vector Hazard, Classified Vector Exposure base class.

    """

    def __init__(self):
        """Constructor"""
        super(ContinuousVHClassifiedVE, self).__init__()
        # check constraint
        valid = check_layer_constraint(
            self.metadata(),
            layer_mode_continuous,
            [layer_geometry_point,
             layer_geometry_line,
             layer_geometry_polygon],
            layer_mode_none,
            [layer_geometry_point,
             layer_geometry_line,
             layer_geometry_polygon])
        if not valid:
            raise MetadataLayerConstraintError()

    @ImpactFunction.hazard.setter
    # pylint: disable=W0221
    def hazard(self, value):
        self._hazard = value
        self.set_up_hazard_layer(value)

    @ImpactFunction.exposure.setter
    # pylint: disable=W0221
    def exposure(self, value):
        self._exposure = value
        self.set_up_exposure_layer(value)
