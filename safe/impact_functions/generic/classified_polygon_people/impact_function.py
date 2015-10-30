# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Generic Impact function on
Land Cover for Classified Hazard.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'Samweli Twesa Mwakisambwe "Samweli" <smwltwesa6@gmail.com>'
__date__ = '8/5/15'


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
from safe.impact_functions.bases.classified_vh_classified_ve import \
    ClassifiedVHClassifiedVE
from safe.impact_functions.generic.classified_polygon_people\
    .metadata_definitions \
    import ClassifiedPolygonHazardPolygonPeopleFunctionMetadata

from safe.impact_reports.area_exposure_report_mixin import \
    AreaExposureReportMixin
from safe.impact_functions.core import no_population_impact_message
from safe.common.exceptions import InaSAFEError, ZeroImpactException


class ClassifiedPolygonHazardPolygonPeopleFunction(
        ClassifiedVHClassifiedVE, AreaExposureReportMixin):

    _metadata = ClassifiedPolygonHazardPolygonPeopleFunctionMetadata()

    def __init__(self):
        super(ClassifiedPolygonHazardPolygonPeopleFunction, self).__init__()

        # Set the question of the IF (as the hazard data is not an event)
        self.question = ('In each of the hazard zones which areas  '
                         'might be affected.')

    def run(self):
        """Risk plugin for classified polygon hazard on area with population.

        Counts areas exposed to hazard zones and then computes the the
        proportion of each area that is inundated. The population in each
        area is then calculated as the proportion of the original population
        to the flooded area.

        :returns: Impact layer
        :rtype: Vector
        """
        self.validate()
        self.prepare()

        # Identify hazard and exposure layers
        hazard = self.hazard.layer
        exposure = self.exposure.layer

        type_attr = self.parameters['area_type_field'].value

        # TODO use keyword to take id and population values
        # id_attr = self.exposure.keyword('id_field')
        # pop_attr = self.exposure.keyword('population_field')

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
        unaffected_fields = exposure.dataProvider().fields()
        unaffected_fields.append(QgsField(self.target_field, QVariant.Int))

        writer = QgsVectorFileWriter(
            filename, "utf-8", impact_fields, QGis.WKBPolygon, exposure.crs())

        # iterate over all exposure polygons and calculate the impact
        all_areas = {}
        imp_areas = {}

        all_areas_ids = {}
        all_affected_areas = {}
        all_areas_population = {}
        all_affected_geometry = []

        area_population_attribute = self.exposure.keyword('area_population_field')
        area_id_attribute = self.exposure.keyword('field')

        for f in exposure.getFeatures(QgsFeatureRequest(extent_exposure)):
            geometry = f.geometry()
            if geometry is not None:
                bbox = geometry.boundingBox()
            else:
                continue
            # clip the exposure geometry to requested extent if necessary
            if not extent_exposure.contains(bbox):
                geometry = geometry.intersection(extent_exposure_geom)
            area_type = f[type_attr]
            area_id = f.attribute(area_id_attribute)
            all_areas_population[area_id] = f.attribute(area_population_attribute)

            # add to the total area of this land cover type
            if area_type not in all_areas:
                all_areas[area_type] = 0.

            if area_id not in all_areas_ids:
                all_areas_ids[area_id] = 0.

            area = geometry.area()

            all_areas[area_type] += area
            all_areas_ids[area_id] += area

            # find possible intersections with hazard layer
            impacted_geometries = []
            # unaffected_geometries = []
            # impacted_features = {}
            for hazard_id in hazard_index.intersects(bbox):
                hazard_geometry = hazard_features[hazard_id].geometry()
                impact_geometry = geometry.intersection(hazard_geometry)

                if not impact_geometry.wkbType() == QGis.WKBPolygon and \
                   not impact_geometry.wkbType() == QGis.WKBMultiPolygon:
                    continue  # no intersection found

                # find unaffected area geometry
                unaffected_geometry = geometry.symDifference(impact_geometry)

                all_affected_geometry.append(impact_geometry)

                # add to the affected area of this area type
                if area_type not in imp_areas:
                    imp_areas[area_type] = 0.
                if area_id not in all_affected_areas:
                    all_affected_areas[area_id] = 0.
                area = impact_geometry.area()
                imp_areas[area_type] += area
                all_affected_areas[area_id] += area

                # for later check of the past affected geometries so as to avoid
                # overlapping of unaffected and affected geometries
                # for geometry in all_affected_geometry:
                #     geo_intersection = geometry.intersection(unaffected_geometry)
                #
                #     if not geo_intersection.wkbType() == QGis.WKBPolygon and \
                #             not geo_intersection.wkbType() == QGis.WKBMultiPolygon:
                #         continue  # no intersection found
                #     unaffected_geometry = geometry.symDifference(unaffected_geometry)

                # write the impacted geometry

                f_impact = QgsFeature(impact_fields)
                f_impact.setGeometry(impact_geometry)
                f_impact.setAttributes(f.attributes()+[1])

                f_unaffected = QgsFeature(unaffected_fields)
                f_unaffected.setGeometry(unaffected_geometry)
                f_unaffected.setAttributes(f.attributes()+[0])
                writer.addFeature(f_impact)
                writer.addFeature(f_unaffected)

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
        impact_layer = QgsVectorLayer(filename, "Impacted Areas", "ogr")

        # Calculating the affect number of people percentage
        # affected_people_percentages = {}
        # for area in exposure.getFeatures(QgsFeatureRequest(extent_exposure)):

        # Generate the report of affected areas

        self.total_population = sum(all_areas_population.values())
        self.areas = all_areas_ids
        self.affected_areas = all_affected_areas
        self.areas_population = all_areas_population

        # Calculating number of people affected
        for t, v in all_areas_ids.iteritems():

            if t in all_affected_areas:
                affected = all_affected_areas[t]
            else:
                affected = 0.0

            single_total_area = v
            if v:
                affected_area_ratio = affected / single_total_area
            else:
                affected_area_ratio = 0

            number_people_affected = (
                affected_area_ratio * all_areas_population[t])

            # rounding to float without decimal, we can't have number
            # of people with decimal
            number_people_affected = round(number_people_affected, 0)

            self.affected_population[t] = number_people_affected

        total_affected_population = self.total_affected_population

        if total_affected_population == 0:
            message = no_population_impact_message(self.question)
            raise ZeroImpactException(message)

        impact_summary = self.html_report()

        # Define style for the impact layer
        transparent_color = QColor()
        transparent_color.setAlpha(0)
        style_classes = [
            dict(
                label=tr('Not Affected'), value=0, colour='#1EFC7C',
                transparency=0, size=0.5),
            dict(
                label=tr('Medium Affected'), value=0.5, colour='#FFA500',
                transparency=0, size=0.5),
            dict(
                label=tr('Affected'), value=1,
                border_color='#F31A1C', colour='#F31A1C',
                transparency=0, size=0.5)]
        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        # Create vector layer and return
        impact_layer = Vector(
            data=impact_layer,
            name=tr('Areas affected by each hazard zone'),
            keywords={
                'impact_summary': impact_summary,
                'map_title': tr('Affected Areas'),
                'target_field': self.target_field
            },
            style_info=style_info)

        self._impact = impact_layer
        return impact_layer
