# Rely on our friends from numpy on the nose tests utils
from numpy.testing import Tester

class SafeTester(Tester):
    pass

test = SafeTester().test
