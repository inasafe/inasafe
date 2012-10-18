"""**Vector Module**

.. tip:: Provides functionality for manipulation of vector data. The data can
   be in-memory or file based.

Resources for understanding vector data formats and the OGR library:
Treatise on vector data model: http://www.esri.com/news/arcuser/0401/topo.html
OGR C++ reference: http://www.gdal.org/ogr


"""

__author__ = 'Ole Nielsen <ole.moller.nielsen@gmail.com>'
__version__ = '0.5.1'
__revision__ = '$Format:%H$'
__date__ = '01/11/2010'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import numpy
import logging

import copy as copy_module
from osgeo import ogr, gdal
from safe.common.utilities import (verify,
                                   ugettext as safe_tr)
from safe.common.exceptions import ReadLayerError, WriteLayerError
from safe.common.exceptions import GetDataError, InaSAFEError

from layer import Layer
from projection import Projection
from geometry import Polygon
from utilities import DRIVER_MAP, TYPE_MAP
from utilities import read_keywords
from utilities import write_keywords
from utilities import get_geometry_type
from utilities import is_sequence
from utilities import array2wkt, array2ring
from utilities import calculate_polygon_centroid
from utilities import points_along_line
from utilities import geometrytype2string
from utilities import get_ringdata
from utilities import rings_equal

LOGGER = logging.getLogger('InaSAFE')
_pseudo_inf = float(999999999999999999999999)


class Vector(Layer):
    """Class for abstraction of vector data.
    """

    def __init__(self, data=None, projection=None, geometry=None,
                 geometry_type=None, name=None, keywords=None,
                 style_info=None, sublayer=None):
        """Initialise object with either geometry or filename

        Args:
            * data: Can be either
                * A filename of a vector file format known to GDAL.
                * List of dictionaries of field names and attribute values
                  associated with each point coordinate.
                * None
            * projection: Geospatial reference in WKT format.
                Only used if geometry is provided as a numeric array,
                if None, WGS84 geographic is assumed.
            * geometry: A list of either point coordinates or polygons/lines
                (see note below).
            * geometry_type: Desired interpretation of geometry.
                Valid options are 'point', 'line', 'polygon' or
                the ogr types: 1, 2, 3.
                If None, a geometry_type will be inferred from the data.
            * name: Optional name for layer. If None, basename is used.
            * keywords: Optional dictionary with keywords that describe the
                layer. When the layer is stored, these keywords will
                be written into an associated file with extension
                '.keywords'.

                Keywords can for example be used to display text about the
                layer in an application.
            * style_info: Dictionary with information about how this layer
                should be styled. See impact_functions/styles.py
                for examples.
            * sublayer: str Optional sublayer (band name in the case of raster,
                  table name in case of sqlite etc.) to load. Only applicable
                  to those dataformats supporting more than one layer in the
                  data file.

        Returns:
            * An instance of class Vector.

        Raises:
            * Propogates any exceptions encountered.

        Notes:

            If data is a filename, all other arguments are ignored
            as they will be inferred from the file.

            The geometry type will be inferred from the dimensions of geometry.
            If each entry is one set of coordinates the type will be
            ogr.wkbPoint,
            if it is an array of coordinates the type will be ogr.wkbPolygon.

            To cast array entries as lines set geometry_type explicitly to
            'line' in the call to Vector. Otherwise, they will default to
            polygons.

            Each polygon or line feature take the form of an Nx2 array
            representing vertices where line segments are joined.

            If polygons have holes, their geometry must be passed in as a
            list of polygon geometry objects
            (as defined in module geometry.py)
        """

        # Invoke common layer constructor
        Layer.__init__(self,
                       name=name,
                       projection=projection,
                       keywords=keywords,
                       style_info=style_info,
                       sublayer=sublayer)

        # Input checks
        if data is None and geometry is None:
            # Instantiate empty object
            self.geometry_type = None
            self.extent = [0, 0, 0, 0]
            return

        if isinstance(data, basestring):
            self.read_from_file(data)
        else:
            # Assume that data is provided as sequences provided as
            # arguments to the Vector constructor
            # with extra keyword arguments supplying metadata

            msg = 'Geometry must be specified'
            verify(geometry is not None, msg)

            msg = 'Geometry must be a sequence'
            verify(is_sequence(geometry), msg)

            if len(geometry) > 0 and isinstance(geometry[0], Polygon):
                self.geometry_type = ogr.wkbPolygon
                self.geometry = geometry
            else:
                self.geometry_type = get_geometry_type(geometry, geometry_type)

                # Convert to objects if input is a list of simple arrays
                if self.is_polygon_data:
                    self.geometry = [Polygon(outer_ring=x) for x in geometry]
                else:
                    self.geometry = geometry

            if data is None:
                # Generate default attribute as OGR will do that anyway
                # when writing
                data = []
                for i in range(len(geometry)):
                    data.append({'ID': i})

            # Check data
            self.data = data
            if data is not None:
                msg = 'Data must be a sequence'
                verify(is_sequence(data), msg)

                msg = ('The number of entries in geometry and data '
                       'must be the same')
                verify(len(geometry) == len(data), msg)

            # Establish extent
            if len(geometry) == 0:
                # Degenerate layer
                self.extent = [0, 0, 0, 0]
                return

            # Compute bounding box for each geometry type
            minx = miny = sys.maxint
            maxx = maxy = -minx
            if self.is_point_data:
                A = numpy.array(self.get_geometry())
                minx = min(A[:, 0])
                maxx = max(A[:, 0])
                miny = min(A[:, 1])
                maxy = max(A[:, 1])
            elif self.is_line_data:
                for g in self.get_geometry():
                    A = numpy.array(g)
                    minx = min(minx, min(A[:, 0]))
                    maxx = max(maxx, max(A[:, 0]))
                    miny = min(miny, min(A[:, 1]))
                    maxy = max(maxy, max(A[:, 1]))
            elif self.is_polygon_data:
                # Do outer ring only
                for g in self.get_geometry(as_geometry_objects=False):
                    A = numpy.array(g)
                    minx = min(minx, min(A[:, 0]))
                    maxx = max(maxx, max(A[:, 0]))
                    miny = min(miny, min(A[:, 1]))
                    maxy = max(maxy, max(A[:, 1]))

            self.extent = [minx, maxx, miny, maxy]

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

        if hasattr(self, 'geometry') and self.geometry is not None:
            return len(self.geometry)
        else:
            return 0

    def __eq__(self, other, rtol=1.0e-5, atol=1.0e-8):
        """Override '==' to allow comparison with other vector objecs

        Args:
           * other: Vector instance to compare to
           * rtol, atol: Relative and absolute tolerance.
                       See numpy.allclose for details

        Note:
            The algorithm will try to falsify every aspect of equality for the
            two layers such as data, geometry, projection, keywords etc.
            Only if none of them can be falsified will it return True.
        """

        # Check type
        if not isinstance(other, Vector):
            msg = ('Vector instance cannot be compared to %s'
                   ' as its type is %s ' % (str(other), type(other)))
            raise TypeError(msg)

        # Check keywords
        if self.keywords != other.keywords:
            return False

        # Check number of features match
        if len(self) != len(other):
            return False

        # Check projection
        if self.projection != other.projection:
            return False

        # Check geometry type
        if self.geometry_type != other.geometry_type:
            return False

        # Check geometry
        if self.is_polygon_data:
            geom0 = self.get_geometry(as_geometry_objects=True)
            geom1 = other.get_geometry(as_geometry_objects=True)
        else:
            geom0 = self.get_geometry()
            geom1 = other.get_geometry()

        if len(geom0) != len(geom1):
            return False

        if self.is_point_data:
            if not numpy.allclose(geom0, geom1,
                                  rtol=rtol, atol=atol):
                return False
        elif self.is_line_data:
            # Check vertices of each line
            for i in range(len(geom0)):

                if not rings_equal(geom0[i], geom1[i], rtol=rtol, atol=atol):
                    return False

        elif self.is_polygon_data:
            # Check vertices of outer and inner rings
            for i in range(len(geom0)):

                x = geom0[i].outer_ring
                y = geom1[i].outer_ring
                if not rings_equal(x, y, rtol=rtol, atol=atol):
                    return False

                for j, ring0 in enumerate(geom0[i].inner_rings):
                    ring1 = geom1[i].inner_rings[j]
                    if not rings_equal(ring0, ring1, rtol=rtol, atol=atol):
                        return False

        else:
            msg = ('== not implemented for geometry type: %s'
                   % self.geometry_type)
            raise InaSAFEError(msg)

        # Check keys for attribute values
        x = self.get_data()
        y = other.get_data()

        if x is None:
            if y is not None:
                return False
        else:
            for key in x[0]:
                for i in range(len(y)):
                    if key not in y[i]:
                        return False

            for key in y[0]:
                for i in range(len(x)):
                    if key not in x[i]:
                        return False

            # Check attribute values
            for i, a in enumerate(x):
                for key in a:
                    X = a[key]
                    Y = y[i][key]

                    if X != Y:
                        # Not obviously equal, try some special cases

                        try:
                            # Try numerical comparison with tolerances
                            res = numpy.allclose(X, Y,
                                                 rtol=rtol, atol=atol)
                        except (NotImplementedError, TypeError):
                            # E.g. '' (Not implemented)
                            # or   None or {} (Type error)
                            pass
                        else:
                            if not res:
                                return False

                        # Finally cast as booleans.
                        # This will e.g. match False with None or ''
                        if not (bool(X) is bool(Y)):
                            return False

        # Vector layers are identical up to the specified tolerance
        return True

    def read_from_file(self, filename):
        """Read and unpack vector data.

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

        Limitation of the Shapefile are documented in
        http://resources.esri.com/help/9.3/ArcGISDesktop/com/Gp_ToolRef/
        geoprocessing_tool_reference/
        geoprocessing_considerations_for_shapefile_output.htm
        """

        basename = os.path.splitext(filename)[0]

        # Look for any keywords
        self.keywords = read_keywords(basename + '.keywords')

        # FIXME (Ole): Should also look for style file to populate style_info

        # Determine name
        if 'title' in self.keywords:
            title = self.keywords['title']

            # Lookup internationalised title if available
            title = safe_tr(title)

            vectorname = title
        else:
            # Use basename without leading directories as name
            vectorname = os.path.split(basename)[-1]

        if self.name is None:
            self.name = vectorname
        self.filename = filename
        self.geometry_type = None  # In case there are no features

        fid = ogr.Open(filename)
        if fid is None:
            msg = 'Could not open %s' % filename
            raise ReadLayerError(msg)

        # Assume that file contains all data in one layer
        msg = 'Only one vector layer currently allowed'
        if fid.GetLayerCount() > 1 and self.sublayer is None:
            msg = ('WARNING: Number of layers in %s are %i. '
                   'Only the first layer will currently be '
                   'used. Specify sublayer when creating '
                   'the Vector if you wish to use a different layer.'
                   % (filename, fid.GetLayerCount()))
            LOGGER.warn(msg)
            # Why do we raise an exception if it is only a warning? TS
            raise ReadLayerError(msg)

        if self.sublayer is not None:
            layer = fid.GetLayerByName(self.sublayer)
        else:
            layer = fid.GetLayerByIndex(0)

        # Get spatial extent
        self.extent = layer.GetExtent()

        # Get projection
        p = layer.GetSpatialRef()
        self.projection = Projection(p)

        layer.ResetReading()

        # Extract coordinates and attributes for all features
        geometry = []
        data = []
        # Use feature iterator
        for feature in layer:
            # Record coordinates ordered as Longitude, Latitude
            G = feature.GetGeometryRef()
            if G is None:
                msg = ('Geometry was None in filename %s ' % filename)
                raise ReadLayerError(msg)
            else:
                self.geometry_type = G.GetGeometryType()
                if self.is_point_data:
                    geometry.append((G.GetX(), G.GetY()))
                elif self.is_line_data:
                    ring = get_ringdata(G)
                    geometry.append(ring)
                elif self.is_polygon_data:
                    # Get outer ring, then inner rings
                    # http://osgeo-org.1560.n6.nabble.com/
                    # gdal-dev-Polygon-topology-td3745761.html
                    number_of_rings = G.GetGeometryCount()

                    # Get outer ring
                    outer_ring = get_ringdata(G.GetGeometryRef(0))

                    # Get inner rings if any
                    inner_rings = []
                    if number_of_rings > 1:
                        for i in range(1, number_of_rings):
                            inner_ring = get_ringdata(G.GetGeometryRef(i))
                            inner_rings.append(inner_ring)

                    # Append Polygon instance to geometry list
                    geometry.append(Polygon(outer_ring=outer_ring,
                                            inner_rings=inner_rings))

                elif self.is_multi_polygon_data:
                    try:
                        G = ogr.ForceToPolygon(G)
                        # FIXME: reuse the code for polygon above
                        ring = G.GetGeometryRef(0)
                        M = ring.GetPointCount()
                        coordinates = []
                        for j in range(M):
                            coordinates.append((ring.GetX(j), ring.GetY(j)))

                        # Record entire polygon ring as an Mx2 numpy array
                        geometry.append(numpy.array(coordinates,
                                                    dtype='d',
                                                    copy=False))
#                    msg = ('Got geometry type Multipolygon (%s) for filename '
#                            '%s which is not yet supported. Only point, line '
#                           'and polygon geometries are supported. However, '
#                           'you can use QGIS functionality to convert '
#                           'multipart vector data to singlepart (Vector -> '
#                           'Geometry Tools -> Multipart to Singleparts and '
#                           'use the resulting dataset.'
#                           % (ogr.wkbMultiPolygon, filename))
                    except:
                        msg = ('Got geometry type multipolygon (%s) when read '
                               '%s and failed to ForceToPolygon')
                        raise ReadLayerError(msg)

                #    # FIXME: Unpact multiple polygons to simple polygons
                #    # For hints on how to unpack see
#http://osgeo-org.1803224.n2.nabble.com/
#gdal-dev-Shapefile-Multipolygon-with-interior-rings-td5391090.html
#http://osdir.com/ml/gdal-development-gis-osgeo/2010-12/msg00107.html

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
                    raise ReadLayerError(msg)

            # Record attributes by name
            number_of_fields = feature.GetFieldCount()
            fields = {}
            for j in range(number_of_fields):
                name = feature.GetFieldDefnRef(j).GetName()

                # FIXME (Ole): Ascertain the type of each field?
                #              We need to cast each appropriately?
                #              This is issue #66
                #              (https://github.com/AIFDR/riab/issues/66)
                #feature_type = feature.GetFieldDefnRef(j).GetType()
                fields[name] = feature.GetField(j)

                    # We do this because there is NaN problem on windows
                    # NaN value must be converted to _pseudo_in to solve the
                    # problem. But, when InaSAFE read the file, it'll be
                    # converted back to NaN value, so that NaN in InaSAFE is a
                    # numpy.nan
                    # please check https://github.com/AIFDR/inasafe/issues/269
                    # for more information
                if fields[name] == _pseudo_inf:
                    fields[name] = float('nan')
                #print 'Field', name, feature_type, j, fields[name]

            data.append(fields)
        # Store geometry coordinates as a compact numeric array
        self.geometry = geometry
        self.data = data

    def write_to_file(self, filename, sublayer=None):
        """Save vector data to file

        Args:
            * filename: filename with extension .shp or .gml
            * sublayer: Optional string for writing a sublayer. Ignored
                  unless we are writing to an sqlite file.

        Note:
            Shp limitation, if attribute names are longer than 10
            characters they will be truncated. This is due to limitations in
            the shp file driver and has to be done here since gdal v1.7 onwards
            has changed its handling of this issue:
            http://www.gdal.org/ogr/drv_shapefile.html

            **For this reason we recommend writing to spatialite.**

        """

        # Check file format
        basename, extension = os.path.splitext(filename)

        msg = ('Invalid file type for file %s. Only extensions '
               'sqlite, shp or gml allowed.' % filename)
        verify(extension in ['.sqlite', '.shp', '.gml'], msg)
        driver = DRIVER_MAP[extension]

        # FIXME (Ole): Tempory flagging of GML issue (ticket #18)
        if extension == '.gml':
            msg = ('OGR GML driver does not store geospatial reference.'
                   'This format is disabled for the time being. See '
                   'https://github.com/AIFDR/riab/issues/18')
            raise WriteLayerError(msg)

        # Derive layername from filename (excluding preceding dirs)
        if sublayer is None or extension == '.shp':
            layername = os.path.split(basename)[-1]
        else:
            layername = sublayer

        # Get vector data
        if self.is_polygon_data:
            geometry = self.get_geometry(as_geometry_objects=True)
        else:
            geometry = self.get_geometry()
        data = self.get_data()

        N = len(geometry)

        # Clear any previous file of this name (ogr does not overwrite)
        try:
            os.remove(filename)
        except OSError:
            pass

        # Create new file with one layer
        drv = ogr.GetDriverByName(driver)
        if drv is None:
            msg = 'OGR driver %s not available' % driver
            raise WriteLayerError(msg)

        ds = drv.CreateDataSource(filename)
        if ds is None:
            msg = 'Creation of output file %s failed' % filename
            raise WriteLayerError(msg)

        lyr = ds.CreateLayer(layername,
                             self.projection.spatial_reference,
                             self.geometry_type)
        if lyr is None:
            msg = 'Could not create layer %s' % layername
            raise WriteLayerError(msg)

        # Define attributes if any
        store_attributes = False
        fields = []
        if data is not None:
            if len(data) > 0:
                try:
                    fields = data[0].keys()
                except:
                    msg = ('Input parameter "attributes" was specified '
                           'but it does not contain list of dictionaries '
                           'with field information as expected. The first '
                           'element is %s' % data[0])
                    raise WriteLayerError(msg)
                else:
                    # Establish OGR types for each element
                    ogrtypes = {}
                    for name in fields:
                        att = data[0][name]
                        py_type = type(att)
                        msg = ('Unknown type for storing vector '
                               'data: %s, %s' % (name, str(py_type)[1:-1]))
                        verify(py_type in TYPE_MAP, msg)
                        ogrtypes[name] = TYPE_MAP[py_type]

            else:
                #msg = ('Input parameter "data" was specified '
                #       'but appears to be empty')
                #raise InaSAFEError(msg)
                pass

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
                    raise WriteLayerError(msg)

                # Restore error handler
                gdal.PopErrorHandler()

        # Store geometry
        geom = ogr.Geometry(self.geometry_type)
        layer_def = lyr.GetLayerDefn()
        for i in range(N):
            # Create new feature instance
            feature = ogr.Feature(layer_def)

            # Store geometry and check
            if self.is_point_data:
                x = float(geometry[i][0])
                y = float(geometry[i][1])
                geom.SetPoint_2D(0, x, y)
            elif self.is_line_data:
                # FIXME (Ole): Change this to use array2ring instead!
                #geom = ogr.Geometry(ogr.wkbLineString)
                #linear_ring = array2ring(geometry[i])
                #geom.AddGeometry(linear_ring)

                wkt = array2wkt(geometry[i], geom_type='LINESTRING')
                geom = ogr.CreateGeometryFromWkt(wkt)
            elif self.is_polygon_data:
                # Create polygon geometry
                geom = ogr.Geometry(ogr.wkbPolygon)

                # Add outer ring
                linear_ring = array2ring(geometry[i].outer_ring)
                geom.AddGeometry(linear_ring)

                # Add inner rings if any
                for A in geometry[i].inner_rings:
                    geom.AddGeometry(array2ring(A))
            else:
                msg = 'Geometry type %s not implemented' % self.geometry_type
                raise WriteLayerError(msg)

            feature.SetGeometry(geom)

            G = feature.GetGeometryRef()
            if G is None:
                msg = 'Could not create GeometryRef for file %s' % filename
                raise WriteLayerError(msg)

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
                    elif val is None:
                        val = ''

                    # We do this because there is NaN problem on windows
                    # NaN value must be converted to _pseudo_in to solve the
                    # problem. But, when InaSAFE read the file, it'll be
                    # converted back to NaN value, so that NaN in InaSAFE is a
                    # numpy.nan
                    # please check https://github.com/AIFDR/inasafe/issues/269
                    # for more information
                    if val != val:
                        val = _pseudo_inf

                    feature.SetField(actual_field_name, val)

            # Save this feature
            if lyr.CreateFeature(feature) != 0:
                msg = 'Failed to create feature %i in file %s' % (i, filename)
                raise WriteLayerError(msg)

            feature.Destroy()

        # Write keywords if any
        write_keywords(self.keywords, basename + '.keywords')

        # FIXME (Ole): Maybe store style_info

    def copy(self):
        """Return copy of vector layer

        This copy will be equal to self in the sense defined by __eq__
        """

        if self.is_polygon_data:
            geometry = self.get_geometry(copy=True, as_geometry_objects=True)
        else:
            geometry = self.get_geometry(copy=True)

        return Vector(data=self.get_data(copy=True),
                      geometry=geometry,
                      projection=self.get_projection(),
                      keywords=self.get_keywords())

    def get_attribute_names(self):
        """Get available attribute names

        These are the ones that can be used with get_data
        """

        return self.data[0].keys()

    def get_data(self, attribute=None, index=None, copy=False):
        """Get vector attributes

        Note:
            Data is returned as a list where each entry is a dictionary of
            attributes for one feature. Entries in get_geometry() and
            get_data() are related as 1-to-1

            If optional argument attribute is specified and a valid name,
            then the list of values for that attribute is returned.

            If optional argument index is specified on the that value will
            be returned. Any value of index is ignored if attribute is None.

            If optional argument copy is True and all attributes are requested,
            a copy will be returned. Otherwise a pointer to the data is
            returned.
        """

        if hasattr(self, 'data'):
            if attribute is None:
                if copy:
                    return copy_module.deepcopy(self.data)
                else:
                    return self.data
            else:
                msg = ('Specified attribute %s does not exist in '
                       'vector layer %s. Valid names are %s'
                       '' % (attribute, self, self.data[0].keys()))
                verify(attribute in self.data[0], msg)

                if index is None:
                    # Return all values for specified attribute
                    return [x[attribute] for x in self.data]
                else:
                    # Return value for specified attribute and index
                    msg = ('Specified index must be either None or '
                           'an integer. I got %s' % index)
                    verify(isinstance(index, int), msg)

                    msg = ('Specified index must lie within the bounds '
                           'of vector layer %s which is [%i, %i]'
                           '' % (self, 0, len(self) - 1))
                    verify(0 <= index < len(self), msg)

                    return self.data[index][attribute]
        else:
            msg = 'Vector data instance does not have any attributes'
            raise GetDataError(msg)

    def get_geometry_type(self):
        """Return geometry type for vector layer
        """
        return self.geometry_type

    def get_geometry_name(self):
        """Return geometry name for vector layer
        """
        return geometrytype2string(self.geometry_type)

    def get_geometry(self, copy=False, as_geometry_objects=False):
        """Return geometry for vector layer.

        Depending on the feature type, geometry is

        geometry type     output type
        -----------------------------
        point             list of 2x1 array of longitudes and latitudes)
        line              list of arrays of coordinates
        polygon           list of arrays of coordinates

        Optional boolean argument as_geometry_objects will change the return
        value to a list of geometry objects rather than a list of arrays.
        This currently only applies to polygon geometries
        """

        if copy:
            geometry = copy_module.deepcopy(self.geometry)
        else:
            geometry = self.geometry

        if self.is_polygon_data:
            if not as_geometry_objects:
                geometry = [p.outer_ring for p in geometry]
        else:
            if as_geometry_objects:
                msg = ('Argument as_geometry_objects can currently '
                       'be True only for polygon data')
                raise InaSAFEError(msg)

        return geometry

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
            raise InaSAFEError(msg)

        x = self.get_data(attribute)
        return min(x), max(x)

    def get_topN(self, attribute, N=10):
        """Get top N features

        Args:
            * attribute: The name of attribute where values are sought
            * N: How many

        Returns:
            * layer: New vector layer with selected features
        """

        # Input checks
        msg = ('Specfied attribute must be a string. '
               'I got %s' % (type(attribute)))
        verify(isinstance(attribute, basestring), msg)

        msg = 'Specified attribute was empty'
        verify(attribute != '', msg)

        msg = 'N must be a positive number. I got %i' % N
        verify(N > 0, msg)

        # Create list of values for specified attribute
        values = self.get_data(attribute)

        # Sort and select using Schwarzian transform
        A = zip(values, self.data, self.geometry)
        A.sort()

        # Pick top N and unpack
        data, geometry = zip(*A[-N:])[1:]

        # Create new Vector instance and return
        return Vector(data=data,
                      projection=self.get_projection(),
                      geometry=geometry,
                      keywords=self.get_keywords())

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
    def is_multi_polygon_data(self):
        return self.is_vector and self.geometry_type == ogr.wkbMultiPolygon


#----------------------------------
# Helper functions for class Vector
#----------------------------------
def convert_line_to_points(V, delta):
    """Convert line vector data to point vector data

    Args:
        * V: Vector layer with line data
        * delta: Incremental step to find the points
    Returns:
        * Vector layer with point data and the same attributes as V
    """

    msg = 'Input data %s must be line vector data' % V
    verify(V.is_line_data, msg)

    geometry = V.get_geometry()
    data = V.get_data()
    N = len(V)

    # Calculate centroids for each polygon
    points = []
    new_data = []
    for i in range(N):
        c = points_along_line(geometry[i], delta)
        # We need to create a data entry for each point.
        # FIXME (Ole): What on earth is this?
        # pylint: disable=W0621
        new_data.extend([data[i] for _ in c])
        # pylint: enable=W0621
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

    Args:
        * V: Vector layer with polygon data

    Returns:
        * Vector layer with point data and the same attributes as V
    """

    msg = 'Input data %s must be polygon vector data' % V
    verify(V.is_polygon_data, msg)

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
