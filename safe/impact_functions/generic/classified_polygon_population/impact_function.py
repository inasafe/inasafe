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

from safe.impact_functions.base import ImpactFunction
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
    get_thousand_separator,
    get_non_conflicting_attribute_name)
from safe.common.tables import Table, TableRow
from safe.common.exceptions import InaSAFEError, ZeroImpactException
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters


class ClassifiedPolygonHazardPopulationFunction(ImpactFunction):
    """Impact Function for Classified Polygon on Population."""

    _metadata = ClassifiedPolygonHazardPopulationFunctionMetadata()

    def __init__(self):
        super(ClassifiedPolygonHazardPopulationFunction, self).__init__()
        self.target_field = 'population'
        # Hazard zones are all unique values from the hazard zone attribute
        self.hazard_zones = []
        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)
        # Set the question of the IF (as the hazard data is not an event)
        self.question = ('In each of the hazard zones how many people '
                         'might be impacted.')

    def run(self, layers=None):
        """Run classified population evacuation Impact Function.

        :param layers: List of layers expected to contain where two layers
            should be present.

            * hazard_layer: Vector polygon layer
            * exposure_layer: Raster layer of population data on the same grid
                as hazard_layer

        Counts number of people exposed to each hazard zones.

        :returns: Map of population exposed to each hazard zone.
            The returned dict will include a table with number of people
            evacuated and supplies required.
        :rtype: dict

        :raises:
            * Exception - When hazard layer is not vector layer
        """
        self.validate()
        self.prepare(layers)

        # Parameters
        hazard_zone_attribute = self.parameters['hazard zone attribute']

        # Identify hazard and exposure layers
        hazard_layer = self.hazard
        exposure_layer = self.exposure

        # Input checks
        if not hazard_layer.is_polygon_data:
            msg = ('Input hazard must be a polygon layer. I got %s with '
                   'layer type %s' % (hazard_layer.get_name(),
                                      hazard_layer.get_geometry_name()))
            raise Exception(msg)

        # Check if hazard_zone_attribute exists in hazard_layer
        if hazard_zone_attribute not in hazard_layer.get_attribute_names():
            msg = ('Hazard data %s does not contain expected hazard '
                   'zone attribute "%s". Please change it in the option. ' %
                   (hazard_layer.get_name(), hazard_zone_attribute))
            # noinspection PyExceptionInherit
            raise InaSAFEError(msg)

        self.hazard_zones = list(
            set(hazard_layer.get_data(hazard_zone_attribute)))

        # Find the target field name that has no conflict with default target
        attribute_names = hazard_layer.get_attribute_names()
        new_target_field = get_non_conflicting_attribute_name(
            self.target_field, attribute_names)
        self.target_field = new_target_field

        # Run interpolation function for polygon2raster
        interpolated_layer = assign_hazard_values_to_exposure_data(
            hazard_layer, exposure_layer, attribute_name=self.target_field)

        # Initialise data_table of output dataset with all data_table
        # from input polygon and a population count of zero
        new_data_table = hazard_layer.get_data()
        categories = {}
        for row in new_data_table:
            row[self.target_field] = 0
            category = row[hazard_zone_attribute]
            categories[category] = 0

        # Count affected population per polygon and total
        for row in interpolated_layer.get_data():
            # Get population at this location
            population = float(row[self.target_field])

            # Update population count for associated polygon
            poly_id = row['polygon_id']
            new_data_table[poly_id][self.target_field] += population

            # Update population count for each category
            category = new_data_table[poly_id][hazard_zone_attribute]
            categories[category] += population

        # Count totals
        total_population = population_rounding(
            int(numpy.sum(exposure_layer.get_data(nan=0))))

        # Count number of affected people for each zone
        cumulative = 0
        all_categories_population = {}
        for hazard_zone in self.hazard_zones:
            key = hazard_zone
            # prevent key error
            population = int(categories.get(key, 0))
            cumulative += population
            all_categories_population[hazard_zone] = population_rounding(
                population)

        # Use final accumulation as total number needing evacuation
        impacted_people = population_rounding(cumulative)

        # Generate impact report for the pdf map
        blank_cell = ''
        table_body = [self.question,
                      TableRow([tr('People impacted'),
                                '%s' % format_int(impacted_people),
                                blank_cell],
                               header=True)]

        for hazard_zone in self.hazard_zones:
            table_body.append(
                TableRow(
                    [hazard_zone,
                     format_int(all_categories_population[hazard_zone])]))

        table_body.extend([
            TableRow(tr(
                'Map shows the number of people impacted in each of the '
                'hazard zones.'))])

        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend(
            [TableRow(tr('Notes'), header=True),
             tr('Total population %s in the exposure layer') % format_int(
                 total_population)])

        population_counts = [x[self.target_field] for x in new_data_table]
        impact_summary = Table(table_body).toNewlineFreeString()

        # check for zero impact
        if numpy.nanmax(population_counts) == 0 == numpy.nanmin(
                population_counts):
            table_body = [
                self.question,
                TableRow([tr('People impacted'),
                          '%s' % format_int(impacted_people),
                          blank_cell], header=True)]
            my_message = Table(table_body).toNewlineFreeString()
            raise ZeroImpactException(my_message)

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        classes = create_classes(
            exposure_layer.get_data().flat[:], len(colours))
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

            if i == 0:
                transparency = 100
            else:
                transparency = 0

            style_class['label'] = label
            style_class['quantity'] = classes[i]
            style_class['colour'] = colours[i]
            style_class['transparency'] = transparency
            style_classes.append(style_class)

        # Override style info with new classes and name
        style_info = dict(
            target_field=None,
            style_classes=style_classes,
            style_type='rasterStyle')

        # For printing map purpose
        map_title = tr('People impacted by each hazard zone')
        legend_notes = tr('Thousand separator is represented by  %s' %
                          get_thousand_separator())
        legend_units = tr('(people per cell)')
        legend_title = tr('Population')

        # Create vector layer and return
        impact_layer = Raster(
            data=exposure_layer.get_data(),
            projection=exposure_layer.get_projection(),
            geotransform=exposure_layer.get_geotransform(),
            name=tr('People impacted by each hazard zone'),
            keywords={'impact_summary': impact_summary,
                      'impact_table': impact_table,
                      'target_field': self.target_field,
                      'map_title': map_title,
                      'legend_notes': legend_notes,
                      'legend_units': legend_units,
                      'legend_title': legend_title},
            style_info=style_info)

        self._impact = impact_layer
        return impact_layer
