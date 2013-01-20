"""Apply minimum needs to polygon layer with displaced people.

Usage:
PYTHONPATH=. python scripts/apply_minimum_needs_to_polygon_layer_with_displaced_people.py Flood_Kel_19113_0600.shp

Returns layer with one attribute for each minimum need.

"""

import sys
from safe.storage.core import read_layer
from safe.storage.vector import Vector

def minimum_needs(input_layer, population_name):
    """
        Args
            input_layer: InaSAFE layer object assumed to contain
                         population counts
            population_name: Attribute name that holds population count
        Returns
            InaSAFE layer with attributes for minimum needs as per Perka 7


    """

    needs_attributes = []
    for attributes in input_layer.get_data():
        attribute_dict = attributes

        # Get population count
        population = attributes[population_name]

        # Clean up and turn into integer
        if population in ['-', None]:
            displaced = 0
        else:
            population = population.replace(',','')
            displaced = int(population)


        # Calculate estimated needs based on BNPB Perka 7/2008 minimum bantuan

        # 400g per person per day
        rice = int(displaced * 2.8)
        # 2.5L per person per day
        drinking_water = int(displaced * 17.5)
        # 15L per person per day
        water = int(displaced * 105)
        # assume 5 people per family (not in perka)
        family_kits = int(displaced / 5)
        # 20 people per toilet
        toilets = int(displaced / 20)

        # Add to attributes

        attribute_dict['Beras'] = rice
        attribute_dict['Air minum'] = drinking_water
        attribute_dict['Air bersih'] = water
        attribute_dict['Kit keluarga'] = family_kits
        attribute_dict['Jamba'] = toilets


        # Record attributes for this feature
        needs_attributes.append(attribute_dict)

    output_layer = Vector(geometry=input_layer.get_geometry(),
                          data=needs_attributes,
                          projection=input_layer.get_projection())
    return output_layer



if __name__ == '__main__':

    filename = sys.argv[1]
    input_layer = read_layer(filename)

    output_layer = minimum_needs(input_layer, 'Pengungsi_')

    output_layer.write_to_file(filename[:-4] + '_perka7' + '.shp')

