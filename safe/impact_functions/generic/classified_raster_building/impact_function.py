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
from collections import OrderedDict

from numpy import round as numpy_round

from definitionsv4.definitions_v3 import generic_raster_hazard_classes
from safe.common.exceptions import KeywordNotFoundError
from safe.common.utilities import get_non_conflicting_attribute_name
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.impact_functions.bases.classified_rh_classified_ve import \
    ClassifiedRHClassifiedVE
from safe.impact_functions.generic.classified_raster_building\
    .metadata_definitions import ClassifiedRasterHazardBuildingMetadata
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.utilities.utilities import main_type

LOGGER = logging.getLogger('InaSAFE')


class ClassifiedRasterHazardBuildingFunction(
        ClassifiedRHClassifiedVE,
        BuildingExposureReportMixin):
    """Impact plugin for classified hazard impact on building data"""

    _metadata = ClassifiedRasterHazardBuildingMetadata()
    # Function documentation

    def __init__(self):
        super(ClassifiedRasterHazardBuildingFunction, self).__init__()
        BuildingExposureReportMixin.__init__(self)
        self.affected_field = 'affected'
        self.target_field = 'hazard'

    def notes(self):
        """Return the notes section of the report as dict.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        fields = [
            tr('Map shows buildings affected in low, medium and high hazard '
               'zones.')
        ]
        # include any generic exposure specific notes from definitions_v3.py
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions_v3.py
        fields = fields + self.hazard_notes()
        return fields

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
        self.hazard_class_mapping = self.hazard.keyword('value_map')

        keys = [x['key'] for x in generic_raster_hazard_classes['classes']]
        names = [x['name'] for x in generic_raster_hazard_classes['classes']]
        classes = OrderedDict()
        for i in range(len(keys)):
            classes[keys[i]] = names[i]

        # Determine attribute name for hazard class
        hazard_class_attribute = get_non_conflicting_attribute_name(
            'haz_class',
            [x.keys() for x in self.exposure.layer.data][0]
        )

        interpolated_result = assign_hazard_values_to_exposure_data(
            self.hazard.layer,
            self.exposure.layer,
            attribute_name=hazard_class_attribute,
            mode='constant')

        # Extract relevant exposure data
        attributes = interpolated_result.get_data()

        # Number of building in the interpolated layer
        buildings_total = len(interpolated_result)

        # Inverse the order from low to high
        self.init_report_var(classes.values()[::-1])

        for i in range(buildings_total):
            # Get the usage of the building
            usage = attributes[i][structure_class_field]
            usage = main_type(usage, exposure_value_mapping)

            # Initialize value as Not affected
            attributes[i][self.target_field] = tr('Not affected')
            attributes[i][self.affected_field] = 0

            # Get the hazard level of the building
            level = float(attributes[i][hazard_class_attribute])
            level = float(numpy_round(level))

            # Find the class according the building's level
            for k, v in self.hazard_class_mapping.items():
                if level in v:
                    impact_class = classes[k]
                    # Set the impact level
                    attributes[i][self.target_field] = impact_class
                    # Set to affected
                    attributes[i][self.affected_field] = 1
                    break

            # Count affected buildings by type
            self.classify_feature(
                attributes[i][self.target_field],
                usage,
                bool(attributes[i][self.affected_field])
            )

        self.reorder_dictionaries()

        # Create style
        # Low, Medium and High are translated in the attribute table.
        # "Not affected" is not translated in the attribute table.
        style_classes = [
            dict(
                label=tr('Not Affected'),
                value='Not affected',
                colour='#1EFC7C',
                transparency=0,
                size=2,
                border_color='#969696',
                border_width=0.2),
            dict(
                label=tr('Low'),
                value=tr('Low hazard zone'),
                colour='#EBF442',
                transparency=0,
                size=2,
                border_color='#969696',
                border_width=0.2),
            dict(
                label=tr('Medium'),
                value=tr('Medium hazard zone'),
                colour='#F4A442',
                transparency=0,
                size=2,
                border_color='#969696',
                border_width=0.2),
            dict(
                label=tr('High'),
                value=tr('High hazard zone'),
                colour='#F31A1C',
                transparency=0,
                size=2,
                border_color='#969696',
                border_width=0.2),
        ]
        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')
        LOGGER.debug('target field : ' + self.target_field)

        impact_data = self.generate_data()

        extra_keywords = {
            'target_field': self.affected_field,
            'map_title': self.map_title(),
            'legend_units': self.metadata().key('legend_units'),
            'legend_title': self.metadata().key('legend_title'),
            'buildings_total': buildings_total,
            'buildings_affected': self.total_affected_buildings
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create impact layer and return
        impact_layer = Vector(
            data=attributes,
            projection=self.exposure.layer.get_projection(),
            geometry=self.exposure.layer.get_geometry(),
            name=self.map_title(),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
