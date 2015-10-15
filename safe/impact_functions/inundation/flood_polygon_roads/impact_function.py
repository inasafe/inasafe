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
from collections import OrderedDict

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
from safe.storage.vector import Vector
from safe.common.utilities import get_utm_epsg
from safe.common.exceptions import GetDataError
from safe.gis.qgis_vector_tools import split_by_polygon, clip_by_polygon
from safe.impact_reports.road_exposure_report_mixin import\
    RoadExposureReportMixin
import safe.messaging as m
from safe.messaging import styles

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

        # The 'wet' variable
        self.wet = 'wet'

    def notes(self):
        """Return the notes section of the report.

        .. versionadded:: 3.2.1

        :return: The notes that should be attached to this impact report.
        :rtype: safe.messaging.Message
        """

        hazard_terminology = tr('inundated')
        flood_value = [unicode(hazard_class)
                       for hazard_class in self.hazard_class_mapping[self.wet]]

        message = m.Message(style_class='container')
        message.add(
            m.Heading(tr('Notes and assumptions'), **styles.INFO_STYLE))

        checklist = m.BulletedList()
        checklist.add(tr(
            'Roads are said to be %s when in a region with field "%s" in '
            '"%s" .' % (
                hazard_terminology,
                self.hazard_class_attribute,
                ', '.join(flood_value))))
        checklist.add(tr(
            'Roads are closed if they are %s.' % hazard_terminology))
        checklist.add(tr(
            'Roads are open if they are not %s.' % hazard_terminology))

        message.add(checklist)
        return message

    def run(self):
        """Experimental impact function for flood polygons on roads."""
        self.validate()
        self.prepare()

        # Get parameters from layer's keywords
        self.hazard_class_attribute = self.hazard.keyword('field')
        self.hazard_class_mapping = self.hazard.keyword('value_map')
        self.exposure_class_attribute = self.exposure.keyword(
            'road_class_field')

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

        LOGGER.info('Affected field: %s' % self.hazard_class_attribute)
        LOGGER.info('Affected field index: %s' % affected_field_index)

        # Filter geometry and data using the extent
        requested_extent = QgsRectangle(*self.requested_extent)
        # This is a hack - we should be setting the extent CRS
        # in the IF base class via safe/engine/core.py:calculate_impact
        # for now we assume the extent is in 4326 because it
        # is set to that from geo_extent
        # See issue #1857
        transform = QgsCoordinateTransform(
            QgsCoordinateReferenceSystem(
                'EPSG:%i' % self._requested_extent_crs),
            self.hazard.layer.crs()
        )
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
        flooded_keyword = tr('Temporarily closed (m)')
        self.affected_road_categories = [flooded_keyword]
        self.affected_road_lengths = OrderedDict([
            (flooded_keyword, {})])
        self.road_lengths = OrderedDict()

        for road in roads_data:
            attributes = road.attributes()
            road_type = attributes[road_type_field_index]
            if road_type.__class__.__name__ == 'QPyNullVariant':
                road_type = tr('Other')
            geom = road.geometry()
            geom.transform(transform)
            length = geom.length()

            if road_type not in self.road_lengths:
                self.affected_road_lengths[flooded_keyword][road_type] = 0
                self.road_lengths[road_type] = 0

            self.road_lengths[road_type] += length
            if attributes[target_field_index] == 1:
                self.affected_road_lengths[
                    flooded_keyword][road_type] += length

        impact_summary = self.html_report()

        # For printing map purpose
        map_title = tr('Roads inundated')
        legend_title = tr('Road inundated status')

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
        line_layer = Vector(
            data=line_layer,
            name=tr('Flooded roads'),
            keywords={
                'impact_summary': impact_summary,
                'map_title': map_title,
                'legend_title': legend_title,
                'target_field': self.target_field},
            style_info=style_info)

        self._impact = line_layer

        return line_layer
