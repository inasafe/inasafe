# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid / DFAT -
**New Metadata for SAFE.**

Contact : etienne@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

# pylint: disable=redefined-builtin
from math import sqrt, pow, cos, sin, atan2, pi


def distance(p1, p2):
    """Compute distance between two points.

    :param p1: Point 1 as a list (x, y)
    :type p1: list

    :param p2: Point 2 as a list (x, y)
    :type p2: list

    :return Distance.
    :rtype float
    """
    delta_x = p2[0] - p1[0]
    delta_y = p2[1] - p1[1]
    return sqrt(pow(delta_x, 2) + pow(delta_y, 2))


def sum_distances(line):
    """Compute the length for each segments in a line.

    :param line: The line as a list of points.
    :type line: list

    :return: List of lengths
    :rtype: list
    """
    segments_length = []
    for p1, p2 in zip(line[0:], line[1:]):
        segments_length.append(distance(p1, p2))
    return segments_length


def azimuth(p1, p2):
    """Compute the azimuth in radians between two points.

    :param p1: Point 1 as a list (x, y)
    :type p1: list

    :param p2: Point 2 as a list (x, y)
    :type p2: list

    :return: The azimuth in radians.
    :rtype float
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    rads = atan2(dy, dx)
    rads %= 2 * pi
    return rads


def get_point(p1, p2, length):
    """Get a point between two points depending of a distance.

    :param p1: Point 1 as a list (x, y)
    :type p1: list

    :param p2: Point 2 as a list (x, y)
    :type p2: list

    :param length: The distance where we want the point.
    :type length: float

    :return: The new point.
    :rtype list
    """
    teta = azimuth(p1, p2)
    x = length * cos(teta) + p1[0]
    y = length * sin(teta) + p1[1]
    return x, y


def split_middle(line):
    """Split a line into two lines in the middle.

    :param line: The line as a list of points.
    :type line: list

    :return: The two new lines.
    :rtype: list
    """
    distances = sum_distances(line)
    half_distance = sum(distances) / 2
    iter_sum = 0
    for i, dist in enumerate(distances):
        if iter_sum < half_distance < iter_sum + dist:
            point_1 = line[i]
            point_2 = line[i + 1]
            d = half_distance - iter_sum
            middle = get_point(point_1, point_2, d)
            line.insert(i + 1, middle)
            return line[0:i + 2], line[i + 1:]
        elif half_distance == iter_sum + dist:
            return line[0:i + 2], line[i + 1:]
        else:
            iter_sum += dist
