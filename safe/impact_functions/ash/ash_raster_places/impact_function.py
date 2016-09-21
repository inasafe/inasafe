# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Tsunami Raster Impact on
Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import logging

from safe.impact_functions.ash.ash_raster_places.metadata_definitions import \
    AshRasterPlacesFunctionMetadata
from safe.impact_functions.bases.continuous_rh_classified_ve import \
    ContinuousRHClassifiedVE
from safe.storage.vector import Vector
from safe.common.exceptions import KeywordNotFoundError, ZeroImpactException
from safe.utilities.i18n import tr
from safe.utilities.utilities import main_type
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.impact_reports.place_exposure_report_mixin import (
    PlaceExposureReportMixin)

__author__ = 'etienne'
__project_name__ = 'inasafe-dev'
__filename__ = 'impact_function.py'
__date__ = '7/13/16'
__copyright__ = 'etienne@kartoza.com'

LOGGER = logging.getLogger('InaSAFE')


class AshRasterPlacesFunction(
        ContinuousRHClassifiedVE,
        PlaceExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Inundation raster impact on building data."""
    _metadata = AshRasterPlacesFunctionMetadata()

    def __init__(self):
        """Constructor (calls ctor of base class)."""
        super(AshRasterPlacesFunction, self).__init__()
        PlaceExposureReportMixin.__init__(self)
        self.hazard_classes = [
            tr('Very Low'),
            tr('Low'),
            tr('Moderate'),
            tr('High'),
            tr('Very High'),
        ]

        self.no_data_warning = False

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        # Range for ash hazard
        group_parameters = self.parameters['group_threshold']
        unaffected_max = group_parameters.value_map[
            'unaffected_threshold']
        very_low_max = group_parameters.value_map['very_low_threshold']
        low_max = group_parameters.value_map['low_threshold']
        medium_max = group_parameters.value_map['moderate_threshold']
        high_max = group_parameters.value_map['high_threshold']

        fields = [
            tr('Dry zone is defined as non-inundated area or has inundation '
               'depth is 0 %s') % low_max.unit.abbreviation,
            tr('Very Low ash hazard zone is defined as ash depth is '
               'more than %s %s but less than %.1f %s') % (
                unaffected_max,
                unaffected_max.unit.abbreviation,
                very_low_max.value,
                very_low_max.unit.abbreviation),
            tr('Low ash hazard zone is defined as ash depth is '
               'more than %s %s but less than %.1f %s') % (
                very_low_max,
                very_low_max.unit.abbreviation,
                low_max.value,
                low_max.unit.abbreviation),
            tr('Medium ash hazard zone is defined as ash depth '
               'is more than %.1f %s but less than %.1f %s') % (
                low_max.value,
                low_max.unit.abbreviation,
                medium_max.value,
                medium_max.unit.abbreviation),
            tr('High ash hazard zone is defined as ash depth is '
               'more than %.1f %s but less than %.1f %s') % (
                medium_max.value,
                medium_max.unit.abbreviation,
                high_max.value,
                high_max.unit.abbreviation),
            tr('Very high ash hazard zone is defined as ash depth '
               'is more than %.1f %s') % (
                high_max.value, high_max.unit.abbreviation)
        ]
        # include any generic exposure specific notes from definitions_v3.py
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions_v3.py
        fields = fields + self.hazard_notes()
        return fields

    def run(self):
        """Ash raster impact to buildings (e.g. from Open Street Map)."""

        # Range for ash hazard
        group_parameters = self.parameters['group_threshold']
        unaffected_max = group_parameters.value_map[
            'unaffected_threshold'].value
        very_low_max = group_parameters.value_map['very_low_threshold'].value
        low_max = group_parameters.value_map['low_threshold'].value
        medium_max = group_parameters.value_map['moderate_threshold'].value
        high_max = group_parameters.value_map['high_threshold'].value

        # Interpolate hazard level to building locations
        interpolated_layer = assign_hazard_values_to_exposure_data(
            self.hazard.layer,
            self.exposure.layer,
            attribute_name=self.target_field)

        # Extract relevant exposure data
        features = interpolated_layer.get_data()
        total_features = len(interpolated_layer)

        try:
            population_field = self.exposure.keyword('population_field')
        except KeywordNotFoundError:
            population_field = None

        # required for real time
        self.exposure.keyword('name_field')

        structure_class_field = self.exposure.keyword('structure_class_field')
        exposure_value_mapping = self.exposure.keyword('value_mapping')

        self.init_report_var(self.hazard_classes)

        unaffected_feats = []

        for i in range(total_features):
            # Get the interpolated depth
            ash_hazard_zone = float(features[i][self.target_field])
            if ash_hazard_zone <= unaffected_max:
                # current_hash_zone = 0  # not affected
                unaffected_feats.append(i)
                continue  # not affected
            elif unaffected_max < ash_hazard_zone <= very_low_max:
                current_hash_zone = 0  # very low
            elif very_low_max < ash_hazard_zone <= low_max:
                current_hash_zone = 1  # low
            elif low_max < ash_hazard_zone <= medium_max:
                current_hash_zone = 2  # medium
            elif medium_max < ash_hazard_zone <= high_max:
                current_hash_zone = 3  # high
            elif high_max < ash_hazard_zone:
                current_hash_zone = 4  # very high
            # If not a number or a value beside real number.
            else:
                # current_hash_zone = 0
                unaffected_feats.append(i)
                continue

            usage = features[i].get(structure_class_field, None)
            usage = main_type(usage, exposure_value_mapping)

            # Add calculated impact to existing attributes
            features[i][self.target_field] = current_hash_zone
            category = self.hazard_classes[current_hash_zone]

            if population_field is not None:
                population = float(features[i][population_field])
            else:
                population = 1

            self.classify_feature(category, usage, population, True)

        geometries = interpolated_layer.get_geometry()
        unaffected_feats.reverse()
        for u in unaffected_feats:
            features.remove(features[u])
            geometries.remove(geometries[u])

        self.reorder_dictionaries()

        style_classes = [
            dict(
                label=self.hazard_classes[0] + ': >%.1f - %.1f cm' % (
                    unaffected_max, very_low_max),
                value=0,
                colour='#00FF00',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[1] + ': >%.1f - %.1f cm' % (
                    very_low_max, low_max),
                value=1,
                colour='#FFFF00',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[2] + ': >%.1f - %.1f cm' % (
                    low_max, medium_max),
                value=2,
                colour='#FFB700',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[3] + ': >%.1f - %.1f cm' % (
                    medium_max, high_max),
                value=3,
                colour='#FF6F00',
                transparency=0,
                size=1
            ),

            dict(
                label=self.hazard_classes[4] + ': <%.1f cm' % high_max,
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
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        if not features or len(features) == 0:
            raise ZeroImpactException()

        impact_layer = Vector(
            data=features,
            projection=interpolated_layer.get_projection(),
            geometry=geometries,
            name=self.map_title(),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
