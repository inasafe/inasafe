"""Raster clipping by polygons
"""

from safe.common.polygon import clip_grid_by_polygons
#from safe.common.polygon import clip_lines_by_polygon


# FIXME (Ole): Order should be reversed and this should move into
# interpolation module.
# Then retire this one
# I THINK WE CAN RETIRE THIS NOW (3/9/12)
def clip_raster_by_polygons(R, P):
    """Separate raster grid points by polygons

    Args:
        * R: Raster layer
        * P: Polygon layer

    Returns:
        * L: List of point vectors and their associated grid values.
             One item for each polygon
    """

    res = clip_grid_by_polygons(R.get_data(),
                                R.get_geotransform(),
                                P.get_geometry(as_geometry_objects=True))

    # Return
    return res
