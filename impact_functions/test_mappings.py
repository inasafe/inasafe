"""Test mappings for impact functions
"""

import sys
import os
import unittest

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from storage.core import read_layer
from storage.utilities_test import TESTDATA
from mappings import *


class Test_mappings(unittest.TestCase):

    def test_osm2padang(self):
        """OSM structure types maps to Padang vulnerability curves
        """

        hazard_filename = '%s/Shakemap_Padang_2009.asc' % TESTDATA
        exposure_filename = ('%s/OSM_building_polygons_20110905.shp'
                             % TESTDATA)

        # Calculate impact using API
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        # Map from OSM attributes to the padang building classes
        Emap = osm2padang(E)

        for i, feature in enumerate(E.get_data()):
            try:
                vclass = int(Emap.get_data('VCLASS', i))
            except KeyError:
                print
                print i, Emap.get_data()[i]
                #import sys; sys.exit()
                pass

            levels = feature['levels']
            structure = feature['structure']
            msg = ('Unexpected VCLASS %i. '
                   'I have levels == %s and structure == %s.'
                   % (vclass, levels, structure))

            if levels is None or structure is None:
                assert vclass == 2, msg
                continue

            # Map string variable levels to integer
            if levels.endswith('+'):
                levels = 100

            try:
                levels = int(levels)
            except:
                # E.g. 'ILP jalan'
                assert vclass == 2, msg
                continue

            levels = int(levels)

            # Check the main cases
            if levels >= 10:
                assert vclass == 6, msg
            elif 4 <= levels < 10:
                assert vclass == 4, msg
            elif 1 <= levels < 4:
                if structure in ['plastered',
                                 'reinforced masonry',
                                 'reinforced_masonry']:
                    assert vclass == 7, msg
                elif structure == 'confined_masonry':
                    assert vclass == 8, msg
                elif 'kayu' in structure or 'wood' in structure:
                    assert vclass == 9, msg
                else:
                    assert vclass == 2, msg
            else:
                assert vclass == 2, msg


if __name__ == '__main__':
    suite = unittest.makeSuite(Test_mappings, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
