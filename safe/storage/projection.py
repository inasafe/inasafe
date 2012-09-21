"""**Class projection**
"""

from osgeo import osr

# The projection string depends on the gdal version
DEFAULT_PROJECTION = '+proj=longlat +datum=WGS84 +no_defs'


class Projection:
    """Represents projections associated with layers
    """

    def __init__(self, p):
        """Constructor for Projection.

        Args:
            * p: Projection information.
                 Any of the GDAL formats are OK including WKT, proj4, ESRI, XML
                 It can also be an instance of Projection.
        """

        if p is None:
            #msg = 'Requested projection is None'
            #raise TypeError(msg)
            p = DEFAULT_PROJECTION

        # Clean input string. This will also work when p is of class
        # Projection by virtue of its __repr__()
        p = str(p).strip()

        # Create OSR spatial reference object
        srs = self.spatial_reference = osr.SpatialReference()

        # Try importing
        input_OK = False
        for import_func in [srs.ImportFromProj4,
                            srs.ImportFromWkt,
                            srs.ImportFromEPSG,
                            srs.ImportFromESRI,
                            # FIXME (Ole): This one emits the warning:
                            # Warning 5: Failed parsing CoordSys:
                            # 'Indonesia TM-3 zone 48.2'
                            #srs.ImportFromMICoordSys,
                            srs.ImportFromPCI,
                            srs.ImportFromXML,
                            srs.ImportFromUSGS,
                            srs.ImportFromUrl]:

            try:
                res = import_func(p)
            except TypeError:
                # FIXME: NetCDF raster layer gives SRS error
                # Occasionally we get things like
                #   File "/usr/lib/python2.7/dist-packages/osgeo/osr.py",
                #   line 639, in ImportFromEPSG
                #   return _osr.SpatialReference_ImportFromEPSG(self, *args)
                #   TypeError: in method 'SpatialReference_ImportFromEPSG',
                #   argument 2 of type 'int'
                # e.g. when using NetCDF multiband data. Why?
                pass

            if res == 0:
                input_OK = True
                break

        if not input_OK:
            msg = 'Spatial reference %s was not recognised' % p
            raise TypeError(msg)

        # Store some - FIXME this is only for backwards compat, remove.
        self.wkt = self.get_projection(proj4=False)
        self.proj4 = self.get_projection(proj4=True)

    def __repr__(self):
        return self.wkt

    def get_projection(self, proj4=False):
        """Return projection

        Args:
            * proj4: If True, projection will be returned in proj4 format.
                     If False (default) projection will be returned in WKT
                     format

        Note:
            To compare projections, use the __eq__ method directly on the
            projection objects: E.g.
            self.projection == other.projection
        """

        if proj4:
            p = self.spatial_reference.ExportToProj4()
        else:
            p = self.spatial_reference.ExportToWkt()

        return p.strip()

    def __eq__(self, other):
        """Override '==' to allow comparison with other projection objecs
        """

        try:
            other = Projection(other)
        except Exception, e:
            msg = ('Argument to == must be a spatial reference or object'
                   ' of class Projection. I got %s with error '
                   'message: %s' % (str(other), e))
            raise TypeError(msg)

        if self.spatial_reference.IsSame(other.spatial_reference):
            # Native comparison checks out
            return True
        else:
            # We have seen cases where the native comparison didn't work
            # for projections that should be identical. See e.g.
            # https://github.com/AIFDR/riab/issues/160
            # Hence do a secondary check using the proj4 string

            return (self.get_projection(proj4=True) ==
                    other.get_projection(proj4=True))

    def __ne__(self, other):
        """Override '!=' to allow comparison with other projection objecs
        """

        return not self == other
