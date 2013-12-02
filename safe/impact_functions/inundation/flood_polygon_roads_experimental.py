import math

from PyQt4.QtCore import QVariant, QSettings
from qgis.core import (
    QgsField,
    QgsVectorLayer,
    QgsFeature,
    QgsRectangle,
    QgsFeatureRequest,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)

from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.common.tables import Table, TableRow
from safe.common.utilities import ugettext as tr
from safe.storage.vector import Vector


class FloodVectorRoadsExperimentalFunction(FunctionProvider):
    """
    Simple experimental impact function for inundation

    :author Dmitry Kolesov
    :rating 1
    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype=='vector'
    :param requires category=='exposure' and \
                    subcategory in ['road'] and \
                    layertype=='vector'
    """

    target_field = 'flooded'    # This field marks inundated roads by '1' value
    road_type_field = 'TYPE'    # This field contains information about road types
    title = tr('Be flooded')

    def get_function_type(self):
        """Get type of the impact function.

        :returns:   'qgis2.0' or 'numpy'
        """
        return 'qgis2.0'

    def set_extent(self, extent):
        """
        Set up the extent of area of interest ([xmin, ymin, xmax, ymax]).

        Mandatory method.
        """
        self.extent = extent

    def get_utm_zone(self, longitude):
        return int((math.floor((longitude + 180.0) / 6.0) + 1) % 60)

    def get_epsg(self, longitude, latitude):
        epsg = 32600
        if latitude < 0.0:
            epsg += 100
        epsg += self.get_utm_zone(longitude)
        return epsg

    def run(self, layers):
        """
        Experimental impact function

        Input
          layers: List of layers expected to contain
              H: Polygon layer of inundation areas
              E: Vector layer of roads
        """

        # Extract data

        H = get_hazard_layer(layers)    # Flood
        E = get_exposure_layer(layers)  # Roads

        question = get_question(H.get_name(),
                                E.get_name(),
                                self)

        E = E.as_qgis_native()
        H = H.as_qgis_native()
        srs = E.crs().toWkt()
        e_provider = E.dataProvider()
        fields = e_provider.fields()
        # If target_field does not exist, add it:
        if fields.indexFromName(self.target_field) == -1:
            e_provider.addAttributes([QgsField(self.target_field,
                                               QVariant.Int)])
        target_field_index = e_provider.fieldNameIndex(self.target_field)
        fields = e_provider.fields()

        # Create layer for store the lines from E and extent
        line_layer = QgsVectorLayer('LineString?crs=' + srs, 'impact_lines', 'memory')
        line_provider = line_layer.dataProvider()

        # Set attributes
        line_provider.addAttributes(fields.toList())
        line_layer.startEditing()
        line_layer.commitChanges()

        # Filter geometry and data using the extent
        extent = QgsRectangle(*self.extent)
        request=QgsFeatureRequest()
        request.setFilterRect(extent)

        # Split line_layer by H and save as result
        h_data = H.getFeatures(request)
        hazard_poly = None
        for mpolygon in h_data:
            if hazard_poly is None:
                hazard_poly = QgsGeometry(mpolygon.geometry())
            else:
                hazard_poly = hazard_poly.combine(mpolygon.geometry())

        e_data = E.getFeatures(request)
        for feat in e_data:
            line_geom = feat.geometry()
            attrs = feat.attributes()
            if hazard_poly.intersects(line_geom):
                # Check intersection
                int_geom = QgsGeometry(line_geom.intersection(hazard_poly)).asGeometryCollection()
                for g in int_geom:
                    if g.type() == 1:   # Linestring
                        l_feat = QgsFeature()
                        l_feat.setGeometry(g)
                        l_feat.setAttributes(attrs)
                        l_feat.setAttribute(target_field_index, 1)
                        (res, out_feat) = line_layer.dataProvider().addFeatures([l_feat])

                # Check difference
                diff_geom = QgsGeometry(line_geom.symDifference(hazard_poly)).asGeometryCollection()
                for g in diff_geom:
                    if g.type() == 1:   # Linestring
                        l_feat = QgsFeature()
                        l_feat.setGeometry(g)
                        l_feat.setAttributes(attrs)
                        l_feat.setAttribute(target_field_index, 0)
                        (res, out_feat) = line_layer.dataProvider().addFeatures([l_feat])
            else:
                l_feat = QgsFeature()
                l_feat.setGeometry(line_geom)
                l_feat.setAttributes(attrs)
                l_feat.setAttribute(target_field_index, 0)
                (res, out_feat) = line_layer.dataProvider().addFeatures([l_feat])
        line_layer.updateExtents()

        # Generate simple impact report
        epsg = self.get_epsg(self.extent[0], self.extent[1])
        crs_dest = QgsCoordinateReferenceSystem(epsg)
        transform = QgsCoordinateTransform(E.crs(), crs_dest)
        road_len = flooded_len = 0  # Length of roads
        roads_by_type = dict()      # Length of flooded roads by types

        roads_data = line_layer.getFeatures()
        road_type_field_index = line_layer.fieldNameIndex(self.road_type_field)
        for road in roads_data:
            attrs = road.attributes()
            road_type = attrs[road_type_field_index]
            geom = road.geometry()
            geom.transform(transform)
            length = geom.length()
            road_len += length

            if not roads_by_type.has_key(road_type):
                roads_by_type[road_type] = {'flooded': 0, 'total': 0}  # (flooded, total)
            roads_by_type[road_type]['total'] += length

            if attrs[target_field_index] == 1:
                flooded_len += length
                roads_by_type[road_type]['flooded'] += length
        table_body = [question,
                      TableRow([tr('Road Type'),
                                tr('Temporarily closed (m)'),
                                tr('Total (m)')],
                               header=True),
                      TableRow([tr('All'), int(flooded_len), int(road_len)])]
        table_body.append(TableRow(tr('Breakdown by road type'),
                                       header=True))
        for t, v in roads_by_type.iteritems():
            table_body.append(
                TableRow([t, int(v['flooded']), int(v['total'])])
            )

        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('Roads inundated')

        style_classes = [dict(label=tr('Not Inundated'), value=0,
                              colour='#1EFC7C', transparency=0, size=1),
                         dict(label=tr('Inundated'), value=1,
                              colour='#F31A1C', transparency=0, size=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')

        # Convert QgsVectorLayer to inasafe layer and return it
        line_layer = Vector(data=line_layer,
                   name=tr('Flooded roads'),
                   keywords={'impact_summary': impact_summary,
                             'map_title': map_title,
                             'target_field': self.target_field},
                   style_info=style_info)
        return line_layer
