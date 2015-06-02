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

from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.inundation.\
    flood_polygon_roads.metadata_definitions import \
    FloodPolygonRoadsMetadata
from safe.utilities.i18n import tr
from safe.storage.vector import Vector
from safe.common.tables import Table, TableRow
from safe.common.utilities import get_utm_epsg
from safe.common.exceptions import GetDataError
from safe.gis.qgis_vector_tools import split_by_polygon, clip_by_polygon

LOGGER = logging.getLogger('InaSAFE')


class FloodVectorRoadsExperimentalFunction(ImpactFunction):
    # noinspection PyUnresolvedReferences
    """Simple experimental impact function for inundation."""
    _metadata = FloodPolygonRoadsMetadata()

    def __init__(self):
        """Constructor."""
        super(FloodVectorRoadsExperimentalFunction, self).__init__()

    def _tabulate(self, flooded_len, question, road_len, roads_by_type):
        table_body = [
            question,
            TableRow(
                [tr('Road Type'),
                 tr('Temporarily closed (m)'),
                 tr('Total (m)')],
                header=True),
            TableRow([tr('All'), int(flooded_len), int(road_len)]),
            TableRow(tr('Breakdown by road type'), header=True)]
        for road_type, value in roads_by_type.iteritems():
            table_body.append(
                TableRow([
                    road_type, int(value['flooded']), int(value['total'])])
            )
        return table_body

    def run(self, layers=None):
        """Experimental impact function for flood polygons on roads.

        :param layers: List of layers expected to contain H: Polygon layer of
            inundation areas E: Vector layer of roads
        """
        self.validate()
        self.prepare(layers)

        # Get the parameters from IF options
        road_type_field = self.parameters['road_type_field']
        affected_field = self.parameters['affected_field']
        affected_value = self.parameters['affected_value']

        # Extract data
        hazard_layer = self.hazard    # Flood
        exposure_layer = self.exposure  # Roads

        hazard_layer = hazard_layer.get_layer()
        hazard_provider = hazard_layer.dataProvider()
        affected_field_index = hazard_provider.fieldNameIndex(affected_field)
        # see #818: should still work if there is no valid attribute
        if affected_field_index == -1:
            pass
            # message = tr('''Parameter "Affected Field"(='%s')
            #     is not present in the attribute table of the hazard layer.
            #     ''' % (affected_field, ))
            # raise GetDataError(message)

        LOGGER.info('Affected field: %s' % affected_field)
        LOGGER.info('Affected field index: %s' % affected_field_index)

        exposure_layer = exposure_layer.get_layer()

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
            hazard_layer.crs()
        )
        projected_extent = transform.transformBoundingBox(requested_extent)
        request = QgsFeatureRequest()
        request.setFilterRect(projected_extent)

        # Split line_layer by hazard and save as result:
        #   1) Filter from hazard inundated features
        #   2) Mark roads as inundated (1) or not inundated (0)

        if affected_field_index != -1:
            affected_field_type = hazard_provider.fields()[
                affected_field_index].typeName()
            if affected_field_type in ['Real', 'Integer']:
                affected_value = float(affected_value)

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

        hazard_features = hazard_layer.getFeatures(request)
        hazard_poly = None
        for feature in hazard_features:
            attributes = feature.attributes()
            if affected_field_index != -1:
                if attributes[affected_field_index] != affected_value:
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
                'Field) = %s (Affected Value). Please check the value or use '
                'a different extent.' % (affected_field, affected_value))
            raise GetDataError(message)

        # Clip exposure by the extent
        extent_as_polygon = QgsGeometry().fromRect(requested_extent)
        line_layer = clip_by_polygon(exposure_layer, extent_as_polygon)
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
            exposure_layer.crs(), destination_crs)
        road_len = flooded_len = 0  # Length of roads
        roads_by_type = dict()      # Length of flooded roads by types

        roads_data = line_layer.getFeatures()
        road_type_field_index = line_layer.fieldNameIndex(road_type_field)
        target_field_index = line_layer.fieldNameIndex(self.target_field)

        for road in roads_data:
            attributes = road.attributes()
            road_type = attributes[road_type_field_index]
            if road_type.__class__.__name__ == 'QPyNullVariant':
                road_type = tr('Other')
            geom = road.geometry()
            geom.transform(transform)
            length = geom.length()
            road_len += length

            if road_type not in roads_by_type:
                roads_by_type[road_type] = {'flooded': 0, 'total': 0}
            roads_by_type[road_type]['total'] += length

            if attributes[target_field_index] == 1:
                flooded_len += length
                roads_by_type[road_type]['flooded'] += length

        table_body = self._tabulate(
            flooded_len, self.question, road_len, roads_by_type)

        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('Roads inundated')

        style_classes = [dict(label=tr('Not Inundated'), value=0,
                              colour='#1EFC7C', transparency=0, size=0.5),
                         dict(label=tr('Inundated'), value=1,
                              colour='#F31A1C', transparency=0, size=0.5)]
        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        # Convert QgsVectorLayer to inasafe layer and return it
        line_layer = Vector(
            data=line_layer,
            name=tr('Flooded roads'),
            keywords={
                'impact_summary': impact_summary,
                'map_title': map_title,
                'target_field': self.target_field},
            style_info=style_info)

        self._impact = line_layer

        return line_layer
