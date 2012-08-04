"""Works with real library impact functions rather than test examples
"""

import sys
import os
import unittest

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(pardir)

from safe.impact_functions.core import get_admissible_plugins
from safe.impact_functions.core import requirements_collect


class Test_real_plugins(unittest.TestCase):
    """Tests of Risiko calculations
    """

    def test_filtering_of_impact_functions(self):
        """Impact functions are filtered correctly
        """

        # Check empty call returns all
        P = get_admissible_plugins([])

        #print
        #for p in P:
        #    print p, P[p]

        # List the known impact function names
        # based on their class names - not their titles
        msg = 'Available impact functions are: %s' % str(P.keys())
        #assert 'Earthquake Guidelines Function' in P, msg
        assert 'Padang Earthquake Building Damage Function' in P, msg
        assert 'Flood Building Impact Function' in P, msg
        assert 'W B Flood Evacuation Function' in P, msg
        #assert 'Tephra Building Impact Function' in P, msg
        #assert 'Tephra Population Impact Function' in P, msg
        #assert 'Flood Road Impact Function' in P, msg
        assert 'I T B Earthquake Building Damage Function' in P, msg
        assert 'Categorised Hazard Building Impact Function' in P, msg

        # This one should get 2 earthquake building impact functions
        D1 = {'category': 'hazard', 'subcategory': 'earthquake', 'unit': 'MMI'}
        D2 = {'category': 'exposure', 'datatype': 'itb',
              'subcategory': 'building'}

        # Add layertype
        D1['layertype'] = 'raster'
        D2['layertype'] = 'vector'
        P = get_admissible_plugins([D1, D2])
        assert len(P) >= 2  # Depending on other tests there could be more
        #assert 'Earthquake Guidelines Function' in P
        assert 'Padang Earthquake Building Damage Function' in P

        # This one should get 3 flood population impact functions
        D1 = {'category': 'hazard', 'subcategory': 'flood', 'unit': 'm'}
        D2 = {'category': 'exposure', 'subcategory': 'population',
              'datatype': 'density'}

        # Add layertype
        D1['layertype'] = 'raster'
        D2['layertype'] = 'raster'
        P = get_admissible_plugins([D1, D2])
        assert len(P) >= 1  # Depending on other tests there could be more
        assert 'W B Flood Evacuation Function' in P

        # Try form where only one dictionary is passed
        # This one gets all the flood related impact functions

        # Try to get general inundation building impact function
        f_name = 'Flood Building Impact Function'

        P = get_admissible_plugins(D1)
        assert len(P) >= 2
        assert 'W B Flood Evacuation Function' in P
        assert f_name in P
        #assert 'Flood Road Impact Function' in P

        D1 = {'category': 'hazard', 'subcategory': 'tsunami'}
        D2 = {'category': 'exposure', 'subcategory': 'building'}

        # Add layertype
        #D1['layertype'] = 'raster'  # Not required for flood building impact
        D2['layertype'] = 'vector'
        P = get_admissible_plugins([D1, D2])

        msg = 'Expected name "%s" in P: %s' % (f_name, P)
        assert f_name in P, msg

        # Get requirements from expected function
        P_all = get_admissible_plugins()
        assert P[f_name] == P_all[f_name]

        requirelines = requirements_collect(P[f_name])
        for i, D in enumerate([D1, D2]):
            for key in D:
                msg = 'Key %s was not found in %s' % (key, requirelines[i])
                assert key in requirelines[i], msg

                msg = 'Val %s was not found in %s' % (D[key], requirelines[i])
                assert D[key] in requirelines[i], msg

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_real_plugins, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
