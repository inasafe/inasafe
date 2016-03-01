# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Volcano Polygon on
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
from safe.impact_functions.volcanic.volcano_polygon_population\
    .metadata_definitions import VolcanoPolygonPopulationFunctionMetadata
from safe.impact_functions.core import (
    population_rounding,
    has_no_data)
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.storage.raster import Raster
from safe.utilities.i18n import tr
from safe.common.utilities import (
    humanize_class,
    create_classes,
    create_label,
    get_thousand_separator)
from safe.impact_functions.core import no_population_impact_message
from safe.common.exceptions import InaSAFEError, ZeroImpactException
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    filter_needs_parameters, get_needs_provenance_value
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin
import safe.messaging as m
from safe.messaging import styles


class VolcanoPolygonPopulationFunction(
        ClassifiedVHContinuousRE,
        PopulationExposureReportMixin):
    """Impact Function for Volcano Point on Building."""

    _metadata = VolcanoPolygonPopulationFunctionMetadata()

    def __init__(self):
        super(VolcanoPolygonPopulationFunction, self).__init__()
        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)
        self.no_data_warning = False
        self.volcano_names = tr('Not specified in data')

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
        checklist.add(tr(
            'Total population in the analysis area: %s'
            ) % population_rounding(self.total_population))
        checklist.add(tr(
            '<sup>1</sup>People need evacuation if they are within '
            'the volcanic hazard zones.'))
        names = tr('Volcanoes considered: %s.') % self.volcano_names
        checklist.add(names)
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
            'values, which may cause discrepancies when adding value.'))
        message.add(checklist)
        return message

    def run(self):
        """Run volcano population evacuation Impact Function.

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
        self.validate()
        self.prepare()

        # Parameters
        self.hazard_class_attribute = self.hazard.keyword('field')
        name_attribute = self.hazard.keyword('volcano_name_field')

        if has_no_data(self.exposure.layer.get_data(nan=True)):
            self.no_data_warning = True

        # Input checks
        if not self.hazard.layer.is_polygon_data:
            msg = ('Input hazard must be a polygon layer. I got %s with '
                   'layer type %s' % (self.hazard.layer.get_name(),
                                      self.hazard.layer.get_geometry_name()))
            raise Exception(msg)

        # Check if hazard_class_attribute exists in hazard_layer
        if (self.hazard_class_attribute not in
                self.hazard.layer.get_attribute_names()):
            msg = ('Hazard data %s did not contain expected attribute %s ' % (
                self.hazard.layer.get_name(), self.hazard_class_attribute))
            # noinspection PyExceptionInherit
            raise InaSAFEError(msg)

        features = self.hazard.layer.get_data()
        hazard_zone_categories = list(
            set(self.hazard.layer.get_data(self.hazard_class_attribute)))

        # Get names of volcanoes considered
        if name_attribute in self.hazard.layer.get_attribute_names():
            volcano_name_list = []
            # Run through all polygons and get unique names
            for row in features:
                volcano_name_list.append(row[name_attribute])

            self.volcano_names = ', '.join(set(volcano_name_list))

        # Run interpolation function for polygon2raster
        interpolated_layer, covered_exposure_layer = \
            assign_hazard_values_to_exposure_data(
                self.hazard.layer,
                self.exposure.layer,
                attribute_name=self.target_field)

        # Initialise total affected per category
        for hazard_zone in hazard_zone_categories:
            self.affected_population[hazard_zone] = 0

        # Count affected population per polygon and total
        for row in interpolated_layer.get_data():
            # Get population at this location
            population = row[self.target_field]
            if not numpy.isnan(population):
                population = float(population)
                # Update population count for this category
                category = row[self.hazard_class_attribute]
                self.affected_population[category] += population

        # Count totals
        self.total_population = int(
            numpy.nansum(self.exposure.layer.get_data()))
        self.unaffected_population = (
            self.total_population - self.total_affected_population)

        self.minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]

        impact_table = impact_summary = self.html_report()

        # check for zero impact
        if self.total_affected_population == 0:
            message = no_population_impact_message(self.question)
            raise ZeroImpactException(message)

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
        map_title = tr('People affected by Volcano Hazard Zones')
        legend_title = tr('Population')
        legend_units = tr('(people per cell)')
        legend_notes = tr(
            'Thousand separator is represented by  %s' %
            get_thousand_separator())

        # Create vector layer and return
        impact_layer = Raster(
            data=covered_exposure_layer.get_data(),
            projection=covered_exposure_layer.get_projection(),
            geotransform=covered_exposure_layer.get_geotransform(),
            name=tr('People affected by volcano hazard zones'),
            keywords={'impact_summary': impact_summary,
                      'impact_table': impact_table,
                      'target_field': self.target_field,
                      'map_title': map_title,
                      'legend_notes': legend_notes,
                      'legend_units': legend_units,
                      'legend_title': legend_title,
                      'total_needs': self.total_needs},
            style_info=style_info)

        self._impact = impact_layer
        return impact_layer
