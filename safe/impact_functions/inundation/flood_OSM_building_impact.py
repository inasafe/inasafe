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
    unit_building_generic)
from safe.common.utilities import OrderedDict
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
                        'subcategory': [
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
                        'subcategory': exposure_structure,
                        'units': [
                            unit_building_type_type,
                            unit_building_generic],
                        'layer_constraints': [layer_vector_polygon]
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
        'Vector polygon layer extracted from OSM where each polygon '
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
                * my_hazard: Hazard layer of flood
                * my_exposure: Vector layer of structure data on
                the same grid as my_hazard
        """
        threshold = self.parameters['threshold [m]']  # Flood threshold [m]

        verify(isinstance(threshold, float),
               'Expected thresholds to be a float. Got %s' % str(threshold))

        # Extract data
        my_hazard = get_hazard_layer(layers)  # Depth
        my_exposure = get_exposure_layer(layers)  # Building locations

        question = get_question(
            my_hazard.get_name(),
            my_exposure.get_name(),
            self)

        # Determine attribute name for hazard levels
        if my_hazard.is_raster:
            mode = 'grid'
            hazard_attribute = 'depth'
        else:
            mode = 'regions'
            hazard_attribute = None

        # Interpolate hazard level to building locations
        I = assign_hazard_values_to_exposure_data(
            my_hazard, my_exposure, attribute_name=hazard_attribute)

        # Extract relevant exposure data
        attribute_names = I.get_attribute_names()
        attributes = I.get_data()
        N = len(I)
        # Calculate building impact
        count = 0
        buildings = {}
        affected_buildings = {}
        for i in range(N):
            if mode == 'grid':
                # Get the interpolated depth
                x = float(attributes[i]['depth'])
                x = x >= threshold
            elif mode == 'regions':
                # Use interpolated polygon attribute
                atts = attributes[i]

                # FIXME (Ole): Need to agree whether to use one or the
                # other as this can be very confusing!
                # For now look for 'affected' first
                if 'affected' in atts:
                    # E.g. from flood forecast
                    # Assume that building is wet if inside polygon
                    # as flagged by attribute Flooded
                    res = atts['affected']
                    if res is None:
                        x = False
                    else:
                        x = bool(res)

                elif 'FLOODPRONE' in atts:
                    res = atts['FLOODPRONE']
                    if res is None:
                        x = False
                    else:
                        x = res.lower() == 'yes'
                elif DEFAULT_ATTRIBUTE in atts:
                    # Check the default attribute assigned for points
                    # covered by a polygon
                    res = atts[DEFAULT_ATTRIBUTE]
                    if res is None:
                        x = False
                    else:
                        x = res
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
            else:
                message = (tr(
                    'Unknown hazard type %s. Must be either "depth" or "grid"')
                    % mode)
                raise Exception(message)

            # Count affected buildings by usage type if available
            if 'type' in attribute_names:
                usage = attributes[i]['type']
            elif 'TYPE' in attribute_names:
                usage = attributes[i]['TYPE']
            else:
                usage = None
            if 'amenity' in attribute_names and (usage is None or usage == 0):
                usage = attributes[i]['amenity']
            if 'building_t' in attribute_names and (usage is None
                                                    or usage == 0):
                usage = attributes[i]['building_t']
            if 'office' in attribute_names and (usage is None or usage == 0):
                usage = attributes[i]['office']
            if 'tourism' in attribute_names and (usage is None or usage == 0):
                usage = attributes[i]['tourism']
            if 'leisure' in attribute_names and (usage is None or usage == 0):
                usage = attributes[i]['leisure']
            if 'building' in attribute_names and (usage is None or usage == 0):
                usage = attributes[i]['building']
                if usage == 'yes':
                    usage = 'building'

            if usage is not None and usage != 0:
                key = usage
            else:
                key = 'unknown'

            if key not in buildings:
                buildings[key] = 0
                affected_buildings[key] = 0

            # Count all buildings by type
            buildings[key] += 1
            if x is True:
                # Count affected buildings by type
                affected_buildings[key] += 1

                # Count total affected buildings
                count += 1

            # Add calculated impact to existing attributes
            attributes[i][self.target_field] = int(x)

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
            TableRow([tr('Building type'), tr('Number flooded'),
                      tr('Total')], header=True),
            TableRow([tr('All'), format_int(count), format_int(N)])]

        school_closed = 0
        hospital_closed = 0
        # Generate break down by building usage type is available
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
                if building_type == 'school':
                    school_closed = affected_buildings[usage]
                if building_type == 'hospital':
                    hospital_closed = affected_buildings[usage]

            # Sort alphabetically
            building_list.sort()

            table_body.append(TableRow(tr('Breakdown by building type'),
                                       header=True))
            for row in building_list:
                s = TableRow(row)
                table_body.append(s)

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

        table_body.append(TableRow(tr('Notes'), header=True))
        assumption = tr('Buildings are said to be flooded when ')
        if mode == 'grid':
            assumption += tr('flood levels exceed %.1f m') % threshold
        else:
            assumption += tr('in regions marked as affected')
        table_body.append(assumption)

        # Result
        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary

        # Create style
        style_classes = [dict(label=tr('Not Inundated'), value=0,
                              colour='#1EFC7C', transparency=0, size=1),
                         dict(label=tr('Inundated'), value=1,
                              colour='#F31A1C', transparency=0, size=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')

        # For printing map purpose
        map_title = tr('Buildings inundated')
        legend_units = tr('(inundated or not inundated)')
        legend_title = tr('Structure inundated status')

        # Create vector layer and return
        vector_layer = Vector(
            data=attributes,
            projection=I.get_projection(),
            geometry=I.get_geometry(),
            name=tr('Estimated buildings affected'),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'target_field': self.target_field,
                'map_title': map_title,
                'legend_units': legend_units,
                'legend_title': legend_title,
                'buildings_total': N,
                'buildings_affected': count},
            style_info=style_info)
        return vector_layer
