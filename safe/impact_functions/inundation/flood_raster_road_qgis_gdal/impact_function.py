# coding=utf-8
"""Impact of flood on roads."""
from qgis.core import (
    QgsRectangle,
    QgsFeatureRequest,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)

from safe.impact_functions.base import ImpactFunction
from safe.common.tables import Table, TableRow
from safe.impact_functions.inundation.flood_raster_road_qgis_gdal\
    .metadata_definitions import FloodRasterRoadsGdalMetadata
from safe.utilities.i18n import tr
from safe.storage.vector import Vector
from safe.common.utilities import get_utm_epsg
from safe.common.exceptions import GetDataError
from safe.gis.qgis_raster_tools import (
    clip_raster, polygonize_gdal)
from safe.gis.qgis_vector_tools import (
    split_by_polygon_in_out,
    extent_to_geo_array,
    reproject_vector_layer)


class FloodRasterRoadsGdalFunction(ImpactFunction):
    # noinspection PyUnresolvedReferences
    """Simple impact function for inundation for road."""
    _metadata = FloodRasterRoadsGdalMetadata()

    def __init__(self):
        """Constructor."""
        super(FloodRasterRoadsGdalFunction, self).__init__()

    def _tabulate(self, flooded_len, question, road_len, roads_by_type):
        table_body = [
            question,
            TableRow(
                [tr('Road Type'),
                 tr('Flooded in the threshold (m)'),
                 tr('Total (m)')],
                header=True),
            TableRow(
                [tr('All'),
                 int(flooded_len),
                 int(road_len)]),
            TableRow(tr('Breakdown by road type'), header=True)]
        for t, v in roads_by_type.iteritems():
            table_body.append(
                TableRow([t, int(v['flooded']), int(v['total'])])
            )
        return table_body

    def run(self, layers=None):
        """Run the impact function.

        :param layers: List of layers expected to contain at least:
            H: Polygon layer of inundation areas
            E: Vector layer of roads
        :type layers: list

        :returns: A new line layer with inundated roads marked.
        :type: safe_layer
        """
        self.validate()
        self.prepare(layers)

        target_field = self.target_field
        road_type_field = self.parameters['road_type_field']
        threshold_min = self.parameters['min threshold [m]']
        threshold_max = self.parameters['max threshold [m]']

        if threshold_min > threshold_max:
            message = tr(
                'The minimal threshold is greater then the maximal specified '
                'threshold. Please check the values.')
            raise GetDataError(message)

        # Extract data
        H = self.hazard    # Flood
        E = self.exposure  # Roads

        H = H.get_layer()
        E = E.get_layer()

        # reproject self.extent to the hazard projection
        hazard_crs = H.crs()
        hazard_authid = hazard_crs.authid()

        if hazard_authid == 'EPSG:4326':
            viewport_extent = self.requested_extent
        else:
            geo_crs = QgsCoordinateReferenceSystem()
            geo_crs.createFromSrid(4326)
            viewport_extent = extent_to_geo_array(
                QgsRectangle(*self.requested_extent), geo_crs, hazard_crs)

        # Align raster extent and viewport
        # assuming they are both in the same projection
        raster_extent = H.dataProvider().extent()
        clip_xmin = raster_extent.xMinimum()
        # clip_xmax = raster_extent.xMaximum()
        clip_ymin = raster_extent.yMinimum()
        # clip_ymax = raster_extent.yMaximum()
        if viewport_extent[0] > clip_xmin:
            clip_xmin = viewport_extent[0]
        if viewport_extent[1] > clip_ymin:
            clip_ymin = viewport_extent[1]
        # TODO: Why have these two clauses when they are not used?
        # Commenting out for now.
        # if viewport_extent[2] < clip_xmax:
        #     clip_xmax = viewport_extent[2]
        # if viewport_extent[3] < clip_ymax:
        #     clip_ymax = viewport_extent[3]

        height = ((viewport_extent[3] - viewport_extent[1]) /
                  H.rasterUnitsPerPixelY())
        height = int(height)
        width = ((viewport_extent[2] - viewport_extent[0]) /
                 H.rasterUnitsPerPixelX())
        width = int(width)

        raster_extent = H.dataProvider().extent()
        xmin = raster_extent.xMinimum()
        xmax = raster_extent.xMaximum()
        ymin = raster_extent.yMinimum()
        ymax = raster_extent.yMaximum()

        x_delta = (xmax - xmin) / H.width()
        x = xmin
        for i in range(H.width()):
            if abs(x - clip_xmin) < x_delta:
                # We have found the aligned raster boundary
                break
            x += x_delta
            _ = i

        y_delta = (ymax - ymin) / H.height()
        y = ymin
        for i in range(H.width()):
            if abs(y - clip_ymin) < y_delta:
                # We have found the aligned raster boundary
                break
            y += y_delta
        clip_extent = [x, y, x + width * x_delta, y + height * y_delta]

        # Clip and polygonize
        small_raster = clip_raster(
            H, width, height, QgsRectangle(*clip_extent))
        (flooded_polygon_inside, flooded_polygon_outside) = polygonize_gdal(
            small_raster, threshold_min, threshold_max)

        # Filter geometry and data using the extent
        extent = QgsRectangle(*self.requested_extent)
        request = QgsFeatureRequest()
        request.setFilterRect(extent)

        if flooded_polygon_inside is None:
            message = tr(
                'There are no objects in the hazard layer with "value">%s.'
                'Please check the value or use other extent.' % (
                    threshold_min, ))
            raise GetDataError(message)

        # reproject the flood polygons to exposure projection
        exposure_crs = E.crs()
        exposure_authid = exposure_crs.authid()

        if hazard_authid != exposure_authid:
            flooded_polygon_inside = reproject_vector_layer(
                flooded_polygon_inside, E.crs())
            flooded_polygon_outside = reproject_vector_layer(
                flooded_polygon_outside, E.crs())

        # Clip exposure by the extent
        # extent_as_polygon = QgsGeometry().fromRect(extent)
        # no need to clip since It is using a bbox request
        # line_layer = clip_by_polygon(
        #    E,
        #    extent_as_polygon
        # )
        # Find inundated roads, mark them
        line_layer = split_by_polygon_in_out(
            E,
            flooded_polygon_inside,
            flooded_polygon_outside,
            target_field, 1, request)

        target_field_index = line_layer.dataProvider().\
            fieldNameIndex(target_field)

        # Generate simple impact report
        epsg = get_utm_epsg(self.requested_extent[0], self.requested_extent[1])
        output_crs = QgsCoordinateReferenceSystem(epsg)
        transform = QgsCoordinateTransform(E.crs(), output_crs)
        road_len = flooded_len = 0  # Length of roads
        roads_by_type = dict()      # Length of flooded roads by types

        roads_data = line_layer.getFeatures()
        road_type_field_index = line_layer.fieldNameIndex(road_type_field)
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

        table_body = self._tabulate(flooded_len, self.question, road_len,
                                    roads_by_type)

        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('Roads inundated')

        style_classes = [
            dict(
                label=tr('Not Inundated'), value=0,
                colour='#1EFC7C', transparency=0, size=0.5),
            dict(
                label=tr('Inundated'), value=1,
                colour='#F31A1C', transparency=0, size=0.5)]
        style_info = dict(
            target_field=target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        # Convert QgsVectorLayer to inasafe layer and return it
        line_layer = Vector(
            data=line_layer,
            name=tr('Flooded roads'),
            keywords={
                'impact_summary': impact_summary,
                'map_title': map_title,
                'target_field': target_field},
            style_info=style_info)
        self._impact = line_layer
        return line_layer
