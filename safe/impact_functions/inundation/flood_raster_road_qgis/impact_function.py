# coding=utf-8
"""Impact of flood on roads.

.. warning:: This Impact Function is currently disabled in
    favour of flood_raster_roads_qgis_gdal which provides
    better performance. TS 11 June 2014
"""
__author__ = 'lucernae'

from qgis.core import (
    QgsRectangle,
    QgsFeatureRequest,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)

from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.inundation\
    .flood_raster_road_qgis.metadata_definitions import \
    FloodRasterRoadsExperimentalMetadata
from safe.common.tables import Table, TableRow
from safe.utilities.i18n import tr
from safe.storage.vector import Vector
from safe.common.utilities import get_utm_epsg
from safe.common.exceptions import GetDataError
from safe.gis.qgis_raster_tools import polygonize, clip_raster
from safe.gis.qgis_vector_tools import split_by_polygon, clip_by_polygon


class FloodRasterRoadsQGISFunction(ImpactFunction):
    """Impact function for inundation on roads using QGIS libs."""
    _metadata = FloodRasterRoadsExperimentalMetadata

    def __init__(self):
        super(FloodRasterRoadsQGISFunction, self).__init__()

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
            TableRow(
                tr('Breakdown by road type'), header=True)]
        for t, v in roads_by_type.iteritems():
            table_body.append(
                TableRow([t, int(v['flooded']), int(v['total'])])
            )
        return table_body

    def run(self, layers=None):
        """Experimental impact function."""
        self.validate()
        self.prepare(layers)

        target_field = self.target_field
        road_type_field = self.parameters['road_type_field']
        threshold_min = self.parameters['min threshold [m]']
        threshold_max = self.parameters['max threshold [m]']

        if threshold_min > threshold_max:
            message = tr('''The minimal threshold is
                greater then the maximal specified threshold.
                Please check the values.''')
            raise GetDataError(message)

        # Extract data
        H = self.hazard    # Flood
        E = self.exposure  # Roads

        H = H.get_layer()
        E = E.get_layer()

        # Get necessary width and height of raster
        height = (self.requested_extent[3] - self.requested_extent[1]) / (
            H.rasterUnitsPerPixelY())
        height = int(height)
        width = (self.requested_extent[2] - self.requested_extent[0]) / (
            H.rasterUnitsPerPixelX())
        width = int(width)

        # Align raster extent and self.extent
        raster_extent = H.dataProvider().extent()
        xmin = raster_extent.xMinimum()
        xmax = raster_extent.xMaximum()
        ymin = raster_extent.yMinimum()
        ymax = raster_extent.yMaximum()

        x_delta = (xmax - xmin) / H.width()
        x = xmin
        for i in range(H.width()):
            if abs(x - self.requested_extent[0]) < x_delta:
                # We have found the aligned raster boundary
                break
            x += x_delta
            _ = i

        y_delta = (ymax - ymin) / H.height()
        y = ymin
        for i in range(H.width()):
            if abs(y - self.requested_extent[1]) < y_delta:
                # We have found the aligned raster boundary
                break
            y += y_delta
        clip_extent = [x, y, x + width * x_delta, y + height * y_delta]

        # Clip and polygonize
        small_raster = clip_raster(
            H, width, height, QgsRectangle(*clip_extent))
        flooded_polygon = polygonize(
            small_raster, threshold_min, threshold_max)

        # Filter geometry and data using the extent
        requested_extent = QgsRectangle(*self.requested_extent)
        request = QgsFeatureRequest()
        request.setFilterRect(requested_extent)

        if flooded_polygon is None:
            message = tr('''There are no objects
                in the hazard layer with
                "value">'%s'.
                Please check the value or use other
                extent.''' % (threshold_min, ))
            raise GetDataError(message)

        # Clip exposure by the extent
        extent_as_polygon = QgsGeometry().fromRect(requested_extent)
        line_layer = clip_by_polygon(
            E,
            extent_as_polygon
        )
        # Find inundated roads, mark them
        line_layer = split_by_polygon(
            line_layer,
            flooded_polygon,
            request,
            mark_value=(target_field, 1))

        # Find inundated roads, mark them
        # line_layer = split_by_polygon(
        #     E,
        #     flooded_polygon,
        #     request,
        #     mark_value=(target_field, 1))
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

        style_classes = [dict(label=tr('Not Inundated'), value=0,
                              colour='#1EFC7C', transparency=0, size=0.5),
                         dict(label=tr('Inundated'), value=1,
                              colour='#F31A1C', transparency=0, size=0.5)]
        style_info = dict(target_field=target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')

        # Convert QgsVectorLayer to inasafe layer and return it
        line_layer = Vector(
            data=line_layer,
            name=tr('Flooded roads'),
            keywords={'impact_summary': impact_summary,
                      'map_title': map_title,
                      'target_field': target_field},
            style_info=style_info)
        self._impact = line_layer
        return line_layer
