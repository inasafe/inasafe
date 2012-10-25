from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.storage.vector import Vector
from safe.common.utilities import ugettext as tr
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import assign_hazard_values_to_exposure_data

import logging
LOGGER = logging.getLogger('InaSAFE')


class FloodBuildingImpactFunction(FunctionProvider):
    """Inundation impact on building data

    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami']

    :param requires category=='exposure' and \
                    subcategory=='structure' and \
                    layertype=='vector'
    """

    target_field = 'INUNDATED'
    title = tr('Be flooded')

    def run(self, layers):
        """Flood impact to buildings (e.g. from Open Street Map)
        """

        threshold = 1.0  # Flood threshold [m]

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        question = get_question(H.get_name(),
                                E.get_name(),
                                self)

        # Determine attribute name for hazard levels
        if H.is_raster:
            hazard_attribute = 'depth'
        else:
            hazard_attribute = 'FLOODPRONE'

        # Interpolate hazard level to building locations
        I = assign_hazard_values_to_exposure_data(H, E,
                                             attribute_name=hazard_attribute)

        # Extract relevant exposure data
        attribute_names = I.get_attribute_names()
        attributes = I.get_data()
        N = len(I)
        # Calculate building impact
        count = 0
        buildings = {}
        affected_buildings = {}
        for i in range(N):
            if hazard_attribute == 'depth':
                # Get the interpolated depth
                x = float(attributes[i]['depth'])
                x = x >= threshold
            elif hazard_attribute == 'FLOODPRONE':
                # Use interpolated polygon attribute
                atts = attributes[i]

                if 'FLOODPRONE' in atts:
                    res = atts['FLOODPRONE']
                    if res is None:
                        x = False
                    else:
                        x = res.lower() == 'yes'
                else:
                    # If there isn't a flood prone attribute,
                    # assume that building is wet if inside polygon
                    # as flag by generic attribute AFFECTED
                    res = atts['Affected']
                    if res is None:
                        x = False
                    else:
                        x = res
            else:
                msg = (tr('Unknown hazard type %s. '
                         'Must be either "depth" or "floodprone"')
                       % hazard_attribute)
                raise Exception(msg)

            # Count affected buildings by usage type if available

            if 'type' in attribute_names:
                usage = attributes[i]['type']
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
            #LOGGER.debug('usage ')
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
            attributes[i][self.target_field] = x

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
        # Generate csv file of results
##        fid = open('C:\dki_table_%s.csv' % H.get_name(), 'wb')
##        fid.write('%s, %s, %s\n' % (tr('Building type'),
##                                    tr('Temporarily closed'),
##                                    tr('Total')))
##        fid.write('%s, %i, %i\n' % (tr('All'), count, N))

        # Generate simple impact report
        table_body = [question,
                      TableRow([tr('Building type'),
                                tr('Number flooded'),
                                tr('Total')],
                               header=True),
                      TableRow([tr('All'), count, N])]

##        fid.write('%s, %s, %s\n' % (tr('Building type'),
##                                    tr('Temporarily closed'),
##                                    tr('Total')))

        school_closed = 0
        hospital_closed = 0
        # Generate break down by building usage type is available
        list_type_attribute = ['type',
                               'amenity',
                               'building_t',
                               'office',
                               'tourism',
                               'leisure',
                               'building']
        intersect_type = set(attribute_names) & set(list_type_attribute)
        if len(intersect_type) > 0:
            # Make list of building types
            building_list = []
            for usage in buildings:

                building_type = usage.replace('_', ' ')

                # Lookup internationalised value if available
                building_type = tr(building_type)
                #==============================================================
                # print ('WARNING: %s could not be translated'
                #        % building_type)
                #==============================================================
                # FIXME (Sunni) : I change affected_buildings[usage] to string
                # because it will be replace with &nbsp in html
                building_list.append([building_type.capitalize(),
                                      str(affected_buildings[usage]),
                                      buildings[usage]])
                if building_type == 'school':
                    school_closed = affected_buildings[usage]
                if building_type == 'hospital':
                    hospital_closed = affected_buildings[usage]
##                fid.write('%s, %i, %i\n' % (building_type.capitalize(),
##                                            affected_buildings[usage],
##                                            buildings[usage]))

            # Sort alphabetically
            building_list.sort()

            #table_body.append(TableRow([tr('Building type'),
            #                            tr('Temporarily closed'),
            #                            tr('Total')], header=True))
            table_body.append(TableRow(tr('Breakdown by building type'),
                                       header=True))
            for row in building_list:
                s = TableRow(row)
                table_body.append(s)

##        fid.close()
        table_body.append(TableRow(tr('Action Checklist:'), header=True))
        table_body.append(TableRow(tr('Are the critical facilities still '
                                     'open?')))
        table_body.append(TableRow(tr('Which structures have warning capacity '
                                     '(eg. sirens, speakers, etc.)?')))
        table_body.append(TableRow(tr('Which buildings will be evacuation '
                                     'centres?')))
        table_body.append(TableRow(tr('Where will we locate the operations '
                                     'centre?')))
        table_body.append(TableRow(tr('Where will we locate warehouse and/or '
                                     'distribution centres?')))
        if school_closed > 0:
            table_body.append(TableRow(tr('Where will the students from the %d'
                                         ' closed schools go to study?') %
                                         school_closed))
        if hospital_closed > 0:
            table_body.append(TableRow(tr('Where will the patients from the %d'
                                         ' closed hospitals go for treatment '
                                         'and how will we transport them?') %
                                         hospital_closed))

        table_body.append(TableRow(tr('Notes'), header=True))
        assumption = tr('Buildings are said to be flooded when ')
        if hazard_attribute == 'depth':
            assumption += tr('flood levels exceed %.1f m') % threshold
        else:
            assumption += tr('in areas marked as flood prone')
        table_body.append(assumption)

        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary
        map_title = tr('Buildings inundated')

        # Create style
        style_classes = [dict(label=tr('Not Flooded'), min=0, max=0,
                              colour='#1EFC7C', transparency=0, size=1),
                         dict(label=tr('Flooded'), min=1, max=1,
                              colour='#F31A1C', transparency=0, size=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        V = Vector(data=attributes,
                   projection=I.get_projection(),
                   geometry=I.get_geometry(),
                   name=tr('Estimated buildings affected'),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title,
                             'target_field': self.target_field},
                   style_info=style_info)
        return V
