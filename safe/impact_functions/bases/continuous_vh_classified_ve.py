# coding=utf-8
import logging
from qgis.core import (
    QgsRectangle,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsFeatureRequest,
    QgsGeometry)

from safe.common.exceptions import (
    GetDataError,
    WrongDataTypeException)
from safe.gis.qgis_vector_tools import clip_by_polygon, split_by_polygon
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.bases.calculation_result import (
    VectorImpactCalculation)
from safe.impact_functions.bases.layer_types.\
    classified_vector_exposure import ClassifiedVectorExposure
from safe.impact_functions.bases.layer_types.classified_vector_impact import \
    VectorImpact
from safe.impact_functions.bases.layer_types.continuous_vector_hazard import \
    ContinuousVectorHazard
from safe.impact_functions.bases.utilities import (
    get_qgis_vector_layer)
from safe.utilities.i18n import tr


__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '05/05/15'


LOGGER = logging.getLogger('InaSAFE')


class ContinuousVHClassifiedVE(ImpactFunction,
                               ContinuousVectorHazard,
                               ClassifiedVectorExposure,
                               VectorImpact):
    """Intermediate base class for:
    Continuous Vector Hazard, Classified Vector Exposure

    """

    def __init__(self):
        """Constructor"""
        super(ContinuousVHClassifiedVE, self).__init__()

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

    def calculate_impact(self):
        # Check the required field
        if (not self.hazard_value_attribute or
                not self.hazard_threshold or
                not self.exposure_class_attribute):
            raise NotImplementedError('The necessary fields of base class '
                                      'must be set')

        # get layers
        hazard_layer = get_qgis_vector_layer(self.hazard)
        exposure_layer = get_qgis_vector_layer(self.exposure)

        hazard_provider = hazard_layer.dataProvider()
        hazard_value_index = hazard_provider.fieldNameIndex(
            self.hazard_value_attribute)

        # check projection stuff of hazard and exposure.
        # make sure requested extent and the hazard layer are using the same
        # crs
        requested_extent = QgsRectangle(*self.requested_extent)
        transform = QgsCoordinateTransform(
            QgsCoordinateReferenceSystem(
                'EPSG:%i' % self._requested_extent_crs),
            hazard_layer.crs()
        )
        projected_extent = transform.transformBoundingBox(requested_extent)
        # create filter request to limit the hazard features
        request = QgsFeatureRequest()
        request.setFilterRect(projected_extent)

        # validate value types is numeric
        hazard_value_object_type = hazard_provider.fields()[
            hazard_value_index].typeName()
        if hazard_value_object_type not in ['Real', 'Integer']:
            message = 'Impact Function only accepts numeric hazard values'
            raise WrongDataTypeException(message)

        hazard_features = hazard_layer.getFeatures(request)
        hazard_poly = None
        for feature in hazard_features:
            attributes = feature.attributes()
            # if the hazard value doesn't exceed the threshold, skip it
            if attributes[hazard_value_index] < self.hazard_threshold:
                continue
            if hazard_poly is None:
                hazard_poly = QgsGeometry(feature.geometry())
            else:
                # Make geometry union of impacted polygons
                # But some feature.geometry() could be invalid, skip them
                tmp_geometry = hazard_poly.combine(feature.geometry())
                try:
                    if tmp_geometry.isGeosValid():
                        hazard_poly = tmp_geometry
                except AttributeError:
                    pass

        if hazard_poly is None:
            message = (
                'There are no objects in the hazard layer with %s (Hazard '
                'Attribute) >= %s (Hazard Threshold). Please check the value '
                'or use a different extent.' % (
                    self.hazard_value_attribute, self.hazard_threshold))
            raise GetDataError(message)

        # Clip exposure by the extent (creating a new layer)
        extent_as_polygon = QgsGeometry().fromRect(requested_extent)
        impact_layer = clip_by_polygon(exposure_layer, extent_as_polygon)
        # Find impacted exposure, mark them
        impact_layer = split_by_polygon(
            impact_layer, hazard_poly, request,
            mark_value=(self.impact_attribute, 1))

        # Calculate simple impact report

        # store impacted object count
        # Count of the exposures
        exposure_count = hazard_count = 0
        # Count of impacted exposures by types
        exposure_by_class = dict()

        exposure_data = impact_layer.getFeatures()
        exposure_class_index = impact_layer.fieldNameIndex(
            self.exposure_class_attribute)
        impact_value_index = impact_layer.fieldNameIndex(
            self.impact_attribute)

        for exposure in exposure_data:
            attributes = exposure.attributes()
            exposure_class = attributes[exposure_class_index]
            # if the exposure object's class can't be determined, add it as
            # 'other'
            if exposure_class.__class__.__name__ == 'QPyNullVariant':
                exposure_class = tr('Other')
            exposure_count += 1

            # initializes detected new exposure class
            if exposure_class not in exposure_by_class:
                exposure_by_class[exposure_class] = {
                    'impacted': 0,
                    'total': 0}
            exposure_by_class[exposure_class]['total'] += 1

            # if the exposed object is impacted, track it
            # this is in the case the hazard value exceeds the threshold
            if attributes[impact_value_index] == 1:
                hazard_count += 1
                exposure_by_class[exposure_class]['impacted'] += 1

        # create structure to store the information
        impact_calculation = VectorImpactCalculation()
        impact_calculation.impact_map = exposure_by_class
        impact_calculation.impacted_count = hazard_count
        impact_calculation.total_count = exposure_count
        impact_calculation.impact_layer = impact_layer
        return impact_calculation
