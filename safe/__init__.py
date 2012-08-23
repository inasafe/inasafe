# Rely on our friends from numpy on the nose tests utils
from numpy.testing import Tester
from safe.common import utilities
from safe.common.version import get_version

# Note - the version string is obtained in safe.common.version
#        and stored in metadata.txt

utilities.setupLogger()

# FIXME (Ole): I don't like this because it mixes test and production code.
#              What is the rationale
class SafeTester(Tester):
    def _show_system_info(self):
        print 'safe version %s' % get_version()
        super(SafeTester, self)._show_system_info()

test = SafeTester().test
