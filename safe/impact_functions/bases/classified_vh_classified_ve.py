# coding=utf-8
import logging
from qgis.core import (
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeatureRequest,
    QgsGeometry)

from safe.common.exceptions import GetDataError, \
    MetadataLayerConstraintError
from safe.definitions import layer_mode_classified, layer_geometry_point, \
    layer_geometry_line, layer_geometry_polygon
from safe.gis.qgis_vector_tools import clip_by_polygon
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.bases.calculation_result import \
    VectorImpactCalculation
from safe.impact_functions.bases.layer_types.classified_vector_exposure import \
    ClassifiedVectorExposure
from safe.impact_functions.bases.layer_types.classified_vector_hazard import \
    ClassifiedVectorHazard
from safe.impact_functions.bases.layer_types.vector_impact import \
    VectorImpact
from safe.impact_functions.bases.utilities import get_qgis_vector_layer, \
    split_by_polygon_class, check_layer_constraint
from safe.utilities.i18n import tr

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/05/15'


LOGGER = logging.getLogger('InaSAFE')


class ClassifiedVHClassifiedVE(ImpactFunction,
                               ClassifiedVectorHazard,
                               ClassifiedVectorExposure,
                               VectorImpact):
    """Intermediate base class for:
    Classified Vector Hazard, Classified Vector Exposure

    """

    def __init__(self):
        super(ClassifiedVHClassifiedVE, self).__init__()
        # check constraint
        valid = check_layer_constraint(self.metadata(),
                                       layer_mode_classified,
                                       [layer_geometry_point,
                                        layer_geometry_line,
                                        layer_geometry_polygon],
                                       layer_mode_classified,
                                       [layer_geometry_point,
                                        layer_geometry_line,
                                        layer_geometry_polygon])
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

    def calculate_impact(self):
        # Check the required field
        if (not self.hazard_class_attribute or
                not self.hazard_class_mapping or
                not self.exposure_class_attribute):
            raise NotImplementedError('The necessary fields of base class '
                                      'must be set')

        # get layers
        hazard_layer = get_qgis_vector_layer(self.hazard)
        exposure_layer = get_qgis_vector_layer(self.exposure)

        hazard_provider = hazard_layer.dataProvider()
        impact_class_index = hazard_provider.fieldNameIndex(
            self.hazard_class_attribute)

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

        hazard_features = hazard_layer.getFeatures(request)
        hazard_poly = dict()
        for feature in hazard_features:
            attributes = feature.attributes()
            # if the hazard value doesn't belong to any class, skip it
            if (attributes[impact_class_index] not in
                    self.hazard_class_mapping):
                    continue
            hazard_class = attributes[impact_class_index]
            if hazard_class not in hazard_poly:
                hazard_poly[hazard_class] = QgsGeometry(feature.geometry())
            else:
                # Make geometry union of impacted polygons
                # But some feature.geometry() could be invalid, skip them
                tmp_geometry = hazard_poly[hazard_class].combine(
                    feature.geometry())
                try:
                    if tmp_geometry.isGeosValid():
                        hazard_poly[hazard_class] = tmp_geometry
                except AttributeError:
                    pass

        if not hazard_poly:
            message = (
                'There are no objects in the hazard layer with %s (Hazard '
                'Attribute) in the %s (Hazard Class). Please check the '
                'value or use a different extent.' % (
                    self.hazard_class_attribute, self.hazard_class_mapping))
            raise GetDataError(message)

        # Clip exposure by the extent (creating a new layer)
        extent_as_polygon = QgsGeometry().fromRect(requested_extent)
        impact_layer = clip_by_polygon(exposure_layer, extent_as_polygon)
        # Find impacted exposure, mark them
        impact_layer = split_by_polygon_class(
            impact_layer, hazard_poly, request,
            self.impact_attribute)

        # Calculate simple impact report

        # store impacted object count
        # Count of the exposures
        exposure_count = hazard_count = 0
        # Count of impacted exposures by types
        exposure_by_class = dict()
        # Count of impacted hazard by types
        hazard_by_class = dict()

        exposure_data = impact_layer.getFeatures()
        exposure_class_index = impact_layer.fieldNameIndex(
            self.exposure_class_attribute)
        impact_class_index = impact_layer.fieldNameIndex(
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

            hazard_class = attributes[impact_class_index]
            # if the exposed object is impacted, track it
            # this is in the case the hazard value belongs to any of the
            # hazard class
            if not hazard_class:
                if hazard_class not in hazard_by_class:
                    hazard_by_class[hazard_class] = 0
                hazard_count += 1
                hazard_by_class[hazard_class] += 1
                exposure_by_class[exposure_class]['impacted'] += 1

        # create structure to store the information
        impact_calculation = VectorImpactCalculation()
        impact_calculation.impact_map = exposure_by_class
        impact_calculation.hazard_map = hazard_by_class
        impact_calculation.impacted_count = hazard_count
        impact_calculation.total_count = exposure_count
        impact_calculation.impact_layer = impact_layer
        return impact_calculation
