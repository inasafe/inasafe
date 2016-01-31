# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Tsunami Raster Impact on
Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'ismailsunni'
__project_name__ = 'inasafe'
__filename__ = 'impact_function'
__date__ = '12/31/15'
__copyright__ = 'imajimatika@gmail.com'


import logging
from collections import OrderedDict

from safe.impact_functions.inundation\
    .tsunami_raster_building.metadata_definitions import \
    TsunamiRasterBuildingMetadata
from safe.impact_functions.bases.continuous_rh_classified_ve import \
    ContinuousRHClassifiedVE
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.common.utilities import get_osm_building_usage, verify
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)
import safe.messaging as m
from safe.messaging import styles
from safe.common.exceptions import KeywordNotFoundError
LOGGER = logging.getLogger('InaSAFE')


class TsunamiRasterBuildingFunction(
        ContinuousRHClassifiedVE,
        BuildingExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Inundation raster impact on building data."""
    _metadata = TsunamiRasterBuildingMetadata()

    def __init__(self):
        """Constructor (calls ctor of base class)."""
        self._target_field = 'depth'
        super(TsunamiRasterBuildingFunction, self).__init__()
        self.hazard_classes = [
            tr('Dry Zone'),
            tr('Low Hazard Zone'),
            tr('Medium Hazard Zone'),
            tr('High Hazard Zone'),
            tr('Very High Hazard Zone'),
        ]
        # From BuildingExposureReportMixin
        self.building_report_threshold = 25

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        message.add(
            m.Heading(tr('Notes and assumptions'), **styles.INFO_STYLE))
        checklist = m.BulletedList()

        # Thresholds for tsunami hazard zone breakdown.
        low_max = self.parameters['low_threshold']
        medium_max = self.parameters['medium_threshold']
        high_max = self.parameters['high_threshold']

        checklist.add(tr(
            'Dry zone is defined as non-inundated area or has inundation '
            'depth is 0 %s') % (low_max.unit.abbreviation)
        )

        checklist.add(tr(
            'Low tsunami hazard zone is defined as inundation depth is more '
            'than 0 %s but less than %.1f %s') % (
            low_max.unit.abbreviation,
            low_max.value,
            low_max.unit.abbreviation)
        )
        checklist.add(tr(
            'Moderate tsunami hazard zone is defined as inundation depth is '
            'more than %.1f %s but less than %.1f %s') % (
            low_max.value,
            low_max.unit.abbreviation,
            medium_max.value,
            medium_max.unit.abbreviation)
        )
        checklist.add(tr(
            'High tsunami hazard zone is defined as inundation depth is '
            'more than %.1f %s but less than %.1f %s') % (
            medium_max.value,
            medium_max.unit.abbreviation,
            high_max.value,
            high_max.unit.abbreviation)
        )
        checklist.add(tr(
            'Very high tsunami hazard zone is defined as inundation depth is '
            'more than %.1f %s') % (
            high_max.value, high_max.unit.abbreviation))

        checklist.add(tr(
            'Buildings are closed if they are in low, moderate, high, or very '
            'high tsunami hazard zone.'))
        checklist.add(tr(
            'Buildings are opened if they are in dry zone.'))
        message.add(checklist)
        return message

    @property
    def _affected_categories(self):
        """Overwriting the affected categories, since 'unaffected' are counted.

        :returns: The categories that equal effected.
        :rtype: list
        """
        return self.hazard_classes[1:]

    def run(self):
        """Tsunami raster impact to buildings (e.g. from Open Street Map)."""
        self.validate()
        self.prepare()

        # Thresholds for tsunami hazard zone breakdown.
        low_max = self.parameters['low_threshold'].value
        medium_max = self.parameters['medium_threshold'].value
        high_max = self.parameters['high_threshold'].value

        # Interpolate hazard level to building locations
        interpolated_layer = assign_hazard_values_to_exposure_data(
            self.hazard.layer,
            self.exposure.layer,
            attribute_name=self.target_field)

        # Extract relevant exposure data
        attribute_names = interpolated_layer.get_attribute_names()
        features = interpolated_layer.get_data()
        total_features = len(interpolated_layer)

        # but use the old get_osm_building_usage
        try:
            structure_class_field = self.exposure.keyword(
                'structure_class_field')
        except KeywordNotFoundError:
            structure_class_field = None

        # Building breakdown
        self.buildings = {}
        # Impacted building breakdown
        self.affected_buildings = OrderedDict([
            (self.hazard_classes[0], {}),
            (self.hazard_classes[1], {}),
            (self.hazard_classes[2], {}),
            (self.hazard_classes[3], {}),
            (self.hazard_classes[4], {})
        ])
        categories = self.affected_buildings.keys()
        for i in range(total_features):
            # Get the interpolated depth
            water_depth = float(features[i][self.target_field])
            if water_depth <= 0:
                inundated_status = 0
            elif 0 < water_depth <= low_max:
                inundated_status = 1  # low
            elif low_max < water_depth <= medium_max:
                inundated_status = 2  # medium
            elif medium_max < water_depth <= high_max:
                inundated_status = 3  # high
            elif high_max < water_depth:
                inundated_status = 4  # very high
            # If not a number or a value beside real number.
            else:
                inundated_status = 0

            # Count affected buildings by usage type if available
            if (structure_class_field in attribute_names and
                    structure_class_field):
                usage = features[i].get(structure_class_field, None)
            else:
                usage = get_osm_building_usage(
                    attribute_names, features[i])

            if usage is None or usage == 0:
                usage = 'unknown'

            if usage not in self.buildings:
                self.buildings[usage] = 0
                for category in self.affected_buildings.keys():
                    self.affected_buildings[category][usage] = OrderedDict([
                        (tr('Buildings Affected'), 0)])

            # Count all buildings by type
            self.buildings[usage] += 1
            # Add calculated impact to existing attributes
            features[i][self.target_field] = inundated_status
            category = categories[inundated_status]
            self.affected_buildings[category][usage][
                tr('Buildings Affected')] += 1

        # Lump small entries and 'unknown' into 'other' category
        # Building threshold #2468
        postprocessors = self.parameters['postprocessors']
        building_postprocessors = postprocessors['BuildingType'][0]
        self.building_report_threshold = building_postprocessors.value[0].value
        self._consolidate_to_other()
        # Generate simple impact report
        impact_table = impact_summary = self.html_report()

        # For printing map purpose
        map_title = tr('Inundated buildings')
        legend_title = tr('Inundated structure status')
        legend_units = tr('(low, medium, high, and very high)')

        style_classes = [
            dict(
                label=self.hazard_classes[0],
                value=0,
                colour='#00FF00',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[1],
                value=1,
                colour='#FFFF00',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[2],
                value=2,
                colour='#FFB700',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[3],
                value=3,
                colour='#FF6F00',
                transparency=0,
                size=1
            ),

            dict(
                label=self.hazard_classes[4],
                value=4,
                colour='#FF0000',
                transparency=0,
                size=1
            ),
        ]

        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        vector_layer = Vector(
            data=features,
            projection=interpolated_layer.get_projection(),
            geometry=interpolated_layer.get_geometry(),
            name=tr('Estimated buildings affected'),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'target_field': self.target_field,
                'map_title': map_title,
                'legend_title': legend_title,
                'legend_units': legend_units,
                'buildings_total': total_features,
                'buildings_affected': self.total_affected_buildings},
            style_info=style_info)
        # Create vector layer and return
        self._impact = vector_layer
        return vector_layer
