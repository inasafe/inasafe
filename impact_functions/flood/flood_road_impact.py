from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.vector import Vector
from storage.utilities import ugettext as _
from impact_functions.utilities import PointZoomSize
from impact_functions.utilities import PointClassColor
from impact_functions.utilities import PointSymbol
from storage.vector import convert_line_to_points


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
        delta = abs(H.get_geotransform()[1]) * 10
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
