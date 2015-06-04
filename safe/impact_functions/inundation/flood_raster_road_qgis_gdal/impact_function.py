# coding=utf-8
"""Impact of flood on roads."""
from qgis.core import (
    QGis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsGeometry,
    QgsPoint,
    QgsRectangle,
    QgsSpatialIndex,
    QgsVectorFileWriter,
    QgsVectorLayer
)
from PyQt4.QtCore import QVariant

from safe.common.tables import Table, TableRow
from safe.impact_functions.bases.continuous_rh_classified_ve import \
    ContinuousRHClassifiedVE
from safe.impact_functions.inundation.flood_raster_road_qgis_gdal\
    .metadata_definitions import FloodRasterRoadsGdalMetadata
from safe.utilities.i18n import tr
from safe.storage.vector import Vector
from safe.common.utilities import get_utm_epsg, unique_filename
from safe.common.exceptions import GetDataError
from safe.gis.qgis_raster_tools import (
    clip_raster, polygonize_gdal)
from safe.gis.qgis_vector_tools import (
    split_by_polygon_in_out,
    extent_to_geo_array,
    create_layer,
    reproject_vector_layer)



def _raster_to_vector_cells(flood, thr_min, thr_max):
    """ take raster and generate vectors features (rectangles) for cells
        which are within threshold (thr_min < V < thr_max) """

    rp = flood.dataProvider()
    rb = rp.block(1, rp.extent(), rp.xSize(), rp.ySize())
    rp_xmin = rp.extent().xMinimum()
    rp_ymax = rp.extent().yMaximum()
    cellx = rp.extent().width() / rp.xSize()
    celly = rp.extent().height() / rp.ySize()

    vl = QgsVectorLayer("Polygon?crs=epsg:4326", "flood polygons", "memory")
    feats = []

    for y in xrange(rp.ySize()):
        for x in xrange(rp.xSize()):
            v = rb.value(y,x)
            if v < thr_min or v > thr_max: continue
            x0,x1 = rp_xmin+(x*cellx), rp_xmin+((x+1)*cellx)
            y0,y1 = rp_ymax-(y*celly), rp_ymax-((y+1)*celly)
            outer_ring = [QgsPoint(x0,y0),QgsPoint(x1,y0),QgsPoint(x1,y1),QgsPoint(x0,y1),QgsPoint(x0,y0)]
            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPolygon([outer_ring]))
            feats.append(f)

    res, feats = vl.dataProvider().addFeatures(feats)

    flood_cells_map = {}
    for f in feats:
        flood_cells_map[f.id()] = f

    if QGis.QGIS_VERSION_INT >= 20800:
        # woohoo we can use bulk insert (much faster)
        index = QgsSpatialIndex(vl.getFeatures())
    else:
        index = QgsSpatialIndex()
        for f in vl.getFeatures():
            index.insertFeature(f)

    return index, flood_cells_map


def _add_output_feature(feats, geom, is_flooded, fields, orig_attrs, target_field):
    # make sure to explode multi-part features
    geoms = geom.asGeometryCollection() if geom.isMultipart() else [ geom ]
    for g in geoms:
        f = QgsFeature(fields)
        f.setGeometry(g)
        for attr_no, attr_val in enumerate(orig_attrs):
            f.setAttribute(attr_no, attr_val)
        f.setAttribute(target_field, is_flooded)
        feats.append(f)



def _union_geometries(geoms):
    """ Return a geometry which is union of the passed list of geometries """
    if QGis.QGIS_VERSION_INT >= 20400:
        # woohoo we can use fast union (needs GEOS >= 3.3)
        return QgsGeometry.unaryUnion(geoms)
    else:
        # uhh we need to use slow iterative union
        if len(geoms) == 0:
            return QgsGeometry()
        result_geometry = QgsGeometry(geoms[0])
        for g in geoms[1:]:
            result_geometry = result_geometry.combine(g)
        return result_geometry


def _intersect_roads_flood(roads, request, index, flood_cells_map, output_layer, target_field):

    feats = []
    fields = output_layer.dataProvider().fields()

    rd = 0
    for f in roads.getFeatures(request):
        ids = index.intersects(f.geometry().boundingBox())
        geoms = [ flood_cells_map[i].geometry() for i in ids ]
        flood_geom = _union_geometries(geoms)

        in_geom = f.geometry().intersection(flood_geom)
        if in_geom and (in_geom.wkbType() == QGis.WKBLineString or in_geom.wkbType() == QGis.WKBMultiLineString):
            _add_output_feature(feats, in_geom, 1, fields, f.attributes(), target_field)

        out_geom = f.geometry().difference(flood_geom)
        if out_geom and (out_geom.wkbType() == QGis.WKBLineString or out_geom.wkbType() == QGis.WKBMultiLineString):
            _add_output_feature(feats, out_geom, 0, fields, f.attributes(), target_field)

        rd += 1
        if rd % 1000 == 0:
            output_layer.dataProvider().addFeatures(feats)
            feats = []

    output_layer.dataProvider().addFeatures(feats)



class FloodRasterRoadsGdalFunction(ContinuousRHClassifiedVE):
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

    def run(self):
        """Run the impact function.

        :returns: A new line layer with inundated roads marked.
        :type: safe_layer
        """
        self.validate()
        self.prepare()

        target_field = self.target_field
        road_type_field = self.parameters['road_type_field'].value
        threshold_min = self.parameters['min threshold'].value
        threshold_max = self.parameters['max threshold'].value

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

        # Clip hazard raster
        small_raster = clip_raster(
            H, width, height, QgsRectangle(*clip_extent))

        # Create vector features from the flood raster
        # For each raster cell there is one rectangular polygon
        # Data also get spatially indexed for faster operation
        index, flood_cells_map = _raster_to_vector_cells(small_raster, threshold_min, threshold_max)

        # Filter geometry and data using the extent
        extent = QgsRectangle(*self.requested_extent)
        request = QgsFeatureRequest()
        request.setFilterRect(extent)

        if len(flood_cells_map) == 0:
            message = tr(
                'There are no objects in the hazard layer with "value">%s.'
                'Please check the value or use other extent.' % (
                    threshold_min, ))
            raise GetDataError(message)

        # reproject the flood polygons to exposure projection
        # TODO[MD] reprojection
        #exposure_crs = E.crs()
        #exposure_authid = exposure_crs.authid()
        #
        #if hazard_authid != exposure_authid:
        #    flooded_polygons = reproject_vector_layer(
        #        flooded_polygons, E.crs())

        line_layer_tmp = create_layer(E)
        new_field = QgsField(target_field, QVariant.Int)
        line_layer_tmp.dataProvider().addAttributes([new_field])
        line_layer_tmp.updateFields()

        filename = unique_filename(suffix='.shp')
        QgsVectorFileWriter.writeAsVectorFormat(
            line_layer_tmp, filename, "utf-8", None, "ESRI Shapefile")
        line_layer = QgsVectorLayer(filename, "flooded roads", "ogr")

        # Do the heavy work - for each road get flood polygon for that area
        # and do the intersection/difference to find out which parts are flooded
        _intersect_roads_flood(E, request, index, flood_cells_map, line_layer, target_field)

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
