# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Generic Impact function on
Land Cover for Classified Hazard.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from qgis.core import (
    QGis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsGeometry,
    QgsRectangle,
    QgsSpatialIndex,
    QgsVectorFileWriter,
    QgsVectorLayer,
)
from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QColor

from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.common.utilities import unique_filename, format_decimal
from safe.utilities.pivot_table import FlatTable, PivotTable
import safe.messaging as m
from safe.impact_functions.bases.classified_vh_classified_ve import \
    ClassifiedVHClassifiedVE
from safe.impact_functions.generic.classified_polygon_landcover\
    .metadata_definitions \
    import ClassifiedPolygonHazardLandCoverFunctionMetadata


class ClassifiedPolygonHazardLandCoverFunction(
    ClassifiedVHClassifiedVE):

    _metadata = ClassifiedPolygonHazardLandCoverFunctionMetadata()

    def __init__(self):
        super(ClassifiedPolygonHazardLandCoverFunction, self).__init__()

        # Set the question of the IF (as the hazard data is not an event)
        self.question = ('In each of the hazard zones which land cover types '
                         'might be affected.')

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        return []   # TODO: what to put here?

    def run(self):
        """Risk plugin for classified polygon hazard on land cover.

        Counts area of land cover types exposed to hazard zones.

        :returns: Impact layer
        :rtype: Vector
        """

        # Identify hazard and exposure layers
        hazard = self.hazard.layer
        exposure = self.exposure.layer

        type_attr = self.parameters['land_cover_type_field'].value

        hazard_class_attribute = self.hazard.keyword('field')
        hazard_value_to_class = {}
        for key, values in self.hazard.keyword('value_map').iteritems():
            for value in values:
                hazard_value_to_class[value] = key

        # prepare objects for re-projection of geometries
        crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
        hazard_to_exposure = QgsCoordinateTransform(
            hazard.crs(), exposure.crs())
        wgs84_to_hazard = QgsCoordinateTransform(
            crs_wgs84, hazard.crs())
        wgs84_to_exposure = QgsCoordinateTransform(
            crs_wgs84, exposure.crs())

        extent = QgsRectangle(
            self.requested_extent[0], self.requested_extent[1],
            self.requested_extent[2], self.requested_extent[3])
        extent_hazard = wgs84_to_hazard.transformBoundingBox(extent)
        extent_exposure = wgs84_to_exposure.transformBoundingBox(extent)
        extent_exposure_geom = QgsGeometry.fromRect(extent_exposure)

        # make spatial index of hazard
        hazard_index = QgsSpatialIndex()
        hazard_features = {}
        for f in hazard.getFeatures(QgsFeatureRequest(extent_hazard)):
            f.geometry().transform(hazard_to_exposure)
            hazard_index.insertFeature(f)
            hazard_features[f.id()] = QgsFeature(f)

        # create impact layer
        filename = unique_filename(suffix='.shp')
        impact_fields = exposure.dataProvider().fields()
        impact_fields.append(QgsField(self.target_field, QVariant.String))
        writer = QgsVectorFileWriter(
            filename, "utf-8", impact_fields, QGis.WKBPolygon, exposure.crs())

        # iterate over all exposure polygons and calculate the impact
        for f in exposure.getFeatures(QgsFeatureRequest(extent_exposure)):
            geometry = f.geometry()
            bbox = geometry.boundingBox()
            # clip the exposure geometry to requested extent if necessary
            if not extent_exposure.contains(bbox):
                geometry = geometry.intersection(extent_exposure_geom)
            landcover_type = f[type_attr]

            # find possible intersections with hazard layer
            impacted_geometries = []
            for hazard_id in hazard_index.intersects(bbox):
                hazard_geometry = hazard_features[hazard_id].geometry()
                impact_geometry = geometry.intersection(hazard_geometry)
                if not impact_geometry.wkbType() == QGis.WKBPolygon and \
                   not impact_geometry.wkbType() == QGis.WKBMultiPolygon:
                    continue   # no intersection found

                hazard_value = hazard_features[hazard_id][hazard_class_attribute]
                hazard_type = hazard_value_to_class.get(hazard_value)

                # write the impacted geometry
                f_impact = QgsFeature(impact_fields)
                f_impact.setGeometry(impact_geometry)
                f_impact.setAttributes(f.attributes()+[hazard_type])
                writer.addFeature(f_impact)

                impacted_geometries.append(impact_geometry)

            # TODO: uncomment if not affected polygons should be written
            # # Make sure the geometry we work with is valid, otherwise geom.
            # # processing operations (especially difference) may fail.
            # # Validity checking is a slow operation, it would be better if we
            # # could assume that all geometries are valid...
            # if not geometry.isGeosValid():
            #     geometry = geometry.buffer(0, 0)
            #
            # # write also not affected part of the exposure's feature
            # geometry_out = geometry.difference(
            #     QgsGeometry.unaryUnion(impacted_geometries))
            # if geometry_out and (geometry_out.wkbType() == QGis.WKBPolygon or
            #         geometry_out.wkbType() == QGis.WKBMultiPolygon):
            #     f_out = QgsFeature(impact_fields)
            #     f_out.setGeometry(geometry_out)
            #     f_out.setAttributes(f.attributes()+[self._not_affected_value])
            #     writer.addFeature(f_out)

        del writer
        impact_layer = QgsVectorLayer(filename, "Impacted Land Cover", "ogr")

        zone_field = None
        if self.aggregator:
            zone_field = self.aggregator.exposure_aggregation_field

        report_data = _report_data(impact_layer,
                                   self.target_field,
                                   type_attr,
                                   zone_field)

        # Generate the report of affected areas
        impact_summary = impact_table = _format_report(report_data)

        # Define style for the impact layer
        transparent_color = QColor()
        transparent_color.setAlpha(0)
        style_classes = [
            dict(
                label=tr('High'), value='high',
                colour='#F31A1C', border_color='#000000',
                transparency=0, size=0.5),
            dict(
                label=tr('Medium'), value='medium',
                colour='#ffe691', border_color='#000000',
                transparency=0, size=0.5),
            dict(
                label=tr('Low'), value='low',
                colour='#acffb6', border_color='#000000',
                transparency=0, size=0.5)]
        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        extra_keywords = {
            'impact_summary': impact_summary,
            'impact_table': impact_table,
            'map_title': tr('Affected Land Cover'),
            'target_field': self.target_field
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create vector layer and return
        impact_layer = Vector(
            data=impact_layer,
            name=tr('Land cover affected by each hazard zone'),
            keywords=impact_layer_keywords,
            style_info=style_info)

        self._impact = impact_layer
        return impact_layer


# non-member private functions used within this module


def format_pivot_table(pivot_table, caption=None, header_text='', total_columns=False, total_rows=False):

    table = m.Table(style_class='table table-condensed table-striped')
    table.caption = caption

    row = m.Row()
    row.add(m.Cell(header_text, header=True))
    for column_name in pivot_table.columns:
        row.add(m.Cell(column_name, header=True))
    table.add(row)

    for row_name, data_row in zip(pivot_table.rows, pivot_table.data):
        row = m.Row()
        row.add(m.Cell(row_name))
        for column_value in data_row:
            row.add(m.Cell(format_decimal(0.1, column_value), align='right'))
        table.add(row)

    if total_columns:
        row = m.Row()
        row.add(m.Cell(tr('All')))
        for column_value in pivot_table.total_columns:
            row.add(m.Cell(format_decimal(0.1, column_value), align='right'))
        table.add(row)

    return table


def _report_data(impact_layer, target_field, land_cover_field, zone_field):
    """
    Prepare report data dictionary that will be used in the final report

    :param impact_layer: Output impact layer from the IF
    :param target_field: Field name in impact layer with hazard type
    :param land_cover_field: Field name in impact layer with land cover
    :param zone_field: Field name in impact layer with aggregation zone
                       (None if aggregation is not being done)
    :return: dict
    """

    # prepare area calculator object
    area_calc = QgsDistanceArea()
    area_calc.setSourceCrs(impact_layer.crs())
    area_calc.setEllipsoid("WGS84")
    area_calc.setEllipsoidalMode(True)

    my_table = FlatTable('landcover', 'hazard', 'zone')
    for f in impact_layer.getFeatures():

        area = area_calc.measure(f.geometry()) / 1e4
        zone = f[zone_field] if zone_field is not None else None

        my_table.add_value(area,
                    landcover=f[land_cover_field],
                    hazard=f[target_field],
                    zone=zone)

    pivot_table = PivotTable(my_table,
                             row_field="landcover",
                             column_field="hazard")

    return { 'impacted': pivot_table }


def _format_report(report_data):
    """
    Convert dictionary with report data to formatted report

    :param report_data: dict
    :return: m.Message
    """

    message = m.Message(style_class='container')

    table = format_pivot_table(report_data['impacted'],
                               header_text=tr('Affected Area (ha)'),
                               total_columns=True)

    message.add(table)
    return message.to_html(suppress_newlines=True)
