# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Volcano Point on
Population Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import numpy

from safe.impact_functions.bases.classified_vh_continuous_re import \
    ClassifiedVHContinuousRE
from safe.impact_functions.volcanic.volcano_point_population\
    .metadata_definitions import VolcanoPointPopulationFunctionMetadata
from safe.impact_functions.core import (
    population_rounding,
    has_no_data)
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.storage.raster import Raster
from safe.utilities.i18n import tr
from safe.common.utilities import (
    format_int,
    humanize_class,
    create_classes,
    create_label,
    get_thousand_separator)
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    filter_needs_parameters, get_needs_provenance_value
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin


class VolcanoPointPopulationFunction(
        ClassifiedVHContinuousRE,
        PopulationExposureReportMixin):
    """Impact Function for Volcano Point on Population."""

    _metadata = VolcanoPointPopulationFunctionMetadata()

    def __init__(self):
        super(VolcanoPointPopulationFunction, self).__init__()
        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)
        # TODO: alternatively to specifying the question here we should
        # TODO: consider changing the 'population' metadata concept to 'people'
        self.question = (
            'In the event of a volcano point how many people might be impacted'
        )
        self.no_data_warning = False
        self.volcano_names = tr('Not specified in data')
        self.hazard_zone_attribute = 'radius'

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: dict
        """
        title = tr('Notes and assumptions')

        if get_needs_provenance_value(self.parameters) is None:
            needs_provenance = ''
        else:
            needs_provenance = tr(get_needs_provenance_value(self.parameters))
        fields = [
            tr('Map shows buildings affected in each of the volcano buffered '
               'zones.'),
            tr('Total population in the analysis area: %s') %
            population_rounding(self.total_population),
            tr('<sup>1</sup>People need evacuation if they are within the '
               'volcanic hazard zones.'),
            tr('Volcanoes considered: %s.') % self.volcano_names,
            needs_provenance
        ]

        if self.no_data_warning:
            fields.append(tr(
                'The layers contained "no data" values. This missing data '
                'was carried through to the impact layer.'))
            fields.append(tr(
                '"No data" values in the impact layer were treated as 0 '
                'when counting the affected or total population.'))

        fields.extend([
            tr('All values are rounded up to the nearest integer in order to '
               'avoid representing human lives as fractions.'),
            tr('Population rounding is applied to all population values, '
               'which may cause discrepancies when adding value.')
        ])

        return {
            'title': title,
            'fields': fields
        }

    def run(self):
        """Run volcano point population evacuation Impact Function.

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

        # Parameters
        radii = self.parameters['distances'].value

        # Get parameters from layer's keywords
        volcano_name_attribute = self.hazard.keyword('volcano_name_field')

        data_table = self.hazard.layer.get_data()

        # Get names of volcanoes considered
        if volcano_name_attribute in self.hazard.layer.get_attribute_names():
            volcano_name_list = []
            # Run through all polygons and get unique names
            for row in data_table:
                volcano_name_list.append(row[volcano_name_attribute])

            volcano_names = ''
            for radius in volcano_name_list:
                volcano_names += '%s, ' % radius
            self.volcano_names = volcano_names[:-2]  # Strip trailing ', '

        # Run interpolation function for polygon2raster
        interpolated_layer, covered_exposure_layer = \
            assign_hazard_values_to_exposure_data(
                self.hazard.layer,
                self.exposure.layer,
                attribute_name=self.target_field
            )

        # Initialise affected population per categories
        for radius in radii:
            category = 'Radius %s km ' % format_int(radius)
            self.affected_population[category] = 0

        if has_no_data(self.exposure.layer.get_data(nan=True)):
            self.no_data_warning = True
        # Count affected population per polygon and total
        for row in interpolated_layer.get_data():
            # Get population at this location
            population = row[self.target_field]
            if not numpy.isnan(population):
                population = float(population)
                # Update population count for this category
                category = 'Radius %s km ' % format_int(
                    row[self.hazard_zone_attribute])
                self.affected_population[category] += population

        # Count totals
        self.total_population = population_rounding(
            int(numpy.nansum(self.exposure.layer.get_data())))

        self.minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]

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
        map_title = tr('People affected by the buffered point volcano')
        legend_title = tr('Population')
        legend_units = tr('(people per cell)')
        legend_notes = tr(
            'Thousand separator is represented by  %s' %
            get_thousand_separator())

        impact_data = self.generate_data()

        # Create vector layer and return
        extra_keywords = {
            'target_field': self.target_field,
            'map_title': map_title,
            'legend_notes': legend_notes,
            'legend_units': legend_units,
            'legend_title': legend_title,
            'total_needs': self.total_needs
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        impact_layer = Raster(
            data=covered_exposure_layer.get_data(),
            projection=covered_exposure_layer.get_projection(),
            geotransform=covered_exposure_layer.get_geotransform(),
            name=tr('People affected by the buffered point volcano'),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
