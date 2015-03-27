# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Flood Vector Impact on OSM
Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import logging

from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.inundation.flood_vector_osm_building_impact\
    .metadata_definitions import FloodVectorBuildingMetadata
from safe.storage.vector import Vector
from safe.storage.utilities import DEFAULT_ATTRIBUTE
from safe.utilities.i18n import tr
from safe.common.utilities import format_int, get_osm_building_usage
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import assign_hazard_values_to_exposure_data


LOGGER = logging.getLogger('InaSAFE')


class FloodVectorBuildingFunction(ImpactFunction):
    # noinspection PyUnresolvedReferences
    """Inundation vector impact on building data."""
    _metadata = FloodVectorBuildingMetadata()

    def __init__(self):
        """Constructor (calls ctor of base class)."""
        super(FloodVectorBuildingFunction, self).__init__()

    def _tabulate(self, affected_buildings, affected_count, attribute_names,
                  buildings, question, total_features):
        # Generate simple impact report
        table_body = [
            question,
            TableRow([tr('Building type'),
                      tr('Number flooded'),
                      tr('Total')], header=True),
            TableRow([tr('All'),
                      format_int(affected_count),
                      format_int(total_features)])]
        school_closed = 0
        hospital_closed = 0
        # Generate break down by building usage type if available
        list_type_attribute = [
            'TYPE', 'type', 'amenity', 'building_t', 'office',
            'tourism', 'leisure', 'building']
        intersect_type = set(attribute_names) & set(list_type_attribute)
        if len(intersect_type) > 0:
            # Make list of building types
            building_list = []
            for usage in buildings:
                building_type = usage.replace('_', ' ')

                # Lookup internationalised value if available
                building_type = tr(building_type)
                building_list.append([
                    building_type.capitalize(),
                    format_int(affected_buildings[usage]),
                    format_int(buildings[usage])])

                if usage.lower() == 'school':
                    school_closed = affected_buildings[usage]
                if usage.lower() == 'hospital':
                    hospital_closed = affected_buildings[usage]

            # Sort alphabetically
            building_list.sort()

            table_body.append(TableRow(tr('Breakdown by building type'),
                                       header=True))
            for row in building_list:
                s = TableRow(row)
                table_body.append(s)

        # Action Checklist Section
        table_body.append(TableRow(tr('Action Checklist:'), header=True))
        table_body.append(TableRow(
            tr('Are the critical facilities still open?')))
        table_body.append(TableRow(
            tr('Which structures have warning capacity (eg. sirens, speakers, '
               'etc.)?')))
        table_body.append(TableRow(
            tr('Which buildings will be evacuation centres?')))
        table_body.append(TableRow(
            tr('Where will we locate the operations centre?')))
        table_body.append(TableRow(
            tr('Where will we locate warehouse and/or distribution centres?')))
        if school_closed > 0:
            table_body.append(TableRow(
                tr('Where will the students from the %s closed schools go to '
                   'study?') % format_int(school_closed)))
        if hospital_closed > 0:
            table_body.append(TableRow(
                tr('Where will the patients from the %s closed hospitals go '
                   'for treatment and how will we transport them?') %
                format_int(hospital_closed)))

        # Notes Section
        table_body.append(TableRow(tr('Notes'), header=True))
        table_body.append(TableRow(
            tr('Buildings are said to be flooded when in regions marked '
               'as affected')))
        return table_body

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

        # Get question
        question = self.question()

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
        buildings = {}

        # The number of affected buildings
        affected_count = 0

        # The variable for regions mode
        affected_buildings = {}
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

            # Count affected buildings by usage type if available
            usage = get_osm_building_usage(attribute_names, features[i])
            if usage is not None and usage != 0:
                key = usage
            else:
                key = 'unknown'

            if key not in buildings:
                buildings[key] = 0
                affected_buildings[key] = 0

            # Count all buildings by type
            buildings[key] += 1
            if inundated_status is True:
                # Count affected buildings by type
                affected_buildings[key] += 1
                # Count total affected buildings
                affected_count += 1

            # Add calculated impact to existing attributes
            features[i][target_field] = int(inundated_status)

        # Lump small entries and 'unknown' into 'other' category
        for usage in buildings.keys():
            x = buildings[usage]
            if x < 25 or usage == 'unknown':
                if 'other' not in buildings:
                    buildings['other'] = 0
                    affected_buildings['other'] = 0

                buildings['other'] += x
                affected_buildings['other'] += affected_buildings[usage]
                del buildings[usage]
                del affected_buildings[usage]

        table_body = self._tabulate(affected_buildings, affected_count,
                                    attribute_names, buildings, question,
                                    total_features)

        # Result
        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary

        # Prepare impact layer
        map_title = tr('Buildings inundated')
        legend_title = tr('Structure inundated status')

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
                'buildings_total': total_features,
                'buildings_affected': affected_count},
            style_info=style_info)
        self._impact = vector_layer
        return vector_layer
