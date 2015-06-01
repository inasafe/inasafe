# coding=utf-8
import logging

from safe.common.exceptions import MetadataLayerConstraintError
from safe.definitions import layer_mode_classified, layer_geometry_point, \
    layer_geometry_line, layer_geometry_polygon, layer_mode_continuous
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.bases.layer_types.classified_vector_hazard import \
    ClassifiedVectorHazardMixin
from safe.impact_functions.bases.layer_types.vector_impact import \
    VectorImpactMixin
from safe.impact_functions.bases.layer_types.continuous_vector_exposure \
    import ContinuousVectorExposureMixin
from safe.impact_functions.bases.utilities import check_layer_constraint

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '08/05/15'


LOGGER = logging.getLogger('InaSAFE')


class ClassifiedVHContinuousVE(ImpactFunction,
                               ClassifiedVectorHazardMixin,
                               ContinuousVectorExposureMixin,
                               VectorImpactMixin):
    """Intermediate base class for:
    Classified Vector Hazard, Continuous Vector Exposure

    """

    def __init__(self):
        super(ClassifiedVHContinuousVE, self).__init__()
        valid = check_layer_constraint(self.metadata(),
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
        self._hazard = value
        self.set_up_hazard_layer(value)

    @ImpactFunction.exposure.setter
    # pylint: disable=W0221
    def exposure(self, value):
        self._exposure = value
        self.set_up_exposure_layer(value)

    @ImpactFunction.impact.setter
    # pylint: disable=W0221
    def impact(self, value):
        self._impact = value
        self.set_up_impact_layer(value)
