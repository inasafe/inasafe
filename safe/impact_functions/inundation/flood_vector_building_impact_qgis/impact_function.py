# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Flood Vector Impact on
Buildings using QGIS.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from collections import OrderedDict

from qgis.core import (
    QgsField,
    QgsVectorLayer,
    QgsFeature,
    QgsRectangle,
    QgsFeatureRequest,
    QgsGeometry)
from PyQt4.QtCore import QVariant

from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.inundation.flood_vector_building_impact_qgis.\
    metadata_definitions import FloodPolygonBuildingQgisMetadata
from safe.utilities.i18n import tr
from safe.storage.vector import Vector
from safe.common.exceptions import GetDataError
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)


class FloodPolygonBuildingQgisFunction(
        ImpactFunction,
        BuildingExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Simple experimental impact function for inundation (polygon-polygon)."""

    _metadata = FloodPolygonBuildingQgisMetadata()

    def __init__(self):
        super(FloodPolygonBuildingQgisFunction, self).__init__()

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        affected_field = self.parameters['affected_field']
        affected_value = self.parameters['affected_value']
        return [
            {
                'content': tr('Notes'),
                'header': True
            },
            {
                'content': tr(
                    'Buildings are said to be inundated when in a region with '
                    'an Affected Field Parameter "%s"(=%s).') % (
                        affected_field, affected_value)
            }
        ]

    def run(self, layers=None):
        """Experimental impact function.

        Input
          layers: List of layers expected to contain
              H: Polygon layer of inundation areas
              E: Vector layer of buildings
        """
        self.validate()
        self.prepare(layers)

        # Set the target field in impact layer
        target_field = 'INUNDATED'

        # Get the IF parameters
        building_type_field = self.parameters['building_type_field']
        affected_field = self.parameters['affected_field']
        affected_value = self.parameters['affected_value']

        # Extract data
        hazard_layer = self.hazard    # Flood
        exposure_layer = self.exposure  # Roads

        hazard_layer = hazard_layer.get_layer()
        h_provider = hazard_layer.dataProvider()
        affected_field_index = h_provider.fieldNameIndex(affected_field)
        if affected_field_index == -1:
            message = tr('''Parameter "Affected Field"(='%s')
                is not present in the
                attribute table of the hazard layer.''' % (affected_field, ))
            raise GetDataError(message)

        exposure_layer = exposure_layer.get_layer()
        srs = exposure_layer.crs().toWkt()
        e_provider = exposure_layer.dataProvider()
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

        # Filter geometry and data using the requested extent
        requested_extent = QgsRectangle(*self.requested_extent)
        request = QgsFeatureRequest()
        request.setFilterRect(requested_extent)

        # Split building_layer by H and save as result:
        #   1) Filter from H inundated features
        #   2) Mark buildings as inundated (1) or not inundated (0)

        affected_field_type = h_provider.fields()[
            affected_field_index].typeName()
        if affected_field_type in ['Real', 'Integer']:
            affected_value = float(affected_value)

        h_data = hazard_layer.getFeatures(request)
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

        e_data = exposure_layer.getFeatures(request)
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
        self.buildings = {}
        self.affected_buildings = OrderedDict([
            (tr('Flooded'), {})
        ])
        buildings_data = building_layer.getFeatures()
        building_type_field_index = building_layer.fieldNameIndex(
            building_type_field)
        for building in buildings_data:
            attributes = building.attributes()
            building_type = attributes[building_type_field_index]
            if building_type in [None, 'NULL', 'null', 'Null']:
                building_type = 'Unknown type'
            if building_type not in self.buildings:
                self.buildings[building_type] = 0
                for category in self.affected_buildings.keys():
                    self.affected_buildings[category][
                        building_type] = OrderedDict([
                            (tr('Buildings Affected'), 0)])
            self.buildings[building_type] += 1

            if attributes[target_field_index] == 1:
                self.affected_buildings[tr('Flooded')][building_type][
                    tr('Buildings Affected')] += 1

        # Lump small entries and 'unknown' into 'other' category
        self._consolidate_to_other()

        impact_summary = self.generate_html_report()
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
                'target_field': target_field,
                'buildings_total': self.total_buildings,
                'buildings_affected': self.total_affected_buildings},
            style_info=style_info)
        self._impact = building_layer
        return building_layer
