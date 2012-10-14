from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.storage.vector import Vector
from safe.common.utilities import ugettext as tr
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import assign_hazard_values_to_exposure_data


class FloodRoadImpactFunctionExperimental(FunctionProvider):
    """Inundation impact on road data (experimental)

    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype=='vector'

    :param requires category=='exposure' and \
                    subcategory=='road' and \
                    layertype=='vector'
    """

    target_field = 'INUNDATED'
    title = tr('Be flooded')

    def run(self, layers):
        """Flood impact to buildings (e.g. from Open Street Map)
        """

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        question = get_question(H.get_name(),
                                E.get_name(),
                                self)

        # Interpolate hazard level to building locations
        I = assign_hazard_values_to_exposure_data(H, E)

        # Extract relevant exposure data
        #attribute_names = I.get_attribute_names()
        attributes = I.get_data()
        N = len(I)

        # Calculate road impact
        count = 0
        #flooded_distance = 0
        for i in range(N):
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

            # Count all roads
            if x is True:
                # Count total affected roads
                count += 1

            # Add calculated impact to existing attributes
            attributes[i][self.target_field] = x
            if i == 0:
                print attributes[0].keys()

        # Generate simple impact report
        table_body = [question,
                      TableRow([tr('Building type'),
                                tr('Temporarily closed'),
                                tr('Total')],
                               header=True),
                      TableRow([tr('All'), count, N])]
        impact_summary = Table(table_body).toNewlineFreeString()
        #impact_table = impact_summary
        map_title = tr('Roads inundated')

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
                   geometry_type=I.get_geometry_type(),
                   name=tr('Estimated roads affected'),
                   keywords={'impact_summary': impact_summary,
                             'map_title': map_title},
                   style_info=style_info)
        return V
