import unittest
import sys
import os


# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from is_utilities import getExceptionWithStacktrace
from storage.utilities import bbox_intersection


class ISUtilitiesTest(unittest.TestCase):
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
            bbox_intersection('aoeu', 'oaeu', [])
        except Exception, e:
            # Display message and traceback

            msg = getExceptionWithStacktrace(e, html=False)
            #print msg
            assert str(e) in msg
            assert 'line' in msg
            assert 'File' in msg

            msg = getExceptionWithStacktrace(e, html=True)
            assert str(e) in msg
            assert '<pre id="traceback"' in msg
            assert 'line' in msg
            assert 'File' in msg


if __name__ == '__main__':
    suite = unittest.makeSuite(Test_U, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
