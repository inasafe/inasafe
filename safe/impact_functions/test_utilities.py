__author__ = 'user'

import unittest
from safe.impact_functions.utilities import add_to_list


class TestUtilities(unittest.TestCase):
    def test_add_to_list(self):
        """Test for add_to_list function
        """
        list_original = ['a', 'b', ['a'], {'a': 'b'}]
        list_a = ['a', 'b', ['a'], {'a': 'b'}]
        # add same immutable element
        list_b = add_to_list(list_a, 'b')
        assert list_b == list_original
        # add list
        list_b = add_to_list(list_a, ['a'])
        assert list_b == list_original
        # add same mutable element
        list_b = add_to_list(list_a, {'a': 'b'})
        assert list_b == list_original
        # add new mutable element
        list_b = add_to_list(list_a, 'c')
        assert len(list_b) == (len(list_original) + 1)
        assert list_b[-1] == 'c'


if __name__ == '__main__':
    unittest.main()
