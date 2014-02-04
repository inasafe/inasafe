# coding=utf-8
"""Polygon flood on roads."""
from PyQt4.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsRectangle,
    QgsFeatureRequest,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)

from safe.common.utilities import OrderedDict
from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.common.tables import Table, TableRow
from safe.common.utilities import ugettext as tr
from safe.storage.vector import Vector
from safe.common.utilities import get_utm_epsg
from safe.common.exceptions import GetDataError
from safe.common.qgis_vector_tools import split_by_polygon


class FloodVectorRoadsExperimentalFunction(FunctionProvider):
    # noinspection PyUnresolvedReferences
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

    title = tr('Be flooded')

    parameters = OrderedDict([
        # This field of impact layer marks inundated roads by '1' value
        ('target_field', 'flooded'),
        # This field of the exposure layer contains
        # information about road types
        ('road_type_field', 'TYPE'),
        # This field of the  hazard layer contains information
        # about inundated areas
        ('affected_field', 'FLOODPRONE'),
        # This value in 'affected_field' of the hazard layer
        # marks the areas as inundated
        ('affected_value', 'YES'),
        ('postprocessors', OrderedDict([('RoadType', {'on': True})]))
    ])

    def __init__(self):
        """Constructor."""
        self.extent = None

    # noinspection PyMethodMayBeStatic
    def get_function_type(self):
        """Get type of the impact function.

        :returns:   'qgis2.0'
        """
        return 'qgis2.0'

    def set_extent(self, extent):
        """
        Set up the extent of area of interest ([xmin, ymin, xmax, ymax]).

        Mandatory method.

        :param extent: Extent for the analysis.
        """
        self.extent = extent

    def run(self, layers):
        """
        Experimental impact function for flood polygons on roads.

        :param layers: List of layers expected to contain H: Polygon layer of
            inundation areas E: Vector layer of roads
        """
        target_field = self.parameters['target_field']
        road_type_field = self.parameters['road_type_field']
        affected_field = self.parameters['affected_field']
        affected_value = self.parameters['affected_value']

        # Extract data
        hazard = get_hazard_layer(layers)    # Flood
        exposure = get_exposure_layer(layers)  # Roads

        question = get_question(hazard.get_name(), exposure.get_name(), self)

        hazard = hazard.get_layer()
        h_provider = hazard.dataProvider()
        affected_field_index = h_provider.fieldNameIndex(affected_field)
        if affected_field_index == -1:
            message = tr('''Parameter "Affected Field"(='%s')
                doesn't presented in the
                attribute table of the hazard layer.''' % (affected_field, ))
            raise GetDataError(message)

        exposure = exposure.get_layer()
        # crs = exposure.crs().toWkt()
        e_provider = exposure.dataProvider()
        fields = e_provider.fields()
        # If target_field does not exist, add it:
        if fields.indexFromName(target_field) == -1:
            e_provider.addAttributes([QgsField(target_field, QVariant.Int)])
        target_field_index = e_provider.fieldNameIndex(target_field)
        # fields = e_provider.fields()

        # Filter geometry and data using the extent
        extent = QgsRectangle(*self.extent)
        request = QgsFeatureRequest()
        request.setFilterRect(extent)

        # Split line_layer by H and save as result:
        #   1) Filter from H inundated features
        #   2) Mark roads as inundated (1) or not inundated (0)

        affected_field_type = \
            h_provider.fields()[affected_field_index].typeName()
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

        h_data = hazard.getFeatures(request)
        hazard_poly = None
        for mpolygon in h_data:
            attrs = mpolygon.attributes()
            if attrs[affected_field_index] != affected_value:
                continue
            if hazard_poly is None:
                hazard_poly = QgsGeometry(mpolygon.geometry())
            else:
                # Make geometry union of inundated polygons

                # But some mpolygon.geometry() could be invalid, skip them
                tmp_geometry = hazard_poly.combine(mpolygon.geometry())
                try:
                    if tmp_geometry.isGeosValid():
                        hazard_poly = tmp_geometry
                except AttributeError:
                    pass

        ###############################################
        # END REMARK 1
        ###############################################

        if hazard_poly is None:
            message = tr('''There are no objects in the hazard layer with
                "Affected value"='%s'. Please check the value or use a
                different extent.''' % (affected_value, ))
            raise GetDataError(message)

        # Set roads as not inundated by default
        exposure.startEditing()
        e_data = exposure.getFeatures(request)
        for feat in e_data:
            feat.setAttribute(target_field_index, 0)
            exposure.updateFeature(feat)
        exposure.commitChanges()
        # Find inundated roads, mark them
        line_layer = split_by_polygon(
            exposure,
            hazard_poly,
            request,
            mark_value=(target_field_index, 1))

        # Generate simple impact report
        epsg = get_utm_epsg(self.extent[0], self.extent[1])
        crs_dest = QgsCoordinateReferenceSystem(epsg)
        transform = QgsCoordinateTransform(exposure.crs(), crs_dest)
        road_len = flooded_len = 0  # Length of roads
        roads_by_type = dict()      # Length of flooded roads by types

        roads_data = line_layer.getFeatures()
        road_type_field_index = line_layer.fieldNameIndex(road_type_field)
        for road in roads_data:
            attrs = road.attributes()
            road_type = attrs[road_type_field_index]
            geom = road.geometry()
            geom.transform(transform)
            length = geom.length()
            road_len += length

            if not road_type in roads_by_type:
                roads_by_type[road_type] = {'flooded': 0, 'total': 0}
            roads_by_type[road_type]['total'] += length

            if attrs[target_field_index] == 1:
                flooded_len += length
                roads_by_type[road_type]['flooded'] += length
        table_body = [
            question,
            TableRow(
                [tr('Road Type'),
                 tr('Temporarily closed (m)'),
                 tr('Total (m)')],
                header=True),
            TableRow([tr('All'), int(flooded_len), int(road_len)]),
            TableRow(tr('Breakdown by road type'), header=True)]
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
