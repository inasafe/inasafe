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

__revision__ = '$Format:%H$'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

import numpy

from safe.common.utilities import OrderedDict
from safe.defaults import (
    get_defaults,
    default_minimum_needs,
    default_provenance)
from safe.impact_functions.core import (
    FunctionProvider,
    get_hazard_layer,
    get_exposure_layer,
    get_question,
    get_function_title,
    evacuated_population_needs,
    population_rounding)
from safe.impact_functions.styles import flood_population_style as style_info
from safe.definitions import (
    hazard_all,
    layer_raster_continuous,
    exposure_population,
    unit_people_per_pixel,
    hazard_definition,
    exposure_definition)
from safe.storage.raster import Raster
from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.common.tables import Table, TableRow
from safe.impact_functions.impact_function_metadata import (
    ImpactFunctionMetadata)
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters


class ContinuousHazardPopulationImpactFunction(FunctionProvider):
    # noinspection PyUnresolvedReferences
    """Plugin for impact of population as derived by continuous hazard.

    :author AIFDR
    :rating 2
    :param requires category=='hazard' and \
                    layertype=='raster' and \
                    data_type=='continuous'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster'
    """

    class Metadata(ImpactFunctionMetadata):
        """Metadata for Continuous Hazard Population Impact Function.

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
                'id': 'ContinuousHazardPopulationImpactFunction',
                'name': tr('Continuous Hazard Population Impact Function'),
                'impact': tr('Be impacted'),
                'title': tr('Be impacted'),
                'author': 'AIFDR',
                'date_implemented': 'N/A',
                'overview': tr(
                    'To assess the impacts of continuous hazards in raster '
                    'format on population raster layer.'),
                'detailed_description': tr(
                    'This function will categorised the continuous hazard '
                    'level into 3 category based on the threshold that has '
                    'been input by the user. After that, this function will '
                    'calculate how many people will be impacted per category '
                    'for all categories in the hazard layer.'),
                'hazard_input': tr(
                    'A hazard raster layer where each cell represents the '
                    'level of the hazard. The hazard has continuous value of '
                    'hazard level.'),
                'exposure_input': tr(
                    'An exposure raster layer where each cell represent '
                    'population count.'),
                'output': tr(
                    'Map of population exposed to high category and a table '
                    'with number of people in each category'),
                'actions': tr(
                    'Provide details about how many people would likely need '
                    'to be impacted for each category.'),
                'limitations': [tr('The number of categories is three.')],
                'citations': [],
                'categories': {
                    'hazard': {
                        'definition': hazard_definition,
                        'subcategories': hazard_all,  # already a list
                        'units': [],
                        'layer_constraints': [layer_raster_continuous]
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

    # Configurable parameters
    defaults = get_defaults()
    parameters = OrderedDict([
        ('Categorical thresholds', [0.34, 0.67, 1]),
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
        """Plugin for impact of population as derived by categorised hazard.

        :param layers: List of layers expected to contain

            * hazard_layer: Raster layer of categorised hazard
            * exposure_layer: Raster layer of population data

        Counts number of people exposed to each category of the hazard

        :returns:
          Map of population exposed to high category
          Table with number of people in each category
        """

        # The 3 category
        high_t = self.parameters['Categorical thresholds'][2]
        medium_t = self.parameters['Categorical thresholds'][1]
        low_t = self.parameters['Categorical thresholds'][0]

        # Identify hazard and exposure layers
        hazard_layer = get_hazard_layer(layers)    # Categorised Hazard
        exposure_layer = get_exposure_layer(layers)  # Population Raster

        question = get_question(
            hazard_layer.get_name(), exposure_layer.get_name(), self)

        # Extract data as numeric arrays
        C = hazard_layer.get_data(nan=0.0)  # Category

        # Calculate impact as population exposed to each category
        P = exposure_layer.get_data(nan=0.0, scaling=True)
        H = numpy.where(C <= high_t, P, 0)
        M = numpy.where(C < medium_t, P, 0)
        L = numpy.where(C < low_t, P, 0)

        # Count totals
        total = int(numpy.sum(P))
        high = int(numpy.sum(H)) - int(numpy.sum(M))
        medium = int(numpy.sum(M)) - int(numpy.sum(L))
        low = int(numpy.sum(L))
        total_impact = high + medium + low

        # Don't show digits less than a 1000
        total = population_rounding(total)
        total_impact = population_rounding(total_impact)
        high = population_rounding(high)
        medium = population_rounding(medium)
        low = population_rounding(low)

        minimum_needs = [
            parameter.serialize() for parameter in
            self.parameters['minimum needs']
        ]

        # Generate impact report for the pdf map
        table_body = [
            question,
            TableRow([tr('People impacted '),
                      '%s' % format_int(total_impact)],
                     header=True),
            TableRow([tr('People in high hazard area '),
                      '%s' % format_int(high)],
                     header=True),
            TableRow([tr('People in medium hazard area '),
                      '%s' % format_int(medium)],
                     header=True),
            TableRow([tr('People in low hazard area'),
                      '%s' % format_int(low)],
                     header=True)]

        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend([
            TableRow(tr('Notes'), header=True),
            tr('Map shows population count in high or medium hazard area'),
            tr('Total population: %s') % format_int(total),
            TableRow(tr(
                'Table below shows the minimum needs for all '
                'affected people'))])

        total_needs = evacuated_population_needs(
            total_impact, minimum_needs)
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

        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('People in high hazard areas')

        # Generate 8 equidistant classes across the range of flooded population
        # 8 is the number of classes in the predefined flood population style
        # as imported
        # noinspection PyTypeChecker
        classes = numpy.linspace(
            numpy.nanmin(M.flat[:]), numpy.nanmax(M.flat[:]), 8)

        # Modify labels in existing flood style to show quantities
        style_classes = style_info['style_classes']

        style_classes[1]['label'] = tr('Low [%i people/cell]') % classes[1]
        style_classes[4]['label'] = tr('Medium [%i people/cell]') % classes[4]
        style_classes[7]['label'] = tr('High [%i people/cell]') % classes[7]

        style_info['legend_title'] = tr('Population Count')

        # Create raster object and return
        raster_layer = Raster(
            M,
            projection=hazard_layer.get_projection(),
            geotransform=hazard_layer.get_geotransform(),
            name=tr('Population which %s') % (
                get_function_title(self).lower()),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'map_title': map_title,
                'total_needs': total_needs},
            style_info=style_info)
        return raster_layer
