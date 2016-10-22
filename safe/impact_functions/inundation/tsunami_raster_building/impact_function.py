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

from safe.impact_functions.inundation\
    .tsunami_raster_building.metadata_definitions import \
    TsunamiRasterBuildingMetadata
from safe.impact_functions.bases.continuous_rh_classified_ve import \
    ContinuousRHClassifiedVE
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.utilities.utilities import main_type
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)
LOGGER = logging.getLogger('InaSAFE')


class TsunamiRasterBuildingFunction(
        ContinuousRHClassifiedVE,
        BuildingExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Inundation raster impact on building data."""
    _metadata = TsunamiRasterBuildingMetadata()

    def __init__(self):
        """Constructor (calls ctor of base class)."""
        super(TsunamiRasterBuildingFunction, self).__init__()
        BuildingExposureReportMixin.__init__(self)
        self._target_field = 'depth'
        self.hazard_classes = [
            tr('Dry Zone'),
            tr('Low Hazard Zone'),
            tr('Medium Hazard Zone'),
            tr('High Hazard Zone'),
            tr('Very High Hazard Zone'),
        ]

    def notes(self):
        """Return the notes section of the report as dict.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        # Thresholds for tsunami hazard zone breakdown.
        low_max = self.parameters['low_threshold']
        medium_max = self.parameters['medium_threshold']
        high_max = self.parameters['high_threshold']

        fields = [
            tr('Dry zone is defined as non-inundated area or has inundation '
               'depth is 0 %s') % low_max.unit.abbreviation,
            tr('Low tsunami hazard zone is defined as inundation depth is '
               'more than 0 %s but less than %.1f %s') % (
                low_max.unit.abbreviation,
                low_max.value,
                low_max.unit.abbreviation),
            tr('Medium tsunami hazard zone is defined as inundation depth '
               'is more than %.1f %s but less than %.1f %s') % (
                low_max.value,
                low_max.unit.abbreviation,
                medium_max.value,
                medium_max.unit.abbreviation),
            tr('High tsunami hazard zone is defined as inundation depth is '
               'more than %.1f %s but less than %.1f %s') % (
                medium_max.value,
                medium_max.unit.abbreviation,
                high_max.value,
                high_max.unit.abbreviation),
            tr('Very high tsunami hazard zone is defined as inundation depth '
               'is more than %.1f %s') % (
                high_max.value, high_max.unit.abbreviation),
            tr('Buildings are closed if they are in low, medium, high, or '
               'very high tsunami hazard zone.'),
            tr('Buildings are open if they are in dry zone.')
        ]
        # include any generic exposure specific notes from definitions
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions
        fields = fields + self.hazard_notes()
        return fields

    @property
    def _affected_categories(self):
        """Overwriting the affected categories, since 'unaffected' are counted.

        :returns: The categories that equal effected.
        :rtype: list
        """
        return self.hazard_classes[1:]

    def run(self):
        """Tsunami raster impact to buildings (e.g. from Open Street Map)."""

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
        features = interpolated_layer.get_data()
        total_features = len(interpolated_layer)

        structure_class_field = self.exposure.keyword('structure_class_field')
        exposure_value_mapping = self.exposure.keyword('value_mapping')

        self.init_report_var(self.hazard_classes)

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

            usage = features[i].get(structure_class_field, None)
            usage = main_type(usage, exposure_value_mapping)

            # Add calculated impact to existing attributes
            features[i][self.target_field] = inundated_status
            category = self.categories[inundated_status]

            self.classify_feature(category, usage, True)

        self.reorder_dictionaries()

        style_classes = [
            dict(
                label=self.hazard_classes[0] + ': 0 m',
                value=0,
                colour='#00FF00',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[1] + ': >0 - %.1f m' % low_max,
                value=1,
                colour='#FFFF00',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[2] + ': %.1f - %.1f m' % (
                    low_max + 0.1, medium_max),
                value=2,
                colour='#FFB700',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[3] + ': %.1f - %.1f m' % (
                    medium_max + 0.1, high_max),
                value=3,
                colour='#FF6F00',
                transparency=0,
                size=1
            ),

            dict(
                label=self.hazard_classes[4] + ' > %.1f m' % high_max,
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

        impact_data = self.generate_data()

        extra_keywords = {
            'target_field': self.target_field,
            'map_title': self.map_title(),
            'legend_title': self.metadata().key('legend_title'),
            'legend_units': self.metadata().key('legend_units'),
            'buildings_total': total_features,
            'buildings_affected': self.total_affected_buildings
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        impact_layer = Vector(
            data=features,
            projection=interpolated_layer.get_projection(),
            geometry=interpolated_layer.get_geometry(),
            name=self.map_title(),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
