# Geometry types


class Geometry:
    """Common class for geometries
    """

    def __init__(self):
        pass


class Polygon(Geometry):
    """Polygon geometry

    Contains outer ring and optionally list of inner rings

    All rings are assumed to be Nx2 numpy arrays of vertex coordinates
    lon, lat
    """

    def __init__(self, outer_ring, inner_rings=None):
        self.outer_ring = outer_ring
        if inner_rings is None:
            inner_rings = []
        self.inner_rings = inner_rings

    def __repr__(self):
        s = 'Polygon(%s, inner_rings=%s' % (self.outer_ring,
                                            self.inner_rings)
        return s
