"""Raster clipping by polygons
"""

def clip_raster_by_polygons(R, P):
    """

    Input
        R: Raster layer
        P: Polygon layer

    Output
        L: List of raster layers, one for each polygon
    """

    # FIXME (Ole): Remember to account for pixel registration by
    # offsetting by half a cellsize. Test this with test_grid.asc

    print A
    print G

    M, N = A.shape

    dx = G[1]
    xmin = G[0]
    xmax = xmin + dx * N

    x = numpy.linspace(start=xmin,
                       stop=xmax,
                       num=N,
                       endpoint=False)
    print x, len(x)

    dy = G[5]
    ymax = G[3]
    ymin =



    y = numpy.linspace(start=xmin,
                       stop=xmax,
                       num=N,
                       endpoint=False)
    print x, len(x)

