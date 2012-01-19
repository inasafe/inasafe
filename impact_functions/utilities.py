"""Module to create damage curves from point data
"""

import numpy
from engine.interpolation1d import interpolate1d


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
        assert len(data.shape) == 2, msg

        msg = 'Damage curve data must have two columns'
        assert data.shape[1] == 2, msg

        self.x = data[:, 0]
        self.y = data[:, 1]

    def __call__(self, zeta):

        return interpolate1d(self.x, self.y, [zeta], mode='linear')[0]


class ColorMapEntry:
    """Representation of color map entry in SLD file

    Input
        color
        quantity
        opacity (default '0')
    """

    def __init__(self, color, quantity, opacity=None):
        self.color = color
        self.opacity = opacity
        self.quantity = quantity


class PointSymbol:
    """
    """

    def __init__(self, value, icon):
        self.value = value
        self.icon = icon


class PointClassColor:
    """
    """

    def __init__(self, name, clmin, clmax, fill_color,
                 stroke_color=None, opacity=1):
        self.name = name
        self.clmin = clmin
        self.clmax = clmax
        self.fill_color = fill_color
        self.stroke_color = stroke_color
        self.opacity = opacity


class PointZoomSize:
    """
    """

    def __init__(self, level, size):
        self.level = level
        self.size = size
