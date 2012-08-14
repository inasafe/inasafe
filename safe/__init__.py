# Rely on our friends from numpy on the nose tests utils
from numpy.testing import Tester

__version__ = (0, 5, 9, 'final', 0)

def get_version():
     import safe.common.version
     return safe.common.version.get_version(__version__)

class SafeTester(Tester):
    def _show_system_info(self):
        print "safe version %s" % get_version()
        super(SafeTester, self)._show_system_info()

test = SafeTester().test
