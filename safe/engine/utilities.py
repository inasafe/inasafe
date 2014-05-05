# coding=utf-8
"""Miscellaneous utility functions for InaSAFE
"""

from safe.common.exceptions import RadiiException
from safe.common.geodesy import Point
from safe.storage.geometry import Polygon
from safe.storage.vector import Vector

# Mandatory keywords that must be present in layers
REQUIRED_KEYWORDS = ['category', 'subcategory']


def buffer_points(centers, radii, data_table=None):
    """Buffer points for each center with defined radii.

    If the data_table is defined, then the data will also be copied to the
    result. This function is used for making buffer of volcano point hazard.

    :param centers: All center of each point (longitude, latitude)
    :type centers: list

    :param radii: Desired approximate radii in meters (must be
        monotonically ascending). Can be either one number or list of numbers
    :type radii: int, list

    :param data_table: Data for each center (optional)
    :type data_table: list

    :return: Vector polygon layer representing circle in WGS84
    :rtype: Vector
    """
    if not isinstance(radii, list):
        radii = [radii]

    # Check that radii are monotonically increasing
    monotonically_increasing_flag = all(
        x < y for x, y in zip(radii, radii[1:]))
    if not monotonically_increasing_flag:
        raise RadiiException(RadiiException.suggestion)

    circles = []
    new_data_table = []
    for i, center in enumerate(centers):
        p = Point(longitude=center[0], latitude=center[1])
        inner_rings = None
        for radius in radii:
            # Generate circle polygon
            C = p.generate_circle(radius)
            circles.append(Polygon(outer_ring=C, inner_rings=inner_rings))

            # Store current circle and inner ring for next poly
            inner_rings = [C]

            # Carry attributes for center forward (deep copy)
            row = {}
            if data_table is not None:
                for key in data_table[i]:
                    row[key] = data_table[i][key]

            # Add radius to this ring
            row['Radius'] = radius

            new_data_table.append(row)

    circular_polygon = Vector(
        geometry=circles,  # List with circular polygons
        data=new_data_table,  # Associated attributes
        geometry_type='polygon')

    return circular_polygon
