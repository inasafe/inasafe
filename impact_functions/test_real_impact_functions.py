"""Works with real library impact functions rather than test examples
"""

import sys
import os
import unittest

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from impact_functions.core import get_admissible_plugins
from impact_functions.core import FunctionProvider # Load all real plugins


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


        # This one should get 2 earthquake building impact functions
        D1 = {'category': 'hazard', 'subcategory': 'earthquake', 'unit': 'MMI'}
        D2 = {'category': 'exposure', 'datatype': 'itb',
              'subcategory': 'building'}

        # Add layer_type
        D1['layer_type'] = 'raster'
        D2['layer_type'] = 'vector'
        P = get_admissible_plugins([D1, D2])
        assert len(P) == 2
        assert 'Earthquake Guidelines Function' in P
        assert 'Padang Earthquake Building Damage Function' in P

        # This one should get 3 flood population impact functions
        D1 = {'category': 'hazard', 'subcategory': 'flood', 'unit': 'm'}
        D2 = {'category': 'exposure', 'datatype': 'population',
              'subcategory': 'population'}

        # Add layer_type
        D1['layer_type'] = 'raster'
        D2['layer_type'] = 'raster'
        P = get_admissible_plugins([D1, D2])
        assert len(P) == 3
        assert 'Terdampak' in P
        assert 'Perlu Evakuasi' in P
        assert 'Meninggal' in P

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_real_plugins, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
