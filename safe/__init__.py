# Rely on our friends from numpy on the nose tests utils
from numpy.testing import Tester
from safe.common import utilities

__version__ = (0, 5, 0, 'alpha', 0)

utilities.setupLogger()


# FIXME (Ole): Delete and use the one in common/version.py
#def get_version():
#    # FIXME (Ole): Why re-import here? (pylint W0404)
#    import safe.common.version
#    return safe.common.version.get_version(__version__)


class SafeTester(Tester):
    def _show_system_info(self):
        print "safe version %s" % get_version()
        super(SafeTester, self)._show_system_info()

test = SafeTester().test
