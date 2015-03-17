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

from safe.definitions import (
    hazard_flood,
    hazard_tsunami,
    unit_wetdry,
    unit_feet_depth,
    unit_metres_depth,
    layer_vector_polygon,
    exposure_structure,
    unit_building_type_type,
    hazard_definition,
    exposure_definition,
    unit_building_generic,
    layer_vector_point)
from safe.common.utilities import OrderedDict, get_osm_building_usage
from safe.impact_functions.core import (
    FunctionProvider, get_hazard_layer, get_exposure_layer, get_question)
from safe.storage.vector import Vector
from safe.storage.utilities import DEFAULT_ATTRIBUTE
from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.impact_functions.impact_function_metadata import (
    ImpactFunctionMetadata)


LOGGER = logging.getLogger('InaSAFE')


class FloodVectorBuildingImpactFunction(FunctionProvider):
    # noinspection PyUnresolvedReferences
    """Inundation vector impact on building data.

    :author Ole Nielsen, Kristy van Putten
    # this rating below is only for testing a function, not the real one
    :rating 0
    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype=='vector'

    :param requires category=='exposure' and \
                    subcategory=='structure' and \
                    layertype=='vector'
    """

    class Metadata(ImpactFunctionMetadata):
        """Metadata for Flood Building Impact Function.

        .. versionadded:: 2.1

        We only need to re-implement get_metadata(), all other behaviours
        are inherited from the abstract base class.
        """

        @staticmethod
        def get_metadata():
            """Return metadata as a dictionary.

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            dict_meta = {
                'id': 'FloodVectorBuildingImpactFunction',
                'name': tr('Flood Vector Building Impact Function'),
                'impact': tr('Be flooded'),
                'title': tr('Be flooded'),
                # should be a list, but we can do it later.
                'author': 'Ole Nielsen and Kristy van Putten',
                'date_implemented': 'N/A',
                'overview': tr(
                    'To assess the impacts of (flood or tsunami) inundation '
                    'on building footprints originating from OpenStreetMap '
                    '(OSM).'),
                'detailed_description': tr(
                    'The inundation status is calculated for each building '
                    '(using the centroid if it is a polygon) based on the '
                    'hazard levels provided. Buildings are '
                    'considered to be impacted depending on the value of '
                    'hazard attributes (in order) affected" or "FLOODPRONE": '
                    'If a building is in a region that has attribute '
                    '"affected" set to True (or 1) it is impacted. If '
                    'attribute "affected" does not exist but "FLOODPRONE" '
                    'does, then the building is considered impacted if '
                    '"FLOODPRONE" is "yes". If neither affected" nor '
                    '"FLOODPRONE" is available, a building will be impacted '
                    'if it belongs to any polygon. The latter behaviour is '
                    'implemented through the attribute "inapolygon" which is '
                    'automatically assigned.'),
                'hazard_input': tr(
                    'a vector polygon layer where each polygon represents an '
                    'inundated area. The following attributes are recognised '
                    '(in order): "affected" (True or False) or "FLOODPRONE" '
                    '(Yes or No). (True may be represented as 1, False as 0'),
                'exposure_input': tr(
                    'Vector polygon or point layer extracted from OSM where '
                    'each feature represents the footprint of a building.'),
                'output': tr(
                    'Vector layer contains building is estimated to be '
                    'flooded and the breakdown of the building by type.'),
                'actions': tr(
                    'Provide details about where critical infrastructure '
                    'might be flooded'),
                'limitations': [
                    tr('This function only flags buildings as impacted or not '
                       'either based on a fixed threshold in case of raster '
                       'hazard or the the attributes mentioned under input '
                       'in case of vector hazard.')
                ],
                'citations': [],
                'categories': {
                    'hazard': {
                        'definition': hazard_definition,
                        'subcategories': [
                            hazard_flood,
                            hazard_tsunami
                        ],
                        'units': [
                            unit_wetdry,
                            unit_metres_depth,
                            unit_feet_depth],
                        'layer_constraints': [layer_vector_polygon]
                    },
                    'exposure': {
                        'definition': exposure_definition,
                        'subcategories': [exposure_structure],
                        'units': [
                            unit_building_type_type,
                            unit_building_generic],
                        'layer_constraints': [
                            layer_vector_polygon,
                            layer_vector_point
                        ]
                    }
                }
            }
            return dict_meta

    target_field = 'INUNDATED'
    # parameters
    parameters = OrderedDict([
        ('postprocessors', OrderedDict([('BuildingType', {'on': True})]))
    ])

    def run(self, layers):
        """Flood impact to buildings (e.g. from Open Street Map).

         :param layers: List of layers expected to contain.
                * hazard_layer: Hazard raster layer of flood
                * exposure_layer: Vector layer of structure data on
                the same grid as hazard_layer
        """

        # Extract data
        hazard_layer = get_hazard_layer(layers)  # Depth
        exposure_layer = get_exposure_layer(layers)  # Building locations

        question = get_question(
            hazard_layer.get_name(),
            exposure_layer.get_name(),
            self)

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
            atts = features[i]

            # FIXME (Ole): Need to agree whether to use one or the
            # other as this can be very confusing!
            # For now look for 'affected' first
            if 'affected' in atts:
                # E.g. from flood forecast
                # Assume that building is wet if inside polygon
                # as flagged by attribute Flooded
                res = atts['affected']
                if res is None:
                    inundated_status = False
                else:
                    inundated_status = bool(res)
            elif 'FLOODPRONE' in atts:
                res = atts['FLOODPRONE']
                if res is None:
                    inundated_status = False
                else:
                    inundated_status = res.lower() == 'yes'
            elif DEFAULT_ATTRIBUTE in atts:
                # Check the default attribute assigned for points
                # covered by a polygon
                res = atts[DEFAULT_ATTRIBUTE]
                if res is None:
                    inundated_status = False
                else:
                    inundated_status = res
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
            features[i][self.target_field] = int(inundated_status)

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
        return vector_layer
