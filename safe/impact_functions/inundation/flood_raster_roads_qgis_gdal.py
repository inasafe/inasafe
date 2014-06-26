# coding=utf-8
"""Impact of flood on roads."""
from qgis.core import (
    QgsRectangle,
    QgsFeatureRequest,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)

from safe.metadata import (
    hazard_flood,
    hazard_tsunami,
    unit_metres_depth,
    unit_feet_depth,
    layer_raster_numeric,
    exposure_road,
    unit_road_type_type,
    layer_vector_line,
    hazard_definition,
    exposure_definition
)
from safe.common.utilities import OrderedDict
from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.common.tables import Table, TableRow
from safe.common.utilities import ugettext as tr
from safe.impact_functions.impact_function_metadata import (
    ImpactFunctionMetadata)
from safe.storage.vector import Vector
from safe.common.utilities import get_utm_epsg
from safe.common.exceptions import GetDataError
from safe.common.qgis_raster_tools import (
    clip_raster, polygonize_gdal)
from safe.common.qgis_vector_tools import (
    split_by_polygon_in_out,
    extent_to_geo_array,
    reproject_vector_layer)


class FloodRasterRoadsExperimentalFunction2(FunctionProvider):
    # noinspection PyUnresolvedReferences
    """Simple experimental impact function for inundation.

    :author Dmitry Kolesov
    :rating 1
    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype=='raster'
    :param requires category=='exposure' and \
                    subcategory in ['road'] and \
                    layertype=='vector'
        """
    def __init__(self):
        """Constructor."""
        self.extent = None

    class Metadata(ImpactFunctionMetadata):
        """Metadata for FloodRasterRoadsExperimentalFunction

        .. versionadded:: 2.1

        We only need to re-implement get_metadata(), all other behaviours
        are inherited from the abstract base class.
        """

        @staticmethod
        def get_metadata():
            """Return metadata as a dictionary.

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            dict_meta = {
                'id': 'FloodRasterRoadsExperimentalFunction',
                'name': tr('Flood Raster Roads Experimental Function'),
                'impact': tr('Be flooded in given thresholds'),
                'author': 'Dmitry Kolesov',
                'date_implemented': 'N/A',
                'overview': tr('N/A'),
                'categories': {
                    'hazard': {
                        'definition': hazard_definition,
                        'subcategory': [
                            hazard_flood,
                            hazard_tsunami
                        ],
                        'units': [
                            unit_metres_depth,
                            unit_feet_depth
                        ],
                        'layer_constraints': [layer_raster_numeric]
                    },
                    'exposure': {
                        'definition': exposure_definition,
                        'subcategory': exposure_road,
                        'units': [unit_road_type_type],
                        'layer_constraints': [layer_vector_line]
                    }
                }
            }
            return dict_meta

    title = tr('Be flooded in given thresholds')

    parameters = OrderedDict([
        # This field of impact layer marks inundated roads by '1' value
        ('target_field', 'flooded'),
        # This field of the exposure layer contains
        # information about road types
        ('road_type_field', 'TYPE'),
        ('min threshold [m]', 1.0),
        ('max threshold [m]', float('inf')),
        ('postprocessors', OrderedDict([('RoadType', {'on': True})]))
    ])

    def get_function_type(self):
        """Get type of the impact function.

        :returns:   'qgis2.0'
        """
        return 'qgis2.0'

    def set_extent(self, extent):
        """Set up the extent of area of interest.

        It is mandatory to call this method before running the analysis.

        :param extent: Extents mutator [xmin, ymin, xmax, ymax].
        :type extent: list
        """
        self.extent = extent

    def run(self, layers):
        """Experimental impact function.

        :param layers: List of layers expected to contain at least:
            H: Polygon layer of inundation areas
            E: Vector layer of roads
        :type layers: list

        :returns: A new line layer with inundated roads marked.
        :type: safe_layer
        """
        target_field = self.parameters['target_field']
        road_type_field = self.parameters['road_type_field']
        threshold_min = self.parameters['min threshold [m]']
        threshold_max = self.parameters['max threshold [m]']

        if threshold_min > threshold_max:
            message = tr(
                'The minimal threshold is greater then the maximal specified '
                'threshold. Please check the values.')
            raise GetDataError(message)

        # Extract data
        H = get_hazard_layer(layers)    # Flood
        E = get_exposure_layer(layers)  # Roads

        question = get_question(
            H.get_name(), E.get_name(), self)

        H = H.get_layer()
        E = E.get_layer()

        #reproject self.extent to the hazard projection
        hazard_crs = H.crs()
        hazard_authid = hazard_crs.authid()

        if hazard_authid == 'EPSG:4326':
            viewport_extent = self.extent
        else:
            geo_crs = QgsCoordinateReferenceSystem()
            geo_crs.createFromSrid(4326)
            viewport_extent = extent_to_geo_array(
                QgsRectangle(*self.extent), geo_crs, hazard_crs)

        #Align raster extent and viewport
        #assuming they are both in the same projection
        raster_extent = H.dataProvider().extent()
        clip_xmin = raster_extent.xMinimum()
        clip_xmax = raster_extent.xMaximum()
        clip_ymin = raster_extent.yMinimum()
        clip_ymax = raster_extent.yMaximum()
        if (viewport_extent[0] > clip_xmin):
            clip_xmin = viewport_extent[0]
        if (viewport_extent[1] > clip_ymin):
            clip_ymin = viewport_extent[1]
        if (viewport_extent[2] < clip_xmax):
            clip_xmax = viewport_extent[2]
        if (viewport_extent[3] < clip_ymax):
            clip_ymax = viewport_extent[3]

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
        extent = QgsRectangle(*self.extent)
        request = QgsFeatureRequest()
        request.setFilterRect(extent)

        if flooded_polygon_inside is None:
            message = tr(
                'There are no objects in the hazard layer with "value">%s.'
                'Please check the value or use other extent.' % (
                    threshold_min, ))
            raise GetDataError(message)

        #reproject the flood polygons to exposure projection
        exposure_crs = E.crs()
        exposure_authid = exposure_crs.authid()

        if hazard_authid != exposure_authid:
            flooded_polygon_inside = reproject_vector_layer(
                flooded_polygon_inside, E.crs())
            flooded_polygon_outside = reproject_vector_layer(
                flooded_polygon_outside, E.crs())

        # Clip exposure by the extent
        #extent_as_polygon = QgsGeometry().fromRect(extent)
        #no need to clip since It is using a bbox request
        #line_layer = clip_by_polygon(
        #    E,
        #    extent_as_polygon
        #)
        # Find inundated roads, mark them
        line_layer = split_by_polygon_in_out(
            E,
            flooded_polygon_inside,
            flooded_polygon_outside,
            target_field, 1, request)

        target_field_index = line_layer.dataProvider().\
            fieldNameIndex(target_field)

        # Generate simple impact report
        epsg = get_utm_epsg(self.extent[0], self.extent[1])
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

            if not road_type in roads_by_type:
                roads_by_type[road_type] = {'flooded': 0, 'total': 0}
            roads_by_type[road_type]['total'] += length

            if attributes[target_field_index] == 1:
                flooded_len += length
                roads_by_type[road_type]['flooded'] += length
        table_body = [
            question,
            TableRow([
                tr('Road Type'),
                tr('Flooded in the threshold (m)'),
                tr('Total (m)')],
                header=True),
            TableRow([tr('All'), int(flooded_len), int(road_len)])
        ]
        table_body.append(TableRow(
            tr('Breakdown by road type'), header=True))
        for t, v in roads_by_type.iteritems():
            table_body.append(
                TableRow([t, int(v['flooded']), int(v['total'])])
            )

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
            keywords={
                'impact_summary': impact_summary,
                'map_title': map_title,
                'target_field': target_field},
            style_info=style_info)
        return line_layer
