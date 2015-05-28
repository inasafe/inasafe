# coding=utf-8

from safe.common.exceptions import (
    MetadataLayerConstraintError)
from safe.definitions import layer_mode_continuous, layer_geometry_raster, \
    layer_mode_classified
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.bases.layer_types.classified_raster_hazard import \
    ClassifiedRasterHazard
from safe.impact_functions.bases.layer_types.continuous_raster_exposure import \
    ContinuousRasterExposure
from safe.impact_functions.bases.layer_types.raster_impact import RasterImpact
from safe.impact_functions.bases.utilities import (
    check_layer_constraint)

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '28/05/15'


class ClassifiedRHContinuousRE(ImpactFunction,
                               ClassifiedRasterHazard,
                               ContinuousRasterExposure,
                               RasterImpact):
    """Intermediate base class for:
    Continuous Vector Hazard, Classified Vector Exposure

    """

    def __init__(self):
        """Constructor"""
        super(ClassifiedRHContinuousRE, self).__init__()
        # check constraint
        valid = check_layer_constraint(self.metadata(),
                                       layer_mode_classified,
                                       [layer_geometry_raster],
                                       layer_mode_continuous,
                                       [layer_geometry_raster])
        if not valid:
            raise MetadataLayerConstraintError()

    @property
    def hazard(self):
        return self._hazard

    @hazard.setter
    def hazard(self, value):
        self._hazard = value
        self.set_up_hazard_layer(value)

    @property
    def exposure(self):
        return self._exposure

    @exposure.setter
    def exposure(self, value):
        self._exposure = value
        self.set_up_exposure_layer(value)

    @property
    def impact(self):
        return self._impact

    @impact.setter
    def impact(self, value):
        self._impact = value
        self.set_up_impact_layer(value)
