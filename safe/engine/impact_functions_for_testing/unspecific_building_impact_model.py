from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.storage.vector import Vector


class EarthquakeBuildingDamageFunction(FunctionProvider):
    """Risk plugin for earthquake damage to buildings

    :param requires category=='hazard' and \
                    subcategory.startswith('earthquake') and \
                    layertype=='raster'
    :param requires category=='exposure' and \
                    subcategory.startswith('building')
    """

    plugin_name = 'Earthquake Building Damage Function'

    @staticmethod
    def run(layers):
        """Risk plugin for earthquake school damage
        """

        # Extract data
        H = get_hazard_layer(layers)    # Ground shaking
        E = get_exposure_layer(layers)  # Building locations

        # Interpolate hazard level to building locations
        H = H.interpolate(E, attribute_name='MMI')

        # Extract relevant numerical data
        coordinates = E.get_geometry()
        shaking = H.get_data()

        # Calculate building damage
        building_damage = []
        for i in range(len(shaking)):
            x = float(shaking[i]['MMI'])
            if x < 6.0 or (x != x):  # x != x -> check for nan pre python 2.6
                value = 0.0
            else:
                value = (0.692 * (x ** 4) -
                         15.82 * (x ** 3) +
                         135.0 * (x ** 2) -
                         509.0 * x + 714.4)

            building_damage.append({'DAMAGE': value, 'MMI': x})

        # FIXME (Ole): Need helper to generate new layer using
        #              correct spatial reference
        #              (i.e. sensibly wrap the following lines)
        projection = E.get_projection()

        V = Vector(data=building_damage,
                   projection=E.get_projection(),
                   geometry=coordinates)
        return V
