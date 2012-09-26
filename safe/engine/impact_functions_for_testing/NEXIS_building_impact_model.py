import sys

from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer

from safe.impact_functions.utilities import Damage_curve
from safe.storage.vector import Vector
from safe.engine.interpolation import assign_hazard_values_to_exposure_data

# A maximum floating point number for this package
MAXFLOAT = float(sys.maxint)

#------------------------------------------------------------
# Define damage curves for tsunami structural building damage
#------------------------------------------------------------
struct_damage_curve = {'Double brick': Damage_curve([[-MAXFLOAT, 0.0],
                                                     [0.0, 0.016],
                                                     [0.1, 0.150],
                                                     [0.3, 0.425],
                                                     [0.5, 0.449],
                                                     [1.0, 0.572],
                                                     [1.5, 0.582],
                                                     [2.0, 0.587],
                                                     [2.5, 0.647],
                                                     [MAXFLOAT, 64.7]]),
                       'Brick veneer': Damage_curve([[-MAXFLOAT, 0.0],
                                                     [0.0, 0.016],
                                                     [0.1, 0.169],
                                                     [0.3, 0.445],
                                                     [0.5, 0.472],
                                                     [1.0, 0.618],
                                                     [1.5, 0.629],
                                                     [2.0, 0.633],
                                                     [2.5, 0.694],
                                                     [MAXFLOAT, 69.4]]),
                       'Timber': Damage_curve([[-MAXFLOAT, 0.0],
                                               [0.0, 0.016],
                                               [0.3, 0.645],
                                               [1.0, 0.818],
                                               [2.0, 0.955],
                                               [MAXFLOAT, 99.4]])}

contents_damage_curve = Damage_curve([[-MAXFLOAT, 0.0],
                                      [0.0, 0.013],
                                      [0.1, 0.102],
                                      [0.3, 0.381],
                                      [0.5, 0.500],
                                      [1.0, 0.970],
                                      [1.5, 0.976],
                                      [2.0, 0.986],
                                      [MAXFLOAT, 98.6]])


class TsunamiBuildingLossFunction(FunctionProvider):
    """Risk plugin for earthquake damage based on empirical results

    :param requires category=='hazard' and \
                    subcategory.startswith('tsunami') and \
                    layertype=='raster'
    :param requires category=='exposure' and \
                    subcategory=='structure' and \
                    layertype=='vector' and \
                    nothing=='never'
    """

    @staticmethod
    def target_value():
        field = 'STRUCT_DAMAGE_fraction'
        return field[0:9]

    @staticmethod
    def run(layers):
        """Risk plugin for tsunami building damage
        """

        # Extract data
        H = get_hazard_layer(layers)    # Ground shaking
        E = get_exposure_layer(layers)  # Building locations

        # Interpolate hazard level to building locations
        H = assign_hazard_values_to_exposure_data(H, E,
                                             attribute_name='depth')

        # Extract relevant numerical data
        coordinates = E.get_geometry()
        inundation = H.get_data()

        # Calculate
        N = len(H)
        impact = []
        for i in range(N):

            #-------------------
            # Extract parameters
            #-------------------
            depth = float(inundation[i]['depth'])
            #shore_distance = E.get_data('SHORE_DIST', i)

            # FIXME: Get rid of the type casting when
            #        issue #66 is done
            number_of_people_in_building = int(E.get_data('NEXIS_PEOP', i))
            wall_type = E.get_data('WALL_TYPE', i)
            contents_value = E.get_data('CONT_VALUE', i)
            structure_value = E.get_data('STR_VALUE', i)

            #------------------------
            # Compute people affected
            #------------------------
            if 0.01 < depth < 1.0:
                people_affected = number_of_people_in_building
            else:
                people_affected = 0

            if depth >= 1.0:
                people_severely_affected = number_of_people_in_building
            else:
                people_severely_affected = 0

            #----------------------------------------
            # Compute impact on buldings and contents
            #----------------------------------------
            depth_floor = depth - 0.3  # Adjust for floor height

            if depth_floor >= 0.0:
                buildings_inundated = 1
            else:
                buildings_inundated = 0

            if depth_floor < 0.0:
                structural_damage = contents_damage = 0.0
            else:
                # Water is deep enough to cause damage
                if wall_type in struct_damage_curve:
                    curve = struct_damage_curve[wall_type]
                else:
                    # Establish default for unknown wall type
                    curve = struct_damage_curve['Brick veneer']

                structural_damage = curve(depth_floor)
                contents_damage = contents_damage_curve(depth_floor)

            #---------------
            # Compute losses
            #---------------
            structural_loss = structural_damage * structure_value
            contents_loss = contents_damage * contents_value

            #-------
            # Return
            #-------
            impact.append({'NEXIS_PEOP': number_of_people_in_building,
                           'PEOPLE_AFFECTED': people_affected,
                           'PEOPLE_SEV_AFFECTED': people_severely_affected,
                           'STRUCT_INUNDATED': buildings_inundated,
                           'STRUCT_DAMAGE_fraction': structural_damage,
                           'CONTENTS_DAMAGE_fraction': contents_damage,
                           'STRUCT_LOSS_AUD': structural_loss,
                           'CONTENTS_LOSS_AUD': contents_loss,
                           'DEPTH': depth})

        # FIXME (Ole): Need helper to generate new layer using
        #              correct spatial reference
        #              (i.e. sensibly wrap the following lines)
        V = Vector(data=impact, projection=E.get_projection(),
                   geometry=coordinates,
                   name='Estimated tsunami impact')
        return V
