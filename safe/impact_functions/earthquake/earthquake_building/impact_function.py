# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Earthquake Impact Function
on Building.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'lucernae'
__date__ = '24/03/15'

import logging
from collections import OrderedDict
from safe.impact_functions.bases.continuous_rh_classified_ve import \
    ContinuousRHClassifiedVE
from safe.impact_functions.earthquake.earthquake_building \
    .metadata_definitions import EarthquakeBuildingMetadata
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.utilities.utilities import main_type
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)
from safe.common.exceptions import ZeroImpactException

LOGGER = logging.getLogger('InaSAFE')


class EarthquakeBuildingFunction(
        ContinuousRHClassifiedVE,
        BuildingExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Earthquake impact on building data.

    This IF is the only Building ong which doesn't use
    """

    _metadata = EarthquakeBuildingMetadata()

    def __init__(self):
        super(EarthquakeBuildingFunction, self).__init__()
        BuildingExposureReportMixin.__init__(self)
        self.is_nexis = False
        self.structure_class_field = None

    def notes(self):
        """Return the notes section of the report as dict.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        # Thresholds for mmi breakdown.
        t0 = self.parameters['low_threshold'].value
        t1 = self.parameters['medium_threshold'].value
        t2 = self.parameters['high_threshold'].value
        is_nexis = self.is_nexis

        fields = [
            tr('High hazard is defined as shake levels greater than %i on '
               'the MMI scale.') % t2,
            tr('Medium hazard is defined as shake levels between %i and %i on '
               'the MMI scale.') % (t1, t2),
            tr('Low hazard is defined as shake levels between %i and %i on '
               'the MMI scale.') % (t0, t1)
        ]

        if is_nexis:
            fields.append(tr(
                'Values are in units of 1 million Australian Dollars'))
        # include any generic exposure specific notes from definitions
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions
        fields = fields + self.hazard_notes()
        return fields

    def run(self):
        """Earthquake impact to buildings (e.g. from OpenStreetMap)."""

        LOGGER.debug('Running earthquake building impact')

        # merely initialize
        building_value = 0
        contents_value = 0

        # Thresholds for mmi breakdown.
        t0 = self.parameters['low_threshold'].value
        t1 = self.parameters['medium_threshold'].value
        t2 = self.parameters['high_threshold'].value

        # Class Attribute and Label.
        class_1 = {'label': tr('Low'), 'class': 1}
        class_2 = {'label': tr('Medium'), 'class': 2}
        class_3 = {'label': tr('High'), 'class': 3}

        # Define attribute name for hazard levels.
        hazard_attribute = 'mmi'

        # Determine if exposure data have NEXIS attributes.
        attribute_names = self.exposure.layer.get_attribute_names()
        if (
                'FLOOR_AREA' in attribute_names and
                'BUILDING_C' in attribute_names and
                'CONTENTS_C' in attribute_names):
            self.is_nexis = True
        else:
            self.is_nexis = False

        # Interpolate hazard level to building locations.
        interpolate_result = assign_hazard_values_to_exposure_data(
            self.hazard.layer,
            self.exposure.layer,
            attribute_name=hazard_attribute
        )

        # Get parameters from layer's keywords
        structure_class_field = self.exposure.keyword('structure_class_field')
        exposure_value_mapping = self.exposure.keyword('value_mapping')
        attributes = interpolate_result.get_data()

        interpolate_size = len(interpolate_result)

        hazard_classes = [tr('Low'), tr('Medium'), tr('High')]
        self.init_report_var(hazard_classes)

        removed = []
        for i in range(interpolate_size):
            # Classify building according to shake level
            # and calculate dollar losses

            if self.is_nexis:
                try:
                    area = float(attributes[i]['FLOOR_AREA'])
                except (ValueError, KeyError):
                    # print 'Got area', attributes[i]['FLOOR_AREA']
                    area = 0.0

                try:
                    building_value_density = float(attributes[i]['BUILDING_C'])
                except (ValueError, KeyError):
                    # print 'Got bld value', attributes[i]['BUILDING_C']
                    building_value_density = 0.0

                try:
                    contents_value_density = float(attributes[i]['CONTENTS_C'])
                except (ValueError, KeyError):
                    # print 'Got cont value', attributes[i]['CONTENTS_C']
                    contents_value_density = 0.0

                building_value = building_value_density * area
                contents_value = contents_value_density * area

            usage = attributes[i].get(structure_class_field, None)
            usage = main_type(usage, exposure_value_mapping)

            if usage not in self.buildings:
                self.buildings[usage] = 0
                for category in self.affected_buildings.keys():
                    if self.is_nexis:
                        self.affected_buildings[category][usage] = OrderedDict(
                            [
                                (tr('Buildings Affected'), 0),
                                (tr('Buildings value ($M)'), 0),
                                (tr('Contents value ($M)'), 0)])
                    else:
                        self.affected_buildings[category][usage] = \
                            OrderedDict([(tr('Buildings Affected'), 0)])
            self.buildings[usage] += 1
            try:
                mmi = float(attributes[i][hazard_attribute])  # MMI
            except TypeError:
                mmi = 0.0
            if t0 <= mmi < t1:
                cls = 1
                category = tr('Low')
            elif t1 <= mmi < t2:
                cls = 2
                category = tr('Medium')
            elif t2 <= mmi:
                cls = 3
                category = tr('High')
            else:
                # Not reported for less than level t0
                # RMN: We still need to add target_field attribute
                # So, set it to None
                attributes[i][self.target_field] = None
                continue

            attributes[i][self.target_field] = cls
            self.affected_buildings[
                category][usage][tr('Buildings Affected')] += 1
            if self.is_nexis:
                self.affected_buildings[category][usage][
                    tr('Buildings value ($M)')] += building_value / 1000000.0
                self.affected_buildings[category][usage][
                    tr('Contents value ($M)')] += contents_value / 1000000.0

        self.reorder_dictionaries()

        # remove un-categorized element
        removed.reverse()
        geometry = interpolate_result.get_geometry()
        for i in range(0, len(removed)):
            del attributes[removed[i]]
            del geometry[removed[i]]

        if len(attributes) < 1:
            raise ZeroImpactException()

        # Create style
        style_classes = [
            dict(
                label=class_1['label'],
                value=class_1['class'],
                colour='#ffff00',
                transparency=1),
            dict(
                label=class_2['label'],
                value=class_2['class'],
                colour='#ffaa00',
                transparency=1),
            dict(
                label=class_3['label'],
                value=class_3['class'],
                colour='#ff0000',
                transparency=1)]
        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol'
        )

        impact_data = self.generate_data()

        extra_keywords = {
            'map_title': self.map_title(),
            'legend_notes': self.metadata().key('legend_notes'),
            'legend_units': self.metadata().key('legend_units'),
            'legend_title': self.metadata().key('legend_title'),
            'target_field': self.target_field,
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create vector layer and return
        impact_layer = Vector(
            data=attributes,
            projection=interpolate_result.get_projection(),
            geometry=geometry,
            name=self.map_title(),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
