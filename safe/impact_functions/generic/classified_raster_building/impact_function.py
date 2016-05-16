# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Generic Impact function on
Building for Classified Hazard.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'lucernae'
__date__ = '23/03/15'

import logging
from numpy import round as numpy_round

from safe.impact_functions.bases.classified_rh_classified_ve import \
    ClassifiedRHClassifiedVE
from safe.storage.vector import Vector
from safe.common.exceptions import KeywordNotFoundError
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.utilities.i18n import tr
from safe.utilities.utilities import main_type
from safe.impact_functions.generic.classified_raster_building\
    .metadata_definitions import ClassifiedRasterHazardBuildingMetadata
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)
LOGGER = logging.getLogger('InaSAFE')


class ClassifiedRasterHazardBuildingFunction(
        ClassifiedRHClassifiedVE,
        BuildingExposureReportMixin):
    """Impact plugin for classified hazard impact on building data"""

    _metadata = ClassifiedRasterHazardBuildingMetadata()
    # Function documentation

    def __init__(self):
        super(ClassifiedRasterHazardBuildingFunction, self).__init__()
        self.affected_field = 'affected'

        # From BuildingExposureReportMixin
        self.building_report_threshold = 25

    def notes(self):
        """Return the notes section of the report as dict.

        :return: The notes that should be attached to this impact report.
        :rtype: dict
        """
        title = tr('Notes and assumptions')
        fields = [
            tr('Map shows buildings affected in low, medium and high hazard '
               'class areas.')
        ]

        return {
            'title': title,
            'fields': fields
        }

    def run(self):
        """Classified hazard impact to buildings (e.g. from Open Street Map).
        """

        # Value from layer's keywords

        structure_class_field = self.exposure.keyword('structure_class_field')
        try:
            exposure_value_mapping = self.exposure.keyword('value_mapping')
        except KeywordNotFoundError:
            # Generic IF, the keyword might not be defined base.py
            exposure_value_mapping = {}

        # The 3 classes
        categorical_hazards = self.parameters['Categorical hazards'].value
        low_t = categorical_hazards[0].value
        medium_t = categorical_hazards[1].value
        high_t = categorical_hazards[2].value

        # Determine attribute name for hazard levels
        if self.hazard.layer.is_raster:
            hazard_attribute = 'level'
        else:
            hazard_attribute = None

        interpolated_result = assign_hazard_values_to_exposure_data(
            self.hazard.layer,
            self.exposure.layer,
            attribute_name=hazard_attribute,
            mode='constant')

        # Extract relevant exposure data
        attributes = interpolated_result.get_data()

        buildings_total = len(interpolated_result)

        hazard_classes = [
            tr('High Hazard Class'),
            tr('Medium Hazard Class'),
            tr('Low Hazard Class')
        ]
        self.init_report_var(hazard_classes)

        for i in range(buildings_total):
            usage = attributes[i][structure_class_field]
            usage = main_type(usage, exposure_value_mapping)

            # Count all buildings by type
            attributes[i][self.target_field] = 0
            attributes[i][self.affected_field] = 0
            level = float(attributes[i]['level'])
            level = float(numpy_round(level))
            if level == high_t:
                impact_level = tr('High Hazard Class')
            elif level == medium_t:
                impact_level = tr('Medium Hazard Class')
            elif level == low_t:
                impact_level = tr('Low Hazard Class')
            else:
                continue

            # Add calculated impact to existing attributes
            attributes[i][self.target_field] = {
                tr('High Hazard Class'): 3,
                tr('Medium Hazard Class'): 2,
                tr('Low Hazard Class'): 1
            }[impact_level]
            attributes[i][self.affected_field] = 1
            # Count affected buildings by type
            self.classify_feature(impact_level, usage, True)

        self.reorder_dictionaries()

        # Consolidate the small building usage groups < 25 to other
        # Building threshold #2468
        postprocessors = self.parameters['postprocessors']
        building_postprocessors = postprocessors['BuildingType'][0]
        self.building_report_threshold = building_postprocessors.value[0].value
        self._consolidate_to_other()

        # Create style
        style_classes = [
            dict(
                label=tr('High'),
                value=3,
                colour='#F31A1C',
                transparency=0,
                size=2,
                border_color='#969696',
                border_width=0.2),
            dict(
                label=tr('Medium'),
                value=2,
                colour='#F4A442',
                transparency=0,
                size=2,
                border_color='#969696',
                border_width=0.2),
            dict(
                label=tr('Low'),
                value=1,
                colour='#EBF442',
                transparency=0,
                size=2,
                border_color='#969696',
                border_width=0.2),
            dict(
                label=tr('Not Affected'),
                value=None,
                colour='#1EFC7C',
                transparency=0,
                size=2,
                border_color='#969696',
                border_width=0.2)]
        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        # For printing map purpose
        map_title = tr('Buildings affected')
        legend_title = tr('Structure inundated status')
        legend_units = tr('(Low, Medium, High)')

        impact_data = self.generate_data()

        extra_keywords = {
            'target_field': self.affected_field,
            'map_title': map_title,
            'legend_units': legend_units,
            'legend_title': legend_title,
            'buildings_total': buildings_total,
            'buildings_affected': self.total_affected_buildings
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create impact layer and return
        impact_layer = Vector(
            data=attributes,
            projection=self.exposure.layer.get_projection(),
            geometry=self.exposure.layer.get_geometry(),
            name=tr('Estimated buildings affected'),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
