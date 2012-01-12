from django.template.loader import render_to_string
from impact.plugins.core import FunctionProvider
from impact.plugins.core import get_hazard_layer, get_exposure_layer
from impact.storage.vector import Vector
from django.utils.translation import ugettext as _
from impact.plugins.utilities import PointZoomSize
from impact.plugins.utilities import PointClassColor
from impact.plugins.utilities import PointSymbol
from impact.storage.vector import convert_line_to_points
import scipy.stats


class FloodRoadImpactFunction(FunctionProvider):
    """Risk plugin for flood impact on road data

    :param requires category=='hazard' and \
                    subcategory.startswith('flood') and \
                    layer_type=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory.startswith('road')
    """

    target_field = 'AFFECTED'

    def run(self, layers):
        """Risk plugin for tsunami population
        """

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        R = get_exposure_layer(layers)  # Building locations

        # Make the delta 10 times the size of the resolution.
        delta = abs(H.get_geotransform()[1])*10
        min_value, max_value = H.get_extrema()

        E = convert_line_to_points(R, delta)

        # Interpolate hazard level to building locations
        H = H.interpolate(E)

        # Extract relevant numerical data
        coordinates = E.get_geometry()
        depth = H.get_data()
        N = len(depth)

        # List attributes to carry forward to result layer
        attributes = E.get_attribute_names()

        #print attributes
        #print 'Number of population points', N

        # Calculate population impact
        road_impact = []
        num_classes = 10
        classes = range(num_classes)
        difference = (max_value - min_value) / num_classes

        for i in range(N):
            dep = float(depth[i].values()[0])
            affected = classes[0]
            for level in classes:
                normalized_depth = dep - min_value
                level_value = level * difference
                if normalized_depth > level_value:
                    affected = level

            # Collect depth and calculated damage
            result_dict = {'AFFECTED': affected,
                           'DEPTH': dep}

            # Carry all original attributes forward
            for key in attributes:
                result_dict[key] = E.get_data(key, i)

            # Record result for this feature
            road_impact.append(result_dict)

        # Create report
        caption = ('')

        # Create vector layer and return
        V = Vector(data=road_impact,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   name='Estimated roads affected',
                   keywords={'caption': caption})
        return V

    def generate_style(self, data):
        """Generates and SLD file based on the data values
        """

        DEFAULT_SYMBOL = 'circle'

        symbol_field = None
        symbol_keys = [None, '']
        symbol_values = [DEFAULT_SYMBOL, DEFAULT_SYMBOL]

        scale_keys = [10000000000,]
        scale_values = [4,]

        class_keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',]
        class_values = [{'min': 0, 'max': 1,
                         'color': '#50BBE6', 'opacity': '0.0'},
                        {'min': 1, 'max': 2,
                         'color': '#50BBE6', 'opacity': '0.3'},
                        {'min': 2, 'max': 3,
                         'color': '#234AE8', 'opacity': '0.9'},
                        {'min': 3, 'max': 4,
                         'color': '#234AE8', 'opacity': '0.9'},
                        {'min': 4, 'max': 5,
                         'color': '#234AE8', 'opacity': '0.9'},
                       {'min': 5, 'max': 6,
                         'color': '#234AE8', 'opacity': '0.9'},
                       {'min': 6, 'max': 7,
                         'color': '#234AE8', 'opacity': '0.9'},
                         {'min': 7, 'max': 8,
                         'color': '#234AE8', 'opacity': '0.9'},
                       {'min': 8, 'max': 9,
                         'color': '#234AE8', 'opacity': '0.9'},
                        {'min': 9, 'max': 10,
                         'color': '#234AE8', 'opacity': '1.0'}]
  




        params = dict(name=data.get_name(),
                      damage_field=self.target_field,
                      symbol_field=symbol_field,
                      symbols=dict(zip(symbol_keys, symbol_values)),
                      scales=dict(zip(scale_keys, scale_values)),
                      classifications=dict(zip(class_keys, class_values)))

        return render_to_string('impact/styles/flood_road.sld', params)
