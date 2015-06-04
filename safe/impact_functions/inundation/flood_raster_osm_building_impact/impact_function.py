# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Flood Raster Impact on OSM
Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'lucernae'

import logging
from collections import OrderedDict

from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.inundation\
    .flood_raster_osm_building_impact.metadata_definitions import \
    FloodRasterBuildingMetadata
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.common.utilities import get_osm_building_usage, verify
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)

LOGGER = logging.getLogger('InaSAFE')


class FloodRasterBuildingFunction(ImpactFunction, BuildingExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Inundation raster impact on building data."""
    _metadata = FloodRasterBuildingMetadata()

    def __init__(self):
        """Constructor (calls ctor of base class)."""
        super(FloodRasterBuildingFunction, self).__init__()

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        threshold = self.parameters['threshold [m]']
        return [
            {
                'content': tr('Notes'),
                'header': True
            },
            {
                'content': tr(
                    'Buildings are said to be inundated when flood levels '
                    'exceed %.1f m') % threshold
            },
            {
                'content': tr(
                    'Buildings are said to be wet when flood levels '
                    'are greater than 0 m but less than %.1f m') % threshold
            },
            {
                'content': tr(
                    'Buildings are said to be dry when flood levels '
                    'are 0 m or less.')
            },
            {
                'content': tr(
                    'Buildings are said to be closed if they are '
                    'inundated or wet.')
            },
            {
                'content': tr(
                    'Buildings are said to be open if they are dry.')
            }]

    @property
    def _affected_categories(self):
        """Overwriting the affected categories, since 'unaffected' are counted.

        :returns: The categories that equal effected.
        :rtype: list
        """
        return [tr('Number Inundated'), tr('Number of Wet Buildings')]

    def run(self, layers=None):
        """Flood impact to buildings (e.g. from Open Street Map).

         :param layers: List of layers expected to contain.
                * hazard_layer: Hazard raster layer of flood
                * exposure_layer: Vector layer of structure data on
                the same grid as hazard_layer
        """
        self.validate()
        self.prepare(layers)

        threshold = self.parameters['threshold [m]']  # Flood threshold [m]

        verify(isinstance(threshold, float),
               'Expected thresholds to be a float. Got %s' % str(threshold))

        # Extract data
        hazard_layer = self.hazard  # Depth
        exposure_layer = self.exposure  # Building locations

        # Determine attribute name for hazard levels
        hazard_attribute = 'depth'

        # Interpolate hazard level to building locations
        interpolated_layer = assign_hazard_values_to_exposure_data(
            hazard_layer, exposure_layer, attribute_name=hazard_attribute)

        # Extract relevant exposure data
        attribute_names = interpolated_layer.get_attribute_names()
        features = interpolated_layer.get_data()
        total_features = len(interpolated_layer)

        # Building breakdown
        self.buildings = {}
        # Impacted building breakdown
        self.affected_buildings = OrderedDict([
            (tr('Number Inundated'), {}),
            (tr('Number of Wet Buildings'), {}),
            (tr('Number of Dry Buildings'), {})
        ])
        for i in range(total_features):
            # Get the interpolated depth
            water_depth = float(features[i]['depth'])
            if water_depth <= 0:
                inundated_status = 0  # dry
            elif water_depth >= threshold:
                inundated_status = 1  # inundated
            else:
                inundated_status = 2  # wet

            # Count affected buildings by usage type if available
            usage = get_osm_building_usage(attribute_names, features[i])
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
            category = [
                tr('Number of Dry Buildings'),
                tr('Number of Wet Buildings'),
                tr('Number Inundated')][inundated_status]
            self.affected_buildings[category][usage][
                tr('Buildings Affected')] += 1

        # Lump small entries and 'unknown' into 'other' category
        self._consolidate_to_other()
        # Generate simple impact report
        impact_table = impact_summary = self.generate_html_report()

        # Prepare impact layer
        map_title = tr('Buildings inundated')
        legend_title = tr('Structure inundated status')

        style_classes = [
            dict(
                label=tr('Dry (<= 0 m)'),
                value=0,
                colour='#1EFC7C',
                transparency=0,
                size=1
            ),
            dict(
                label=tr('Wet (0 m - %.1f m)') % threshold,
                value=2,
                colour='#FF9900',
                transparency=0,
                size=1
            ),
            dict(
                label=tr('Inundated (>= %.1f m)') % threshold,
                value=1,
                colour='#F31A1C',
                transparency=0,
                size=1
            )]
        legend_units = tr('(inundated, wet, or dry)')

        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')

        # Create vector layer and return
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
                'legend_units': legend_units,
                'legend_title': legend_title,
                'buildings_total': total_features,
                'buildings_affected': self.total_affected_buildings},
            style_info=style_info)
        self._impact = vector_layer
        return vector_layer
