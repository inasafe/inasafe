# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Flood Vector Impact on OSM
Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from collections import OrderedDict

import logging

from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.inundation.flood_vector_osm_building_impact\
    .metadata_definitions import FloodVectorBuildingMetadata
from safe.storage.vector import Vector
from safe.storage.utilities import DEFAULT_ATTRIBUTE
from safe.utilities.i18n import tr
from safe.common.utilities import get_osm_building_usage
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)


LOGGER = logging.getLogger('InaSAFE')


class FloodVectorBuildingFunction(ImpactFunction, BuildingExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Inundation vector impact on building data."""
    _metadata = FloodVectorBuildingMetadata()

    def __init__(self):
        """Constructor (calls ctor of base class)."""
        super(FloodVectorBuildingFunction, self).__init__()

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        return [
            {
                'content': tr('Notes'),
                'header': True
            },
            {
                'content': tr(
                    'Buildings are said to be flooded when in '
                    'regions marked as affected')
            }]

    def run(self, layers=None):
        """Flood impact to buildings (e.g. from Open Street Map).

         :param layers: List of layers expected to contain.
                * hazard_layer: Hazard raster layer of flood
                * exposure_layer: Vector layer of structure data on
                the same grid as hazard_layer
        """
        self.validate()
        self.prepare(layers)

        # Extract data
        hazard_layer = self.hazard  # Depth
        exposure_layer = self.exposure  # Building locations

        # Define the target field in the impact layer
        target_field = 'INUNDATED'

        # Get parameters from user
        affected_field = self.parameters['affected_field']
        affected_value = self.parameters['affected_value']

        # Determine attribute name for hazard levels
        hazard_attribute = None

        # Interpolate hazard level to building locations
        interpolated_layer = assign_hazard_values_to_exposure_data(
            hazard_layer, exposure_layer, attribute_name=hazard_attribute)

        # Extract relevant exposure data
        attribute_names = interpolated_layer.get_attribute_names()
        features = interpolated_layer.get_data()
        total_features = len(interpolated_layer)
        self.buildings = {}
        # The variable for regions mode
        self.affected_buildings = OrderedDict([
            (tr('Inundated'), {})
        ])
        for i in range(total_features):
            # Use interpolated polygon attribute
            feature = features[i]

            if affected_field in attribute_names:
                affected_status = feature[affected_field]
                if affected_status is None:
                    inundated_status = False
                else:
                    inundated_status = affected_status == affected_value
            elif DEFAULT_ATTRIBUTE in attribute_names:
                # Check the default attribute assigned for points
                # covered by a polygon
                affected_status = feature[DEFAULT_ATTRIBUTE]
                if affected_status is None:
                    inundated_status = False
                else:
                    inundated_status = affected_status == affected_value
            else:
                # there is no flood related attribute
                message = (
                    'No flood related attribute found in %s. I was '
                    'looking for either "affected", "FLOODPRONE" or '
                    '"inapolygon". The latter should have been '
                    'automatically set by call to '
                    'assign_hazard_values_to_exposure_data(). Sorry I '
                    'can\'t help more.')
                raise Exception(message)

            # Add calculated impact to existing attributes
            features[i][target_field] = int(inundated_status)

            # Count affected buildings by usage type if available
            usage = get_osm_building_usage(attribute_names, features[i])
            if usage is None or usage == 0:
                usage = 'unknown'

            if usage not in self.buildings:
                self.buildings[usage] = 0
                for category in self.affected_buildings.keys():
                    self.affected_buildings[category][
                        usage] = OrderedDict([
                            (tr('Buildings Affected'), 0)])

            # Count all buildings by type
            self.buildings[usage] += 1
            if inundated_status is True:
                self.affected_buildings[tr('Inundated')][usage][
                    tr('Buildings Affected')] += 1

        # Lump small entries and 'unknown' into 'other' category
        self._consolidate_to_other()

        # Prepare impact layer
        map_title = tr('Buildings inundated')
        legend_title = tr('Structure inundated status')
        impact_table = impact_summary = self.generate_html_report()
        style_classes = [
            dict(
                label=tr('Not Inundated'),
                value=0,
                colour='#1EFC7C',
                transparency=0,
                size=1),
            dict(
                label=tr('Inundated'),
                value=1,
                colour='#F31A1C',
                ztransparency=0, size=1)]
        legend_units = tr('(inundated or not inundated)')

        style_info = dict(target_field=target_field,
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
                'target_field': target_field,
                'map_title': map_title,
                'legend_units': legend_units,
                'legend_title': legend_title,
                'buildings_total': self.total_buildings,
                'buildings_affected': self.total_affected_buildings},
            style_info=style_info)
        self._impact = vector_layer
        return vector_layer
