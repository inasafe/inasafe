"""Module to create damage curves from point data
"""

import numpy
from safe.common.interpolation1d import interpolate1d


class Damage_curve:
    """Class for implementation of damage curves based on point data
    """

    def __init__(self, data):

        try:
            data = numpy.array(data)
        except:
            msg = 'Could not convert data %s to damage curve' % str(data)
            raise Exception(msg)

        msg = 'Damage curve data must be a 2d array or a list of lists'
        if len(data.shape) != 2:
            raise RuntimeError(msg)

        msg = 'Damage curve data must have two columns'
        if data.shape[1] != 2:
            raise RuntimeError(msg)

        self.x = data[:, 0]
        self.y = data[:, 1]

    def __call__(self, zeta):
        return interpolate1d(self.x, self.y, [zeta], mode='linear')[0]
