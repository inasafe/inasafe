# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Flood Polygon on Roads
Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import logging

from qgis.core import (
    QgsRectangle,
    QgsFeatureRequest,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)

from safe.impact_functions.bases.classified_vh_classified_ve import \
    ClassifiedVHClassifiedVE
from safe.impact_functions.inundation. \
    flood_polygon_roads.metadata_definitions import \
    FloodPolygonRoadsMetadata
from safe.common.exceptions import ZeroImpactException
from safe.utilities.i18n import tr
from safe.utilities.utilities import main_type
from safe.storage.vector import Vector
from safe.common.utilities import get_utm_epsg
from safe.common.exceptions import GetDataError
from safe.gis.qgis_vector_tools import split_by_polygon, clip_by_polygon
from safe.impact_reports.road_exposure_report_mixin import\
    RoadExposureReportMixin

LOGGER = logging.getLogger('InaSAFE')


class FloodPolygonRoadsFunction(
        ClassifiedVHClassifiedVE,
        RoadExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Simple experimental impact function for inundation."""
    _metadata = FloodPolygonRoadsMetadata()

    def __init__(self):
        """Constructor."""
        super(FloodPolygonRoadsFunction, self).__init__()
        RoadExposureReportMixin.__init__(self)
        # The 'wet' variable
        self.wet = 'wet'

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        hazard_terminology = tr('inundated')
        flood_value = [unicode(hazard_class)
                       for hazard_class in self.hazard_class_mapping[self.wet]]
        fields = [
            tr('Roads are said to be %s when in a region with field "%s" in '
               '"%s".') % (
                hazard_terminology,
                self.hazard_class_attribute,
                ', '.join(flood_value)),
        ]
        # include any generic exposure specific notes from definitions_v3.py
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions_v3.py
        fields = fields + self.hazard_notes()
        return fields

    def run(self):
        """Experimental impact function for flood polygons on roads."""

        # Get parameters from layer's keywords
        self.hazard_class_attribute = self.hazard.keyword('field')
        self.hazard_class_mapping = self.hazard.keyword('value_map')
        # There is no wet in the class mapping
        if self.wet not in self.hazard_class_mapping:
            raise ZeroImpactException(tr(
                'There is no flooded area in the hazard layers, thus there '
                'is no affected road.'))
        self.exposure_class_attribute = self.exposure.keyword(
            'road_class_field')
        exposure_value_mapping = self.exposure.keyword('value_mapping')

        hazard_provider = self.hazard.layer.dataProvider()
        affected_field_index = hazard_provider.fieldNameIndex(
            self.hazard_class_attribute)
        # see #818: should still work if there is no valid attribute
        if affected_field_index == -1:
            pass
            # message = tr('''Parameter "Affected Field"(='%s')
            # is not present in the attribute table of the hazard layer.
            #     ''' % (affected_field, ))
            # raise GetDataError(message)

        # LOGGER.info('Affected field: %s' % self.hazard_class_attribute)
        # LOGGER.info('Affected field index: %s' % affected_field_index)

        # Filter geometry and data using the extent
        requested_extent = QgsRectangle(*self.requested_extent)
        # This is a hack - we should be setting the extent CRS
        # in the IF base class via safe/engine/core.py:calculate_impact
        # for now we assume the extent is in 4326 because it
        # is set to that from geo_extent
        # See issue #1857
        transform = QgsCoordinateTransform(
            self.requested_extent_crs, self.hazard.crs())

        projected_extent = transform.transformBoundingBox(requested_extent)
        request = QgsFeatureRequest()
        request.setFilterRect(projected_extent)

        # Split line_layer by hazard and save as result:
        # 1) Filter from hazard inundated features
        #   2) Mark roads as inundated (1) or not inundated (0)

        #################################
        #           REMARK 1
        #  In qgis 2.2 we can use request to filter inundated
        #  polygons directly (it allows QgsExpression). Then
        #  we can delete the lines and call
        #
        #  request = ....
        #  hazard_poly = union_geometry(H, request)
        #
        ################################

        hazard_features = self.hazard.layer.getFeatures(request)
        hazard_poly = None
        for feature in hazard_features:
            attributes = feature.attributes()
            if affected_field_index != -1:
                value = attributes[affected_field_index]
                if value not in self.hazard_class_mapping[self.wet]:
                    continue
            if hazard_poly is None:
                hazard_poly = QgsGeometry(feature.geometry())
            else:
                # Make geometry union of inundated polygons
                # But some feature.geometry() could be invalid, skip them
                tmp_geometry = hazard_poly.combine(feature.geometry())
                try:
                    if tmp_geometry.isGeosValid():
                        hazard_poly = tmp_geometry
                except AttributeError:
                    pass

        ###############################################
        # END REMARK 1
        ###############################################

        if hazard_poly is None:
            message = tr(
                'There are no objects in the hazard layer with %s (Affected '
                'Field) in %s (Affected Value). Please check the value or use '
                'a different extent.' % (
                    self.hazard_class_attribute,
                    self.hazard_class_mapping[self.wet]))
            raise GetDataError(message)

        # Clip exposure by the extent
        extent_as_polygon = QgsGeometry().fromRect(requested_extent)
        line_layer = clip_by_polygon(self.exposure.layer, extent_as_polygon)
        # Find inundated roads, mark them
        line_layer = split_by_polygon(
            line_layer,
            hazard_poly,
            request,
            mark_value=(self.target_field, 1))

        # Generate simple impact report
        epsg = get_utm_epsg(self.requested_extent[0], self.requested_extent[1])
        destination_crs = QgsCoordinateReferenceSystem(epsg)
        transform = QgsCoordinateTransform(
            self.exposure.layer.crs(), destination_crs)

        roads_data = line_layer.getFeatures()
        road_type_field_index = line_layer.fieldNameIndex(
            self.exposure_class_attribute)
        target_field_index = line_layer.fieldNameIndex(self.target_field)

        classes = [tr('Temporarily closed')]
        self.init_report_var(classes)

        for road in roads_data:
            attributes = road.attributes()

            usage = attributes[road_type_field_index]
            usage = main_type(usage, exposure_value_mapping)

            geom = road.geometry()
            geom.transform(transform)
            length = geom.length()

            affected = False
            if attributes[target_field_index] == 1:
                affected = True

            self.classify_feature(classes[0], usage, length, affected)

        self.reorder_dictionaries()

        style_classes = [dict(label=tr('Not Inundated'), value=0,
                              colour='#1EFC7C', transparency=0, size=0.5),
                         dict(label=tr('Inundated'), value=1,
                              colour='#F31A1C', transparency=0, size=0.5)]
        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        # Convert QgsVectorLayer to inasafe layer and return it
        if line_layer.featureCount() == 0:
            # Raising an exception seems poor semantics here....
            raise ZeroImpactException(
                tr('No roads are flooded in this scenario.'))

        impact_data = self.generate_data()

        extra_keywords = {
            'map_title': self.map_title(),
            'legend_title': self.metadata().key('legend_title'),
            'target_field': self.target_field
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        impact_layer = Vector(
            data=line_layer,
            name=self.map_title(),
            keywords=impact_layer_keywords,
            style_info=style_info
        )

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
