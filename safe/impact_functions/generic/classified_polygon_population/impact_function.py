# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Classified Polygon on
Population Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import numpy
from collections import OrderedDict

from safe.impact_functions.bases.classified_vh_continuous_re import \
    ClassifiedVHContinuousRE
from safe.impact_functions.generic.classified_polygon_population\
    .metadata_definitions import \
    ClassifiedPolygonHazardPopulationFunctionMetadata
from safe.impact_functions.core import population_rounding
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.storage.raster import Raster
from safe.utilities.i18n import tr
from safe.common.utilities import (
    format_int,
    humanize_class,
    create_classes,
    create_label,
    get_thousand_separator)
from safe.impact_functions.core import (
    no_population_impact_message,
    get_key_for_value)
from safe.common.exceptions import InaSAFEError, ZeroImpactException
from safe.gui.tools.minimum_needs.needs_profile import (
    add_needs_parameters,
    filter_needs_parameters)
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin
import safe.messaging as m
from safe.messaging import styles
from safe.utilities.keyword_io import definition


class ClassifiedPolygonHazardPopulationFunction(
        ClassifiedVHContinuousRE,
        PopulationExposureReportMixin):
    """Impact Function for Classified Polygon on Population."""

    _metadata = ClassifiedPolygonHazardPopulationFunctionMetadata()

    def __init__(self):
        super(ClassifiedPolygonHazardPopulationFunction, self).__init__()
        # Hazard zones are all unique values from the hazard zone attribute
        self.hazard_zones = []
        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)
        # Set the question of the IF (as the hazard data is not an event)
        self.question = tr(
            'In each of the hazard zones how many people might be impacted.')

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        message.add(m.Heading(
            tr('Notes and assumptions'), **styles.INFO_STYLE))
        checklist = m.BulletedList()
        population = format_int(population_rounding(self.total_population))
        checklist.add(tr(
            'Total population in the analysis area: %s') % population)
        checklist.add(tr(
            '<sup>1</sup>People need evacuation if they are in a '
            'hazard zone.'))
        checklist.add(tr(
            'Map shows population count in high, medium, and low '
            'hazard areas.'))
        checklist.add(tr(
            'All values are rounded up to the nearest integer in '
            'order to avoid representing human lives as fractions.'))
        checklist.add(tr(
            'Population rounding is applied to all population '
            'values, which may cause discrepancies when adding values.'))
        message.add(checklist)
        return message

    def run(self):
        """Run classified population evacuation Impact Function.

        Counts number of people exposed to each hazard zones.

        :returns: Map of population exposed to each hazard zone.
            The returned dict will include a table with number of people
            evacuated and supplies required.
        :rtype: dict

        :raises:
            * Exception - When hazard layer is not vector layer
        """

        # Value from layer's keywords
        self.hazard_class_attribute = self.hazard.keyword('field')
        self.hazard_class_mapping = self.hazard.keyword('value_map')
        # TODO: Remove check to self.validate (Ismail)
        # Input checks
        message = tr(
            'Input hazard must be a polygon layer. I got %s with layer type '
            '%s' % (self.hazard.name, self.hazard.layer.get_geometry_name()))
        if not self.hazard.layer.is_polygon_data:
            raise Exception(message)

        # Check if hazard_class_attribute exists in hazard_layer
        if (self.hazard_class_attribute not in
                self.hazard.layer.get_attribute_names()):
            message = ('Hazard data %s does not contain expected hazard '
                   'zone attribute "%s". Please change it in the option. ' %
                   (self.hazard.name, self.hazard_class_attribute))
            # noinspection PyExceptionInherit
            raise InaSAFEError(message)

        # Retrieve the classification that is used by the hazard layer.
        vector_hazard_classification = self.hazard.keyword(
            'vector_hazard_classification')
        # Get the dictionary that contains the definition of the classification
        vector_hazard_classification = definition(vector_hazard_classification)
        # Get the list classes in the classification
        vector_hazard_classes = vector_hazard_classification['classes']
        # Initialize OrderedDict of affected buildings
        self.affected_population = OrderedDict()
        # Iterate over vector hazard classes
        for vector_hazard_class in vector_hazard_classes:
            # Check if the key of class exist in hazard_class_mapping
            if vector_hazard_class['key'] in self.hazard_class_mapping.keys():
                # Replace the key with the name as we need to show the human
                # friendly name in the report.
                self.hazard_class_mapping[vector_hazard_class['name']] = \
                    self.hazard_class_mapping.pop(vector_hazard_class['key'])
                # Adding the class name as a key in affected_building
                self.affected_population[vector_hazard_class['name']] = 0

        # Interpolated layer represents grid cell that lies in the polygon
        interpolated_layer, covered_exposure_layer = \
            assign_hazard_values_to_exposure_data(
                self.hazard.layer,
                self.exposure.layer,
                attribute_name=self.target_field
            )

        # Count total affected population per hazard zone
        for row in interpolated_layer.get_data():
            # Get population at this location
            population = row[self.target_field]
            if not numpy.isnan(population):
                population = float(population)
                # Update population count for this hazard zone
                hazard_value = get_key_for_value(
                    row[self.hazard_class_attribute],
                    self.hazard_class_mapping)
                if not hazard_value:
                    hazard_value = self._not_affected_value
                self.affected_population[hazard_value] += population

        # Count total population from exposure layer
        self.total_population = int(
            numpy.nansum(self.exposure.layer.get_data()))

        # Count total affected population
        total_affected_population = self.total_affected_population
        self.unaffected_population = (
            self.total_population - total_affected_population)

        self.minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]

        # check for zero impact
        if total_affected_population == 0:
            message = no_population_impact_message(self.question)
            raise ZeroImpactException(message)

        impact_table = impact_summary = self.html_report()

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        classes = create_classes(
            covered_exposure_layer.get_data().flat[:], len(colours))
        interval_classes = humanize_class(classes)
        # Define style info for output polygons showing population counts
        style_classes = []
        for i in xrange(len(colours)):
            style_class = dict()
            style_class['label'] = create_label(interval_classes[i])
            if i == 1:
                label = create_label(
                    interval_classes[i],
                    tr('Low Population [%i people/cell]' % classes[i]))
            elif i == 4:
                label = create_label(
                    interval_classes[i],
                    tr('Medium Population [%i people/cell]' % classes[i]))
            elif i == 7:
                label = create_label(
                    interval_classes[i],
                    tr('High Population [%i people/cell]' % classes[i]))
            else:
                label = create_label(interval_classes[i])

            style_class['label'] = label
            style_class['quantity'] = classes[i]
            style_class['colour'] = colours[i]
            style_class['transparency'] = 0
            style_classes.append(style_class)

        # Override style info with new classes and name
        style_info = dict(
            target_field=None,
            style_classes=style_classes,
            style_type='rasterStyle')

        # For printing map purpose
        map_title = tr('People impacted by each hazard zone')
        legend_title = tr('Population')
        legend_units = tr('(people per cell)')
        legend_notes = tr(
            'Thousand separator is represented by  %s' %
            get_thousand_separator())

        extra_keywords = {
            'impact_summary': impact_summary,
            'impact_table': impact_table,
            'target_field': self.target_field,
            'map_title': map_title,
            'legend_notes': legend_notes,
            'legend_units': legend_units,
            'legend_title': legend_title
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create vector layer and return
        impact_layer = Raster(
            data=covered_exposure_layer.get_data(),
            projection=covered_exposure_layer.get_projection(),
            geotransform=covered_exposure_layer.get_geotransform(),
            name=tr('People impacted by each hazard zone'),
            keywords=impact_layer_keywords,
            style_info=style_info)

        self._impact = impact_layer
        return impact_layer
