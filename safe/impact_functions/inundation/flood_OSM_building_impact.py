# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Flood Impact on OSM
Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe.metadata import (
    hazard_flood,
    hazard_tsunami,
    unit_wetdry,
    unit_feet_depth,
    unit_metres_depth,
    layer_vector_polygon,
    layer_raster_numeric,
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
from safe.common.utilities import ugettext as tr, format_int, verify
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.impact_functions.impact_function_metadata import (
    ImpactFunctionMetadata)
import logging

LOGGER = logging.getLogger('InaSAFE')


class FloodBuildingImpactFunction(FunctionProvider):
    # noinspection PyUnresolvedReferences
    """Inundation impact on building data.

    :author Ole Nielsen, Kristy van Putten
    # this rating below is only for testing a function, not the real one
    :rating 0
    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami']

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
                'id': 'FloodBuildingImpactFunction',
                'name': tr('Flood Building Impact Function'),
                'impact': tr('Be flooded'),
                'author': ['Ole Nielsen', 'Kristy van Putten'],
                'date_implemented': 'N/A',
                'overview': tr(
                    'To assess the impacts of (flood or tsunami) inundation '
                    'on building footprints originating from OpenStreetMap '
                    '(OSM).'),
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
                        'layer_constraints': [
                            layer_vector_polygon,
                            layer_raster_numeric,
                        ]
                    },
                    'exposure': {
                        'definition': exposure_definition,
                        'subcategories': [exposure_structure],
                        'units': [
                            unit_building_type_type,
                            unit_building_generic],
                        'layer_constraints': [
                            layer_vector_polygon,
                            layer_vector_point]
                    }
                }
            }
            return dict_meta

    # Function documentation
    target_field = 'INUNDATED'
    title = tr('Be flooded')
    synopsis = tr(
        'To assess the impacts of (flood or tsunami) inundation on building '
        'footprints originating from OpenStreetMap (OSM).')
    actions = tr(
        'Provide details about where critical infrastructure might be flooded')
    detailed_description = tr(
        'The inundation status is calculated for each building (using the '
        'centroid if it is a polygon) based on the hazard levels provided. if '
        'the hazard is given as a raster a threshold of 1 meter is used. This '
        'is configurable through the InaSAFE interface. If the hazard is '
        'given as a vector polygon layer buildings are considered to be '
        'impacted depending on the value of hazard attributes (in order) '
        '"affected" or "FLOODPRONE": If a building is in a region that has '
        'attribute "affected" set to True (or 1) it is impacted. If attribute '
        '"affected" does not exist but "FLOODPRONE" does, then the building '
        'is considered impacted if "FLOODPRONE" is "yes". If neither '
        '"affected" nor "FLOODPRONE" is available, a building will be '
        'impacted if it belongs to any polygon. The latter behaviour is '
        'implemented through the attribute "inapolygon" which is automatically'
        ' assigned.')
    hazard_input = tr(
        'A hazard raster layer where each cell represents flood depth (in '
        'meters), or a vector polygon layer where each polygon represents an '
        'inundated area. In the latter case, the following attributes are '
        'recognised (in order): "affected" (True or False) or "FLOODPRONE" '
        '(Yes or No). (True may be represented as 1, False as 0')
    exposure_input = tr(
        'Vector polygon or point layer extracted from OSM where each feature '
        'represents the footprint of a building.')
    output = tr(
        'Vector layer contains building is estimated to be flooded and the '
        'breakdown of the building by type.')
    limitation = tr(
        'This function only flags buildings as impacted or not either based '
        'on a fixed threshold in case of raster hazard or the the attributes '
        'mentioned under input in case of vector hazard.')

    # parameters
    parameters = OrderedDict([
        ('threshold [m]', 1.0),
        ('postprocessors', OrderedDict([('BuildingType', {'on': True})]))
    ])

    def run(self, layers):
        """Flood impact to buildings (e.g. from Open Street Map).

         :param layers: List of layers expected to contain.
                * hazard_layer: Hazard layer of flood
                * exposure_layer: Vector layer of structure data on
                the same grid as hazard_layer
        """
        threshold = self.parameters['threshold [m]']  # Flood threshold [m]

        verify(isinstance(threshold, float),
               'Expected thresholds to be a float. Got %s' % str(threshold))

        # Extract data
        hazard_layer = get_hazard_layer(layers)  # Depth
        exposure_layer = get_exposure_layer(layers)  # Building locations

        question = get_question(
            hazard_layer.get_name(),
            exposure_layer.get_name(),
            self)

        # Determine attribute name for hazard levels
        if hazard_layer.is_raster:
            mode = 'grid'
            hazard_attribute = 'depth'
        else:
            mode = 'regions'
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

        # The variable for grid mode
        inundated_count = 0
        wet_count = 0
        dry_count = 0
        inundated_buildings = {}
        wet_buildings = {}
        dry_buildings = {}

        # The variable for regions mode
        affected_buildings = {}

        if mode == 'grid':
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
        elif mode == 'regions':
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
        else:
            message = (tr('Unknown hazard type %s. Must be either "depth" or '
                          '"grid"') % mode)
            raise Exception(message)

        if mode == 'grid':
            affected_count = inundated_count + wet_count

        # Lump small entries and 'unknown' into 'other' category
        for usage in buildings.keys():
            x = buildings[usage]
            if x < 25 or usage == 'unknown':
                if 'other' not in buildings:
                    buildings['other'] = 0
                    if mode == 'grid':
                        inundated_buildings['other'] = 0
                        wet_buildings['other'] = 0
                        dry_buildings['other'] = 0
                    elif mode == 'regions':
                        affected_buildings['other'] = 0

                buildings['other'] += x
                if mode == 'grid':
                    inundated_buildings['other'] += inundated_buildings[usage]
                    wet_buildings['other'] += wet_buildings[usage]
                    dry_buildings['other'] += dry_buildings[usage]
                    del buildings[usage]
                    del inundated_buildings[usage]
                    del wet_buildings[usage]
                    del dry_buildings[usage]
                elif mode == 'regions':
                    affected_buildings['other'] += affected_buildings[usage]
                    del buildings[usage]
                    del affected_buildings[usage]

        # Generate simple impact report
        table_body = []
        if mode == 'grid':
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
        elif mode == 'regions':
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
                if mode == 'grid':
                    building_list.append([
                        building_type.capitalize(),
                        format_int(inundated_buildings[usage]),
                        format_int(wet_buildings[usage]),
                        format_int(dry_buildings[usage]),
                        format_int(buildings[usage])])
                elif mode == 'regions':
                    building_list.append([
                        building_type.capitalize(),
                        format_int(affected_buildings[usage]),
                        format_int(buildings[usage])])

                if usage.lower() == 'school':
                    school_closed = 0
                    if mode == 'grid':
                        school_closed += inundated_buildings[usage]
                        school_closed += wet_buildings[usage]
                    elif mode == 'regions':
                        school_closed = affected_buildings[usage]
                if usage.lower() == 'hospital':
                    hospital_closed = 0
                    if mode == 'grid':
                        hospital_closed += inundated_buildings[usage]
                        hospital_closed += wet_buildings[usage]
                    elif mode == 'regions':
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
        if mode == 'grid':
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
        else:
            table_body.append(TableRow(
                tr('Buildings are said to be flooded when in regions marked '
                   'as affected')))

        # Result
        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary

        # Prepare impact layer
        map_title = tr('Buildings inundated')
        legend_title = tr('Structure inundated status')
        legend_units = ''
        style_classes = []

        if mode == 'grid':
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
        elif mode == 'regions':
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
