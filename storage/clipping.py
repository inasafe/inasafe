"""Raster clipping by polygons
"""

from common.polygon import clip_lines_by_polygon, clip_grid_by_polygons

def clip_raster_by_polygons(R, P):
    """Separate raster grid points by polygons

    Input
        R: Raster layer
        P: Polygon layer

    Output
        L: List of point vectors and their associated grid values.
           One item for each polygon
    """

    res = clip_grid_by_polygons(R.get_data(),
                                R.get_geotransform(),
                                P.get_geometry())


    return res
