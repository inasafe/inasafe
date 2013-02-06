"""Works with real library impact functions rather than test examples
"""

import unittest

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

        # List the known impact function names
        # based on their class names - not their titles
        msg = 'Available impact functions are: %s' % str(P.keys())
        #print msg
        assert 'Flood Evacuation Function Vector Hazard' in P, msg
        assert 'I T B Earthquake Building Damage Function' in P, msg
        assert 'Earthquake Building Impact Function' in P, msg
        assert 'P A G Fatality Function' in P, msg
        assert 'Flood Evacuation Function' in P, msg
        assert 'Flood Building Impact Function' in P, msg
        assert 'I T B Fatality Function' in P, msg
        assert 'Volcano Building Impact' in P, msg
        assert 'Volcano Polygon Hazard Population' in P, msg

        # This one should get 2 earthquake building impact functions
        D1 = {'category': 'hazard', 'subcategory': 'earthquake', 'unit': 'MMI'}
        D2 = {'category': 'exposure', 'datatype': 'itb',
              'subcategory': 'structure'}

        # Add layertype
        D1['layertype'] = 'raster'
        D2['layertype'] = 'vector'
        P = get_admissible_plugins([D1, D2])
        msg = 'Expected: len(P) >= 2, Got: len(P) is %i' % len(P)
        assert len(P) >= 1, msg  # Depending on other tests there could be more
        assert 'Earthquake Building Impact Function' in P

        # This one should get 3 flood population impact functions
        D1 = {'category': 'hazard', 'subcategory': 'flood', 'unit': 'm'}
        D2 = {'category': 'exposure', 'subcategory': 'population'}

        # Add layertype
        D1['layertype'] = 'raster'
        D2['layertype'] = 'raster'
        P = get_admissible_plugins([D1, D2])
        assert len(P) >= 1  # Depending on other tests there could be more
        #assert 'W B Flood Evacuation Function' in P

        # Try form where only one dictionary is passed
        # This one gets all the flood related impact functions

        # Try to get general inundation building impact function
        f_name = 'Flood Building Impact Function'

        P = get_admissible_plugins(D1)
        assert len(P) >= 2
        #assert 'W B Flood Evacuation Function' in P
        assert f_name in P
        #assert 'Flood Road Impact Function' in P

        D1 = {'category': 'hazard', 'subcategory': 'tsunami'}
        D2 = {'category': 'exposure', 'subcategory': 'structure'}

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
