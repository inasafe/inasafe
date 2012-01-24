import unittest
import numpy
import sys
import os


# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from utilities import *
from engine.core import get_bounding_boxes


class Test_U(unittest.TestCase):
    """Tests for reading and writing of raster and vector data
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_stacktrace_html(self):
        """Stack traces can be caught and rendered as html
        """

        try:
            get_bounding_boxes('aoeu', 'oaeu', [])
        except Exception, e:
            # Display message and traceback

            msg = get_exception_with_stacktrace(e, html=False)
            print msg
            assert str(e) in msg
            assert 'line' in msg
            assert 'File' in msg

            msg = get_exception_with_stacktrace(e, html=True)
            assert str(e) in msg
            assert '<pre id="traceback"' in msg
            assert 'line' in msg
            assert 'File' in msg


if __name__ == '__main__':
    suite = unittest.makeSuite(Test_U, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
