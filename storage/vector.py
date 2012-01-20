"""Class Vector
"""

import os
import numpy
from osgeo import ogr, gdal
from projection import Projection
from utilities import DRIVER_MAP, TYPE_MAP
from utilities import read_keywords
from utilities import write_keywords
from utilities import get_geometry_type
from utilities import is_sequence
from utilities import array2wkt
from utilities import calculate_polygon_centroid
from utilities import points_along_line
from utilities import geometrytype2string


# FIXME (Ole): Consider using pyshp to read and write shapefiles
#              See http://code.google.com/p/pyshp
class Vector:
    """Class for abstraction of vector data
    """

    def __init__(self, data=None, projection=None, geometry=None,
                 name='', keywords=None, style_info=None):
        """Initialise object with either geometry or filename

        Input
            data: Can be either
                * a filename of a vector file format known to GDAL
                * List of dictionaries of fields associated with
                  point coordinates
                * None
            projection: Geospatial reference in WKT format.
                        Only used if geometry is provide as a numeric array,
            geometry: A list of either point coordinates or polygons
            name: Optional name for layer.
                  Only used if geometry is provide as a numeric array
            keywords: Optional dictionary with keywords that describe the
                      layer. When the layer is stored, these keywords will
                      be written into an associated file with extension
                      .keywords.

                      Keywords can for example be used to display text
                      about the layer in a web application.

        Note that if data is a filename, all other arguments are ignored
        as they will be inferred from the file.

        The geometry type will be inferred from the dimensions of geometry.
        If each entry is one set of coordinates the type will be ogr.wkbPoint,
        if it is an array of coordinates the type will be ogr.wkbPolygon.
        """

        if data is None and projection is None and geometry is None:
            # Instantiate empty object
            self.name = name
            self.projection = None
            self.geometry = None
            self.geometry_type = None
            self.filename = None
            self.data = None
            self.extent = None
            self.keywords = {}
            self.style_info = {}
            return

        if isinstance(data, basestring):
            self.read_from_file(data)
        else:
            # Assume that data is provided as sequences provided as
            # arguments to the Vector constructor
            # with extra keyword arguments supplying metadata

            self.name = name
            self.filename = None

            if keywords is None:
                self.keywords = {}
            else:
                msg = ('Specified keywords must be either None or a '
                       'dictionary. I got %s' % keywords)
                assert isinstance(keywords, dict), msg
                self.keywords = keywords

            if style_info is None:
                self.style_info = {}
            else:
                msg = ('Specified style_info must be either None or a '
                       'dictionary. I got %s' % style_info)
                assert isinstance(style_info, dict), msg
                self.style_info = style_info

            msg = 'Geometry must be specified'
            assert geometry is not None, msg

            msg = 'Geometry must be a sequence'
            assert is_sequence(geometry), msg
            self.geometry = geometry

            self.geometry_type = get_geometry_type(geometry)

            msg = 'Projection must be specified'
            assert projection is not None, msg
            self.projection = Projection(projection)

            self.data = data
            if data is not None:
                msg = 'Data must be a sequence'
                assert is_sequence(data), msg

                msg = ('The number of entries in geometry and data '
                       'must be the same')
                assert len(geometry) == len(data), msg

            # FIXME: Need to establish extent here

    def __str__(self):
        """Render as name, number of features, geometry type
        """

        g_type_str = geometrytype2string(self.geometry_type)
        return ('Vector data set: %s, %i features, geometry type '
                '%s (%s)' % (self.name,
                             len(self),
                             str(self.geometry_type),
                             g_type_str))

    def __len__(self):
        """Size of vector layer defined as number of features
        """

        return len(self.geometry)

    def __eq__(self, other, rtol=1.0e-5, atol=1.0e-8):
        """Override '==' to allow comparison with other vector objecs

        Input
           other: Vector instance to compare to
           rtol, atol: Relative and absolute tolerance.
                       See numpy.allclose for details
        """

        # Check type
        if not isinstance(other, Vector):
            msg = ('Vector instance cannot be compared to %s'
                   ' as its type is %s ' % (str(other), type(other)))
            raise TypeError(msg)

        # Check projection
        if self.projection != other.projection:
            return False

        # Check geometry
        if not numpy.allclose(self.get_geometry(),
                              other.get_geometry(),
                              rtol=rtol, atol=atol):
            return False

        # Check keys
        x = self.get_data()
        y = other.get_data()

        for key in x[0]:
            for i in range(len(y)):
                if key not in y[i]:
                    return False

        for key in y[0]:
            for i in range(len(x)):
                if key not in x[i]:
                    return False

        # Check data
        for i, a in enumerate(x):
            for key in a:
                if a[key] != y[i][key]:
                    # Not equal, try numerical comparison with tolerances

                    if not numpy.allclose(a[key], y[i][key],
                                          rtol=rtol, atol=atol):
                        return False

        # Check keywords
        if self.keywords != other.keywords:
            return False

        # Vector layers are identical up to the specified tolerance
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
                msg = ('Keyword %s does not exist in %s: Options are '
                       '%s' % (key, self.get_name(), self.keywords.keys()))
                raise Exception(msg)

    def get_style_info(self):
        """Return style_info dictionary
        """
        return self.style_info

    def get_caption(self):
        """Return 'caption' keyword if present. Otherwise ''.
        """
        if 'caption' in self.keywords:
            return self.keywords['caption']
        else:
            return ''

    def read_from_file(self, filename):
        """ Read and unpack vector data.

        It is assumed that the file contains only one layer with the
        pertinent features. Further it is assumed for the moment that
        all geometries are points.

        * A feature is a geometry and a set of attributes.
        * A geometry refers to location and can be point, line, polygon or
          combinations thereof.
        * The attributes or obtained through GetField()

        The full OGR architecture is documented at
        * http://www.gdal.org/ogr/ogr_arch.html
        * http://www.gdal.org/ogr/ogr_apitut.html

        Examples are at
        * danieljlewis.org/files/2010/09/basicpythonmap.pdf
        * http://invisibleroads.com/tutorials/gdal-shapefile-points-save.html
        * http://www.packtpub.com/article/geospatial-data-python-geometry
        """

        basename, _ = os.path.splitext(filename)

        # Look for any keywords
        self.keywords = read_keywords(basename + '.keywords')

        # FIXME (Ole): Should also look for style file to populate style_info

        # Determine name
        if 'title' in self.keywords:
            vectorname = self.keywords['title']
        else:
            # Use basename without leading directories as name
            vectorname = os.path.split(basename)[-1]

        self.name = vectorname
        self.filename = filename
        self.geometry_type = None  # In case there are no features

        fid = ogr.Open(filename)
        if fid is None:
            msg = 'Could not open %s' % filename
            raise IOError(msg)

        # Assume that file contains all data in one layer
        msg = 'Only one vector layer currently allowed'
        if fid.GetLayerCount() > 1:
            msg = ('WARNING: Number of layers in %s are %i. '
                   'Only the first layer will currently be '
                   'used.' % (filename, fid.GetLayerCount()))
            raise Exception(msg)

        layer = fid.GetLayerByIndex(0)

        # Get spatial extent
        self.extent = layer.GetExtent()

        # Get projection
        p = layer.GetSpatialRef()
        self.projection = Projection(p)

        # Get number of features
        N = layer.GetFeatureCount()

        # Extract coordinates and attributes for all features
        geometry = []
        data = []
        for i in range(N):
            feature = layer.GetFeature(i)
            if feature is None:
                msg = 'Could not get feature %i from %s' % (i, filename)
                raise Exception(msg)

            # Record coordinates ordered as Longitude, Latitude
            G = feature.GetGeometryRef()
            if G is None:
                msg = ('Geometry was None in filename %s ' % filename)
                raise Exception(msg)
            else:
                self.geometry_type = G.GetGeometryType()
                if self.geometry_type == ogr.wkbPoint:
                    geometry.append((G.GetX(), G.GetY()))
                elif self.geometry_type == ogr.wkbLineString:
                    M = G.GetPointCount()
                    coordinates = []
                    for j in range(M):
                        coordinates.append((G.GetX(j), G.GetY(j)))

                    # Record entire line as an Mx2 numpy array
                    geometry.append(numpy.array(coordinates,
                                                dtype='d',
                                                copy=False))
                elif self.geometry_type == ogr.wkbPolygon:
                    ring = G.GetGeometryRef(0)
                    M = ring.GetPointCount()
                    coordinates = []
                    for j in range(M):
                        coordinates.append((ring.GetX(j), ring.GetY(j)))

                    # Record entire polygon ring as an Mx2 numpy array
                    geometry.append(numpy.array(coordinates,
                                                dtype='d',
                                                copy=False))
                #elif self.geometry_type == ogr.wkbMultiPolygon:
                #    # FIXME: Unpact multiple polygons to simple polygons
                #    # For hints on how to unpack see
#http://osgeo-org.1803224.n2.nabble.com/
#gdal-dev-Shapefile-Multipolygon-with-interior-rings-td5391090.html

                #    ring = G.GetGeometryRef(0)
                #    M = ring.GetPointCount()
                #    coordinates = []
                #    for j in range(M):
                #        coordinates.append((ring.GetX(j), ring.GetY(j)))

                #    # Record entire polygon ring as an Mx2 numpy array
                #    geometry.append(numpy.array(coordinates,
                #                                dtype='d',
                #                                copy=False))

                else:
                    msg = ('Only point, line and polygon geometries are '
                           'supported. '
                           'Geometry type in filename %s '
                           'was %s.' % (filename,
                                        self.geometry_type))
                    raise Exception(msg)

            # Record attributes by name
            number_of_fields = feature.GetFieldCount()
            fields = {}
            for j in range(number_of_fields):
                name = feature.GetFieldDefnRef(j).GetName()

                # FIXME (Ole): Ascertain the type of each field?
                #              We need to cast each appropriately?
                #              This is issue #66
                #feature_type = feature.GetFieldDefnRef(j).GetType()
                fields[name] = feature.GetField(j)
                #print 'Field', name, feature_type, j, fields[name]

            data.append(fields)

        # Store geometry coordinates as a compact numeric array
        self.geometry = geometry
        self.data = data

    def write_to_file(self, filename):
        """Save vector data to file

        Input
            filename: filename with extension .shp or .gml

        Note, if attribute names are longer than 10 characters they will be
        truncated. This is due to limitations in the shp file driver and has
        to be done here since gdal v1.7 onwards has changed its handling of
        this issue: http://www.gdal.org/ogr/drv_shapefile.html
        """

        # Check file format
        basename, extension = os.path.splitext(filename)

        msg = ('Invalid file type for file %s. Only extensions '
               'shp or gml allowed.' % filename)
        assert extension == '.shp' or extension == '.gml', msg
        driver = DRIVER_MAP[extension]

        # FIXME (Ole): Tempory flagging of GML issue (ticket #18)
        if extension == '.gml':
            msg = ('OGR GML driver does not store geospatial reference.'
                   'This format is disabled for the time being. See '
                   'https://github.com/AIFDR/riab/issues/18')
            raise Exception(msg)

        # Derive layername from filename (excluding preceding dirs)
        layername = os.path.split(basename)[-1]

        # Get vector data
        geometry = self.get_geometry()
        data = self.get_data()

        N = len(geometry)

        # Clear any previous file of this name (ogr does not overwrite)
        try:
            os.remove(filename)
        except:
            pass

        # Create new file with one layer
        drv = ogr.GetDriverByName(driver)
        if drv is None:
            msg = 'OGR driver %s not available' % driver
            raise Exception(msg)

        ds = drv.CreateDataSource(filename)
        if ds is None:
            msg = 'Creation of output file %s failed' % filename
            raise Exception(msg)

        lyr = ds.CreateLayer(layername,
                             self.projection.spatial_reference,
                             self.geometry_type)
        if lyr is None:
            msg = 'Could not create layer %s' % layername
            raise Exception(msg)

        # Define attributes if any
        store_attributes = False
        if data is not None:
            if len(data) > 0:
                try:
                    fields = data[0].keys()
                except:
                    msg = ('Input parameter "attributes" was specified '
                           'but it does not contain dictionaries with '
                           'field information as expected. The first'
                           'element is %s' % data[0])
                    raise Exception(msg)
                else:
                    # Establish OGR types for each element
                    ogrtypes = {}
                    for name in fields:
                        att = data[0][name]
                        py_type = type(att)
                        msg = ('Unknown type for storing vector '
                               'data: %s, %s' % (name, str(py_type)[1:-1]))
                        assert py_type in TYPE_MAP, msg
                        ogrtypes[name] = TYPE_MAP[py_type]

            else:
                msg = ('Input parameter "data" was specified '
                       'but appears to be empty')
                raise Exception(msg)

            # Create attribute fields in layer
            store_attributes = True
            for name in fields:
                fd = ogr.FieldDefn(name, ogrtypes[name])
                # FIXME (Ole): Trying to address issue #16
                #              But it doesn't work and
                #              somehow changes the values of MMI in test
                #width = max(128, len(name))
                #print name, width
                #fd.SetWidth(width)

                # Silent handling of warnings like
                # Warning 6: Normalized/laundered field name:
                #'CONTENTS_LOSS_AUD' to 'CONTENTS_L'
                gdal.PushErrorHandler('CPLQuietErrorHandler')
                if lyr.CreateField(fd) != 0:
                    msg = 'Could not create field %s' % name
                    raise Exception(msg)

                # Restore error handler
                gdal.PopErrorHandler()

        # Store geometry
        geom = ogr.Geometry(self.geometry_type)
        layer_def = lyr.GetLayerDefn()
        for i in range(N):
            # Create new feature instance
            feature = ogr.Feature(layer_def)

            # Store geometry and check
            if self.geometry_type == ogr.wkbPoint:
                x = float(geometry[i][0])
                y = float(geometry[i][1])
                geom.SetPoint_2D(0, x, y)
            elif self.geometry_type == ogr.wkbPolygon:
                wkt = array2wkt(geometry[i], geom_type='POLYGON')
                geom = ogr.CreateGeometryFromWkt(wkt)
            else:
                msg = 'Geometry type %s not implemented' % self.geometry_type
                raise Exception(msg)

            feature.SetGeometry(geom)

            G = feature.GetGeometryRef()
            if G is None:
                msg = 'Could not create GeometryRef for file %s' % filename
                raise Exception(msg)

            # Store attributes
            if store_attributes:
                for j, name in enumerate(fields):
                    actual_field_name = layer_def.GetFieldDefn(j).GetNameRef()

                    val = data[i][name]
                    if type(val) == numpy.ndarray:
                        # A singleton of type <type 'numpy.ndarray'> works
                        # for gdal version 1.6 but fails for version 1.8
                        # in SetField with error: NotImplementedError:
                        # Wrong number of arguments for overloaded function
                        val = float(val)

                    feature.SetField(actual_field_name, val)

            # Save this feature
            if lyr.CreateFeature(feature) != 0:
                msg = 'Failed to create feature %i in file %s' % (i, filename)
                raise Exception(msg)

            feature.Destroy()

        # Write keywords if any
        write_keywords(self.keywords, basename + '.keywords')

        # FIXME (Ole): Maybe store style_info

    def get_attribute_names(self):
        """ Get available attribute names

        These are the ones that can be used with get_data
        """

        return self.data[0].keys()

    def get_data(self, attribute=None, index=None):
        """Get vector attributes

        Data is returned as a list where each entry is a dictionary of
        attributes for one feature. Entries in get_geometry() and
        get_data() are related as 1-to-1

        If optional argument attribute is specified and a valid name,
        then the list of values for that attribute is returned.

        If optional argument index is specified on the that value will
        be returned. Any value of index is ignored if attribute is None.
        """

        if hasattr(self, 'data'):
            if attribute is None:
                return self.data
            else:
                msg = ('Specified attribute %s does not exist in '
                       'vector layer %s. Valid names are %s'
                       '' % (attribute, self, self.data[0].keys()))
                assert attribute in self.data[0], msg

                if index is None:
                    # Return all values for specified attribute
                    return [x[attribute] for x in self.data]
                else:
                    # Return value for specified attribute and index
                    msg = ('Specified index must be either None or '
                           'an integer. I got %s' % index)
                    assert type(index) == type(0)

                    msg = ('Specified index must lie within the bounds '
                           'of vector layer %s which is [%i, %i]'
                           '' % (self, 0, len(self) - 1))
                    assert 0 <= index < len(self)

                    return self.data[index][attribute]
        else:
            msg = 'Vector data instance does not have any attributes'
            raise Exception(msg)

    def get_geometry(self):
        """Return geometry for vector layer.

        Depending on the feature type, geometry is

        geometry type     output type
        -----------------------------
        point             coordinates (Nx2 array of longitudes and latitudes)
        line              TODO
        polygon           list of arrays of coordinates

        """
        return self.geometry

    def get_projection(self, proj4=False):
        """Return projection of this layer as a string
        """
        return self.projection.get_projection(proj4)

    def get_bounding_box(self):
        """Get bounding box coordinates for vector layer.

        Format is [West, South, East, North]
        """
        e = self.extent
        return [e[0],  # West
                e[2],  # South
                e[1],  # East
                e[3]]  # North

    def get_extrema(self, attribute=None):
        """Get min and max values from specified attribute

        Return min, max
        """
        if attribute is None:
            msg = ('Valid attribute name must be specified in get_extrema '
                   'for vector layers. I got None.')
            raise RuntimeError(msg)

        x = self.get_data(attribute)
        return min(x), max(x)

    def get_topN(self, attribute, N=10):
        """Get top N features

        Input
            attribute: The name of attribute where values are sought
            N: How many

        Output
            layer: New vector layer with selected features
        """

        # FIXME (Ole): Maybe generalise this to arbitrary expressions

        # Input checks
        msg = ('Specfied attribute must be a string. '
               'I got %s' % (type(attribute)))
        assert isinstance(attribute, basestring), msg

        msg = 'Specified attribute was empty'
        assert attribute != '', msg

        msg = 'N must be a positive number. I got %i' % N
        assert N > 0, msg

        # Create list of values for specified attribute
        values = self.get_data(attribute)

        # Sort and select using Schwarzian transform
        A = zip(values, self.data, self.geometry)
        A.sort()

        # Pick top N and unpack
        _, data, geometry = zip(*A[-N:])

        # Create new Vector instance and return
        return Vector(data=data,
                      projection=self.get_projection(),
                      geometry=geometry)

    def interpolate(self, X, name=None):
        """Interpolate values of this vector layer to other layer

        Input
            X: Layer object defining target
            name: Optional name of interpolated layer

        Output
            Y: Layer object with values of this vector layer interpolated to
               geometry of input layer X
        """

        msg = 'Interpolation from vector layers not yet implemented'
        raise Exception(msg)

    @property
    def is_raster(self):
        return False

    @property
    def is_vector(self):
        return True

    @property
    def is_point_data(self):
        return self.is_vector and self.geometry_type == ogr.wkbPoint

    @property
    def is_line_data(self):
        return self.is_vector and self.geometry_type == ogr.wkbLineString

    @property
    def is_polygon_data(self):
        return self.is_vector and self.geometry_type == ogr.wkbPolygon

    @property
    def is_riab_spatial_object(self):
        return True


#----------------------------------
# Helper functions for class Vector
#----------------------------------
def convert_line_to_points(V, delta):
    """Convert line vector data to point vector data

    Input
        V: Vector layer with line data
        delta: Incremental step to find the points
    Output
        Vector layer with point data and the same attributes as V
    """

    msg = 'Input data %s must be line vector data' % V
    assert V.is_line_data, msg

    geometry = V.get_geometry()
    data = V.get_data()
    N = len(V)

    # Calculate centroids for each polygon
    points = []
    new_data = []
    for i in range(N):
        c = points_along_line(geometry[i], delta)
        # We need to create a data entry for each point.
        new_data.extend([data[i] for thing in c])
        points.extend(c)

    # Create new point vector layer with same attributes and return
    V = Vector(data=new_data,
               projection=V.get_projection(),
               geometry=points,
               name='%s_point_data' % V.get_name(),
               keywords=V.get_keywords())
    return V


def convert_polygons_to_centroids(V):
    """Convert polygon vector data to point vector data

    Input
        V: Vector layer with polygon data

    Output
        Vector layer with point data and the same attributes as V
    """

    msg = 'Input data %s must be polygon vector data' % V
    assert V.is_polygon_data, msg

    geometry = V.get_geometry()
    N = len(V)
    # Calculate points for each polygon
    centroids = []
    for i in range(N):
        c = calculate_polygon_centroid(geometry[i])
        centroids.append(c)

    # Create new point vector layer with same attributes and return
    V = Vector(data=V.get_data(),
               projection=V.get_projection(),
               geometry=centroids,
               name='%s_centroid_data' % V.get_name(),
               keywords=V.get_keywords())
    return V
