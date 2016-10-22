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
from PyQt4.QtCore import QVariant, QPyNullVariant
from PyQt4.QtGui import QColor

from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.common.utilities import unique_filename, format_int
from safe.impact_functions.bases.classified_vh_continuous_ve import \
    ClassifiedVHContinuousVE
from safe.impact_functions.generic.classified_polygon_people\
    .metadata_definitions \
    import ClassifiedPolygonHazardPolygonPeopleFunctionMetadata
from safe.impact_reports.polygon_people_exposure_report_mixin import \
    PolygonPeopleExposureReportMixin

from safe.impact_functions.core import (
    no_population_impact_message, population_rounding)
from safe.common.exceptions import ZeroImpactException
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters

from safe.utilities.keyword_io import definition

import logging


LOGGER = logging.getLogger('InaSAFE')


class ClassifiedPolygonHazardPolygonPeopleFunction(
        ClassifiedVHContinuousVE, PolygonPeopleExposureReportMixin):

    _metadata = ClassifiedPolygonHazardPolygonPeopleFunctionMetadata()

    def __init__(self):
        super(ClassifiedPolygonHazardPolygonPeopleFunction, self).__init__()
        PolygonPeopleExposureReportMixin.__init__(self)

        # Set the question of the IF (as the hazard data is not an event)
        self.question = tr(
            'In each of the hazard zones which areas might be affected?')

        # Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)
        self.all_areas_ids = {}
        self.all_affected_areas = {}
        self.all_areas_population = {}
        self.areas_names = {}
        self.hazard_levels = {}
        self.hazard_class_mapping = {}
        self.hazard_class_field = None

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        population = format_int(population_rounding(self.total_population))
        fields = [
            tr('The total people in the area is %s') % population,
            tr('Null values will be considered as zero.')
        ]
        # include any generic exposure specific notes from definitions
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions
        fields = fields + self.hazard_notes()
        return fields

    def run(self):
        """Risk plugin for classified polygon hazard on polygon population.

        Counts population in an area exposed to hazard zones and then
        computes the proportion of each area that is affected.
        The population in each area is then calculated as the proportion
        of the original population to the affected area.

        :returns: Impact layer
        :rtype: Vector
        """

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
        # impact_fields.append(QgsField(self.people_field, QVariant.Int))
        unaffected_fields = exposure.dataProvider().fields()
        unaffected_fields.append(QgsField(self.target_field, QVariant.Int))
        # unaffected_fields.append(QgsField(self.people_field, QVariant.Int))

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
        impact_layer = QgsVectorLayer(filename, "Impacted People", "ogr")

        # Generate the report of affected populations in the areas
        # To avoid Null
        for value in self.all_areas_population.values():
            if isinstance(value, QPyNullVariant):
                value = 0
            self.total_population += value
        self.areas = self.all_areas_ids
        self.affected_areas = self.all_affected_areas
        self.areas_population = self.all_areas_population

        # Calculating number of people affected
        # This will help area report mixin to know how
        # to calculate the all row values before other
        # rows values in the report table

        self.evaluate_affected_people()

        # Define style for the impact layer
        transparent_color = QColor()
        transparent_color.setAlpha(0)

        # Retrieve the classification that is used by the hazard layer.
        vector_hazard_classification = self.hazard.keyword(
            'vector_hazard_classification')
        # Get the dictionary that contains the definition of the
        # classification
        vector_hazard_classification = definition(
            vector_hazard_classification)
        # Get the list classes in the classification
        vector_hazard_classes = vector_hazard_classification['classes']

        classes = self.hazard_class_mapping

        classes_colours = {}

        color_mapping = {
            'wet': '#F31A1C',
            'low': '#1EFC7C',
            'medium': '#FFA500',
            'high': '#F31A1C'
            }
        classes_values = {
            'wet': 1,
            'low': 1,
            'medium': 2,
            'high': 3
        }
        # Assigning colors
        for vector_hazard_class in vector_hazard_classes:
            key = vector_hazard_class['key']
            if key in classes.keys() and key in color_mapping.keys():
                classes_colours[key] = color_mapping[key]

        # Define style info for output polygons showing population counts
        style_classes = []
        index = 0
        for class_key, colour in classes_colours.items():
            style_class = dict()
            if class_key in classes.keys():
                # label = classes[class_key][0]
                label = class_key
            else:
                continue
            transparency = 0
            style_class['label'] = label
            style_class['value'] = classes_values[class_key]
            style_class['colour'] = colour
            style_class['transparency'] = transparency
            style_classes.append(style_class)

            index += 1

        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        impact_data = self.generate_data()

        extra_keywords = {
            'target_field': self.target_field,
            'map_title': self.map_title(),
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create vector layer and return
        impact_layer = Vector(
            data=impact_layer,
            name=self.map_title(),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
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
        area_id_attribute = self.exposure.keyword('area_id_field')
        area_population_attribute = self.exposure.keyword('field')
        area_name_attribute = self.exposure.keyword('area_name_field')

        all_affected_geometry = []
        impacted_geometries = []

        for feature in exposure.getFeatures(
                QgsFeatureRequest(extent_exposure)):
            geometry = feature.geometry()

            if geometry is not None:
                bbox = geometry.boundingBox()
                geometry_area = geometry.area()
            else:
                # Skip if it is an empty geometry
                # Nothing we can do
                continue

            # clip the exposure geometry to requested extent if necessary
            if not extent_exposure.contains(bbox):
                geometry = geometry.intersection(extent_exposure_geom)

            area_id = feature.attribute(area_id_attribute)

            self.all_areas_population[area_id] = feature.attribute(
                area_population_attribute)

            # To avoid Null
            if isinstance(self.all_areas_population[area_id], QPyNullVariant):
                self.all_areas_population[area_id] = 0

            if area_id not in self.all_areas_ids:
                self.all_areas_ids[area_id] = 0.

            self.all_areas_ids[area_id] += geometry_area

            # storing area id with its respective area name in
            # self.areas_names this will help us in later in showing
            # user names and not ids
            if area_id not in self.areas_names:
                self.areas_names[area_id] = feature[area_name_attribute]

            # find possible intersections with hazard layer
            # unaffected_geometries = []
            # impacted_features = {}
            for hazard_id in hazard_index.intersects(bbox):
                hazard_geometry = hazard_features[hazard_id].geometry()
                impact_geometry = geometry.intersection(hazard_geometry)

                if not impact_geometry:
                    LOGGER.warning(
                        'Impact geometry is None for hazard_id %s' % hazard_id)
                    continue

                if not impact_geometry.wkbType() == QGis.WKBPolygon and \
                   not impact_geometry.wkbType() == QGis.WKBMultiPolygon:
                    continue  # no intersection found

                # See #2744
                if (not impact_geometry.asPolygon() and
                        not impact_geometry.asMultiPolygon()):
                    # impact_geometry is actually an empty polygon
                    # so there is no impact
                    continue
                hazard = hazard_features[hazard_id]
                hazard_attribute_key = self.get_hazard_class_field_key(hazard)

                # find unaffected area geometry
                is_unaffected = (
                    (hazard_attribute_key == "dry") or
                    (hazard_attribute_key == "unaffected") or
                    (not hazard_attribute_key))

                if is_unaffected:
                    # In case the impact geometry has a 'no or NO' value in
                    # the flood column
                    unaffected_geometry = geometry.symDifference(
                        impact_geometry)
                    if not unaffected_geometry:
                        LOGGER.debug('None result symDif')
                        LOGGER.debug(
                            'Geometry: %s' %
                            geometry.exportToWkt())
                        LOGGER.debug(
                            'Impact Geometry: %s' %
                            impact_geometry.exportToWkt())
                    if area_id not in self.all_affected_areas:
                        self.all_affected_areas[area_id] = 0.
                    area = 0

                    self.all_affected_areas[area_id] += area
                else:
                    unaffected_geometry = geometry.symDifference(
                        impact_geometry)
                    if not unaffected_geometry:
                        LOGGER.debug('None result symDif')
                        LOGGER.debug(
                            'Geometry: %s' %
                            geometry.exportToWkt())
                        LOGGER.debug(
                            'Impact Geometry: %s' %
                            impact_geometry.exportToWkt())
                    # add to the affected area of this area type

                    if area_id not in self.all_affected_areas:
                        self.all_affected_areas[area_id] = 0.
                    area = impact_geometry.area()

                    self.all_affected_areas[area_id] += area

                all_affected_geometry.append(impact_geometry)
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

        area_population_attribute = self.exposure.keyword('field')
        unaffected_feature = QgsFeature(unaffected_fields)
        impacted_feature = QgsFeature(impact_fields)

        if not unaffected_geometry:
            LOGGER.warning(
                'Unaffected geometry %s is None' % unaffected_geometry)
            return
        unaffected_feature.setGeometry(unaffected_geometry)
        impacted_feature.setGeometry(impact_geometry)

        hazard = hazard_features[hazard_id]
        hazard_attribute_key = self.get_hazard_class_field_key(hazard)

        self.assign_hazard_levels(
            feature,
            hazard_attribute_key,
            unaffected_feature,
            impacted_feature)

        # passing the number of affected population
        # to new resulted(impacted or unaffected) features

        unaffected_population_number = self.calculate_population_number(
            unaffected_geometry,
            feature,
            area_population_attribute)

        unaffected_feature.setAttribute(
            area_population_attribute,
            unaffected_population_number)

        impacted_population_number = self.calculate_population_number(
            impact_geometry,
            feature,
            area_population_attribute)

        impacted_feature.setAttribute(
            area_population_attribute,
            impacted_population_number)

        # Getting number of population in different hazard
        # levels
        if hazard_attribute_key is not None:
            if hazard_attribute_key not in self.hazard_levels:
                self.hazard_levels[hazard_attribute_key] = \
                    impacted_population_number
            else:
                self.hazard_levels[hazard_attribute_key] += \
                    impacted_population_number

        # Writing all features except a no zone feature
        writer.addFeature(impacted_feature)

    def get_hazard_class_field_key(self, hazard):
        """ Get the value of the class field key for the given hazard

        :param hazard: hazard feature
        :type hazard: QgsFeature

        :returns hazard_attribute_key: Key for the hazard class field
        :rtype hazard_attribute_key: string

        """

        self.hazard_class_field = self.hazard.keyword('field')
        hazard_attribute = hazard[self.hazard_class_field]
        self.hazard_class_mapping = self.hazard.keyword('value_map')

        hazard_attribute_key = None
        for key, value in self.hazard_class_mapping.iteritems():
            if isinstance(value, list):
                for v in value:
                    if str(hazard_attribute) == str(v):
                        hazard_attribute_key = key
                        break
            else:
                if str(hazard_attribute) == str(value):
                    hazard_attribute_key = key
                    break
        return hazard_attribute_key

    def assign_hazard_levels(
            self,
            feature,
            hazard_attribute_key,
            unaffected_feature,
            impacted_feature):
        """ Assign different impacted areas with their
        respective level of impact(Affected, Not Affected, Medium)

        :param feature: exposure feature
        :type feature: QgsFeature

        :param hazard_attribute_key: attribute key of the analyzed hazard
        :type hazard_attribute_key: string

        :param unaffected_feature: Unaffected feature in the impact layer
        :type unaffected_feature: QgsFeature

        :param impacted_feature: Impacted feature in the impact layer
        :type impacted_feature: QgsFeature
        """

        if hazard_attribute_key is not None:
            unaffected_feature.setAttributes(feature.attributes() + [0])
            if hazard_attribute_key == "low":
                impacted_feature.setAttributes(feature.attributes() + [1])
            elif hazard_attribute_key == "medium":
                impacted_feature.setAttributes(feature.attributes() + [2])
            elif hazard_attribute_key == "high":
                impacted_feature.setAttributes(feature.attributes() + [3])
            elif hazard_attribute_key == "wet":
                impacted_feature.setAttributes(feature.attributes() + [1])
            elif hazard_attribute_key == "dry":
                impacted_feature.setAttributes(feature.attributes() + [2])
            elif hazard_attribute_key == "unaffected":
                impacted_feature.setAttributes(feature.attributes() + [0])

            # if hazard_attribute_key == "unaffected":
            #     unaffected_feature.setAttributes(feature.attributes() + [1])
            # else:
            #     unaffected_feature.setAttributes(feature.attributes() + [0])
        else:
            # RMN:
            # if hazard_attribute_key is None then it is not classified
            # the value is outside the class. Shouldn't we take this as not
            # not affected?
            unaffected_feature.setAttributes(feature.attributes() + [0])
            impacted_feature.setAttributes(feature.attributes() + [0])

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
        unaffected_population = (
            self.total_population - self.total_affected_population)
        self.unaffected_population = unaffected_population

        if total_affected_population == 0:
            message = no_population_impact_message(self.question)
            raise ZeroImpactException(message)

    def calculate_population_number(
            self,
            target_geometry,
            feature,
            area_population_attribute):

        """ Calculate population number given the geometry of
            the part of the layer and the whole layer
            (as a feature)

        :param target_geometry: geometry of layer part
        :type target_geometry: QgsGeometry

        :param feature: feature of the whole layer
        :type feature: QgsFeature

        :param area_population_attribute: attribute of population
        :type area_population_attribute: string

        :returns population_number: Number of Population
        :rtype population_number:int


        :raises:
            * Exception - When exposure data does not containing
            expected values
        """
        if target_geometry is not None and feature is not None:

            target_area = target_geometry.area()
            total_area = feature.geometry().area()

            population_total = feature.attribute(area_population_attribute)
            # To avoid Null
            if isinstance(population_total, QPyNullVariant):
                population_total = 0

            population_number = (
                (target_area / total_area) * population_total)

        else:
            population_number = 0

        return population_number
