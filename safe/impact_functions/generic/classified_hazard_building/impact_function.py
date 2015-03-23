# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Impact on OSM
Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'lucernae'
__date__ = '23/03/15'

import logging
from numpy import round as numpy_round

from safe.storage.vector import Vector
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.common.tables import Table, TableRow
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.generic.classified_hazard_building.metadata_definitions import \
    ClassifiedHazardBuildingMetadata


LOGGER = logging.getLogger('InaSAFE')


class ClassifiedHazardBuildingImpactFunction(ImpactFunction):
    """Impact plugin for classified hazard impact on building data"""
    
    _metadata = ClassifiedHazardBuildingMetadata()
    # Function documentation
    target_field = 'DAMAGED'
    affected_field = 'affected'

    def __init__(self):
        super(ClassifiedHazardBuildingImpactFunction, self).__init__()

    def _tabulate(self, N, affected_buildings, attribute_names, buildings,
                  count, count1, count2, count3, question):
        # Lump small entries and 'unknown' into 'other' category

        # Generate impact summary
        table_body = [question,
                      TableRow([tr('Hazard Level'),
                                tr('Number of Buildings')], header=True),
                      TableRow([tr('High Hazard Class'),
                                format_int(count3)]),
                      TableRow([tr('Medium Hazard Class'),
                                format_int(count2)]),
                      TableRow([tr('Low Hazard Class'),
                                format_int(count1)]),
                      TableRow([tr('Total Buildings Affected'),
                                format_int(count1 + count2 + count3)],
                               header=True),
                      TableRow([tr('Buildings Not Affected'),
                                format_int(count)],
                               header=True),
                      TableRow([tr('All Buildings'), format_int(N)],
                               header=True)]
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
        table_body.append(tr('Map shows buildings affected in'
                             ' low, medium and high hazard class areas.'))
        return table_body

    def run(self, layers=None):
        """Classified hazard impact to buildings (e.g. from Open Street Map).

         :param layers: List of layers expected to contain.
                * hazard: Classified Hazard layer
                * exposure: Vector layer of structure data on
                the same grid as hazard
        """
        super(ClassifiedHazardBuildingImpactFunction, self).run(layers)

        # The 3 classes
        low_t = self.parameters['low_hazard_class']
        medium_t = self.parameters['medium_hazard_class']
        high_t = self.parameters['high_hazard_class']

        # Extract data
        hazard = self.hazard      # Classified Hazard
        exposure = self.exposure  # Building locations

        question = self.question()

        # Determine attribute name for hazard levels
        if hazard.is_raster:
            hazard_attribute = 'level'
        else:
            hazard_attribute = None

        interpolated_result = assign_hazard_values_to_exposure_data(
            hazard,
            exposure,
            attribute_name=hazard_attribute,
            mode='constant')

        # Extract relevant exposure data
        attribute_names = interpolated_result.get_attribute_names()
        attributes = interpolated_result.get_data()

        N = len(interpolated_result)
        # Calculate building impact
        count = 0
        count1 = 0
        count2 = 0
        count3 = 0
        buildings = {}
        affected_buildings = {}
        for i in range(N):
            # Get class value
            val = float(attributes[i]['level'])
            # FIXME it would be good if the affected were words not numbers
            # FIXME need to read hazard layer and see class or keyword
            val = float(numpy_round(val))
            if val == high_t:
                count3 += 1
            elif val == medium_t:
                count2 += 1
            elif val == low_t:
                count1 += 1
            else:
                count += 1

            # Count affected buildings by usage type if available
            if 'type' in attribute_names:
                usage = attributes[i]['type']
            elif 'TYPE' in attribute_names:
                usage = attributes[i]['TYPE']
            else:
                usage = None
            if 'amenity' in attribute_names and (usage is None or usage == 0):
                usage = attributes[i]['amenity']
            if ('building_t' in attribute_names and
                    (usage is None or usage == 0)):
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
            if val is True:
                # Count affected buildings by type
                affected_buildings[key] += 1

            # Add calculated impact to existing attributes
            if val == high_t:
                attributes[i][self.target_field] = 3
                attributes[i][self.affected_field] = 1

            elif val == medium_t:
                attributes[i][self.target_field] = 2
                attributes[i][self.affected_field] = 1

            elif val == low_t:
                attributes[i][self.target_field] = 1
                attributes[i][self.affected_field] = 1

            else:
                attributes[i][self.target_field] = 0
                attributes[i][self.affected_field] = 0

        for usage in buildings.keys():
            val = buildings[usage]
            if val < 25 or usage == 'unknown':
                if 'other' not in buildings:
                    buildings['other'] = 0
                    affected_buildings['other'] = 0

                buildings['other'] += val
                affected_buildings['other'] += affected_buildings[usage]
                del buildings[usage]
                del affected_buildings[usage]

        table_body = self._tabulate(N, affected_buildings, attribute_names,
                                    buildings, count, count1, count2, count3,
                                    question)

        # Result
        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary

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

        # For printing map purpose
        map_title = tr('Buildings affected')
        legend_units = tr('(Low, Medium, High)')
        legend_title = tr('Structure inundated status')

        # Create vector layer and return
        vector_layer = Vector(
            data=attributes,
            projection=exposure.get_projection(),
            geometry=exposure.get_geometry(),
            name=tr('Estimated buildings affected'),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'target_field': self.affected_field,
                'map_title': map_title,
                'legend_units': legend_units,
                'legend_title': legend_title,
                'buildings_total': N,
                'buildings_affected': count1 + count2 + count3},
            style_info=style_info)
        self._impact = vector_layer
        return vector_layer
