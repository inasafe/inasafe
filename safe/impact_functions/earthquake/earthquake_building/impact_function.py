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
from safe.common.utilities import get_osm_building_usage
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)
from safe.common.exceptions import KeywordNotFoundError, ZeroImpactException
import safe.messaging as m
from safe.messaging import styles

LOGGER = logging.getLogger('InaSAFE')


class EarthquakeBuildingFunction(ContinuousRHClassifiedVE,
                                 BuildingExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Earthquake impact on building data."""

    _metadata = EarthquakeBuildingMetadata()

    def __init__(self):
        super(EarthquakeBuildingFunction, self).__init__()
        self.is_nexis = False
        self.statistics_type = 'class_count'
        self.statistics_classes = [0, 1, 2, 3]
        self.structure_class_field = None

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        message.add(
            m.Heading(tr('Notes and assumptions'), **styles.INFO_STYLE))
        checklist = m.BulletedList()

        # Thresholds for mmi breakdown.
        t0 = self.parameters['low_threshold'].value
        t1 = self.parameters['medium_threshold'].value
        t2 = self.parameters['high_threshold'].value
        is_nexis = self.is_nexis

        checklist.add(tr(
            'High hazard is defined as shake levels greater '
            'than %i on the MMI scale.') % t2)

        checklist.add(tr(
            'Medium hazard is defined as shake levels '
            'between %i and %i on the MMI scale.') % (t1, t2))

        checklist.add(tr(
            'Low hazard is defined as shake levels '
            'between %i and %i on the MMI scale.') % (t0, t1))

        if is_nexis:
            checklist.add(tr(
                'Values are in units of 1 million Australian Dollars'))

        message.add(checklist)
        return message

    def run(self):
        """Earthquake impact to buildings (e.g. from OpenStreetMap)."""
        self.validate()
        self.prepare()

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

        # Extract relevant exposure data
        # Try to get the value from keyword, if not exist, it will not fail,
        # but use the old get_osm_building_usage
        try:
            structure_class_field = self.exposure.keyword(
                'structure_class_field')
        except KeywordNotFoundError:
            structure_class_field = None
        attributes = interpolate_result.get_data()

        interpolate_size = len(interpolate_result)

        # Building breakdown
        self.buildings = {}
        # Impacted building breakdown
        self.affected_buildings = OrderedDict([
            (tr('High'), {}),
            (tr('Medium'), {}),
            (tr('Low'), {})
        ])
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

            if (structure_class_field in attribute_names and
                    structure_class_field):
                usage = attributes[i].get(structure_class_field, None)
            else:
                usage = get_osm_building_usage(
                    attribute_names, attributes[i])

            if usage is None or usage == 0:
                usage = 'unknown'

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
                removed.append(i)
                continue
            attributes[i][self.target_field] = cls
            self.affected_buildings[
                category][usage][tr('Buildings Affected')] += 1
            if self.is_nexis:
                self.affected_buildings[category][usage][
                    tr('Buildings value ($M)')] += building_value / 1000000.0
                self.affected_buildings[category][usage][
                    tr('Contents value ($M)')] += contents_value / 1000000.0

        # remove uncategorized element
        removed.reverse()
        geometry = interpolate_result.get_geometry()
        for i in range(0, len(removed)):
            del attributes[removed[i]]
            del geometry[removed[i]]

        if len(attributes) < 1:
            raise ZeroImpactException()
        # Consolidate the small building usage groups < 25 to other
        self._consolidate_to_other()

        impact_table = impact_summary = self.html_report()

        # Create style
        style_classes = [dict(label=class_1['label'], value=class_1['class'],
                              colour='#ffff00', transparency=1),
                         dict(label=class_2['label'], value=class_2['class'],
                              colour='#ffaa00', transparency=1),
                         dict(label=class_3['label'], value=class_3['class'],
                              colour='#ff0000', transparency=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')

        # For printing map purpose
        map_title = tr('Building affected by earthquake')
        legend_notes = tr('The level of the impact is according to the '
                          'threshold the user input.')
        legend_units = tr('(mmi)')
        legend_title = tr('Impact level')

        # Create vector layer and return
        result_layer = Vector(
            data=attributes,
            projection=interpolate_result.get_projection(),
            geometry=geometry,
            name=tr('Estimated buildings affected'),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'map_title': map_title,
                'legend_notes': legend_notes,
                'legend_units': legend_units,
                'legend_title': legend_title,
                'target_field': self.target_field,
                'statistics_type': self.statistics_type,
                'statistics_classes': self.statistics_classes},
            style_info=style_info)

        msg = 'Created vector layer %s' % str(result_layer)
        LOGGER.debug(msg)
        self._impact = result_layer
        return result_layer
