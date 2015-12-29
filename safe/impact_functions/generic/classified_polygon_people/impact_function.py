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
from safe.common.exceptions import ZeroImpactException


class ClassifiedPolygonHazardPolygonPeopleFunction(
        ClassifiedVHClassifiedVE, AreaExposureReportMixin):

    _metadata = ClassifiedPolygonHazardPolygonPeopleFunctionMetadata()

    def __init__(self):
        super(ClassifiedPolygonHazardPolygonPeopleFunction, self).__init__()

        # Set the question of the IF (as the hazard data is not an event)
        self.question = ('In each of the hazard zones which areas  '
                         'might be affected.')
        self.all_areas_ids = {}
        self.all_affected_areas = {}
        self.all_areas_population = {}

    def run(self):
        """Risk plugin for classified polygon hazard on area with population.

        Counts areas exposed to hazard zones and then computes the the
        proportion of each area that is affected. The population in each
        area is then calculated as the proportion of the original population
        to the affected area.

        :returns: Impact layer
        :rtype: Vector
        """
        self.validate()
        self.prepare()

        self.provenance.append_step(
            'Calculating Step',
            'Impact function is calculating the impact.')

        # Identify hazard and exposure layers
        hazard = self.hazard.layer
        exposure = self.exposure.layer

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
        for feature in hazard.getFeatures(QgsFeatureRequest(extent_hazard)):
            feature.geometry().transform(hazard_to_exposure)
            hazard_index.insertFeature(feature)
            hazard_features[feature.id()] = QgsFeature(feature)

        # create impact layer
        filename = unique_filename(suffix='.shp')
        impact_fields = exposure.dataProvider().fields()
        impact_fields.append(QgsField(self.target_field, QVariant.Int))
        unaffected_fields = exposure.dataProvider().fields()
        unaffected_fields.append(QgsField(self.target_field, QVariant.Int))

        writer = QgsVectorFileWriter(
            filename, "utf-8", impact_fields, QGis.WKBPolygon, exposure.crs())

        # Evaluating the impact
        self.evaluate_impact(
            exposure,
            extent_exposure,
            extent_exposure_geom,
            hazard_index,
            hazard_features,
            writer,
            unaffected_fields,
            impact_fields)

        del writer
        impact_layer = QgsVectorLayer(filename, "Impacted Areas", "ogr")

        # Generate the report of affected areas

        self.total_population = sum(self.all_areas_population.values())
        self.areas = self.all_areas_ids
        self.affected_areas = self.all_affected_areas
        self.areas_population = self.all_areas_population

        # Calculating number of people affected
        # This will help area report mixin to know how
        # to calculate the all row values before other
        # rows values in the report table

        self.evaluate_affected_people()

        impact_summary = self.html_report()

        # Define style for the impact layer
        transparent_color = QColor()
        transparent_color.setAlpha(0)
        style_classes = [
            dict(
                label=tr('Not Affected'), value=1, colour='#1EFC7C',
                transparency=0, size=0.5),
            dict(
                label=tr('Medium Affected'), value=2, colour='#FFA500',
                transparency=0, size=0.5),
            dict(
                label=tr('Affected'), value=3,
                border_color='#F31A1C', colour='#F31A1C',
                transparency=0, size=0.5)]
        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        extra_keywords = {
            'impact_summary': impact_summary,
            'target_field': self.target_field,
            'map_title': tr('Affected Areas'),
        }

        self.set_if_provenance()

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create vector layer and return
        impact_layer = Vector(
            data=impact_layer,
            name=tr('Areas affected by each hazard zone'),
            keywords=impact_layer_keywords,
            style_info=style_info)

        self._impact = impact_layer
        return impact_layer

    def evaluate_impact(
            self,
            exposure,
            extent_exposure,
            extent_exposure_geom,
            hazard_index,
            hazard_features,
            writer,
            unaffected_fields,
            impact_fields):

        """ Iterate over all exposure polygons and calculate the impact
        :param exposure: Exposure layer
        :type exposure: QgsMapLayer, Layer

        :param extent_exposure: Exposure extent
        :type extent_exposure: QgsRectangle

        :param extent_exposure_geom: Geometry of the extent exposure
        :type extent_exposure_geom: QgsGeometry

        :param hazard_index: Index on hazard features
        :type hazard_index: QgsSpatialIndex

        :param hazard_features: List of hazard features
        :type hazard_features: {}

        :param writer: Object of writing the impact layer
        :type writer: QgsVectorFileWriter

        :param unaffected_fields: Unaffected fields in the impact layer
        :type unaffected_fields: {}

        :param impact_fields: Impacted fields in the impact layer
        :type impact_fields: {}


        :returns: impacted_geometries
        :rtype: []
        """
        # Taking area necessary attributes
        area_id_attribute = self.exposure.keyword('field')
        type_attr = self.exposure.keyword('area_population_field')
        area_population_attribute = self.exposure.keyword(
            'area_population_field')

        all_affected_geometry = []

        all_areas = {}
        imp_areas = {}
        impacted_geometries = []

        for feature in exposure.getFeatures(
                QgsFeatureRequest(extent_exposure)):
            geometry = feature.geometry()

            if geometry is not None:
                bbox = geometry.boundingBox()
                geometry_area = geometry.area()
            else:
                continue

            # clip the exposure geometry to requested extent if necessary
            if not extent_exposure.contains(bbox):
                geometry = geometry.intersection(extent_exposure_geom)

            area_type = feature[type_attr]
            area_id = feature.attribute(area_id_attribute)
            self.all_areas_population[area_id] = feature.attribute(
                area_population_attribute)

            # add to the total area of this land cover type
            if area_type not in all_areas:
                all_areas[area_type] = 0.

            if area_id not in self.all_areas_ids:
                self.all_areas_ids[area_id] = 0.

            area = geometry.area()

            all_areas[area_type] += area
            self.all_areas_ids[area_id] += geometry_area

            # find possible intersections with hazard layer

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
                if area_id not in self.all_affected_areas:
                    self.all_affected_areas[area_id] = 0.
                area = impact_geometry.area()
                imp_areas[area_type] += area
                self.all_affected_areas[area_id] += area

                self.assign_impact_level(
                    feature,
                    hazard_id,
                    hazard_features,
                    unaffected_fields,
                    impact_fields,
                    unaffected_geometry,
                    impact_geometry,
                    writer)

                impacted_geometries.append(impact_geometry)

        return impacted_geometries

    def assign_impact_level(
            self,
            feature,
            hazard_id,
            hazard_features,
            unaffected_fields,
            impact_fields,
            unaffected_geometry,
            impact_geometry,
            writer):
        """ Assign different impacted areas with their
        respective level of impact(Affected, Not Affected, Medium)

        :param feature: exposure feature
        :type feature: QgsFeature

        :param hazard_id: id of analyzed hazard
        :type hazard_id: int

        :param hazard_features: List of hazard features
        :type hazard_features: {}

        :param unaffected_fields: Unaffected fields in the impact layer
        :type unaffected_fields: {}

        :param impact_fields: Impacted fields in the impact layer
        :type impact_fields: {}

        :param unaffected_geometry: untouched geometry by the hazard
         layer
        :type unaffected_geometry: QgsGeometry

        :param impact_geometry: touched geometry by the hazard layer
        :type impact_geometry: QgsGeometry

        :param writer: Object of writing the impact layer
        :type writer: QgsVectorFileWriter

        """

        # Checking the type of provided hazard using
        # current flood and earthquake distinguishing
        # attributes
        try:
            hazard_attribute = hazard_features[hazard_id].\
                attribute('h_zone')
        except KeyError:
            try:
                hazard_attribute = hazard_features[hazard_id].\
                    attribute('FLOODPRONE')
            except KeyError:
                hazard_attribute = None

        unaffected_feature = QgsFeature(unaffected_fields)
        impacted_feature = QgsFeature(impact_fields)

        if hazard_attribute is not None:
            unaffected_feature.setGeometry(unaffected_geometry)
            unaffected_feature.setAttributes(feature.attributes() + [0])
            impacted_feature.setGeometry(impact_geometry)

            if hazard_attribute == "Low Hazard Zone":
                impacted_feature.setAttributes(feature.attributes() + [1])

            elif hazard_attribute == "Medium Hazard Zone":
                impacted_feature.setAttributes(feature.attributes() + [2])

            elif hazard_attribute == "High Hazard Zone":
                impacted_feature.setAttributes(feature.attributes() + [3])

            elif hazard_attribute == "YES":
                impacted_feature.setAttributes(feature.attributes() + [3])

            elif hazard_attribute == "NO":
                impacted_feature.setAttributes(feature.attributes() + [1])

        else:
            impacted_feature.setGeometry(impact_geometry)
            unaffected_feature.setAttributes(feature.attributes() + [1])
            impacted_feature.setAttributes(feature.attributes() + [3])

        writer.addFeature(impacted_feature)
        writer.addFeature(unaffected_feature)

    def evaluate_affected_people(self):
        """Calculate the number of people affected on the area
        based on the affected area.
        Currently we assume the population distribution is
        uniform

        :raises: ZeroImpactException

        """

        for area_id, area_value in self.all_areas_ids.iteritems():

            if area_id in self.all_affected_areas:
                affected = self.all_affected_areas[area_id]
            else:
                affected = 0.0

            single_total_area = area_value
            if area_value:
                affected_area_ratio = affected / single_total_area
            else:
                affected_area_ratio = 0

            number_people_affected = (
                affected_area_ratio * self.all_areas_population[area_id])

            # rounding to float without decimal, we can't have number
            # of people with decimal
            number_people_affected = round(number_people_affected, 0)

            self.affected_population[area_id] = number_people_affected

        total_affected_population = self.total_affected_population

        if total_affected_population == 0:
            message = no_population_impact_message(self.question)
            raise ZeroImpactException(message)
