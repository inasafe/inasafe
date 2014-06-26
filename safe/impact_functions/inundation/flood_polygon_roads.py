# coding=utf-8
"""Polygon flood on roads."""
import logging
from qgis.core import (
    QgsRectangle,
    QgsFeatureRequest,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)
from safe.metadata import (
    unit_wetdry,
    hazard_flood,
    layer_vector_polygon,
    hazard_tsunami,
    exposure_road,
    unit_road_type_type,
    layer_vector_line,
    exposure_definition,
    hazard_definition
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
from safe.common.qgis_vector_tools import split_by_polygon, clip_by_polygon

LOGGER = logging.getLogger('InaSAFE')


class FloodVectorRoadsExperimentalFunction(FunctionProvider):
    # noinspection PyUnresolvedReferences
    """Simple experimental impact function for inundation.

    :author Dmitry Kolesov
    :rating 1
    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype=='vector'
    :param requires category=='exposure' and \
                    subcategory in ['road'] and \
                    layertype=='vector'
    """
    class Metadata(ImpactFunctionMetadata):
        """Metadata for FloodVectorRoadsExperimentalFunction.

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
                'id': 'FloodVectorRoadsExperimentalFunction',
                'name': tr('Flood Vector Roads Experimental Function'),
                'impact': tr('Be flooded'),
                'author': 'Dmitry Kolesov',
                'date_implemented': 'N/A',
                'overview': tr('N/A'),
                'categories': {
                    'hazard': {
                        'definition': hazard_definition,
                        'subcategory': [hazard_flood, hazard_tsunami],
                        'units': unit_wetdry,
                        'layer_constraints': [layer_vector_polygon]
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

    title = tr('Be flooded')

    parameters = OrderedDict([
        # This field of impact layer marks inundated roads by '1' value
        ('target_field', 'flooded'),
        # This field of the exposure layer contains
        # information about road types
        ('road_type_field', 'TYPE'),
        # This field of the  hazard layer contains information
        # about inundated areas
        ('affected_field', 'affected'),
        # This value in 'affected_field' of the hazard layer
        # marks the areas as inundated
        ('affected_value', '1'),
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
        """Set up the extent of area of interest ([xmin, ymin, xmax, ymax]).

        Mandatory method.

        :param extent: Extent for the analysis.
        """
        self.extent = extent

    def run(self, layers):
        """Experimental impact function for flood polygons on roads.

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
        hazard_provider = hazard.dataProvider()
        affected_field_index = hazard_provider.fieldNameIndex(affected_field)
        #see #818: should still work if there is no valid attribute
        if affected_field_index == -1:
            pass
            # message = tr('''Parameter "Affected Field"(='%s')
            #     is not present in the attribute table of the hazard layer.
            #     ''' % (affected_field, ))
            #raise GetDataError(message)

        LOGGER.info('Affected field: %s' % affected_field)
        LOGGER.info('Affected field index: %s' % affected_field_index)

        exposure = exposure.get_layer()
        # Filter geometry and data using the extent
        extent = QgsRectangle(*self.extent)
        request = QgsFeatureRequest()
        request.setFilterRect(extent)

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

        hazard_features = hazard.getFeatures(request)
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
                '''There are no objects in the hazard layer with "Affected
                value"='%s'. Please check the value or use a different
                extent.''' % (affected_value, ))
            raise GetDataError(message)

        # Clip exposure by the extent
        extent_as_polygon = QgsGeometry().fromRect(extent)
        line_layer = clip_by_polygon(exposure, extent_as_polygon)
        # Find inundated roads, mark them
        line_layer = split_by_polygon(
            line_layer, hazard_poly, request, mark_value=(target_field, 1))

        # Generate simple impact report
        epsg = get_utm_epsg(self.extent[0], self.extent[1])
        destination_crs = QgsCoordinateReferenceSystem(epsg)
        transform = QgsCoordinateTransform(exposure.crs(), destination_crs)
        road_len = flooded_len = 0  # Length of roads
        roads_by_type = dict()      # Length of flooded roads by types

        roads_data = line_layer.getFeatures()
        road_type_field_index = line_layer.fieldNameIndex(road_type_field)
        target_field_index = line_layer.fieldNameIndex(target_field)

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
