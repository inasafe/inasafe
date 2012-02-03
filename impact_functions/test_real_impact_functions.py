"""Works with real library impact functions rather than test examples
"""

import sys
import os
import unittest

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from impact_functions.core import get_admissible_plugins, get_plugins
from impact_functions.core import requirements_collect
from impact_functions.core import FunctionProvider  # Load all real plugins


class Test_real_plugins(unittest.TestCase):
    """Tests of Risiko calculations
    """

    def test_filtering_of_impact_functions(self):
        """Impact functions are filtered correctly
        """

        # Check empty call returns all
        P = get_admissible_plugins([])

        # NOTE: These are hardwired tests that will need to change
        # when impact functions change.
        assert 'Earthquake Guidelines Function' in P
        assert 'Padang Earthquake Building Damage Function' in P
        assert 'Ditutup Sementara' in P
        assert 'Earthquake Population Exposure Function' in P
        assert 'Tsunami Population Impact Function' in P
        assert 'Perlu Evakuasi' in P
        assert 'Tsunami Building Impact Function' in P
        assert 'Tephra Impact Function' in P
        assert 'Padang Earthquake Building Damage Function' in P
        assert 'Earthquake Fatality Function' in P
        assert 'Earthquake Guidelines Function' in P
        assert 'Tephra Population Impact Function' in P
        assert 'Flood Road Impact Function' in P
        assert 'Dalam bahaya' in P
        assert 'U S G S Fatality Function' in P
        assert 'Earthquake Fatality Function Podes' in P
        assert 'Terdampak' in P
        assert 'Meninggal' in P

        #print
        #for p in P:
        #    print p, P[p]

        # This one should get 2 earthquake building impact functions
        D1 = {'category': 'hazard', 'subcategory': 'earthquake', 'unit': 'MMI'}
        D2 = {'category': 'exposure', 'datatype': 'itb',
              'subcategory': 'building'}

        # Add layertype
        D1['layertype'] = 'raster'
        D2['layertype'] = 'vector'
        P = get_admissible_plugins([D1, D2])
        assert len(P) >= 2  # Depending on other tests there could be more
        assert 'Earthquake Guidelines Function' in P
        assert 'Padang Earthquake Building Damage Function' in P

        # This one should get 3 flood population impact functions
        D1 = {'category': 'hazard', 'subcategory': 'flood', 'unit': 'm'}
        D2 = {'category': 'exposure', 'datatype': 'population',
              'subcategory': 'population'}

        # Add layertype
        D1['layertype'] = 'raster'
        D2['layertype'] = 'raster'
        P = get_admissible_plugins([D1, D2])
        assert len(P) >= 3  # Depending on other tests there could be more
        assert 'Terdampak' in P
        assert 'Perlu Evakuasi' in P
        assert 'Meninggal' in P

        # Try form where only one dictionary is passed
        # This one gets all the flood related impact functions
        P = get_admissible_plugins(D1)
        assert len(P) >= 6
        assert 'Terdampak' in P
        assert 'Perlu Evakuasi' in P
        assert 'Meninggal' in P
        assert 'Ditutup Sementara' in P
        assert 'Flood Road Impact Function' in P
        assert 'Dalam bahaya' in P

        # Try to get general tsunami building impact function (e.g. BB data)
        f_name = 'Tsunami Building Impact Function'

        D1 = {'category': 'hazard', 'subcategory': 'tsunami', 'unit': 'm'}
        D2 = {'category': 'exposure', 'subcategory': 'building'}

        # Add layertype
        D1['layertype'] = 'raster'
        D2['layertype'] = 'vector'
        P = get_admissible_plugins([D1, D2])

        assert f_name in P

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
