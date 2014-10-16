"""**Class Raster**
"""

import os
import gc
import numpy
import copy as copy_module
from osgeo import gdal

qgis_imported = True
try:
    from qgis.core import (
        QgsRasterLayer,
        QgsRasterFileWriter,
        QgsRasterPipe
    )
except ImportError:
    qgis_imported = False

from safe.common.utilities import (verify,
                                   ugettext as safe_tr,
                                   unique_filename)
from safe.common.numerics import (nan_allclose,
                                  geotransform_to_axes,
                                  grid_to_points)
from safe.common.exceptions import ReadLayerError, WriteLayerError
from safe.common.exceptions import GetDataError, InaSAFEError

from layer import Layer
from vector import Vector
from projection import Projection

from utilities import DRIVER_MAP
from utilities import read_keywords
from utilities import write_keywords
from utilities import (geotransform_to_bbox, geotransform_to_resolution,
                       check_geotransform)
from utilities import safe_to_qgis_layer


class Raster(Layer):
    """InaSAFE representation of raster data

    Args:
        * data: Can be either
            * a filename of a raster file format known to GDAL
            * an MxN array of raster data
            * None (FIXME (Ole): Don't think we need this option)
        * projection: Geospatial reference in WKT format.
            Only used if data is provide as a numeric array,
            if None, WGS84 geographic is assumed
        * geotransform: GDAL geotransform (6-tuple).
            (top left x, w-e pixel resolution, rotation,
            top left y, rotation, n-s pixel resolution).
            See e.g. http://www.gdal.org/gdal_tutorial.html
            Only used if data is provide as a numeric array,
        * name: Optional name for layer. If None, basename is used.
        * keywords: Optional dictionary with keywords that describe the
            layer. When the layer is stored, these keywords will
            be written into an associated file with extension .keywords.
            Keywords can for example be used to display text
            about the layer in a web application.
        * style_info: Dictionary with information about how this layer
            should be styled. See impact_functions/styles.py
            for examples.

    Returns:
        * InaSAFE raster layer instance

    Raises:
        * TypeError, ReadLayerError, WriteLayerError, InaSAFEError,
          GetDataError

    Note:
        If data is a filename, all other arguments are ignored
        as they will be inferred from the file.
    """

    def __init__(self, data=None, projection=None, geotransform=None,
                 name=None, keywords=None, style_info=None):
        """Initialise object with either data or filename

        NOTE: Doc strings in constructor are not harvested and exposed in
        online documentation. Hence the details are specified in the
        class docstring.
        """

        # Invoke common layer constructor
        Layer.__init__(self,
                       name=name,
                       projection=projection,
                       keywords=keywords,
                       style_info=style_info)

        # Input checks
        if data is None:
            # Instantiate empty object
            self.geotransform = None
            self.rows = self.columns = 0
            return

        # Initialisation
        if isinstance(data, basestring):
            self.read_from_file(data)
        elif isinstance(data, QgsRasterLayer):
            self.read_from_qgis_native(data)
        else:
            # Assume that data is provided as a numpy array
            # with extra keyword arguments supplying metadata

            self.data = numpy.array(data, dtype='d', copy=False)

            proj4 = self.get_projection(proj4=True)
            if 'longlat' in proj4 and 'WGS84' in proj4:
                # This is only implemented for geographic coordinates
                # Omit check for projected coordinate systems
                check_geotransform(geotransform)
            self.geotransform = geotransform

            self.rows = data.shape[0]
            self.columns = data.shape[1]

            self.number_of_bands = 1

    def __str__(self):
        """Render as name and dimensions
        """
        return ('Raster data set: %s [%i x %i] '
                % (self.name, self.rows, self.columns))

    def __len__(self):
        """Size of data set defined as total number of grid points
        """
        return len(self.get_data().flat)

    def __eq__(self, other, rtol=1.0e-5, atol=1.0e-8):
        """Override '==' to allow comparison with other raster objecs

        Args:
           * other: Raster instance to compare to
           * rtol, atol: Relative and absolute tolerance.
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
        if not nan_allclose(
                self.get_data(),
                other.get_data(),
                rtol=rtol, atol=atol):
            return False

        # Check keywords
        if self.keywords != other.keywords:
            return False

        # Raster layers are identical up to the specified tolerance
        return True

    def read_from_file(self, filename):
        """Read and unpack raster data
        """

        # Open data file for reading
        # File must be kept open, otherwise GDAL methods segfault.
        fid = self.fid = gdal.Open(filename, gdal.GA_ReadOnly)
        if fid is None:
            # As gdal doesn't return to us what the problem is we have to
            # figure it out ourselves. Maybe capture stderr?
            if not os.path.exists(filename):
                msg = 'Could not find file %s' % filename
            else:
                msg = ('File %s exists, but could not be read. '
                       'Please check if the file can be opened with '
                       'e.g. qgis or gdalinfo' % filename)
            raise ReadLayerError(msg)

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
                raise ReadLayerError(msg)

        # Look for any keywords
        self.keywords = read_keywords(basename + '.keywords')

        # Determine name
        if 'title' in self.keywords:
            title = self.keywords['title']

            # Lookup internationalised title if available
            title = safe_tr(title)

            rastername = title
        else:
            # Use basename without leading directories as name
            rastername = os.path.split(basename)[-1]

        if self.name is None:
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
            raise ReadLayerError(msg)

        # Get first band.
        band = self.band = fid.GetRasterBand(1)
        if band is None:
            msg = 'Could not read raster band from %s' % filename
            raise ReadLayerError(msg)

        # Force garbage collection to free up any memory we can (TS)
        gc.collect()

        # Read from raster file
        data = band.ReadAsArray()

        # Convert to double precision (issue #75)
        data = numpy.array(data, dtype=numpy.float64)

        # Self check
        M, N = data.shape
        msg = (
            'Dimensions of raster array do not match those of '
            'raster file %s' % self.filename)
        verify(M == self.rows, msg)
        verify(N == self.columns, msg)
        nodata = self.band.GetNoDataValue()
        if nodata is None:
            nodata = -9999

        if nodata is not numpy.nan:
            NaN = numpy.ones((M, N), numpy.float64) * numpy.nan
            data = numpy.where(data == nodata, NaN, data)

        self.data = data

    def write_to_file(self, filename):
        """Save raster data to file

        Args:
            * filename: filename with extension .tif

        Gdal documentation at: http://www.gdal.org/classGDALRasterBand.html
        """

        # Check file format
        basename, extension = os.path.splitext(filename)

        msg = ('Invalid file type for file %s. Only extension '
               'tif allowed.' % filename)
        verify(extension in ['.tif'], msg)
        file_format = DRIVER_MAP[extension]

        # Get raster data
        A = self.get_data()

        # Get Dimensions. Note numpy and Gdal swap order
        N, M = A.shape

        # Create empty file.
        # FIXME (Ole): It appears that this is created as single
        #              precision even though Float64 is specified
        #              - see issue #17
        driver = gdal.GetDriverByName(file_format)
        fid = driver.Create(filename, M, N, 1, gdal.GDT_Float64)
        if fid is None:
            msg = ('Gdal could not create filename %s using '
                   'format %s' % (filename, file_format))
            raise WriteLayerError(msg)

        self.filename = filename

        # Write metada
        fid.SetProjection(str(self.projection))
        fid.SetGeoTransform(self.geotransform)

        # Write data
        fid.GetRasterBand(1).WriteArray(A)
        fid.GetRasterBand(1).SetNoDataValue(self.get_nodata_value())
        fid = None  # Close

        # Write keywords if any
        write_keywords(self.keywords, basename + '.keywords')

    def read_from_qgis_native(self, qgis_layer):
        """Read raster data from qgis layer QgsRasterLayer.

            A stub is used now:
                save all data in a file,
                then call safe.read_from_file

            Raises:
                * TypeError         if qgis is not avialable
                * IOError           if can't store temporary file
                * GetDataError      if can't create copy of qgis_layer's
                                        dataProvider
        """
        if not qgis_imported:   # FIXME (DK): this branch isn't covered by test
            msg = ('Used data is QgsRasterLayer instance, '
                   'but QGIS is not available.')
            raise TypeError(msg)

        base_name = unique_filename()
        file_name = base_name + '.tif'

        file_writer = QgsRasterFileWriter(file_name)
        pipe = QgsRasterPipe()
        provider = qgis_layer.dataProvider()
        if not pipe.set(provider.clone()):
            msg = "Cannot set pipe provider"
            raise GetDataError(msg)

        file_writer.writeRaster(
            pipe,
            provider.xSize(),
            provider.ySize(),
            provider.extent(),
            provider.crs())

        # Write keywords if any
        write_keywords(self.keywords, base_name + '.keywords')
        self.read_from_file(file_name)

    def as_qgis_native(self):
        """Return raster layer data as qgis QgsRasterayer.

            A stub is used now:
                save all data in a file,
                then create QgsRaterLayer from the file.

            Raises:
                * TypeError         if qgis is not avialable
        """
        if not qgis_imported:   # FIXME (DK): this branch isn't covered by test
            msg = ('Tried to convert layer to QgsRasterLayer instance, '
                   'but QGIS is not avialable.')
            raise TypeError(msg)

        qgis_layer = safe_to_qgis_layer(self)
        return qgis_layer

    def get_data(self, nan=True, scaling=None, copy=False):
        """Get raster data as numeric array

        Args:
            * nan: Optional flag controlling handling of missing values.

                   If keyword nan has a numeric value, nodata values will
                   be replaced by that value. E.g. to set missing values to 0,
                   do get_data(nan=0.0)

                   NOTE: The following behaviour is depricated,
                   since we handle this on file load:
                   [If nan is True (default), nodata values will be replaced
                   with numpy.nan]


            * scaling: Optional flag controlling if data is to be scaled
                       if it has been resampled. Admissible values are

                       False: data is retrieved without modification.

                       True: Data is rescaled based on the squared ratio
                             between its current and native resolution. This
                             is typically required if raster data represents a
                             density such as population per km^2

                       None: The behaviour will depend on the keyword
                             "population" associated with the layer. If
                             it is "density", scaling will be applied
                             otherwise not. This is the default.

                       scalar value: If scaling takes a numerical scalar value,
                                     that will be use to scale the data

            * copy (optional): If present and True return copy

        Note:
            Scaling does not currently work with projected layers.
            See issue #123
        """

        if copy:
            A = copy_module.deepcopy(self.data)
        else:
            A = self.data
            verify(A.shape[0] == self.rows and A.shape[1] == self.columns)

        # Handle no data value
        # Must explicit comparison to False and True as nan can be a number
        # so 0 would evaluate to False and e.g. 1 to True.
        if type(nan) is not bool:
            # We are handling all non-NaN's in read_from_file and
            # assuming NaN's in internal numpy arrays [issue #297].
            try:
                # Use user specified number
                new_nodata_value = float(nan)
            except (ValueError, TypeError):
                msg = ('Argument nan must be either True, False or a '
                       'number. I got "nan=%s"' % str(nan))
                raise InaSAFEError(msg)

            # Replace NODATA_VALUE with NaN array
            NoData = numpy.ones(A.shape, A.dtype) * new_nodata_value
            A = numpy.where(numpy.isnan(A), NoData, A)

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
            sigma = (actual_res / native_res) ** 2
        else:
            # See if scaling can work as a scalar value
            try:
                sigma = float(scaling)
            except ValueError, e:
                msg = ('Keyword scaling "%s" could not be converted to a '
                       'number. It must be either True, False, None or a '
                       'number: %s' % (scaling, str(e)))
                raise GetDataError(msg)

        # Return possibly scaled data
        return sigma * A

    def get_geotransform(self, copy=False):
        """Return geotransform for this raster layer

        Returns:

        * geotransform: 6 digit vector
            (top left x, w-e pixel resolution, rotation,
            top left y, rotation, n-s pixel resolution).

            See e.g. http://www.gdal.org/gdal_tutorial.html

        * copy (optional): If present and True return copy
        """

        if copy:
            return copy_module.copy(self.geotransform)
        else:
            return self.geotransform

    def get_geometry(self):
        """Return longitudes and latitudes (the axes) for grid.

        Note:
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
        nx = self.columns
        ny = self.rows

        # Compute x and y axes
        x, y = geotransform_to_axes(g, nx, ny)

        # Return them
        return x, y

    def copy(self):
        """Return copy of raster layer

        This copy will be equal to self in the sense defined by __eq__
        """

        return Raster(data=self.get_data(copy=True),
                      geotransform=self.get_geotransform(copy=True),
                      projection=self.get_projection(),
                      keywords=self.get_keywords())

    def __mul__(self, other):
        return self.get_data() * other.get_data()

    def __add__(self, other):
        return self.get_data() + other.get_data()

    def get_extrema(self):
        """Get min and max from raster

        Note:
          If raster has a nominated no_data value, this is ignored.

        Returns:
          min, max
        """

        A = self.get_data()
        Amin = numpy.nanmin(A.flat[:])
        Amax = numpy.nanmax(A.flat[:])

        return Amin, Amax

    def get_nodata_value(self):
        """Get the internal representation of NODATA

        Note:
            This is always numpy.NaN [issue #297]
        """
        return numpy.nan

    def get_bins(self, N=10, quantiles=False):
        """Get N values between the min and the max occurred in this dataset.

        Return sorted list of length N+1 where the first element is min and
        the last is max. Intermediate values depend on the keyword quantiles:
        If quantiles is True, they represent boundaries between quantiles.
        If quantiles is False, they represent equidistant interval boundaries.
        """

        rmin, rmax = self.get_extrema()

        levels = []
        if quantiles is False:
            # Linear intervals
            d = (rmax - rmin) / N

            for i in range(N):
                levels.append(rmin + i * d)
        else:
            # Quantiles
            # FIXME (Ole): Not 100% sure about this algorithm,
            # but it is close enough

            A = self.get_data().flat[:]

            mask = numpy.logical_not(numpy.isnan(A))  # Omit NaN's
            A = A.compress(mask)

            A.sort()

            verify(len(A) == A.shape[0])

            d = float(len(A) + 0.5) / N
            for i in range(N):
                levels.append(A[int(i * d)])

        levels.append(rmax)

        return levels

    def get_bounding_box(self):
        """Get bounding box coordinates for raster layer

        Note:
            Format is [West, South, East, North]
        """

        return geotransform_to_bbox(self.geotransform, self.columns, self.rows)

    def get_resolution(self, isotropic=False, native=False):
        """Get raster resolution as a 2-tuple (resx, resy)

        Args:
            * isotropic: If True, verify that dx == dy and return dx
                         If False return 2-tuple (dx, dy)
            * native: Optional flag. If True, return native resolution if
                                     available. Otherwise return actual.
        """

        # Get actual resolution first
        try:
            res = geotransform_to_resolution(self.geotransform,
                                          isotropic=isotropic)
        except Exception, e:
            msg = ('Resolution for layer %s could not be obtained: %s '
                   % (self.get_name(), str(e)))
            raise InaSAFEError(msg)

        if native:
            keywords = self.get_keywords()
            if 'resolution' in keywords:

                resolution = keywords['resolution']
                try:
                    res = float(resolution)
                except TypeError:
                    # Assume resolution is a tuple of the form:
                    # (0.00045228819716044, 0.00045228819716044)

                    msg = ('Unknown format for resolution keyword: %s'
                           % str(resolution))
                    verify(isinstance(resolution, tuple), msg)

                    dx, dy = [float(s) for s in resolution]
                    if not isotropic:
                        res = (dx, dy)
                    else:
                        res = (dx + dy) / 2
                else:
                    if not isotropic:
                        res = (res, res)

        # Return either 2-tuple or scale depending on isotropic
        return res

    def to_vector_points(self):
        """Convert raster grid to vector point data

        Returns:
           * coordinates: Nx2 array of x, y (lon, lat) coordinates
           * values: N array of corresponding grid values
        """

        # Convert grid data to point data
        A = self.get_data()
        x, y = self.get_geometry()
        P, V = grid_to_points(A, x, y)

        return P, V

    def to_vector_layer(self):
        """Convert raster grid to vector point data

        Returns:
            a vector layer object with data points corresponding to
            grid points. The order is row-major which means that the
            x (longitude) direction is varying the fastest.
        """

        # Get vector data
        coordinates, values = self.to_vector_points()

        # Create corresponding vector layer
        attributes = [{'value': x} for x in values]
        V = Vector(geometry=coordinates,
                   data=attributes,
                   projection=self.get_projection(),
                   geometry_type='point')

        return V
