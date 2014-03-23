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
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.metadata import hazard_volcano, unit_volcano_categorical, \
    layer_vector_polygon, layer_vector_point, layer_raster_numeric, \
    exposure_population, unit_people_per_pixel
from third_party.odict import OrderedDict

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
    get_thousand_separator)
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import (
    assign_hazard_values_to_exposure_data, make_circular_polygon)
from safe.common.exceptions import InaSAFEError, ZeroImpactException


class VolcanoPolygonHazardPopulation(FunctionProvider):
    """Impact function for volcano hazard zones impact on population

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
        """Metadata for Volcano Polygon Hazard Population

           We only need to re-implement get_metadata(), all other behaviours
           are inherited from the abstract base class.
           """

        @staticmethod
        def get_metadata():
            """
            Return metadata as a dictionary

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            values = {
                'id': 'VolcanoPolygonHazardPopulation',
                'name': tr('Volcano Polygon Hazard Population'),
                'impact': tr('Be affected'),
                'author': 'AIFDR',
                'date_implemented': 'N/A',
                'overview': tr('To assess the impacts of volcano eruption '
                               'on population.')
            }

            dict_meta = {
                'id': values['id'],
                'name': values['name'],
                'impact': values['impact'],
                'author': values['author'],
                'date_implemented': values['date_implemented'],
                'overview': values['overview'],
                'categories': {
                    'hazard': {
                        'subcategory':  hazard_volcano,
                        'units': [unit_volcano_categorical],
                        'layer_constraints': [
                            layer_vector_polygon,
                            layer_vector_point
                        ]
                    },
                    'exposure': {
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
                    ('elder_ratio', defaults['ELDER_RATIO'])])}),
            ('MinimumNeeds', {'on': True})]))])

    def run(self, layers):
        """Risk plugin for volcano population evacuation

        :param layers: List of layers expected to contain where two layers
            should be present.

            * my_hazard: Vector polygon layer of volcano impact zones
            * my_exposure: Raster layer of population data on the same grid as
              my_hazard

        Counts number of people exposed to volcano event.

        :returns: Map of population exposed to the volcano hazard zone.
            The returned dict will include a table with number of people
            evacuated and supplies required.
        :rtype: dict
        """

        # Identify hazard and exposure layers
        my_hazard = get_hazard_layer(layers)  # Volcano KRB
        my_exposure = get_exposure_layer(layers)

        question = get_question(
            my_hazard.get_name(), my_exposure.get_name(), self)

        # Input checks
        if not my_hazard.is_vector:
            msg = ('Input hazard %s  was not a vector layer as expected '
                   % my_hazard.get_name())
            raise Exception(msg)

        msg = ('Input hazard must be a polygon or point layer. I got %s with '
               'layer type %s' % (my_hazard.get_name(),
                                  my_hazard.get_geometry_name()))
        if not (my_hazard.is_polygon_data or my_hazard.is_point_data):
            raise Exception(msg)

        if my_hazard.is_point_data:
            # Use concentric circles
            radii = self.parameters['distance [km]']

            centers = my_hazard.get_geometry()
            attributes = my_hazard.get_data()
            rad_m = [x * 1000 for x in radii]  # Convert to meters
            my_hazard = make_circular_polygon(
                centers, rad_m, attributes=attributes)

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
            attributes = my_hazard.get_data()

        # Get names of volcanos considered
        if name_attribute in my_hazard.get_attribute_names():
            D = {}
            for att in my_hazard.get_data():
                # Run through all polygons and get unique names
                D[att[name_attribute]] = None

            volcano_names = ''
            for name in D:
                volcano_names += '%s, ' % name
            volcano_names = volcano_names[:-2]  # Strip trailing ', '
        else:
            volcano_names = tr('Not specified in data')

        if not category_title in my_hazard.get_attribute_names():
            msg = ('Hazard data %s did not contain expected '
                   'attribute %s ' % (my_hazard.get_name(), category_title))
            # noinspection PyExceptionInherit
            raise InaSAFEError(msg)

        # Run interpolation function for polygon2raster
        P = assign_hazard_values_to_exposure_data(
            my_hazard, my_exposure, attribute_name='population')

        # Initialise attributes of output dataset with all attributes
        # from input polygon and a population count of zero
        new_attributes = my_hazard.get_data()

        categories = {}
        for attr in new_attributes:
            attr[self.target_field] = 0
            cat = attr[category_title]
            categories[cat] = 0

        # Count affected population per polygon and total
        evacuated = 0
        for attr in P.get_data():
            # Get population at this location
            pop = float(attr['population'])

            # Update population count for associated polygon
            poly_id = attr['polygon_id']
            new_attributes[poly_id][self.target_field] += pop

            # Update population count for each category
            cat = new_attributes[poly_id][category_title]
            categories[cat] += pop

        # Count totals
        total = int(numpy.sum(my_exposure.get_data(nan=0)))

        # Don't show digits less than a 1000
        total = round_thousand(total)

        # Count number and cumulative for each zone
        cum = 0
        pops = {}
        cums = {}
        for name in category_names:
            if category_title == 'Radius':
                key = name * 1000  # Convert to meters
            else:
                key = name
            # prevent key error
            pop = int(categories.get(key, 0))

            pop = round_thousand(pop)

            cum += pop
            cum = round_thousand(cum)

            pops[name] = pop
            cums[name] = cum

        # Use final accumulation as total number needing evac
        evacuated = cum

        tot_needs = evacuated_population_weekly_needs(evacuated)

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
            table_body.append(TableRow([name,
                                        format_int(pops[name]),
                                        format_int(cums[name])]))

        table_body.extend([TableRow(tr('Map shows population affected in '
                                       'each of volcano hazard polygons.')),
                           TableRow([tr('Needs per week'), tr('Total'),
                                     blank_cell],
                                    header=True),
                           [tr('Rice [kg]'), format_int(tot_needs['rice']),
                            blank_cell],
                           [tr('Drinking Water [l]'),
                            format_int(tot_needs['drinking_water']),
                            blank_cell],
                           [tr('Clean Water [l]'),
                            format_int(tot_needs['water']),
                            blank_cell],
                           [tr('Family Kits'),
                            format_int(tot_needs['family_kits']),
                            blank_cell],
                           [tr('Toilets'), format_int(tot_needs['toilets']),
                            blank_cell]])
        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend([TableRow(tr('Notes'), header=True),
                           tr('Total population %s in the exposure layer')
                           % format_int(total),
                           tr('People need evacuation if they are within the '
                              'volcanic hazard zones.')])

        population_counts = [x[self.target_field] for x in new_attributes]
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
        V = Vector(data=new_attributes,
                   projection=my_hazard.get_projection(),
                   geometry=my_hazard.get_geometry(as_geometry_objects=True),
                   name=tr('Population affected by volcanic hazard zone'),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'target_field': self.target_field,
                             'map_title': map_title,
                             'legend_notes': legend_notes,
                             'legend_units': legend_units,
                             'legend_title': legend_title},
                   style_info=style_info)
        return V
