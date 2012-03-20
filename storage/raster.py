"""Class Raster
"""

import os
import numpy
from osgeo import gdal
from projection import Projection
from utilities import DRIVER_MAP
from engine.interpolation import interpolate_raster_vector
from utilities import read_keywords
from utilities import write_keywords
from utilities import nanallclose
from utilities import geotransform2bbox, geotransform2resolution
from utilities import verify


class Raster:
    """Internal representation of raster data
    """

    def __init__(self, data=None, projection=None, geotransform=None,
                 name='', keywords=None, style_info=None):
        """Initialise object with either data or filename

        Input
            data: Can be either
                * a filename of a raster file format known to GDAL
                * an MxN array of raster data
                * None (FIXME (Ole): Remove this option)
            projection: Geospatial reference in WKT format.
                        Only used if data is provide as a numeric array,
            geotransform: GDAL geotransform (6-tuple).
                          (top left x, w-e pixel resolution, rotation,
                           top left y, rotation, n-s pixel resolution).
                          See e.g. http://www.gdal.org/gdal_tutorial.html
                          Only used if data is provide as a numeric array,
            name: Optional name for layer.
                  Only used if data is provide as a numeric array,
            keywords: Optional dictionary with keywords that describe the
                      layer. When the layer is stored, these keywords will
                      be written into an associated file with extension
                      .keywords.

                      Keywords can for example be used to display text
                      about the layer in a web application.

        Note that if data is a filename, all other arguments are ignored
        as they will be inferred from the file.
        """

        # Input checks
        if data is None:
            # Instantiate empty object
            self.name = name
            self.data = None
            self.projection = None
            self.coordinates = None
            self.filename = None
            self.keywords = {}
            return

        # Initialisation
        if isinstance(data, basestring):
            self.read_from_file(data)
        else:
            # Assume that data is provided as an array
            # with extra keyword arguments supplying metadata
            if keywords is None:
                self.keywords = {}
            else:
                msg = ('Specified keywords must be either None or a '
                       'dictionary. I got %s' % keywords)
                verify(isinstance(keywords, dict), msg)
                self.keywords = keywords

            if style_info is None:
                self.style_info = {}
            else:
                msg = ('Specified style_info must be either None or a '
                       'dictionary. I got %s' % style_info)
                verify(isinstance(style_info, dict), msg)
                self.style_info = style_info

            self.data = numpy.array(data, dtype='d', copy=False)

            self.filename = None
            self.name = name

            self.projection = Projection(projection)
            self.geotransform = geotransform

            self.rows = data.shape[0]
            self.columns = data.shape[1]

            self.number_of_bands = 1

    def __str__(self):
        """Render as name
        """
        return self.name

    def __len__(self):
        """Size of data set defined as total number of grid points
        """
        return len(self.get_data().flat)

    def __eq__(self, other, rtol=1.0e-5, atol=1.0e-8):
        """Override '==' to allow comparison with other raster objecs

        Input
           other: Raster instance to compare to
           rtol, atol: Relative and absolute tolerance.
                       See numpy.allclose for details
        """

        # Check type
        if not isinstance(other, Raster):
            msg = ('Raster instance cannot be compared to %s'
                   ' as its type is %s ' % (str(other), type(other)))
            raise TypeError(msg)

        # Check projection
        if self.projection != other.projection:
            return False

        # Check geotransform
        if self.get_geotransform() != other.get_geotransform():
            return False

        # Check data
        if not nanallclose(self.get_data(),
                           other.get_data(),
                           rtol=rtol, atol=atol):
            return False

        # Check keywords
        if self.keywords != other.keywords:
            return False

        # Raster layers are identical up to the specified tolerance
        return True

    def __ne__(self, other):
        """Override '!=' to allow comparison with other projection objecs
        """
        return not self == other

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_filename(self):
        return self.filename

    def get_keywords(self, key=None):
        """Return keywords dictionary
        """
        if key is None:
            return self.keywords
        else:
            if key in self.keywords:
                return self.keywords[key]
            else:
                msg = ('Keyword "%s" does not exist in %s: Options are '
                       '%s' % (key, self.get_name(), self.keywords.keys()))
                raise Exception(msg)

    def get_style_info(self):
        """Return style_info dictionary
        """
        return self.style_info

    def get_caption(self):
        """Return 'impact_summary' keyword if present. Otherwise ''.
        """
        if 'impact_summary' in self.keywords:
            return self.keywords['impact_summary']
        else:
            return ''

    def get_impact_summary(self):
        """Return 'impact_summary' keyword if present. Otherwise ''.
        """
        if 'impact_summary' in self.keywords:
            return self.keywords['impact_summary']
        else:
            return ''

    def read_from_file(self, filename):

        # Open data file for reading
        # File must be kept open, otherwise GDAL methods segfault.
        fid = self.fid = gdal.Open(filename, gdal.GA_ReadOnly)
        if fid is None:
            msg = 'Could not open file %s' % filename
            raise Exception(msg)

        # Record raster metadata from file
        basename, ext = os.path.splitext(filename)

        # If file is ASCII, check that projection is around.
        # GDAL does not check this nicely, so it is worth an
        # error message
        if ext == '.asc':
            try:
                open(basename + '.prj')
            except IOError:
                msg = ('Projection file not found for %s. You must supply '
                       'a projection file with extension .prj' % filename)
                raise RuntimeError(msg)

        # Look for any keywords
        self.keywords = read_keywords(basename + '.keywords')

        # Determine name
        if 'title' in self.keywords:
            rastername = self.keywords['title']
        else:
            # Use basename without leading directories as name
            rastername = os.path.split(basename)[-1]

        self.name = rastername
        self.filename = filename

        self.projection = Projection(self.fid.GetProjection())
        self.geotransform = self.fid.GetGeoTransform()
        self.columns = fid.RasterXSize
        self.rows = fid.RasterYSize
        self.number_of_bands = fid.RasterCount

        # Assume that file contains all data in one band
        msg = 'Only one raster band currently allowed'
        if self.number_of_bands > 1:
            msg = ('WARNING: Number of bands in %s are %i. '
                   'Only the first band will currently be '
                   'used.' % (filename, self.number_of_bands))
            # FIXME(Ole): Let us use python warnings here
            raise Exception(msg)

        # Get first band.
        band = self.band = fid.GetRasterBand(1)
        if band is None:
            msg = 'Could not read raster band from %s' % filename
            raise Exception(msg)

    def write_to_file(self, filename):
        """Save raster data to file

        Input
            filename: filename with extension .tif
        """

        # Check file format
        basename, extension = os.path.splitext(filename)

        msg = ('Invalid file type for file %s. Only extension '
               'tif allowed.' % filename)
        verify(extension in ['.tif', '.asc'], msg)
        format = DRIVER_MAP[extension]

        # Get raster data
        A = self.get_data()

        # Get Dimensions. Note numpy and Gdal swap order
        N, M = A.shape

        # Create empty file.
        # FIXME (Ole): It appears that this is created as single
        #              precision even though Float64 is specified
        #              - see issue #17
        driver = gdal.GetDriverByName(format)
        fid = driver.Create(filename, M, N, 1, gdal.GDT_Float64)
        if fid is None:
            msg = ('Gdal could not create filename %s using '
                   'format %s' % (filename, format))
            raise Exception(msg)

        # Write metada
        fid.SetProjection(str(self.projection))
        fid.SetGeoTransform(self.geotransform)

        # Write data
        fid.GetRasterBand(1).WriteArray(A)

        # Write keywords if any
        write_keywords(self.keywords, basename + '.keywords')

    def interpolate(self, X, name=None):
        """Interpolate values of this raster layer to other layer

        Input
            X: Layer object defining target
            name: Optional name of interpolated layer.
                  If name is None, the name of self is used.

        Output
            Y: Layer object with values of this raster layer interpolated to
               geometry of input layer X

        Note: If target geometry is polygon, data will be interpolated to
        its centroids and the output is a point data set.
        """

        if X.is_raster:
            if self.get_geotransform() != X.get_geotransform():
                # Need interpolation between grids
                msg = 'Intergrid interpolation not yet implemented'
                raise Exception(msg)
            else:
                # Rasters are aligned, no need to interpolate
                return self
        else:
            # Interpolate this raster layer to geometry of X
            msg = ('Name must be either a string or None. I got %s'
                   % (str(type(X)))[1:-1])
            verify(name is None or isinstance(name, basestring), msg)

            return interpolate_raster_vector(self, X, name)

    def get_data(self, nan=True, scaling=None):
        """Get raster data as numeric array

        Input
            nan: Optional flag controlling handling of missing values.
                 If nan is True (default), nodata values will be replaced
                 with numpy.nan
                 If keyword nan has a numeric value, nodata values will
                 be replaced by that value. E.g. to set missing values to 0,
                 do get_data(nan=0.0)
            scaling: Optional flag controlling if data is to be scaled
                     if it has been resampled. Admissible values are
                     False: data is retrieved without modification.
                     True: Data is rescaled based on the squared ratio between
                           its current and native resolution. This is typically
                           required if raster data represents a density
                           such as population per km^2
                     None: The behaviour will depend on the keyword
                           "population" associated with the layer. If
                           it is "density", scaling will be applied
                           otherwise not. This is the default.
                     scalar value: If scaling takes a numerical scalar value,
                                   that will be use to scale the data

        """

        if hasattr(self, 'data'):
            A = self.data
            verify(A.shape[0] == self.rows and A.shape[1] == self.columns)
        else:
            # Read from raster file
            A = self.band.ReadAsArray()

            # Convert to double precision (issue #75)
            A = numpy.array(A, dtype=numpy.float64)

            # Self check
            M, N = A.shape
            msg = ('Dimensions of raster array do not match those of '
                   'raster file %s' % self.filename)
            verify(M == self.rows, msg)
            verify(N == self.columns, msg)

        # Handle no data value
        if nan is False:
            pass
        else:
            if nan is True:
                NAN = numpy.nan
            else:
                NAN = nan

            # Replace NODATA_VALUE with NaN
            nodata = self.get_nodata_value()

            NaN = numpy.ones(A.shape, A.dtype) * NAN
            A = numpy.where(A == nodata, NaN, A)

        # Take care of possible scaling
        if scaling is None:
            # Redefine scaling from density keyword if possible
            kw = self.get_keywords()
            if 'datatype' in kw and kw['datatype'].lower() == 'density':
                scaling = True
            else:
                scaling = False

        if scaling is False:
            # No change
            sigma = 1
        elif scaling is True:
            # Calculate scaling based on resolution change

            actual_res = self.get_resolution(isotropic=True)
            native_res = self.get_resolution(isotropic=True, native=True)
            #print
            #print 'Actual res', actual_res
            #print 'Native res', native_res
            sigma = (actual_res / native_res) ** 2
            #print 'Scaling', sigma
        else:
            # See if scaling can work as a scalar value
            try:
                sigma = float(scaling)
            except Exception, e:
                msg = ('Keyword scaling "%s" could not be converted to a '
                       'number. It must be either True, False, None or a '
                       'number: %s' % (scaling, str(e)))
                raise Exception(msg)

        # Return possibly scaled data
        return sigma * A

    def get_projection(self, proj4=False):
        """Return projection of this layer as a string.
        """
        return self.projection.get_projection(proj4)

    def get_geotransform(self):
        """Return geotransform for this raster layer

        Output
        geotransform: 6 digit vector
                      (top left x, w-e pixel resolution, rotation,
                       top left y, rotation, n-s pixel resolution).

                       See e.g. http://www.gdal.org/gdal_tutorial.html
        """

        return self.geotransform

    def get_geometry(self):
        """Return longitudes and latitudes (the axes) for grid.

        Return two vectors (longitudes and latitudes) corresponding to
        grid. The values are offset by half a pixel size to correspond to
        pixel registration.

        I.e. If the grid origin (top left corner) is (105, 10) and the
        resolution is 1 degrees in each direction, then the vectors will
        take the form

        longitudes = [100.5, 101.5, ..., 109.5]
        latitudes = [0.5, 1.5, ..., 9.5]
        """

        # Get parameters for axes
        g = self.get_geotransform()

        lon_ul = g[0]  # Longitude of upper left corner
        lat_ul = g[3]  # Latitude of upper left corner
        dx = g[1]      # Longitudinal resolution
        dy = - g[5]    # Latitudinal resolution (always(?) negative)
        nx = self.columns
        ny = self.rows

        verify(dx > 0)
        verify(dy > 0)

        # Coordinates of lower left corner
        lon_ll = lon_ul
        lat_ll = lat_ul - ny * dy

        # Coordinates of upper right corner
        lon_ur = lon_ul + nx * dx

        # Define pixel centers along each directions
        dy2 = dy / 2
        dx2 = dx / 2

        # Define longitudes and latitudes for each axes
        x = numpy.linspace(lon_ll + dx2,
                           lon_ur - dx2, nx)
        y = numpy.linspace(lat_ll + dy2,
                           lat_ul - dy2, ny)

        # Return
        return x, y

    def __mul__(self, other):
        return self.get_data() * other.get_data()

    def __add__(self, other):
        return self.get_data() + other.get_data()

    def get_extrema(self):
        """Get min and max from raster
        If raster has a nominated no_data value, this is ignored.

        Return min, max
        """

        A = self.get_data(nan=True)
        min = numpy.nanmin(A.flat[:])
        max = numpy.nanmax(A.flat[:])

        return min, max

    def get_nodata_value(self):
        """Get the internal representation of NODATA

        If the internal value is None, the standard -9999 is assumed
        """

        if hasattr(self, 'band'):
            nodata = self.band.GetNoDataValue()
        else:
            nodata = None

        # Use common default in case nodata was not registered in raster file
        if nodata is None:
            nodata = -9999

        return nodata

    def get_bins(self, N=10, quantiles=False):
        """Get N values between the min and the max occurred in this dataset.

        Return sorted list of length N+1 where the first element is min and
        the last is max. Intermediate values depend on the keyword quantiles:
        If quantiles is True, they represent boundaries between quantiles.
        If quantiles is False, they represent equidistant interval boundaries.
        """

        min, max = self.get_extrema()

        levels = []
        if quantiles is False:
            # Linear intervals
            d = (max - min) / N

            for i in range(N):
                levels.append(min + i * d)
        else:
            # Quantiles
            # FIXME (Ole): Not 100% sure about this algorithm,
            # but it is close enough

            A = self.get_data(nan=True).flat[:]

            mask = numpy.logical_not(numpy.isnan(A))  # Omit NaN's
            A = A.compress(mask)

            A.sort()

            verify(len(A) == A.shape[0])

            d = float(len(A) + 0.5) / N
            for i in range(N):
                levels.append(A[int(i * d)])

        levels.append(max)

        return levels

    def get_bounding_box(self):
        """Get bounding box coordinates for raster layer

        Format is [West, South, East, North]
        """

        return geotransform2bbox(self.geotransform, self.columns, self.rows)

    def get_resolution(self, isotropic=False, native=False):
        """Get raster resolution as a 2-tuple (resx, resy)

        Input
            isotropic: If True, verify that dx == dy and return dx
                       If False return 2-tuple (dx, dy)
            native: Optional flag. If True, return native resolution if
                                   available. Otherwise return actual.
        """

        # Get actual resolution first
        try:
            res = geotransform2resolution(self.geotransform,
                                          isotropic=isotropic)
        except Exception, e:
            msg = ('Resolution for layer %s could not be obtained: %s '
                   % (self.get_name(), str(e)))
            raise Exception(msg)

        if native:
            keywords = self.get_keywords()
            if 'resolution' in keywords:

                resolution = keywords['resolution']
                try:
                    res = float(resolution)
                except:
                    # Assume resolution is a string of the form:
                    # (0.00045228819716044, 0.00045228819716044)

                    msg = ('Unknown format for resolution keyword: %s'
                           % resolution)
                    verify((resolution.startswith('(') and
                            resolution.endswith(')')), msg)

                    dx, dy = [float(s) for s in resolution[1:-1].split(',')]
                    if not isotropic:
                        res = (dx, dy)
                    else:
                        msg = ('Resolution of layer "%s" was not isotropic: '
                               '[dx, dy] == %s' % (self.get_name(), res))
                        verify(numpy.allclose(dx, dy,
                                              rtol=1.0e-12, atol=1.0e-12), msg)
                        res = dx
                else:
                    if not isotropic:
                        res = (res, res)

        # Return either 2-tuple or scale depending on isotropic
        return res

    @property
    def is_raster(self):
        return True

    @property
    def is_vector(self):
        return False

    @property
    def is_inasafe_spatial_object(self):
        return True
