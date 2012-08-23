import unittest
import logging

from core import FunctionProvider
from core import requirements_collect
from core import requirement_check
from core import requirements_met
from core import get_admissible_plugins
from core import get_function_title
from core import get_plugins_as_table

LOGGER = logging.getLogger('InaSAFE')


class BasicFunction(FunctionProvider):
    """Risk plugin for testing

    :author Allen
    :rating 1
    :param requires category=="test_cat1"
    :param requires unit=="MMI"
    """

    @staticmethod
    def run():
        return None


class F1(FunctionProvider):
    """Risk plugin for testing

    :param requires category=='test_cat1' and \
                    subcategory.startswith('flood') and \
                    layertype=='raster' and \
                    unit=='m'

    :param requires category=='test_cat2' and \
                    subcategory.startswith('population') and \
                    layertype=='raster' and \
                    datatype=='population'

    """

    title = 'Title for F1'

    @staticmethod
    def run():
        return None


class F2(FunctionProvider):
    """Risk plugin for testing

    :param requires category=='test_cat1' and \
                    subcategory.startswith('flood') and \
                    layertype=='raster' and \
                    unit=='m'

    :param requires category=='test_cat2' and \
                    subcategory.startswith('building')
    """

    title = 'Title for F2'

    @staticmethod
    def run():
        return None


class F3(FunctionProvider):
    """Risk plugin for testing

    :param requires category=='test_cat1'
    :param requires category=='test_cat2'
    """

    @staticmethod
    def run():
        return None


class SyntaxErrorFunction(FunctionProvider):
    """Risk plugin for testing

    :author Allen
    :rating 1
    :param requires category=="test_cat1"
    :param requires unit="MMI"  # Note the error should be ==
    """

    @staticmethod
    def run():
        return None


class Test_plugin_core(unittest.TestCase):
    """Tests of Risiko calculations
    """

    def test_basic_plugin_requirements(self):
        """Basic plugin requirements collection
        """
        requirelines = requirements_collect(BasicFunction)
        params = {'category': 'test_cat1', 'unit': 'MMI'}
        assert requirements_met(requirelines, params)

        params = {'category': 'test_cat2', 'unit': 'mmi2'}
        assert requirements_met(requirelines, params) == False

    def test_basic_plugin_requirements_met(self):
        """Basic plugin requirements met
        """
        requirelines = requirements_collect(BasicFunction)
        valid_return = ['category=="test_cat1"', 'unit=="MMI"']
        for ret1, ret2 in zip(valid_return, requirelines):
            assert ret1 == ret2, "Error in requirements extraction"

    def test_basic_requirements_check(self):
        """Basic plugin requirements check
        """
        requirelines = requirements_collect(BasicFunction)
        params = {'category': 'test_cat2'}
        for line in requirelines:
            check = requirement_check(params, line)
            assert check == False

        line = "unit='MMI'"
        params = {'category': 'test_cat2'}
        msg = 'Malformed statement (logged)'
        assert requirement_check(params, line) == False, msg
        #self.assertRaises(SyntaxError, requirement_check, params, line)

    def test_keywords_error(self):
        """Handling of reserved python keywords """
        line = "unit=='MMI'"
        params = {'class': 'myclass'}
        msg = 'Reserved keyword in statement (logged)'
        assert requirement_check(params, line) == False, msg

    def test_filtering_of_impact_functions(self):
        """Impact functions are filtered correctly
        """

        # Keywords matching F1 and F3
        haz_keywords1 = dict(category='test_cat1', subcategory='flood',
                             layertype='raster', unit='m')
        exp_keywords1 = dict(category='test_cat2', subcategory='population',
                             layertype='raster', datatype='population')

        # Keywords matching F2 and F3
        haz_keywords2 = dict(category='test_cat1', subcategory='flood',
                             layertype='raster', unit='m')
        exp_keywords2 = dict(category='test_cat2', subcategory='building')

        # Check correct matching of keyword set 1
        P = get_admissible_plugins([haz_keywords1, exp_keywords1])
        msg = 'Expected impact functions F1 and F3 in %s' % str(P.keys())
        assert 'F1' in P and 'F3' in P, msg

        # Check correctness of title attribute
        assert get_function_title(P['F1']) == 'Title for F1'
        assert get_function_title(P['F3']) == 'F3'

        # Check correct matching of keyword set 2
        P = get_admissible_plugins([haz_keywords2, exp_keywords2])
        msg = 'Expected impact functions F2 and F3 in %s' % str(P.keys())
        assert 'F2' in P and 'F3' in P, msg

        # Check correctness of title attribute
        assert get_function_title(P['F2']) == 'Title for F2'
        assert get_function_title(P['F3']) == 'F3'

        # Check empty call returns all
        P = get_admissible_plugins([])
        msg = ('Expected at least impact functions F1, F2 and F3 in %s'
               % str(P.keys()))
        assert 'F1' in P and 'F2' in P and 'F3' in P, msg

    def test_get_plugins_as_table(self):
        """Test get plugins as table"""
        T = get_plugins_as_table()
        S = T.toNewlineFreeString()
        LOGGER.debug(S)
        #f = file('/tmp/tbl.html', 'wt')
        #f.write(S)
        #f.close()
        # Rather arbitrary way to see if the table has some data in it
        # maybe there is a nicer way to test given that fn list can change? TS
        assert len(S) > 1000

        # Now test the table for a single nominated fn
        T = get_plugins_as_table('F1')
        S = T.toNewlineFreeString()
        LOGGER.debug(S)
        #f = file('/tmp/tbl.html', 'wt')
        #f.write(S)
        #f.close()
        # Expecting that F1 test wont change and that the table produced for
        # it is of a deterministic length
        assert len(S) == 518

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_plugin_core, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
