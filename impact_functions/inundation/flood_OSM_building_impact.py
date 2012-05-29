from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from impact_functions.core import get_question
from storage.vector import Vector
from storage.utilities import ugettext as _
from impact_functions.tables import (Table, TableRow)


class DKIFloodBuildingImpactFunction(FunctionProvider):
    """Risk plugin for flood impact on building data

    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami']

    :param requires category=='exposure' and \
                    subcategory=='building' and \
                    layertype=='vector' and \
                    purpose=='dki'
    """

    target_field = 'INUNDATED'
    plugin_name = _('Be inundated')

    def run(self, layers):
        """Risk plugin for flood building impact
        """

        threshold = 1.0  # Flood threshold [m]

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        question = get_question(H.get_name(),
                                E.get_name(),
                                self.plugin_name.lower())

        # Interpolate hazard level to building locations
        if H.is_raster:
            I = H.interpolate(E, attribute_name='depth')
            hazard_type = 'depth'
        else:
            I = H.interpolate(E)
            hazard_type = 'floodprone'

        # Extract relevant numerical data
        attributes = I.get_data()
        N = len(I)

        # Calculate population impact
        count = 0
        buildings = {}
        affected_buildings = {}
        for i in range(N):
            if hazard_type == 'depth':
                # Get the interpolated depth
                x = float(attributes[i]['depth'])
                x = x > threshold
            elif hazard_type == 'floodprone':
                # Use interpolated polygon attribute
                res = attributes[i]['FLOODPRONE']
                if res is None:
                    x = False
                else:
                    x = res.lower() == 'yes'
            else:
                msg = ('Unknown hazard type %s. '
                       'Must be either "depth" or "floodprone"' % hazard_type)
                raise Exception(msg)

            usage = attributes[i]['type']
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

            # Count total
            if x is True:
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

        # Generate impact report for the pdf map
        table_body = [question,
                      TableRow([_('Building type'), _('Flooded'), _('Total')],
                               header=True)]

        building_list = []
        for usage in buildings:
            building_list.append([usage.replace('_', ' ').capitalize(),
                                  affected_buildings[usage],
                                  buildings[usage]])

        building_list.sort()

        for row in building_list:
            s = TableRow(row)
            table_body.append(s)

        table_body.append(TableRow(_('Notes:'), header=True))
        assumption = _('Buildings are said to be flooded when ')
        if hazard_type == 'depth':
            assumption += _('flood levels exceed %.1f m') % threshold
        else:
            assumption += _('in areas marked as flood prone')
        table_body.append(assumption)

        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary
        map_title = _('Buildings inundated')
        # Create style
        style_classes = [dict(label=_('Not Flooded'), min=0, max=0,
                              colour='#1EFC7C', transparency=0, size=1),
                         dict(label=_('Flooded'), min=1, max=1,
                              colour='#F31A1C', transparency=0, size=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        V = Vector(data=attributes,
                   projection=I.get_projection(),
                   geometry=I.get_geometry(),
                   name=_('Estimated buildings affected'),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title},
                   style_info=style_info)
        return V
