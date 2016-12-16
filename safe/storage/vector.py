# coding=utf-8
"""**Vector Module**

.. tip:: Provides functionality for manipulation of vector data. The data can
   be in-memory or file based.

Resources for understanding vector data formats and the OGR library:
Treatise on vector data model: http://www.esri.com/news/arcuser/0401/topo.html
OGR C++ reference: http://www.gdal.org/ogr


"""

__author__ = 'Ole Nielsen <ole.moller.nielsen@gmail.com>'
__revision__ = '$Format:%H$'
__date__ = '01/11/2010'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import numpy
import logging

QGIS_IS_AVAILABLE = True
try:
    from qgis.core import QgsVectorLayer, QgsVectorFileWriter
except ImportError:
    QGIS_IS_AVAILABLE = False

import copy as copy_module
from osgeo import ogr, gdal
from safe.common.exceptions import (
    ReadLayerError,
    WriteLayerError,
    GetDataError,
    InaSAFEError
)
from layer import Layer
from projection import Projection
from geometry import Polygon
from utilities import verify
from utilities import DRIVER_MAP, TYPE_MAP
from utilities import get_geometry_type
from utilities import is_sequence
from utilities import array_to_line
from utilities import calculate_polygon_centroid
from utilities import geometry_type_to_string
from utilities import get_ring_data, get_polygon_data
from utilities import rings_equal
from utilities import safe_to_qgis_layer
from safe.common.utilities import unique_filename
from safe.utilities.unicode import get_string
from safe.utilities.i18n import tr
from safe.utilities.metadata import (
    write_iso19115_metadata,
    read_iso19115_metadata,
)

LOGGER = logging.getLogger('InaSAFE')
_pseudo_inf = float(99999999)


# noinspection PyExceptionInherit
class Vector(Layer):
    """InaSAFE representation of vector data.


        Args:
            * data: Can be either
                * A filename of a vector file format known to GDAL.
                * List of dictionaries of field names and attribute values
                  associated with each point coordinate.
                * A QgsVectorLayer associated with geometry and data.
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
                be written into an associated file with extension '.xml'.

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
            * InaSAFE vector layer instance

        Raises:
            * TypeError, ReadLayerError, WriteLayerError, InaSAFEError,
              GetDataError

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

    def __init__(
            self,
            data=None,
            projection=None,
            geometry=None,
            geometry_type=None,
            name=None,
            keywords=None,
            style_info=None,
            sublayer=None):
        """Initialise object with either geometry or filename

        NOTE: Doc strings in constructor are not harvested and exposed in
        online documentation. Hence the details are specified in the
        class docstring.
        """

        # Invoke common layer constructor
        Layer.__init__(
            self,
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
        # check QGIS_IS_AVAILABLE to avoid QgsVectorLayer undefined error
        elif QGIS_IS_AVAILABLE and isinstance(data, QgsVectorLayer):
            self.read_from_qgis_native(data)
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

                if self.is_polygon_data:
                    # Convert to objects if input is a list of simple arrays
                    self.geometry = [Polygon(outer_ring=x) for x in geometry]
                else:
                    # Convert to list if input is an array
                    if isinstance(geometry, numpy.ndarray):
                        self.geometry = geometry.tolist()
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

                msg = ('The number of entries in geometry (%s) and data (%s)'
                       'must be the same' % (len(geometry), len(data)))
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

        g_type_str = geometry_type_to_string(self.geometry_type)
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
            # noinspection PyExceptionInherit
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

    # noinspection PyExceptionInherit
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

        :param filename: a fully qualified location to the file
        :type filename: str

        :raises: ReadLayerError
        """

        base_name = os.path.splitext(filename)[0]

        # Look for any keywords
        self.keywords = read_iso19115_metadata(filename)

        # FIXME (Ole): Should also look for style file to populate style_info

        # Determine name
        if 'title' in self.keywords:
            title = self.keywords['title']

            # Lookup internationalised title if available
            title = tr(title)

            vector_name = title
        else:
            # Use base_name without leading directories as name
            vector_name = os.path.split(base_name)[-1]

        if self.name is None:
            self.name = vector_name
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
                # Updated in 3.5.4 to skip invalid features TS
                LOGGER.warning('Skipping feature with invalid geometry')
                continue
                # msg = ('Geometry was None in filename %s ' % filename)
                # raise ReadLayerError(msg)
            else:
                self.geometry_type = G.GetGeometryType()
                if self.is_point_data:
                    geometry.append((G.GetX(), G.GetY()))
                elif self.is_line_data:
                    ring = get_ring_data(G)
                    geometry.append(ring)
                elif self.is_polygon_data:
                    polygon = get_polygon_data(G)
                    geometry.append(polygon)
                elif self.is_multi_polygon_data:
                    try:
                        G = ogr.ForceToPolygon(G)
                    except:
                        msg = ('Got geometry type Multipolygon (%s) for '
                               'filename %s and could not convert it to '
                               'singlepart. However, you can use QGIS '
                               'functionality to convert multipart vector '
                               'data to singlepart (Vector -> Geometry Tools '
                               '-> Multipart to Singleparts and use the '
                               'resulting dataset.'
                               % (ogr.wkbMultiPolygon, filename))
                        raise ReadLayerError(msg)
                    else:
                        # Read polygon data as single part
                        self.geometry_type = ogr.wkbPolygon
                        polygon = get_polygon_data(G)
                        geometry.append(polygon)
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
                # feature_type = feature.GetFieldDefnRef(j).GetType()
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
                    # print 'Field', name, feature_type, j, fields[name]

            data.append(fields)
        # Store geometry coordinates as a compact numeric array
        self.geometry = geometry
        self.data = data

    def read_from_qgis_native(self, qgis_layer):
        """Read and unpack vector data from qgis layer QgsVectorLayer.

            A stub is used now:
                save all data in a file,
                then call safe.read_from_file

            Raises:
                * TypeError         if qgis is not avialable
                * IOError           if can't store temporary file
        """
        # FIXME (DK): this branch isn't covered by test
        if not QGIS_IS_AVAILABLE:
            msg = ('Used data is QgsVectorLayer instance, '
                   'but QGIS is not available.')
            raise TypeError(msg)

        base_name = unique_filename()
        file_name = base_name + '.shp'
        error = QgsVectorFileWriter.writeAsVectorFormat(
            qgis_layer,
            file_name,
            "UTF8",
            qgis_layer.crs(),
            "ESRI Shapefile"
        )
        if error != QgsVectorFileWriter.NoError:
            # FIXME (DK): this branch isn't covered by test
            msg = ('Can not save data in temporary file.')
            raise IOError(msg)

        # Write keywords if any
        write_iso19115_metadata(file_name, self.keywords)
        self.read_from_file(file_name)

    def as_qgis_native(self):
        """Return vector layer data as qgis QgsVectorLayer.

            A stub is used now:
                save all data in a file,
                then create QgsVectorLayer from the file.

            Raises:
                * TypeError         if qgis is not avialable
        """
        # FIXME (DK): this branch isn't covered by test
        if not QGIS_IS_AVAILABLE:
            msg = ('Tried to convert layer to QgsVectorLayer instance, '
                   'but QGIS is not available.')
            raise TypeError(msg)

        # FIXME (DK): ? move code from safe_to_qgis_layer to this method
        #           and call layer.as_qgis_native from safe_to_qgis_layer ?

        qgis_layer = safe_to_qgis_layer(self)
        return qgis_layer

    def write_to_file(self, filename, sublayer=None):
        """Save vector data to file

        :param filename: filename with extension .shp or .gml
        :type filename: str

        :param sublayer: Optional parameter for writing a sublayer. Ignored
            unless we are writing to an sqlite file.
        :type sublayer: str

        :raises: WriteLayerError

        Note:
            Shp limitation, if attribute names are longer than 10
            characters they will be truncated. This is due to limitations in
            the shp file driver and has to be done here since gdal v1.7 onwards
            has changed its handling of this issue:
            http://www.gdal.org/ogr/drv_shapefile.html

            **For this reason we recommend writing to spatialite.**

        """

        # Check file format
        base_name, extension = os.path.splitext(filename)

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

        # Derive layer_name from filename (excluding preceding dirs)
        if sublayer is None or extension == '.shp':
            layer_name = os.path.split(base_name)[-1]
        else:
            layer_name = sublayer

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

        ds = drv.CreateDataSource(get_string(filename))
        if ds is None:
            msg = 'Creation of output file %s failed' % filename
            raise WriteLayerError(msg)
        lyr = ds.CreateLayer(
            get_string(layer_name),
            self.projection.spatial_reference,
            self.geometry_type)
        if lyr is None:
            msg = 'Could not create layer %s' % layer_name
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
                    ogr_types = {}
                    for name in fields:
                        att = data[0][name]
                        py_type = type(att)
                        # If unicode, convert to string
                        if isinstance(att, unicode):
                            att = get_string(att)
                            py_type = type(att)
                        msg = (
                            'Unknown type for storing vector data: %s, %s, '
                            '%s' % (name, str(py_type)[1:-1], att))
                        verify(py_type in TYPE_MAP, msg)
                        ogr_types[name] = TYPE_MAP[py_type]

            else:
                # msg = ('Input parameter "data" was specified '
                #       'but appears to be empty')
                # raise InaSAFEError(msg)
                pass

            # Create attribute fields in layer
            store_attributes = True
            for name in fields:
                # Rizky : OGR can't handle unicode field name, thus we
                # convert it to ASCII
                fd = ogr.FieldDefn(str(name), ogr_types[name])
                # FIXME (Ole): Trying to address issue #16
                #              But it doesn't work and
                #              somehow changes the values of MMI in test
                # width = max(128, len(name))
                # print name, width
                # fd.SetWidth(width)

                # Silent handling of warnings like
                # Warning 6: Normalized/laundered field name:
                # 'CONTENTS_LOSS_AUD' to 'CONTENTS_L'
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
                geom = array_to_line(
                    geometry[i], geometry_type=ogr.wkbLineString)
            elif self.is_polygon_data:
                # Create polygon geometry
                geom = ogr.Geometry(ogr.wkbPolygon)

                # Add outer ring
                linear_ring = array_to_line(
                    geometry[i].outer_ring, geometry_type=ogr.wkbLinearRing)
                geom.AddGeometry(linear_ring)

                # Add inner rings if any
                for A in geometry[i].inner_rings:
                    geom.AddGeometry(array_to_line(
                        A, geometry_type=ogr.wkbLinearRing))
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

                    if isinstance(val, numpy.ndarray):
                        # A singleton of type <type 'numpy.ndarray'> works
                        # for gdal version 1.6 but fails for version 1.8
                        # in SetField with error: NotImplementedError:
                        # Wrong number of arguments for overloaded function
                        val = float(val)
                    if isinstance(val, unicode):
                        val = get_string(val)
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
        write_iso19115_metadata(filename, self.keywords)
        self.keywords = read_iso19115_metadata(filename)

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
        """Get available attribute names.

        These are the ones that can be used with get_data
        """

        return self.data[0].keys()

    def get_data(self, attribute=None, index=None, copy=False):
        """Get vector attributes.

        :param attribute: Specify an attribute name of which to return data.
        :type attribute: str

        :param index: Indicates a specific value on which to call the
            attribute. Ignored if no attribute is set.
        :type index: int

        :param copy: Indicate whether to return a pointer to the data,
            or a copy of.
        :type copy: bool

        :raises: GetDataError

        :returns: A list where each entry is a dictionary of attributes for one
            feature.
        :rtype: list,

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
        return geometry_type_to_string(self.geometry_type)

    def get_geometry(self, copy=False, as_geometry_objects=False):
        """Return geometry for vector layer.

        Depending on the feature type, geometry is::

          geometry type   output type

          point           list of 2x1 array of longitudes and latitudes)
          line            list of arrays of coordinates
          polygon         list of arrays of coordinates

        Optional boolean argument as_geometry_objects will change the return
        value to a list of geometry objects rather than a list of arrays.
        This currently only applies to polygon geometries

        :param copy: Set to return a copy of the data rather than a pointer.
        :type copy: bool

        :param as_geometry_objects: Set to return geometry objects rather
            than a list of arrays.
        :type as_geometry_objects: bool

        :raises: InaSAFEError

        :returns: A list of geometry objects or arrays.
        :rtype: list
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

        :param attribute: Specify an attribute name of which to return data.
        :type attribute: str

        :raises: InaSAFEError

        :returns: minimum and maximum attribute values
        :rtype:
        """
        if attribute is None:
            msg = ('Valid attribute name must be specified in get_extrema '
                   'for vector layers. I got None.')
            raise InaSAFEError(msg)

        x = self.get_data(attribute)
        return min(x), max(x)

    def get_topN(self, attribute, N=10):
        """Get top N features

        :param attribute: The name of attribute where values are sought
        :type attribute: str

        :param N: How many
        :type N: int

        :returns: New vector layer with selected features
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
        """ Check whether this is a point

        :return: Test result
        :rtype: bool
        """
        return (
            self.is_vector and (
                self.geometry_type == ogr.wkbPoint or
                self.geometry_type == ogr.wkbPoint25D))

    @property
    def is_line_data(self):
        """ Check whether this is a line

        :return: Test result
        :rtype: bool
        """
        return (
            self.is_vector and (
                self.geometry_type == ogr.wkbLineString or
                self.geometry_type == ogr.wkbLineString25D))

    @property
    def is_polygon_data(self):
        """ Check whether this is a polygon

        :return: Test result
        :rtype: bool
        """
        return (
            self.is_vector and (
                self.geometry_type == ogr.wkbPolygon or
                self.geometry_type == ogr.wkbPolygon25D))

    @property
    def is_multi_polygon_data(self):
        """ Check whether this is multipolygon

        :return: Test result
        :rtype: bool
        """

        return self.is_vector and self.geometry_type == ogr.wkbMultiPolygon


def convert_polygons_to_centroids(V):
    """Convert polygon vector data to point vector data

    :param V: Vector layer with polygon data
    :type V: Vector

    :returns: Vector layer with point data and the same attributes as V
    :rtype: Vector
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
