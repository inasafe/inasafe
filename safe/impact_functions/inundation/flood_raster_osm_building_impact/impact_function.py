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

from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.inundation\
    .flood_raster_osm_building_impact.metadata_definitions import \
    FloodRasterBuildingMetadata
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.common.utilities import format_int, get_osm_building_usage, verify
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import assign_hazard_values_to_exposure_data


LOGGER = logging.getLogger('InaSAFE')


class FloodRasterBuildingImpactFunction(ImpactFunction):
    # noinspection PyUnresolvedReferences
    """Inundation raster impact on building data."""
    _metadata = FloodRasterBuildingMetadata()

    def __init__(self):
        """Constructor (calls ctor of base class)."""
        super(FloodRasterBuildingImpactFunction, self).__init__()
        self.target_field = 'INUNDATED'

    def _tabulate(self, attribute_names, buildings, dry_buildings, dry_count,
                  inundated_buildings, inundated_count, question, threshold,
                  total_features, wet_buildings, wet_count):
        table_body = [
            question,
            TableRow([tr('Building type'),
                      tr('Number Inundated'),
                      tr('Number of Wet Buildings'),
                      tr('Number of Dry Buildings'),
                      tr('Total')], header=True),
            TableRow(
                [tr('All'),
                 format_int(inundated_count),
                 format_int(wet_count),
                 format_int(dry_count),
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
                    format_int(inundated_buildings[usage]),
                    format_int(wet_buildings[usage]),
                    format_int(dry_buildings[usage]),
                    format_int(buildings[usage])])

                if usage.lower() == 'school':
                    school_closed = 0
                    school_closed += inundated_buildings[usage]
                    school_closed += wet_buildings[usage]
                if usage.lower() == 'hospital':
                    hospital_closed = 0
                    hospital_closed += inundated_buildings[usage]
                    hospital_closed += wet_buildings[usage]

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
            tr('Buildings are said to be inundated when flood levels '
               'exceed %.1f m') % threshold))
        table_body.append(TableRow(
            tr('Buildings are said to be wet when flood levels '
               'are greater than 0 m but less than %.1f m') % threshold))
        table_body.append(TableRow(
            tr('Buildings are said to be dry when flood levels '
               'are less than 0 m')))
        table_body.append(TableRow(
            tr('Buildings are said to be closed if they are inundated or '
               'wet')))
        table_body.append(TableRow(
            tr('Buildings are said to be open if they are dry')))
        return table_body

    def run(self, layers=None):
        """Flood impact to buildings (e.g. from Open Street Map).

         :param layers: List of layers expected to contain.
                * hazard_layer: Hazard raster layer of flood
                * exposure_layer: Vector layer of structure data on
                the same grid as hazard_layer
        """
        self.prepare(layers)
        threshold = self.parameters['threshold [m]']  # Flood threshold [m]

        verify(isinstance(threshold, float),
               'Expected thresholds to be a float. Got %s' % str(threshold))

        # Extract data
        hazard_layer = self.hazard  # Depth
        exposure_layer = self.exposure  # Building locations

        question = self.question()

        # Determine attribute name for hazard levels
        hazard_attribute = 'depth'

        # Interpolate hazard level to building locations
        interpolated_layer = assign_hazard_values_to_exposure_data(
            hazard_layer, exposure_layer, attribute_name=hazard_attribute)

        # Extract relevant exposure data
        attribute_names = interpolated_layer.get_attribute_names()
        features = interpolated_layer.get_data()
        total_features = len(interpolated_layer)
        buildings = {}

        # The number of affected buildings

        # The variable for grid mode
        inundated_count = 0
        wet_count = 0
        dry_count = 0
        inundated_buildings = {}
        wet_buildings = {}
        dry_buildings = {}

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
            if usage is not None and usage != 0:
                key = usage
            else:
                key = 'unknown'

            if key not in buildings:
                buildings[key] = 0
                inundated_buildings[key] = 0
                wet_buildings[key] = 0
                dry_buildings[key] = 0

            # Count all buildings by type
            buildings[key] += 1
            if inundated_status is 0:
                # Count dry buildings by type
                dry_buildings[key] += 1
                # Count total dry buildings
                dry_count += 1
            if inundated_status is 1:
                # Count inundated buildings by type
                inundated_buildings[key] += 1
                # Count total dry buildings
                inundated_count += 1
            if inundated_status is 2:
                # Count wet buildings by type
                wet_buildings[key] += 1
                # Count total wet buildings
                wet_count += 1
            # Add calculated impact to existing attributes
            features[i][self.target_field] = inundated_status

        affected_count = inundated_count + wet_count

        # Lump small entries and 'unknown' into 'other' category
        for usage in buildings.keys():
            x = buildings[usage]
            if x < 25 or usage == 'unknown':
                if 'other' not in buildings:
                    buildings['other'] = 0
                    inundated_buildings['other'] = 0
                    wet_buildings['other'] = 0
                    dry_buildings['other'] = 0

                buildings['other'] += x
                inundated_buildings['other'] += inundated_buildings[usage]
                wet_buildings['other'] += wet_buildings[usage]
                dry_buildings['other'] += dry_buildings[usage]
                del buildings[usage]
                del inundated_buildings[usage]
                del wet_buildings[usage]
                del dry_buildings[usage]

        # Generate simple impact report
        table_body = self._tabulate(attribute_names, buildings, dry_buildings,
                                    dry_count, inundated_buildings,
                                    inundated_count, question, threshold,
                                    total_features, wet_buildings, wet_count)

        # Result
        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary

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
                'buildings_affected': affected_count},
            style_info=style_info)
        self._impact = vector_layer
        return vector_layer
