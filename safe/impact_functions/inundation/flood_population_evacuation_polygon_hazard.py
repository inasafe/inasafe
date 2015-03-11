# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid - **Flood polygon evacuation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""
from safe.utilities.i18n import tr

__author__ = 'Ole Nielson'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import numpy
import logging

from safe.definitions import (
    hazard_flood,
    unit_wetdry,
    layer_vector_polygon,
    exposure_population,
    unit_people_per_pixel,
    layer_raster_continuous,
    exposure_definition,
    hazard_definition
)
from safe.impact_functions.impact_function_metadata import (
    ImpactFunctionMetadata)
from safe.common.utilities import OrderedDict
from safe.defaults import (
    get_defaults,
    default_minimum_needs,
    default_provenance
)
from safe.impact_functions.core import (
    FunctionProvider,
    get_hazard_layer,
    get_exposure_layer,
    get_question,
    evacuated_population_needs,
    population_rounding_full,
    population_rounding
)
from safe.storage.vector import Vector
from safe.common.utilities import (
    format_int,
    humanize_class,
    create_classes,
    create_label
)
from safe.common.tables import Table, TableRow, TableCell
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters

LOGGER = logging.getLogger('InaSAFE')


class FloodEvacuationFunctionVectorHazard(FunctionProvider):
    # noinspection PyUnresolvedReferences
    """Impact function for vector flood evacuation.

    :author AIFDR
    :rating 4

    :param requires category=='hazard' and \
                    subcategory=='flood' and \
                    layertype=='vector'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster'
    """

    class Metadata(ImpactFunctionMetadata):
        """Metadata for FloodEvacuationFunctionVectorHazard.

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
                'id': 'FloodEvacuationFunctionVectorHazard',
                'name': tr('Flood Evacuation Function Vector Hazard'),
                'impact': tr('Need evacuation'),
                'title': tr('Need evacuation'),
                'author': 'AIFDR',
                'date_implemented': 'N/A',
                'overview': tr(
                    'To assess the impacts of flood inundation in vector '
                    'format on population.'),
                'detailed_description': tr(
                    'The population subject to inundation is determined '
                    'whether in an area which affected or not. You can also '
                    'set an evacuation percentage to calculate how many '
                    'percent of the total population affected to be '
                    'evacuated. This number will be used to estimate needs'
                    ' based on BNPB Perka 7/2008 minimum bantuan.'),
                'hazard_input': tr(
                    'A hazard vector layer which has attribute affected the '
                    'value is either 1 or 0'),
                'exposure_input': tr(
                    'An exposure raster layer where each cell represent '
                    'population count.'),
                'output': tr(
                    'Vector layer contains people affected and the minimum '
                    'needs based on evacuation percentage.'),
                'actions': tr(
                    'Provide details about how many people would likely need '
                    'to be evacuated, where they are located and what '
                    'resources would be required to support them.'),
                'limitations': [],
                'citations': [],
                'categories': {
                    'hazard': {
                        'definition': hazard_definition,
                        'subcategories': [hazard_flood],
                        'units': [unit_wetdry],
                        'layer_constraints': [layer_vector_polygon]
                    },
                    'exposure': {
                        'definition': exposure_definition,
                        'subcategories': [exposure_population],
                        'units': [unit_people_per_pixel],
                        'layer_constraints': [layer_raster_continuous]
                    }
                }
            }
            return dict_meta

    target_field = 'population'
    defaults = get_defaults()

    # Configurable parameters
    # TODO: Share the mimimum needs and make another default value
    parameters = OrderedDict([
        ('evacuation_percentage', 1),  # Percent of affected needing evacuation
        ('postprocessors', OrderedDict([
            ('Gender', {'on': True}),
            ('Age', {
                'on': True,
                'params': OrderedDict([
                    ('youth_ratio', defaults['YOUTH_RATIO']),
                    ('adult_ratio', defaults['ADULT_RATIO']),
                    ('elderly_ratio', defaults['ELDERLY_RATIO'])])}),
            ('MinimumNeeds', {'on': True}),
        ])),
        ('minimum needs', default_minimum_needs()),
        ('provenance', default_provenance())
    ])
    parameters = add_needs_parameters(parameters)

    def run(self, layers):
        """Risk plugin for flood population evacuation.

        :param layers: List of layers expected to contain

            * hazard_layer : Vector polygon layer of flood depth
            * exposure_layer : Raster layer of population data on the same grid
                as hazard_layer

        Counts number of people exposed to areas identified as flood prone

        :returns: Map of population exposed to flooding Table with number of
            people evacuated and supplies required.
        :rtype: tuple
        """
        # Identify hazard and exposure layers
        hazard_layer = get_hazard_layer(layers)  # Flood inundation
        exposure_layer = get_exposure_layer(layers)

        question = get_question(
            hazard_layer.get_name(), exposure_layer.get_name(), self)

        # Check that hazard is polygon type
        if not hazard_layer.is_vector:
            message = (
                'Input hazard %s  was not a vector layer as expected ' %
                hazard_layer.get_name())
            raise Exception(message)

        message = (
            'Input hazard must be a polygon layer. I got %s with layer type '
            '%s' % (hazard_layer.get_name(), hazard_layer.get_geometry_name()))
        if not hazard_layer.is_polygon_data:
            raise Exception(message)

        # Run interpolation function for polygon2raster
        combined = assign_hazard_values_to_exposure_data(
            hazard_layer, exposure_layer, attribute_name='population')

        # Initialise attributes of output dataset with all attributes
        # from input polygon and a population count of zero
        new_attributes = hazard_layer.get_data()
        category_title = 'affected'  # FIXME: Should come from keywords
        deprecated_category_title = 'FLOODPRONE'
        categories = {}
        for attr in new_attributes:
            attr[self.target_field] = 0
            try:
                title = attr[category_title]
            except KeyError:
                try:
                    title = attr['FLOODPRONE']
                    categories[title] = 0
                except KeyError:
                    pass

        # Count affected population per polygon, per category and total
        affected_population = 0
        for attr in combined.get_data():

            affected = False
            if 'affected' in attr:
                res = attr['affected']
                if res is None:
                    x = False
                else:
                    x = bool(res)
                affected = x
            elif 'FLOODPRONE' in attr:
                # If there isn't an 'affected' attribute,
                res = attr['FLOODPRONE']
                if res is not None:
                    affected = res.lower() == 'yes'
            elif 'Affected' in attr:
                # Check the default attribute assigned for points
                # covered by a polygon
                res = attr['Affected']
                if res is None:
                    x = False
                else:
                    x = res
                affected = x
            else:
                # assume that every polygon is affected (see #816)
                affected = True
                # there is no flood related attribute
                # message = ('No flood related attribute found in %s. '
                #       'I was looking for either "Flooded", "FLOODPRONE" '
                #       'or "Affected". The latter should have been '
                #       'automatically set by call to '
                #       'assign_hazard_values_to_exposure_data(). '
                #       'Sorry I can\'t help more.')
                # raise Exception(message)

            if affected:
                # Get population at this location
                pop = float(attr['population'])

                # Update population count for associated polygon
                poly_id = attr['polygon_id']
                new_attributes[poly_id][self.target_field] += pop

                # Update population count for each category
                if len(categories) > 0:
                    try:
                        title = new_attributes[poly_id][category_title]
                    except KeyError:
                        title = new_attributes[poly_id][
                            deprecated_category_title]
                    categories[title] += pop

                # Update total
                affected_population += pop

        # Estimate number of people in need of evacuation
        evacuated = (
            affected_population *
            self.parameters['evacuation_percentage'] /
            100.0)

        affected_population, rounding = population_rounding_full(
            affected_population)

        total = int(numpy.sum(exposure_layer.get_data(nan=0, scaling=False)))

        # Don't show digits less than a 1000
        total = population_rounding(total)
        evacuated, rounding_evacuated = population_rounding_full(evacuated)

        minimum_needs = [
            parameter.serialize() for parameter in
            self.parameters['minimum needs']
        ]

        # Generate impact report for the pdf map
        table_body = [
            question,
            TableRow(
                [tr('People affected'), '%s*' % (
                    format_int(int(affected_population)))],
                header=True),
            TableRow(
                [TableCell(
                    tr('* Number is rounded up to the nearest %s') % (
                        rounding),
                    col_span=2)]),
            TableRow([tr('People needing evacuation'), '%s*' % (
                format_int(int(evacuated)))], header=True),
            TableRow(
                [TableCell(
                    tr('* Number is rounded up to the nearest %s') % (
                        rounding_evacuated),
                    col_span=2)]),
            TableRow([tr('Evacuation threshold'), '%s%%' % format_int(
                self.parameters['evacuation_percentage'])], header=True),
            TableRow(tr(
                'Map shows the number of people affected in each flood prone '
                'area')),
            TableRow(tr(
                'Table below shows the weekly minimum needs for all '
                'evacuated people'))]
        total_needs = evacuated_population_needs(
            evacuated, minimum_needs)
        for frequency, needs in total_needs.items():
            table_body.append(TableRow(
                [
                    tr('Needs should be provided %s' % frequency),
                    tr('Total')
                ],
                header=True))
            for resource in needs:
                table_body.append(TableRow([
                    tr(resource['table name']),
                    format_int(resource['amount'])]))

        impact_table = Table(table_body).toNewlineFreeString()

        table_body.append(TableRow(tr('Action Checklist:'), header=True))
        table_body.append(TableRow(tr('How will warnings be disseminated?')))
        table_body.append(TableRow(tr('How will we reach stranded people?')))
        table_body.append(TableRow(tr('Do we have enough relief items?')))
        table_body.append(TableRow(
            'If yes, where are they located and how will we distribute '
            'them?'))
        table_body.append(TableRow(
            'If no, where can we obtain additional relief items from and '
            'how will we transport them to here?'))

        # Extend impact report for on-screen display
        table_body.extend([
            TableRow(tr('Notes'), header=True),
            tr('Total population: %s') % format_int(total),
            tr('People need evacuation if in the area identified as '
               '"Flood Prone"'),
            tr('Minimum needs are defined in BNPB regulation 7/2008')])
        impact_summary = Table(table_body).toNewlineFreeString()

        # Create style
        # Define classes for legend for flooded population counts
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']

        population_counts = [x['population'] for x in new_attributes]
        classes = create_classes(population_counts, len(colours))
        interval_classes = humanize_class(classes)

        # Define style info for output polygons showing population counts
        style_classes = []
        for i in xrange(len(colours)):
            style_class = dict()
            style_class['label'] = create_label(interval_classes[i])
            if i == 0:
                transparency = 0
                style_class['min'] = 0
            else:
                transparency = 0
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
        map_title = tr('People affected by flood prone areas')
        legend_notes = tr('Thousand separator is represented by \'.\'')
        legend_units = tr('(people per polygon)')
        legend_title = tr('Population Count')

        # Create vector layer and return
        vector_layer = Vector(
            data=new_attributes,
            projection=hazard_layer.get_projection(),
            geometry=hazard_layer.get_geometry(),
            name=tr('People affected by flood prone areas'),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'target_field': self.target_field,
                'map_title': map_title,
                'legend_notes': legend_notes,
                'legend_units': legend_units,
                'legend_title': legend_title,
                'affected_population': affected_population,
                'total_population': total,
                'total_needs': total_needs},
            style_info=style_info)
        return vector_layer
