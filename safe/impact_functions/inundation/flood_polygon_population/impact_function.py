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

import logging
import numpy

from safe.utilities.i18n import tr
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.impact_functions.core import (
    population_rounding,
    has_no_data)
from safe.impact_functions.inundation.flood_polygon_population \
    .metadata_definitions import FloodEvacuationVectorHazardMetadata
from safe.impact_functions.bases.classified_vh_continuous_re import \
    ClassifiedVHContinuousRE
from safe.impact_functions.core import no_population_impact_message
from safe.storage.raster import Raster
from safe.common.utilities import (
    format_int,
    create_classes,
    humanize_class,
    create_label,
    get_thousand_separator)
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    get_needs_provenance_value, filter_needs_parameters
from safe.common.exceptions import ZeroImpactException
from safe.impact_functions.core import get_key_for_value
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin
import safe.messaging as m
from safe.messaging import styles

__author__ = 'Rizky Maulana Nugraha'

LOGGER = logging.getLogger('InaSAFE')


class FloodEvacuationVectorHazardFunction(
        ClassifiedVHContinuousRE,
        PopulationExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Impact function for vector flood evacuation."""
    _metadata = FloodEvacuationVectorHazardMetadata()

    def __init__(self):
        """Constructor."""
        super(FloodEvacuationVectorHazardFunction, self).__init__()

        # Use affected field flag (if False, all polygon will be considered as
        # affected)
        self.use_affected_field = False
        # The 'wet' variable
        self.wet = 'wet'

        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)
        self.no_data_warning = False

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: safe.messaging.Message
        """
        if get_needs_provenance_value(self.parameters) is None:
            needs_provenance = ''
        else:
            needs_provenance = tr(get_needs_provenance_value(self.parameters))

        message = m.Message(style_class='container')

        message.add(
            m.Heading(tr('Notes and assumptions'), **styles.INFO_STYLE))
        checklist = m.BulletedList()
        population = format_int(population_rounding(self.total_population))
        checklist.add(tr(
            'Total population in the analysis area: %s') % population)
        threshold = format_int(self.parameters['evacuation_percentage'].value)
        checklist.add(tr(
            '<sup>1</sup>The evacuation threshold used to determine '
            'population needing evacuation is %s%%.') % threshold)

        checklist.add(needs_provenance)
        if self.no_data_warning:
            checklist.add(tr(
                'The layers contained "no data" values. This missing data '
                'was carried through to the impact layer.'))
            checklist.add(tr(
                '"No data" values in the impact layer were treated as 0 '
                'when counting the affected or total population.'))
        checklist.add(tr(
            'All values are rounded up to the nearest integer in '
            'order to avoid representing human lives as fractions.'))
        checklist.add(tr(
            'Population rounding is applied to all population '
            'values, which may cause discrepancies when adding values.'))

        message.add(checklist)
        return message

    def run(self):
        """Risk plugin for flood population evacuation.

        Counts number of people exposed to areas identified as flood prone

        :returns: Map of population exposed to flooding Table with number of
            people evacuated and supplies required.
        :rtype: tuple
        """
        self.validate()
        self.prepare()

        # Get parameters from layer's keywords
        self.hazard_class_attribute = self.hazard.keyword('field')
        self.hazard_class_mapping = self.hazard.keyword('value_map')

        # Get the IF parameters
        self._evacuation_percentage = (
            self.parameters['evacuation_percentage'].value)

        # Check that hazard is polygon type
        if not self.hazard.layer.is_polygon_data:
            message = (
                'Input hazard must be a polygon layer. I got %s with layer '
                'type %s' % (
                    self.hazard.name,
                    self.hazard.layer.get_geometry_name()))
            raise Exception(message)

        if has_no_data(self.exposure.layer.get_data(nan=True)):
            self.no_data_warning = True

        # Check that affected field exists in hazard layer
        if (self.hazard_class_attribute in
                self.hazard.layer.get_attribute_names()):
            self.use_affected_field = True

        # Run interpolation function for polygon2raster
        interpolated_layer, covered_exposure = \
            assign_hazard_values_to_exposure_data(
                self.hazard.layer,
                self.exposure.layer,
                attribute_name=self.target_field)

        # Data for manipulating the covered_exposure layer
        new_covered_exposure_data = covered_exposure.get_data()
        covered_exposure_top_left = numpy.array([
            covered_exposure.get_geotransform()[0],
            covered_exposure.get_geotransform()[3]])
        covered_exposure_dimension = numpy.array([
            covered_exposure.get_geotransform()[1],
            covered_exposure.get_geotransform()[5]])

        # Count affected population per polygon, per category and total
        total_affected_population = 0
        for attr in interpolated_layer.get_data():
            affected = False
            if self.use_affected_field:
                row_affected_value = attr[self.hazard_class_attribute]
                if row_affected_value is not None:
                    affected = get_key_for_value(
                        row_affected_value, self.hazard_class_mapping)
            else:
                # assume that every polygon is affected (see #816)
                affected = self.wet

            if affected == self.wet:
                # Get population at this location
                population = attr[self.target_field]
                if not numpy.isnan(population):
                    population = float(population)
                    total_affected_population += population
            else:
                # If it's not affected, set the value of the impact layer to 0
                grid_point = attr['grid_point']
                index = numpy.floor(
                    (grid_point - covered_exposure_top_left) / (
                        covered_exposure_dimension)).astype(int)
                new_covered_exposure_data[index[1]][index[0]] = 0

        # Estimate number of people in need of evacuation
        if self.use_affected_field:
            affected_population = tr(
                'People within hazard field ("%s") of value "%s"') % (
                    self.hazard_class_attribute,
                    ','.join([
                        unicode(hazard_class) for
                        hazard_class in self.hazard_class_mapping[self.wet]
                    ]))
        else:
            affected_population = tr('People within any hazard polygon.')

        self.affected_population[affected_population] = (
            total_affected_population)

        self.total_population = int(
            numpy.nansum(self.exposure.layer.get_data(scaling=False)))

        self.minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]

        impact_table = impact_summary = self.html_report()

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        classes = create_classes(
            new_covered_exposure_data.flat[:], len(colours))

        # check for zero impact
        if total_affected_population == 0:
            message = no_population_impact_message(self.question)
            raise ZeroImpactException(message)

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
        map_title = tr('People affected by flood prone areas')
        legend_title = tr('Population Count')
        legend_units = tr('(people per polygon)')
        legend_notes = tr(
            'Thousand separator is represented by %s' %
            get_thousand_separator())

        # Create vector layer and return
        impact_layer = Raster(
            data=new_covered_exposure_data,
            projection=covered_exposure.get_projection(),
            geotransform=covered_exposure.get_geotransform(),
            name=tr('People affected by flood prone areas'),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'target_field': self.target_field,
                'map_title': map_title,
                'legend_notes': legend_notes,
                'legend_units': legend_units,
                'legend_title': legend_title,
                'affected_population': total_affected_population,
                'total_population': self.total_population,
                'total_needs': self.total_needs},
            style_info=style_info)
        self._impact = impact_layer
        return impact_layer
