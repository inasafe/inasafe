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
from safe.common.utilities import unique_filename
from safe.common.tables import Table, TableRow
from safe.impact_functions.bases.classified_vh_classified_ve import \
    ClassifiedVHClassifiedVE
from safe.impact_functions.generic.classified_polygon_landcover\
    .metadata_definitions \
    import ClassifiedPolygonHazardLandCoverFunctionMetadata


class ClassifiedPolygonHazardLandCoverFunction(ClassifiedVHClassifiedVE):

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
        self.validate()
        self.prepare()

        # Identify hazard and exposure layers
        hazard = self.hazard.layer
        exposure = self.exposure.layer

        type_attr = self.parameters['land_cover_type_field'].value

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
        impact_fields.append(QgsField(self.target_field, QVariant.Int))
        writer = QgsVectorFileWriter(
            filename, "utf-8", impact_fields, QGis.WKBPolygon, exposure.crs())

        # prepare area calculator object
        area_calc = QgsDistanceArea()
        area_calc.setSourceCrs(exposure.crs())
        area_calc.setEllipsoid("WGS84")
        area_calc.setEllipsoidalMode(True)

        # iterate over all exposure polygons and calculate the impact
        all_landcovers = {}
        imp_landcovers = {}
        for f in exposure.getFeatures(QgsFeatureRequest(extent_exposure)):
            geometry = f.geometry()
            bbox = geometry.boundingBox()
            # clip the exposure geometry to requested extent if necessary
            if not extent_exposure.contains(bbox):
                geometry = geometry.intersection(extent_exposure_geom)
            landcover_type = f[type_attr]

            # add to the total area of this land cover type
            if landcover_type not in all_landcovers:
                all_landcovers[landcover_type] = 0.
            area = area_calc.measure(geometry) / 1e4
            all_landcovers[landcover_type] += area

            # find possible intersections with hazard layer
            impacted_geometries = []
            for hazard_id in hazard_index.intersects(bbox):
                hazard_geometry = hazard_features[hazard_id].geometry()
                impact_geometry = geometry.intersection(hazard_geometry)
                if not impact_geometry.wkbType() == QGis.WKBPolygon and \
                   not impact_geometry.wkbType() == QGis.WKBMultiPolygon:
                    continue   # no intersection found

                # add to the affected area of this land cover type
                if landcover_type not in imp_landcovers:
                    imp_landcovers[landcover_type] = 0.
                area = area_calc.measure(impact_geometry) / 1e4
                imp_landcovers[landcover_type] += area

                # write the impacted geometry
                f_impact = QgsFeature(impact_fields)
                f_impact.setGeometry(impact_geometry)
                f_impact.setAttributes(f.attributes()+[1])
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
            #     f_out.setAttributes(f.attributes()+[0])
            #     writer.addFeature(f_out)

        del writer
        impact_layer = QgsVectorLayer(filename, "Impacted Land Cover", "ogr")

        # Generate the report of affected areas
        total_affected_area = round(sum(imp_landcovers.values()), 1)
        total_area = round(sum(all_landcovers.values()), 1)
        table_body = [
            self.question,
            TableRow(
                [tr('Land Cover Type'),
                 tr('Affected Area (ha)'),
                 tr('Affected Area (%)'),
                 tr('Total (ha)')],
                header=True),
            TableRow(
                [tr('All'),
                 total_affected_area,
                 "%.0f%%" % ((total_affected_area / total_area) \
                              if total_area != 0 else 0) * 100,
                 total_area]),
            TableRow(tr('Breakdown by land cover type'), header=True)]
        for t, v in all_landcovers.iteritems():
            affected = imp_landcovers[t] if t in imp_landcovers else 0.
            affected_area = round(affected, 1)
            area = round(v, 1)
            percent_affected = affected_area / area * 100
            table_body.append(
                TableRow([t, affected_area, "%.0f%%" % percent_affected, area])
            )
        impact_summary = Table(table_body).toNewlineFreeString()

        # Define style for the impact layer
        transparent_color = QColor()
        transparent_color.setAlpha(0)
        style_classes = [
            dict(
                label=tr('Affected'), value=1,
                colour=transparent_color, border_color='#F31A1C',
                transparency=0, size=0.5)]
        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        # Create vector layer and return
        impact_layer = Vector(
            data=impact_layer,
            name=tr('Land cover affected by each hazard zone'),
            keywords={
                'impact_summary': impact_summary,
                'map_title': tr('Affected Land Cover'),
                'target_field': self.target_field
            },
            style_info=style_info)

        self._impact = impact_layer
        return impact_layer
