# coding=utf-8
"""
InaSAFE Disaster risk tool by AusAid - **Volcano polygon evacuation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""
import numpy
from safe.engine.utilities import buffer_points
from safe.impact_functions.impact_function_metadata import (
    ImpactFunctionMetadata)
from safe.metadata import (
    hazard_volcano,
    unit_volcano_categorical,
    layer_vector_polygon,
    layer_vector_point,
    layer_raster_numeric,
    exposure_population,
    unit_people_per_pixel,
    hazard_definition,
    exposure_definition)
from collections import OrderedDict
from safe.defaults import get_defaults
from safe.impact_functions.core import (
    FunctionProvider,
    get_hazard_layer,
    get_exposure_layer,
    get_question,
    default_minimum_needs,
    evacuated_population_weekly_needs)
from safe.storage.vector import Vector
from safe.common.utilities import (
    ugettext as tr,
    format_int,
    round_thousand,
    humanize_class,
    create_classes,
    create_label,
    get_thousand_separator,
    get_non_conflicting_attribute_name)
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import (
    assign_hazard_values_to_exposure_data)
from safe.common.exceptions import InaSAFEError, ZeroImpactException


class VolcanoPolygonHazardPopulation(FunctionProvider):
    # noinspection PyUnresolvedReferences
    """Impact function for volcano hazard zones impact on population.

    :author AIFDR
    :rating 4
    :param requires category=='hazard' and \
                    subcategory in ['volcano'] and \
                    layertype=='vector'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster'
    """

    class Metadata(ImpactFunctionMetadata):
        """Metadata for Volcano Polygon Hazard Population.

        .. versionadded:: 2.1

        We only need to re-implement get_metadata(), all other behaviours
        are inherited from the abstract base class.
        """

        @staticmethod
        def get_metadata():
            """Return metadata as a dictionary.

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            dict_meta = {
                'id': 'VolcanoPolygonHazardPopulation',
                'name': tr('Volcano Polygon Hazard Population'),
                'impact': tr('Need evacuation'),
                'author': 'AIFDR',
                'date_implemented': 'N/A',
                'overview': tr('To assess the impacts of volcano eruption '
                               'on population.'),
                'categories': {
                    'hazard': {
                        'definition': hazard_definition,
                        'subcategory': hazard_volcano,
                        'units': [unit_volcano_categorical],
                        'layer_constraints': [
                            layer_vector_polygon,
                            layer_vector_point
                        ]
                    },
                    'exposure': {
                        'definition': exposure_definition,
                        'subcategory': exposure_population,
                        'units': [unit_people_per_pixel],
                        'layer_constraints': [layer_raster_numeric]
                    }
                }
            }
            return dict_meta

    title = tr('Need evacuation')
    target_field = 'population'
    defaults = get_defaults()
    # Function documentation
    synopsis = tr('To assess the impacts of volcano eruption on population.')
    actions = tr(
        'Provide details about how many population would likely be affected '
        'by each hazard zones.')
    hazard_input = tr(
        'A hazard vector layer can be polygon or point. If polygon, it must '
        'have "KRB" attribute and the valuefor it are "Kawasan Rawan '
        'Bencana I", "Kawasan Rawan Bencana II", or "Kawasan Rawan Bencana '
        'III."If you want to see the name of the volcano in the result, you '
        'need to add "NAME" attribute for point data or "GUNUNG" attribute '
        'for polygon data.')
    exposure_input = tr(
        'An exposure raster layer where each cell represent population count.')
    output = tr(
        'Vector layer contains population affected and the minimum needs '
        'based on the population affected.')

    parameters = OrderedDict([
        ('distance [km]', [3, 5, 10]),
        ('minimum needs', default_minimum_needs()),
        ('postprocessors', OrderedDict([
            ('Gender', {'on': True}),
            ('Age', {
                'on': True,
                'params': OrderedDict([
                    ('youth_ratio', defaults['YOUTH_RATIO']),
                    ('adult_ratio', defaults['ADULT_RATIO']),
                    ('elderly_ratio', defaults['ELDERLY_RATIO'])])}),
            ('MinimumNeeds', {'on': True})
        ])),
        ('minimum needs', default_minimum_needs())
    ])

    def run(self, layers):
        """Risk plugin for volcano population evacuation.

        :param layers: List of layers expected to contain where two layers
            should be present.

            * hazard_layer: Vector polygon layer of volcano impact zones
            * exposure_layer: Raster layer of population data on the same grid
                as hazard_layer

        Counts number of people exposed to volcano event.

        :returns: Map of population exposed to the volcano hazard zone.
            The returned dict will include a table with number of people
            evacuated and supplies required.
        :rtype: dict

        :raises:
            * Exception - When hazard layer is not vector layer
            * RadiiException - When radii are not valid (they need to be
                monotonically increasing)
        """

        # Identify hazard and exposure layers
        hazard_layer = get_hazard_layer(layers)  # Volcano KRB
        exposure_layer = get_exposure_layer(layers)

        question = get_question(
            hazard_layer.get_name(), exposure_layer.get_name(), self)

        # Input checks
        if not hazard_layer.is_vector:
            msg = ('Input hazard %s  was not a vector layer as expected '
                   % hazard_layer.get_name())
            raise Exception(msg)

        msg = ('Input hazard must be a polygon or point layer. I got %s with '
               'layer type %s' % (hazard_layer.get_name(),
                                  hazard_layer.get_geometry_name()))
        if not (hazard_layer.is_polygon_data or hazard_layer.is_point_data):
            raise Exception(msg)

        data_table = hazard_layer.get_data()
        if hazard_layer.is_point_data:
            # Use concentric circles
            radii = self.parameters['distance [km]']

            centers = hazard_layer.get_geometry()
            rad_m = [x * 1000 for x in radii]  # Convert to meters
            hazard_layer = buffer_points(centers, rad_m, data_table=data_table)

            category_title = 'Radius'
            category_header = tr('Distance [km]')
            category_names = radii

            name_attribute = 'NAME'  # As in e.g. the Smithsonian dataset
        else:
            # Use hazard map
            category_title = 'KRB'
            category_header = tr('Category')

            # FIXME (Ole): Change to English and use translation system
            category_names = ['Kawasan Rawan Bencana III',
                              'Kawasan Rawan Bencana II',
                              'Kawasan Rawan Bencana I']

            name_attribute = 'GUNUNG'  # As in e.g. BNPB hazard map

        # Get names of volcanoes considered
        if name_attribute in hazard_layer.get_attribute_names():
            volcano_name_list = []
            # Run through all polygons and get unique names
            for row in data_table:
                volcano_name_list.append(row[name_attribute])

            volcano_names = ''
            for name in volcano_name_list:
                volcano_names += '%s, ' % name
            volcano_names = volcano_names[:-2]  # Strip trailing ', '
        else:
            volcano_names = tr('Not specified in data')

        # Check if category_title exists in hazard_layer
        if not category_title in hazard_layer.get_attribute_names():
            msg = ('Hazard data %s did not contain expected '
                   'attribute %s ' % (hazard_layer.get_name(), category_title))
            # noinspection PyExceptionInherit
            raise InaSAFEError(msg)

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
            category = row[category_title]
            categories[category] = 0

        # Count affected population per polygon and total
        for row in interpolated_layer.get_data():
            # Get population at this location
            population = float(row[self.target_field])

            # Update population count for associated polygon
            poly_id = row['polygon_id']
            new_data_table[poly_id][self.target_field] += population

            # Update population count for each category
            category = new_data_table[poly_id][category_title]
            categories[category] += population

        # Count totals
        total = int(numpy.sum(exposure_layer.get_data(nan=0)))

        # Don't show digits less than a 1000
        total = round_thousand(total)

        # Count number and cumulative for each zone
        cumulative = 0
        all_categories_population = {}
        all_categories_cumulative = {}
        for name in category_names:
            if category_title == 'Radius':
                key = name * 1000  # Convert to meters
            else:
                key = name
            # prevent key error
            population = int(categories.get(key, 0))

            population = round_thousand(population)

            cumulative += population
            cumulative = round_thousand(cumulative)

            all_categories_population[name] = population
            all_categories_cumulative[name] = cumulative

        # Use final accumulation as total number needing evacuation
        evacuated = cumulative

        # Calculate estimated minimum needs
        minimum_needs = self.parameters['minimum needs']
        total_needs = evacuated_population_weekly_needs(
            evacuated, minimum_needs)

        # Generate impact report for the pdf map
        blank_cell = ''
        table_body = [question,
                      TableRow([tr('Volcanoes considered'),
                                '%s' % volcano_names, blank_cell],
                               header=True),
                      TableRow([tr('People needing evacuation'),
                                '%s' % format_int(evacuated),
                                blank_cell],
                               header=True),
                      TableRow([category_header,
                                tr('Total'), tr('Cumulative')],
                               header=True)]

        for name in category_names:
            table_body.append(
                TableRow([name,
                          format_int(all_categories_population[name]),
                          format_int(all_categories_cumulative[name])]))

        table_body.extend([
            TableRow(tr(
                'Map shows population affected in each of volcano hazard '
                'polygons.')),
            TableRow(
                [tr('Needs per week'), tr('Total'), blank_cell], header=True),
            [tr('Rice [kg]'), format_int(total_needs['rice']), blank_cell], [
                tr('Drinking Water [l]'),
                format_int(total_needs['drinking_water']),
                blank_cell],
            [tr('Clean Water [l]'), format_int(total_needs['water']),
                blank_cell],
            [tr('Family Kits'), format_int(total_needs['family_kits']),
                blank_cell],
            [tr('Toilets'), format_int(total_needs['toilets']), blank_cell]])
        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend(
            [TableRow(tr('Notes'), header=True),
             tr('Total population %s in the exposure layer') % format_int(
                 total),
             tr('People need evacuation if they are within the '
                'volcanic hazard zones.')])

        population_counts = [x[self.target_field] for x in new_data_table]
        impact_summary = Table(table_body).toNewlineFreeString()

        # check for zero impact
        if numpy.nanmax(population_counts) == 0 == numpy.nanmin(
                population_counts):
            table_body = [
                question,
                TableRow([tr('People needing evacuation'),
                          '%s' % format_int(evacuated),
                          blank_cell], header=True)]
            my_message = Table(table_body).toNewlineFreeString()
            raise ZeroImpactException(my_message)

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        classes = create_classes(population_counts, len(colours))
        interval_classes = humanize_class(classes)
        # Define style info for output polygons showing population counts
        style_classes = []
        for i in xrange(len(colours)):
            style_class = dict()
            style_class['label'] = create_label(interval_classes[i])
            if i == 0:
                transparency = 100
                style_class['min'] = 0
            else:
                transparency = 30
                style_class['min'] = classes[i - 1]
            style_class['transparency'] = transparency
            style_class['colour'] = colours[i]
            style_class['max'] = classes[i]
            style_classes.append(style_class)

        # Override style info with new classes and name
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='graduatedSymbol')

        # For printing map purpose
        map_title = tr('People affected by volcanic hazard zone')
        legend_notes = tr('Thousand separator is represented by  %s' %
                          get_thousand_separator())
        legend_units = tr('(people)')
        legend_title = tr('Population count')

        # Create vector layer and return
        impact_layer = Vector(
            data=new_data_table,
            projection=hazard_layer.get_projection(),
            geometry=hazard_layer.get_geometry(as_geometry_objects=True),
            name=tr('Population affected by volcanic hazard zone'),
            keywords={'impact_summary': impact_summary,
                      'impact_table': impact_table,
                      'target_field': self.target_field,
                      'map_title': map_title,
                      'legend_notes': legend_notes,
                      'legend_units': legend_units,
                      'legend_title': legend_title},
            style_info=style_info)
        return impact_layer
