import unittest

import numpy
import sys
import os
import unittest
import warnings

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from core import FunctionProvider
from core import requirements_collect
from core import requirement_check
from core import requirements_met


class BasicFunction(FunctionProvider):
    """Risk plugin for testing

    :author Allen
    :rating 1
    :param requires category=="hazard"
    :param requires unit=="mmi"
    """

    @staticmethod
    def run(H, E,
            a=0.97429, b=11.037):

        return None


class SyntaxErrorFunction(FunctionProvider):
    """Risk plugin for testing

    :author Allen
    :rating 1
    :param requires category=="hazard"
    :param requires unit="mmi" #Note the error should be ==
    """

    @staticmethod
    def run(H, E,
            a=0.97429, b=11.037):
        return None


class Test_plugin_core(unittest.TestCase):
    """Tests of Risiko calculations
    """

    def test_basic_plugin_requirements(self):
        """Basic plugin requirements collection
        """
        requirelines = requirements_collect(BasicFunction)
        params = {'category': 'hazard', 'unit': 'mmi'}
        assert requirements_met(requirelines, params)

        params = {'category': 'exposure', 'unit': 'mmi2'}
        assert requirements_met(requirelines, params, True) == False

    def test_basic_plugin_requirements_met(self):
        """Basic plugin requirements met
        """
        requirelines = requirements_collect(BasicFunction)
        valid_return = ['category=="hazard"', 'unit=="mmi"']
        for ret1, ret2 in zip(valid_return, requirelines):
            assert ret1 == ret2, "Error in requirements extraction"

    def test_basic_requirements_check(self):
        """Basic plugin requirements check
        """
        requirelines = requirements_collect(BasicFunction)
        params = {'category': 'exposure'}
        for line in requirelines:
            check = requirement_check(params, line)
            assert check == False

        line = "unit='mmi'"
        params = {'category': 'exposure'}
        msg = 'Malformed statement (logged)'
        assert requirement_check(params, line) == False, msg
        #self.assertRaises(SyntaxError, requirement_check, params, line)

    def test_keywords_error(self):
        """ Handling of reserved python keywords """
        line = "unit=='mmi'"
        params = {'class': 'myclass'}
        msg = 'Reserved keyword in statement (logged)'
        assert requirement_check(params, line) == False, msg

if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'risiko.settings'
    suite = unittest.makeSuite(Test_plugin_core, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
