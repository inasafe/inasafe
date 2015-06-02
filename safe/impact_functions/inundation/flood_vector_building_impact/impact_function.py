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
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsGeometry)

from PyQt4.QtCore import QVariant

from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.inundation.flood_vector_building_impact.\
    metadata_definitions import FloodPolygonBuildingFunctionMetadata
from safe.utilities.i18n import tr
from safe.storage.vector import Vector
from safe.common.exceptions import GetDataError
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)


class FloodPolygonBuildingFunction(
        ImpactFunction,
        BuildingExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Impact function for inundation (polygon-polygon)."""

    _metadata = FloodPolygonBuildingFunctionMetadata()

    def __init__(self):
        super(FloodPolygonBuildingFunction, self).__init__()

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
                    'field "%s" = "%s" .') % (
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

        # Get the IF parameters
        building_type_field = self.parameters['building_type_field']
        affected_field = self.parameters['affected_field']
        affected_value = self.parameters['affected_value']

        # Extract data
        hazard_layer = self.hazard    # Flood
        exposure_layer = self.exposure  # Roads

        # Prepare Hazard Layer
        hazard_layer = hazard_layer.get_layer()
        hazard_provider = hazard_layer.dataProvider()

        # Check affected field exists in the hazard layer
        affected_field_index = hazard_provider.fieldNameIndex(affected_field)
        if affected_field_index == -1:
            message = tr('Field "%s" is not present in the attribute table of '
                         'the hazard layer. Please change the Affected Field '
                         'parameter in the IF Option.') % affected_field
            raise GetDataError(message)

        # Prepare Exposure Layer
        exposure_layer = exposure_layer.get_layer()
        srs = exposure_layer.crs().toWkt()
        exposure_provider = exposure_layer.dataProvider()
        exposure_fields = exposure_provider.fields()

        # Check building_type_field exists in exposure layer
        building_type_field_index = exposure_provider.fieldNameIndex(
            building_type_field)
        if building_type_field_index == -1:
            message = tr(
                'Field "%s" is not present in the attribute table of '
                'the exposure layer. Please change the Building Type '
                'Field parameter in the IF Option.') % building_type_field
            raise GetDataError(message)

        # If target_field does not exist, add it:
        if exposure_fields.indexFromName(self.target_field) == -1:
            exposure_provider.addAttributes(
                [QgsField(self.target_field, QVariant.Int)])
        target_field_index = exposure_provider.fieldNameIndex(
            self.target_field)
        exposure_fields = exposure_provider.fields()

        # Create layer to store the lines from E and extent
        building_layer = QgsVectorLayer(
            'Polygon?crs=' + srs, 'impact_buildings', 'memory')
        building_provider = building_layer.dataProvider()

        # Set attributes
        building_provider.addAttributes(exposure_fields.toList())
        building_layer.startEditing()
        building_layer.commitChanges()

        # Filter geometry and data using the requested extent
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

        # Split building_layer by H and save as result:
        #   1) Filter from H inundated features
        #   2) Mark buildings as inundated (1) or not inundated (0)

        affected_field_type = hazard_provider.fields()[
            affected_field_index].typeName()
        if affected_field_type in ['Real', 'Integer']:
            affected_value = float(affected_value)

        hazard_data = hazard_layer.getFeatures(request)
        hazard_poly = None
        for feature in hazard_data:
            record = feature.attributes()
            if record[affected_field_index] != affected_value:
                continue
            if hazard_poly is None:
                hazard_poly = QgsGeometry(feature.geometry())
            else:
                # Make geometry union of inundated polygons
                # But some polygon.geometry() could be invalid, skip them
                tmp_geometry = hazard_poly.combine(feature.geometry())
                try:
                    if tmp_geometry.isGeosValid():
                        hazard_poly = tmp_geometry
                except AttributeError:
                    pass

        if hazard_poly is None:
            message = tr(
                'There are no objects in the hazard layer with %s '
                'value=%s. Please check your data or use another '
                'attribute.') % (
                    affected_field,
                    affected_value)
            raise GetDataError(message)

        exposure_data = exposure_layer.getFeatures(request)
        for feature in exposure_data:
            building_geom = feature.geometry()
            record = feature.attributes()
            l_feat = QgsFeature()
            l_feat.setGeometry(building_geom)
            l_feat.setAttributes(record)
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
            record = building.attributes()
            building_type = record[building_type_field_index]
            if building_type in [None, 'NULL', 'null', 'Null']:
                building_type = 'Unknown type'
            if building_type not in self.buildings:
                self.buildings[building_type] = 0
                for category in self.affected_buildings.keys():
                    self.affected_buildings[category][
                        building_type] = OrderedDict([
                            (tr('Buildings Affected'), 0)])
            self.buildings[building_type] += 1

            if record[target_field_index] == 1:
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
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        # Convert QgsVectorLayer to inasafe layer and return it.
        building_layer = Vector(
            data=building_layer,
            name=tr('Flooded buildings'),
            keywords={
                'impact_summary': impact_summary,
                'map_title': map_title,
                'target_field': self.target_field,
                'buildings_total': self.total_buildings,
                'buildings_affected': self.total_affected_buildings},
            style_info=style_info)
        self._impact = building_layer
        return building_layer
