# coding=utf-8
from qgis.core import (
    QgsField,
    QgsVectorLayer,
    QgsFeature,
    QgsRectangle,
    QgsFeatureRequest,
    QgsGeometry)
from PyQt4.QtCore import QVariant
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.common.tables import Table, TableRow
from safe.impact_functions.inundation.flood_vector_building_impact_qgis.\
    metadata_definitions import FloodPolygonBuildingQgisMetadata
from safe.utilities.i18n import tr
from safe.storage.vector import Vector
from safe.common.exceptions import GetDataError


class FloodNativePolygonExperimentalFunction(ImpactFunction):
    # noinspection PyUnresolvedReferences
    """Simple experimental impact function for inundation (polygon-polygon).

    :author Dmitry Kolesov
    :rating 1
    :param requires category=='hazard' and \
                    subcategory=='flood' and \
                    layertype=='vector'
    :param requires category=='exposure' and \
                    subcategory in ['structure'] and \
                    layertype=='vector'
    """

    _metadata = FloodPolygonBuildingQgisMetadata

    def __init__(self):
        super(FloodNativePolygonExperimentalFunction, self).__init__()

    @property
    def function_type(self):
        """Property for the type of impact function ('old-style' or 'qgis2.0')."""
        return 'qgis2.0'

    def prepare(self, layers=None):
        """Prepare this impact function for running the analysis"""
        super(FloodNativePolygonExperimentalFunction, self).prepare()

        if layers is not None:
            self.hazard = get_hazard_layer(layers)
            self.exposure = get_exposure_layer(layers)

    def method_name(self, building_count, buildings_by_type, flooded_count,
                    question):
        table_body = [
            question,
            TableRow(
                [tr('Building Type'), tr('Flooded'), tr('Total')],
                header=True),
            TableRow(
                [tr('All'), int(flooded_count), int(building_count)]),
            TableRow(
                tr('Breakdown by building type'), header=True)]
        for t, v in buildings_by_type.iteritems():
            table_body.append(
                TableRow([t, int(v['flooded']), int(v['total'])]))
        return table_body

    def run(self, layers=None):
        """Experimental impact function.

        Input
          layers: List of layers expected to contain
              H: Polygon layer of inundation areas
              E: Vector layer of roads
        """
        self.prepare(layers)

        target_field = self.parameters['target_field'].value
        building_type_field = self.parameters['building_type_field'].value
        affected_field = self.parameters['affected_field'].value
        affected_value = self.parameters['affected_value'].value

        # Extract data
        H = self.hazard    # Flood
        E = self.exposure  # Roads

        question = get_question(
            H.get_name(), E.get_name(), self)

        H = H.get_layer()
        h_provider = H.dataProvider()
        affected_field_index = h_provider.fieldNameIndex(affected_field)
        if affected_field_index == -1:
            message = tr('''Parameter "Affected Field"(='%s')
                is not present in the
                attribute table of the hazard layer.''' % (affected_field, ))
            raise GetDataError(message)

        E = E.get_layer()
        srs = E.crs().toWkt()
        e_provider = E.dataProvider()
        fields = e_provider.fields()
        # If target_field does not exist, add it:
        if fields.indexFromName(target_field) == -1:
            e_provider.addAttributes(
                [QgsField(target_field, QVariant.Int)])
        target_field_index = e_provider.fieldNameIndex(target_field)
        fields = e_provider.fields()

        # Create layer for store the lines from E and extent
        building_layer = QgsVectorLayer(
            'Polygon?crs=' + srs, 'impact_buildings', 'memory')
        building_provider = building_layer.dataProvider()

        # Set attributes
        building_provider.addAttributes(fields.toList())
        building_layer.startEditing()
        building_layer.commitChanges()

        # Filter geometry and data using the extent
        extent = QgsRectangle(*self.extent)
        request = QgsFeatureRequest()
        request.setFilterRect(extent)

        # Split building_layer by H and save as result:
        #   1) Filter from H inundated features
        #   2) Mark buildings as inundated (1) or not inundated (0)

        affected_field_type = h_provider.fields()[
            affected_field_index].typeName()
        if affected_field_type in ['Real', 'Integer']:
            affected_value = float(affected_value)

        h_data = H.getFeatures(request)
        hazard_poly = None
        for mpolygon in h_data:
            attributes = mpolygon.attributes()
            if attributes[affected_field_index] != affected_value:
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

        if hazard_poly is None:
            message = tr(
                '''There are no objects in the hazard layer with "Affected
                value"='%s'. Please check the value or use other extent.''' %
                (affected_value, ))
            raise GetDataError(message)

        e_data = E.getFeatures(request)
        for feat in e_data:
            building_geom = feat.geometry()
            attributes = feat.attributes()
            l_feat = QgsFeature()
            l_feat.setGeometry(building_geom)
            l_feat.setAttributes(attributes)
            if hazard_poly.intersects(building_geom):
                l_feat.setAttribute(target_field_index, 1)
            else:

                l_feat.setAttribute(target_field_index, 0)
            (_, __) = building_layer.dataProvider().addFeatures([l_feat])
        building_layer.updateExtents()

        # Generate simple impact report

        building_count = flooded_count = 0  # Count of buildings
        buildings_by_type = dict()      # Length of flooded roads by types

        buildings_data = building_layer.getFeatures()
        building_type_field_index = building_layer.fieldNameIndex(
            building_type_field)
        for building in buildings_data:
            building_count += 1
            attributes = building.attributes()
            building_type = attributes[building_type_field_index]
            if building_type in [None, 'NULL', 'null', 'Null']:
                building_type = 'Unknown type'
            if building_type not in buildings_by_type:
                buildings_by_type[building_type] = {'flooded': 0, 'total': 0}
            buildings_by_type[building_type]['total'] += 1

            if attributes[target_field_index] == 1:
                flooded_count += 1
                buildings_by_type[building_type]['flooded'] += 1

        table_body = self.method_name(building_count, buildings_by_type,
                                      flooded_count, question)

        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('Buildings inundated')

        style_classes = [
            dict(label=tr('Not Inundated'), value=0, colour='#1EFC7C',
                 transparency=0, size=0.5),
            dict(label=tr('Inundated'), value=1, colour='#F31A1C',
                 transparency=0, size=0.5)]
        style_info = dict(
            target_field=target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        # Convert QgsVectorLayer to inasafe layer and return it.
        building_layer = Vector(
            data=building_layer,
            name=tr('Flooded buildings'),
            keywords={
                'impact_summary': impact_summary,
                'map_title': map_title,
                'target_field': target_field},
            style_info=style_info)
        return building_layer
