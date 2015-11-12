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

from safe.impact_functions.bases.classified_rh_classified_ve import \
    ClassifiedRHClassifiedVE
from safe.storage.vector import Vector
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.utilities.i18n import tr
from safe.common.utilities import get_osm_building_usage
from safe.impact_functions.generic.classified_raster_building\
    .metadata_definitions import ClassifiedRasterHazardBuildingMetadata
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)
from safe.common.exceptions import KeywordNotFoundError
import safe.messaging as m
from safe.messaging import styles
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

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: safe.messaging.Message
        """
        message = m.Message()
        message.add(m.Heading(
            tr('Notes and assumptions'), **styles.INFO_STYLE))
        message.add(tr(
            'Map shows buildings affected in low, medium and '
            'high hazard class areas.'))
        return message

    def run(self):
        """Classified hazard impact to buildings (e.g. from Open Street Map).
        """
        self.validate()
        self.prepare()

        # Value from layer's keywords
        # Try to get the value from keyword, if not exist, it will not fail,
        # but use the old get_osm_building_usage
        try:
            structure_class_field = self.exposure.keyword(
                'structure_class_field')
        except KeywordNotFoundError:
            structure_class_field = None

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
        attribute_names = interpolated_result.get_attribute_names()
        attributes = interpolated_result.get_data()

        buildings_total = len(interpolated_result)
        # Calculate building impact
        self.buildings = {}
        self.affected_buildings = OrderedDict([
            (tr('High Hazard Class'), {}),
            (tr('Medium Hazard Class'), {}),
            (tr('Low Hazard Class'), {})
        ])
        for i in range(buildings_total):

            if (structure_class_field and
                    structure_class_field in attribute_names):
                usage = attributes[i][structure_class_field]
            else:
                usage = get_osm_building_usage(attribute_names, attributes[i])

            if usage is None or usage == 0:
                usage = 'unknown'

            if usage not in self.buildings:
                self.buildings[usage] = 0
                for category in self.affected_buildings.keys():
                    self.affected_buildings[category][usage] = OrderedDict([
                        (tr('Buildings Affected'), 0)])

            # Count all buildings by type
            self.buildings[usage] += 1
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
            self.affected_buildings[impact_level][usage][
                tr('Buildings Affected')] += 1

        # Consolidate the small building usage groups < 25 to other
        self._consolidate_to_other()

        # Create style
        style_classes = [dict(label=tr('High'),
                              value=3,
                              colour='#F31A1C',
                              transparency=0,
                              size=2,
                              border_color='#969696',
                              border_width=0.2),
                         dict(label=tr('Medium'),
                              value=2,
                              colour='#F4A442',
                              transparency=0,
                              size=2,
                              border_color='#969696',
                              border_width=0.2),
                         dict(label=tr('Low'),
                              value=1,
                              colour='#EBF442',
                              transparency=0,
                              size=2,
                              border_color='#969696',
                              border_width=0.2),
                         dict(label=tr('Not Affected'),
                              value=None,
                              colour='#1EFC7C',
                              transparency=0,
                              size=2,
                              border_color='#969696',
                              border_width=0.2)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')

        impact_table = impact_summary = self.html_report()

        # For printing map purpose
        map_title = tr('Buildings affected')
        legend_title = tr('Structure inundated status')
        legend_units = tr('(Low, Medium, High)')

        # Create vector layer and return
        vector_layer = Vector(
            data=attributes,
            projection=self.exposure.layer.get_projection(),
            geometry=self.exposure.layer.get_geometry(),
            name=tr('Estimated buildings affected'),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'target_field': self.affected_field,
                'map_title': map_title,
                'legend_units': legend_units,
                'legend_title': legend_title,
                'buildings_total': buildings_total,
                'buildings_affected': self.total_affected_buildings},
            style_info=style_info)
        self._impact = vector_layer
        return vector_layer
