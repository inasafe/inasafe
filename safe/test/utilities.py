# coding=utf-8
"""Helper module for gui test suite."""




import codecs
import hashlib
import inspect
import logging
import os
import re
import shutil
import sys

from os.path import exists, splitext, basename, join
from tempfile import mkdtemp

from qgis.PyQt import QtGui  # pylint: disable=W0621
from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsRectangle,
    QgsCoordinateReferenceSystem)

from qgis.utils import iface

from safe.common.utilities import unique_filename, temp_dir
from safe.definitions.constants import HAZARD_EXPOSURE
from safe.gis.tools import load_layer
from safe.gis.vector.tools import create_memory_layer, copy_layer
from safe.utilities.utilities import monkey_patch_keywords

QGIS_APP = None  # Static variable used to hold hand to running QGIS app
CANVAS = None
PARENT = None
IFACE = None
LOGGER = logging.getLogger('InaSAFE')
GEOCRS = 4326  # constant for EPSG:GEOCRS Geographic CRS id
GOOGLECRS = 3857  # constant for EPSG:GOOGLECRS Google Mercator id
DEVNULL = open(os.devnull, 'w')


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def qgis_iface():
    """Helper method to get the iface for testing.

    :return: The QGIS interface.
    :rtype: QgsInterface
    """
    from qgis.utils import iface
    if iface is not None:
        return iface
    else:
        from qgis.testing.mocked import get_iface
        return get_iface()


def get_qgis_app():
    """ Start one QGIS application to test against.

    :returns: Handle to QGIS app, canvas, iface and parent. If there are any
        errors the tuple members will be returned as None.
    :rtype: (QgsApplication, CANVAS, IFACE, PARENT)

    If QGIS is already running the handle to that app will be returned.
    """
    global QGIS_APP, PARENT, IFACE, CANVAS  # pylint: disable=W0603

    if iface:
        from qgis.core import QgsApplication
        QGIS_APP = QgsApplication
        CANVAS = iface.mapCanvas()
        PARENT = iface.mainWindow()
        IFACE = iface
        return QGIS_APP, CANVAS, IFACE, PARENT

    try:
        from qgis.core import QgsApplication
        from qgis.gui import QgsMapCanvas  # pylint: disable=no-name-in-module
        # noinspection PyPackageRequirements
        from qgis.PyQt import QtGui, QtCore  # pylint: disable=W0621
        # noinspection PyPackageRequirements
        from qgis.PyQt.QtCore import QCoreApplication, QSettings
        from safe.test.qgis_interface import QgisInterface
    except ImportError:
        return None, None, None, None

    if QGIS_APP is None:
        gui_flag = True  # All test will run qgis in gui mode

        # AG: For testing purposes, we use our own configuration file instead
        # of using the QGIS apps conf of the host
        # noinspection PyCallByClass,PyArgumentList
        QCoreApplication.setOrganizationName('QGIS')
        # noinspection PyCallByClass,PyArgumentList
        QCoreApplication.setOrganizationDomain('qgis.org')
        # noinspection PyCallByClass,PyArgumentList
        QCoreApplication.setApplicationName('QGIS2InaSAFETesting')

        # noinspection PyPep8Naming
        if 'argv' in dir(sys):
            QGIS_APP = QgsApplication(sys.argv, gui_flag)
        else:
            QGIS_APP = QgsApplication([], gui_flag)

        # Make sure QGIS_PREFIX_PATH is set in your env if needed!
        QGIS_APP.initQgis()
        s = QGIS_APP.showSettings()
        LOGGER.debug(s)

        # Save some settings
        settings = QSettings()
        settings.setValue('locale/overrideFlag', True)
        settings.setValue('locale/userLocale', 'en_US')
        # We disabled message bars for now for extent selector as
        # we don't have a main window to show them in TS - version 3.2
        settings.setValue('inasafe/show_extent_confirmations', False)
        settings.setValue('inasafe/show_extent_warnings', False)
        settings.setValue('inasafe/showRubberBands', True)
        settings.setValue('inasafe/analysis_extents_mode', HAZARD_EXPOSURE)

    if PARENT is None:
        # noinspection PyPep8Naming
        PARENT = QtGui.QWidget()

    if CANVAS is None:
        # noinspection PyPep8Naming
        CANVAS = QgsMapCanvas(PARENT)
        CANVAS.resize(QtCore.QSize(400, 400))

    if IFACE is None:
        # QgisInterface is a stub implementation of the QGIS plugin interface
        # noinspection PyPep8Naming
        IFACE = QgisInterface(CANVAS)

    return QGIS_APP, CANVAS, IFACE, PARENT


def get_dock():
    """Get a dock for testing.

    If you call this function from a QGIS Desktop, you will get the real dock,
    however, you use a fake QGIS interface, it will create a fake dock for you.

    :returns: A dock.
    :rtype: QDockWidget
    """
    # Don't move this import.
    from safe.gui.widgets.dock import Dock as DockObject
    if iface:
        docks = iface.mainWindow().findChildren(QtGui.QDockWidget)
        for dock in docks:
            if isinstance(dock, DockObject):
                return dock
        else:
            return DockObject(iface)
    else:
        return DockObject(IFACE)


def assert_hash_for_file(hash_string, filename):
    """Assert that a files hash matches its expected hash.
    :param filename:
    :param hash_string:
    """
    file_hash = hash_for_file(filename)
    message = (
        'Unexpected hash'
        '\nGot: %s'
        '\nExpected: %s' % (file_hash, hash_string))
    if file_hash != hash_string:
        raise Exception(message)


def hash_for_file(filename):
    """Return an md5 checksum for a file
    :param filename:
    """
    path = filename
    data = file(path, 'rb').read()
    data_hash = hashlib.md5()
    data_hash.update(data)
    data_hash = data_hash.hexdigest()
    return data_hash


def standard_data_path(*args):
    """Return the absolute path to the InaSAFE test data or directory path.

    .. versionadded:: 3.0

    :param *args: List of path e.g. ['control', 'files',
        'test-error-message.txt'] or ['control', 'scenarios'] to get the path
        to scenarios dir.
    :type *args: str

    :return: Absolute path to the test data or dir path.
    :rtype: str

    """
    path = os.path.dirname(__file__)
    path = os.path.abspath(os.path.join(path, 'data'))
    for item in args:
        path = os.path.abspath(os.path.join(path, item))

    return path


def load_local_vector_layer(test_file, **kwargs):
    """Return the test vector layer.

    See documentation of load_path_vector_layer

    :param test_file: The file to load in the data directory next to the file.
    :type test_file: str

    :param kwargs: It can be :
        clone=True if you want to copy the layer first to a temporary file.

        clone_to_memory=True if you want to create a memory layer.

        with_keywords=False if you do not want keywords. "clone_to_memory" is
            required.

    :type kwargs: dict

    :return: The vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    caller_path = inspect.getouterframes(inspect.currentframe())[1][1]
    path = os.path.join(os.path.dirname(caller_path), 'data', test_file)
    return load_path_vector_layer(path, **kwargs)


def load_test_vector_layer(*args, **kwargs):
    """Return the test vector layer.

    See documentation of load_path_vector_layer

    :param *args: List of path e.g. ['exposure', 'buildings.shp'].
    :type *args: list

    :param *kwargs: It can be :
        clone=True if you want to copy the layer first to a temporary file.

        clone_to_memory=True if you want to create a memory layer.

        with_keywords=False if you do not want keywords. "clone_to_memory" is
            required.

    :type *kwargs: dict

    :return: The vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    path = standard_data_path(*args)
    return load_path_vector_layer(path, **kwargs)


def load_path_vector_layer(path, **kwargs):
    """Return the test vector layer.

    :param path: Path to the vector layer.
    :type path: str

    :param kwargs: It can be :
        clone=True if you want to copy the layer first to a temporary file.

        clone_to_memory=True if you want to create a memory layer.

        with_keywords=False if you do not want keywords. "clone_to_memory" is
            required.

    :type kwargs: dict

    :return: The vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    if not exists(path):
        raise Exception('%s do not exist.' % path)

    path = os.path.normcase(os.path.abspath(path))
    name = splitext(basename(path))[0]
    extension = splitext(path)[1]

    extensions = [
        '.shp', '.shx', '.dbf', '.prj', '.gpkg', '.geojson', '.xml', '.qml']

    if kwargs.get('with_keywords'):
        if not kwargs.get('clone_to_memory'):
            raise Exception('with_keywords needs a clone_to_memory')

    if kwargs.get('clone', False):
        target_directory = mkdtemp()
        current_path = splitext(path)[0]
        path = join(target_directory, name + extension)

        for ext in extensions:
            src_path = current_path + ext
            if exists(src_path):
                target_path = join(target_directory, name + ext)
                shutil.copy2(src_path, target_path)

    if path.endswith('.csv'):
        # Explicitly use URI with delimiter or tests fail in Windows. TS.
        uri = 'file:///%s?delimiter=%s' % (path, ',')
        layer = QgsVectorLayer(uri, name, 'delimitedtext')
    else:
        layer = QgsVectorLayer(path, name, 'ogr')

    if not layer.isValid():
        raise Exception('%s is not a valid layer.' % name)

    monkey_patch_keywords(layer)

    if kwargs.get('clone_to_memory', False):
        keywords = layer.keywords.copy()
        memory_layer = create_memory_layer(
            name, layer.geometryType(), layer.crs(), layer.fields())
        copy_layer(layer, memory_layer)
        if kwargs.get('with_keywords', True):
            memory_layer.keywords = keywords
        return memory_layer
    else:
        return layer


def load_local_raster_layer(test_file, **kwargs):
    """Return the test raster layer.

    See documentation of load_path_raster_layer

    :param test_file: The file to load in the data directory next to the file.
    :type test_file: str

    :param kwargs: It can be :
        clone=True if you want to copy the layer first to a temporary file.

        with_keywords=False if you do not want keywords. "clone" is
            required.

    :type kwargs: dict

    :return: The raster layer.
    :rtype: QgsRasterLayer

    .. versionadded:: 4.0
    """
    caller_path = inspect.getouterframes(inspect.currentframe())[1][1]
    path = os.path.join(os.path.dirname(caller_path), 'data', test_file)
    return load_path_raster_layer(path, **kwargs)


def load_test_raster_layer(*args, **kwargs):
    """Return the test raster layer.

    See documentation of load_path_raster_layer

    :param *args: List of path e.g. ['exposure', 'population.asc]'.
    :type *args: list[str]

    :param *kwargs: It can be :
        clone=True if you want to copy the layer first to a temporary file.

        with_keywords=False if you do not want keywords. "clone" is
            required.

    :type *kwargs: dict

    :return: The raster layer.
    :rtype: QgsRasterLayer

    .. versionadded:: 4.0
    """
    path = standard_data_path(*args)
    return load_path_raster_layer(path, **kwargs)


def load_path_raster_layer(path, **kwargs):
    """Return the test raster layer.

    :param path: Path to the raster layer.
    :type path: str

    :param kwargs: It can be :
        clone=True if you want to copy the layer first to a temporary file.

        with_keywords=False if you do not want keywords. "clone" is
            required.

    :return: The raster layer.
    :rtype: QgsRasterLayer

    .. versionadded:: 4.0
    """
    if not exists(path):
        raise Exception('%s do not exist.' % path)

    name = splitext(basename(path))[0]
    extension = splitext(path)[1]

    extensions = [
        '.tiff', '.tif', '.asc', '.xml', '.qml']

    if kwargs.get('with_keywords'):
        if not kwargs.get('clone'):
            raise Exception('with_keywords needs a clone')

    if not kwargs.get('with_keywords', True):
        index = extensions.index('.xml')
        extensions.pop(index)

    if kwargs.get('clone', False):
        target_directory = mkdtemp()
        current_path = splitext(path)[0]
        path = join(target_directory, name + extension)

        for ext in extensions:
            src_path = current_path + ext
            if exists(src_path):
                target_path = join(target_directory, name + ext)
                shutil.copy2(src_path, target_path)

    name = os.path.basename(path)
    layer = QgsRasterLayer(path, name)

    if not layer.isValid():
        raise Exception('%s is not a valid layer.' % name)

    monkey_patch_keywords(layer)

    return layer


def set_canvas_crs(epsg_id, enable_projection=False):
    """Helper to set the crs for the CANVAS before a test is run.

    :param epsg_id: Valid EPSG identifier
    :type epsg_id: int

    :param enable_projection: whether on the fly projections should be
        enabled on the CANVAS. Default to False.
    :type enable_projection: bool

    """
    # Enable on-the-fly reprojection
    CANVAS.mapRenderer().setProjectionsEnabled(enable_projection)

    # Create CRS Instance
    crs = QgsCoordinateReferenceSystem()
    crs.createFromSrid(epsg_id)

    # Reproject all layers to WGS84 geographic CRS
    CANVAS.mapRenderer().setDestinationCrs(crs)


def set_jakarta_extent(dock=None):
    """Zoom to an area occupied by both Jakarta layers in Geo.

    :param dock: A dock widget - if supplied, the extents will also be
        set as the user extent and an appropriate CRS set.
    :type dock: Dock
    """
    rect = QgsRectangle(106.52, -6.38, 107.14, -6.07)
    CANVAS.setExtent(rect)
    if dock is not None:
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        dock.define_user_analysis_extent(rect, crs)


def set_jakarta_google_extent(dock=None):
    """Zoom to an area occupied by both Jakarta layers in 900913 crs.

    :param dock: A dock widget - if supplied, the extents will also be
        set as the user extent and an appropriate CRS set.
    :type dock: Dock
    """
    rect = QgsRectangle(11873524, -695798, 11913804, -675295)
    CANVAS.setExtent(rect)
    if dock is not None:
        crs = QgsCoordinateReferenceSystem('EPSG:3857')
        dock.define_user_analysis_extent(rect, crs)


def set_yogya_extent(dock=None):
    """Zoom to an area occupied by both Jakarta layers in Geo.

    :param dock: A dock widget - if supplied, the extents will also be
        set as the user extent and an appropriate CRS set.
    :type dock: Dock
    """
    rect = QgsRectangle(110.348, -7.732, 110.368, -7.716)
    CANVAS.setExtent(rect)
    if dock is not None:
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        dock.define_user_analysis_extent(rect, crs)


def set_small_jakarta_extent(dock=None):
    """Zoom to an area occupied by both Jakarta layers in Geo.

    :param dock: A dock widget - if supplied, the extents will also be
        set as the user extent and an appropriate CRS set.
    :type dock: Dock
    """
    rect = QgsRectangle(106.8382152, -6.1649805, 106.8382152, -6.1649805)
    CANVAS.setExtent(rect)
    if dock is not None:
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        dock.define_user_analysis_extent(rect, crs)


def compare_two_vector_layers(control_layer, test_layer):
    """Compare two vector layers (same geometries and same attributes)

    :param control_layer: The control layer.
    :type control_layer: QgsVectorLayer

    :param test_layer: The layer being checked.
    :type test_layer: QgsVectorLayer

    :returns: Success or failure indicator, message providing notes.
    :rtype: bool, str
    """

    if test_layer.geometryType() != control_layer.geometryType():
        return False, 'These two layers are not using the same geometry type.'

    if test_layer.crs().authid() != control_layer.crs().authid():
        return False, 'These two layers are not using the same CRS.'

    if test_layer.featureCount() != control_layer.featureCount():
        return False, 'These two layers haven\'t the same number of features'

    for feature in test_layer.getFeatures():
        for expected in control_layer.getFeatures():
            if feature.attributes() == expected.attributes():
                if feature.geometry().isGeosEqual(expected.geometry()):
                    break
        else:
            return False, 'A feature could not be found in the control layer.'
    else:
        return True, None


class RedirectStreams():
    """Context manager for redirection of stdout and stderr.

    This is from
    http://stackoverflow.com/questions/6796492/
    python-temporarily-redirect-stdout-stderr

    In this context, the class is used to get rid of QGIS
    output in the test suite - BUT IT DOESN'T WORK (Maybe
    because QGIS starts its providers in a different process?)

    Usage:

    devnull = open(os.devnull, 'w')
    print('Fubar')

    with RedirectStreams(stdout=devnull, stderr=devnull):
        print("You'll never see me")

    print("I'm back!")
    """

    def __init__(self, stdout=None, stderr=None):
        """

        :param stdout:
        :param stderr:
        """
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr
        self.old_stdout = None
        self.old_stderr = None

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush()
        self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush()
        self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr


def get_ui_state(dock):
    """Get state of the 3 combos on the DOCK dock.

    This method is purely for testing and not to be confused with the
    saveState and restoreState methods of dock.

    :param dock: The dock instance to get the state from.
    :type dock: Dock

    :returns: A dictionary of key, value pairs. See below for details.
    :rtype: dict

    Example return:: python

        {'Hazard': 'flood',
         'Exposure': 'population',
         'Run Button Enabled': False}

    """

    hazard = str(dock.hazard_layer_combo.currentText())
    exposure = str(dock.exposure_layer_combo.currentText())
    run_button = dock.run_button.isEnabled()

    return {'Hazard': hazard,
            'Exposure': exposure,
            'Run Button Enabled': run_button}


def canvas_list():
    """Return a string representing the list of canvas layers.

    :returns: The returned string will list layers in correct order but
        formatted with line breaks between each entry.
    :rtype: str
    """
    list_string = ''
    for layer in CANVAS.layers():
        list_string += layer.name() + '\n'
    return list_string


def combos_to_string(dock):
    """Helper to return a string showing the state of all combos.

    :param dock: A dock instance to get the state of combos from.
    :type dock: Dock

    :returns: A descriptive list of the contents of each combo with the
        active combo item highlighted with a >> symbol.
    :rtype: unicode
    """

    string = 'Hazard Layers\n'
    string += '-------------------------\n'
    current_id = dock.hazard_layer_combo.currentIndex()
    for count in range(0, dock.hazard_layer_combo.count()):
        item_text = dock.hazard_layer_combo.itemText(count)
        if count == current_id:
            string += '>> '
        else:
            string += '   '
        string += item_text + '\n'
    string += '\n'
    string += 'Exposure Layers\n'
    string += '-------------------------\n'
    current_id = dock.exposure_layer_combo.currentIndex()
    for count in range(0, dock.exposure_layer_combo.count()):
        item_text = dock.exposure_layer_combo.itemText(count)
        if count == current_id:
            string += '>> '
        else:
            string += '   '
        string += item_text + '\n'

    string += '\n'
    string += 'Aggregation Layers\n'
    string += '-------------------------\n'
    current_id = dock.aggregation_layer_combo.currentIndex()
    for count in range(0, dock.aggregation_layer_combo.count()):
        item_text = dock.aggregation_layer_combo.itemText(count)
        if count == current_id:
            string += '>> '
        else:
            string += '   '
        string += item_text + '\n'

    string += '\n\n >> means combo item is selected'
    return string


def setup_scenario(
        dock,
        hazard,
        exposure,
        ok_button_flag=True,
        aggregation_layer=None,
        aggregation_enabled_flag=None):
    """Helper function to set the gui state to a given scenario.

    :param dock: Dock instance.
    :type dock: Dock

    :param hazard: Name of the hazard combo entry to set.
    :type hazard: str

    :param exposure: Name of exposure combo entry to set.
    :type exposure: str

    :param function: Name of the function combo entry to set.
    :type function: str

    :param function_id: Impact function id that should be used.
    :type function_id: str

    :param ok_button_flag: Optional - whether the ok button should be enabled
            after this scenario is set up.
    :type ok_button_flag: bool

    :param aggregation_layer: Optional - which layer should be used for
            aggregation
    :type aggregation_layer: str

    :param aggregation_enabled_flag: Optional -whether it is expected that
            aggregation should be enabled when the scenario is loaded.
    :type aggregation_enabled_flag: bool

    We require both function and function_id because safe allows for
    multiple functions with the same name but different id's so we need to be
    sure we have the right one.

    .. note:: Layers are not actually loaded - the calling function is
        responsible for that.

    :returns: Two tuple indicating if the setup was successful, and a message
        indicating why it may have failed.
    :rtype: (bool, str)
    """
    if hazard is not None:
        index = dock.hazard_layer_combo.findText(hazard)
        message = ('\nHazard Layer Not Found: %s\n Combo State:\n%s' %
                   (hazard, combos_to_string(dock)))
        if index == -1:
            return False, message
        dock.hazard_layer_combo.setCurrentIndex(index)

    if exposure is not None:
        index = dock.exposure_layer_combo.findText(exposure)
        message = ('\nExposure Layer Not Found: %s\n Combo State:\n%s' %
                   (exposure, combos_to_string(dock)))
        if index == -1:
            return False, message
        dock.exposure_layer_combo.setCurrentIndex(index)

    if aggregation_layer is not None:
        index = dock.aggregation_layer_combo.findText(aggregation_layer)
        message = ('Aggregation layer Not Found: %s\n Combo State:\n%s' %
                   (aggregation_layer, combos_to_string(dock)))
        if index == -1:
            return False, message
        dock.aggregation_layer_combo.setCurrentIndex(index)

    if aggregation_enabled_flag is not None:
        combo_enabled_flag = dock.aggregation_layer_combo.isEnabled()
        if combo_enabled_flag != aggregation_enabled_flag:
            message = (
                'The aggregation combobox should be %s' %
                ('enabled' if aggregation_enabled_flag else 'disabled'))
            return False, message

    # Check that layers and impact function are correct
    state = get_ui_state(dock)

    expected_state = {'Run Button Enabled': ok_button_flag,
                      'Hazard': hazard,
                      'Exposure': exposure}

    message = 'Expected versus Actual State\n'
    message += '--------------------------------------------------------\n'

    for key in list(expected_state.keys()):
        message += 'Expected %s: %s\n' % (key, expected_state[key])
        message += 'Actual   %s: %s\n' % (key, state[key])
        message += '----\n'
    message += '--------------------------------------------------------\n'
    message += combos_to_string(dock)

    if state != expected_state:
        return False, message

    return True, 'Matched ok.'


def populate_dock(dock):
    """A helper function to populate the DOCK and set it to a valid state.

    :param dock: A dock instance.
    :type dock: Dock
    """
    load_standard_layers(dock)
    dock.hazard_layer_combo.setCurrentIndex(0)
    dock.exposure_layer_combo.setCurrentIndex(0)


def load_standard_layers(dock=None):
    """Helper function to load standard layers into the dialog.

    :param dock: A valid dock instance.
    :type dock: Dock
    """
    # NOTE: Adding new layers here may break existing tests since
    # combos are populated alphabetically. Each test will
    # provide a detailed diagnostic if you break it so make sure
    # to consult that and clean up accordingly.
    #
    # Update on above. We are refactoring tests so they use find on combos
    # to set them appropriately, instead of relative in combo position
    # so you should be able to put datasets in any order below.
    # If changing the order does cause tests to fail, please update the tests
    # to also use find instead of relative position. (Tim)
    #
    # WARNING: Please keep test/data/project/load_standard_layers.qgs in sync
    file_list = [
        standard_data_path('hazard', 'flood_multipart_polygons.shp'),
        standard_data_path('hazard', 'floods.shp'),
        standard_data_path('hazard', 'classified_generic_polygon.shp'),
        standard_data_path('hazard', 'volcano_krb.shp'),
        standard_data_path('hazard', 'classified_flood_20_20.asc'),
        standard_data_path('hazard', 'continuous_flood_20_20.asc'),
        standard_data_path('hazard', 'tsunami_wgs84.tif'),
        standard_data_path('hazard', 'earthquake.tif'),
        standard_data_path('hazard', 'ash_raster_wgs84.tif'),
        standard_data_path('hazard', 'volcano_point.geojson'),
        standard_data_path('exposure', 'building-points.shp'),
        standard_data_path('exposure', 'buildings.shp'),
        standard_data_path('exposure', 'census.geojson'),
        standard_data_path('exposure', 'roads.shp'),
        standard_data_path('exposure', 'landcover.geojson'),
        standard_data_path('exposure', 'pop_binary_raster_20_20.asc'),
        standard_data_path('aggregation', 'grid_jakarta.geojson'),
        standard_data_path('aggregation', 'district_osm_jakarta.geojson'),
    ]
    hazard_layer_count, exposure_layer_count = load_layers(
        file_list, dock=dock)
    # FIXME (MB) -2 is until we add the aggregation category because of
    # kabupaten_jakarta_singlepart not being either hazard nor exposure layer

    number_exposure_hazard = hazard_layer_count + exposure_layer_count
    expected_number_exposure_hazard = len(file_list) - 2
    if number_exposure_hazard != expected_number_exposure_hazard:
        message = (
            'Loading standard layers failed. Expecting layer the number of '
            'hazard_layer and exposure_layer is equals to %d but got %d' % (
                (expected_number_exposure_hazard),
                number_exposure_hazard))
        raise Exception(message)

    return hazard_layer_count, exposure_layer_count


def compare_wkt(a, b, tol=0.000001):
    """Helper function to compare WKT geometries with given tolerance
    Taken from QGIS test suite

    :param a: Input WKT geometry
    :type a: str

    :param b: Expected WKT geometry
    :type b: str

    :param tol: compare tolerance
    :type tol: float

    :return: True on success, False on failure
    :rtype: bool
    """
    r = re.compile(r'-?\d+(?:\.\d+)?(?:[eE]\d+)?')

    # Text might upper or lower case
    a = a.upper()
    b = b.upper()

    # Might have a space between the text and coordinates
    geometry_type = a.split('(', 1)
    a = geometry_type[0].replace(' ', '') + '('.join(geometry_type[1:])
    geometry_type = b.split('(', 1)
    b = geometry_type[0].replace(' ', '') + '('.join(geometry_type[1:])

    # compare the structure
    a0 = r.sub("#", a)
    b0 = r.sub("#", b)
    if a0 != b0:
        return False

    # compare the numbers with given tolerance
    a0 = r.findall(a)
    b0 = r.findall(b)
    if len(a0) != len(b0):
        return False

    for (a1, b1) in zip(a0, b0):
        if abs(float(a1) - float(b1)) > tol:
            return False

    return True


def load_layers(
        layer_list,
        clear_flag=True,
        dock=None):
    """Helper function to load layers as defined in a python list.

    :param dock: A valid dock instance.
    :type dock: Dock

    :param clear_flag: Whether to clear currently loaded layers before loading
        the new layers.
    :type clear_flag: bool

    :param layer_list: A list of layer's paths to load.
    :type layer_list: list(str)
    """
    # First unload any layers that may already be loaded
    if clear_flag:
        # noinspection PyArgumentList
        QgsProject.instance().removeAllMapLayers()

    # Now go ahead and load our layers
    exposure_layer_count = 0
    hazard_layer_count = 0
    map_layer_list = []
    # Now create our new layers
    for layer_file in layer_list:

        layer, layer_type = load_layer(layer_file)
        if layer_type == 'hazard':
            hazard_layer_count += 1
        elif layer_type == 'exposure':
            exposure_layer_count += 1

        # Add layer to the registry (that Qgis knows about) a slot
        # in qgis_interface will also ensure it gets added to the canvas

        # noinspection PyArgumentList
        map_layer_list.append(layer)

    # noinspection PyArgumentList
    QgsProject.instance().addMapLayers(map_layer_list)

    if dock is not None:
        dock.get_layers()

    # Add MCL's to the CANVAS
    return hazard_layer_count, exposure_layer_count


def clone_shp_layer(
        name,
        include_keywords,
        source_directory,
        target_directory='test'):
    """Helper function that copies a test shp layer and returns it.

    :param name: The default name for the shp layer.
    :type name: str

    :param include_keywords: Include keywords file if True.
    :type include_keywords: bool

    :param source_directory: Directory where the file is located.
    :type source_directory: str

    :param target_directory: Subdirectory in InaSAFE temp dir that we want to
        put the files into. Default to 'test'.
    :type target_directory: str
    """
    extensions = ['.shp', '.shx', '.dbf', '.prj']
    if include_keywords:
        extensions.append('.xml')
    temp_path = unique_filename(dir=temp_dir(target_directory))
    # copy to temp file
    for ext in extensions:
        src_path = os.path.join(source_directory, name + ext)
        if os.path.exists(src_path):
            target_path = temp_path + ext
            shutil.copy2(src_path, target_path)

    shp_path = '%s.shp' % temp_path
    layer = QgsVectorLayer(shp_path, os.path.basename(shp_path), 'ogr')

    monkey_patch_keywords(layer)

    return layer


def clone_csv_layer(
        name,
        source_directory,
        target_directory='test'):
    """Helper function that copies a test csv layer and returns it.

    :param name: The default name for the csv layer.
    :type name: str

    :param source_directory: Directory where the file is located.
    :type source_directory: str

    :param target_directory: Subdirectory in InaSAFE temp dir that we want to
        put the files into. Default to 'test'.
    :type target_directory: str
    """
    file_path = '%s.csv' % name
    temp_path = unique_filename(dir=temp_dir(target_directory))
    # copy to temp file
    source_path = os.path.join(source_directory, file_path)
    shutil.copy2(source_path, temp_path)
    # return a single predefined layer
    layer = QgsVectorLayer(temp_path, '', 'delimitedtext')
    return layer


def clone_raster_layer(
        name,
        extension,
        include_keywords,
        source_directory,
        target_directory='test'):
    """Helper function that copies a test raster.

    :param name: The default name for the raster layer.
    :type name: str

    :param extension: The extension of the raster file.
    :type extension: str

    :param include_keywords: Include keywords file if True.
    :type include_keywords: bool

    :param source_directory: Directory where the file is located.
    :type source_directory: str

    :param target_directory: Subdirectory in InaSAFE temp dir that we want to
        put the files into. Default to 'testing'.
    :type target_directory: str
    """
    extensions = ['.prj', '.sld', '.qml', extension]
    if include_keywords:
        extensions.append('.xml')
    temp_path = unique_filename(dir=temp_dir(target_directory))
    # copy to temp file
    for ext in extensions:
        src_path = os.path.join(source_directory, name + ext)
        if os.path.exists(src_path):
            trg_path = temp_path + ext
            shutil.copy2(src_path, trg_path)

    raster_path = '%s%s' % (temp_path, extension)
    if not os.path.exists(raster_path):
        raise Exception('Path not found : %s' % raster_path)

    layer = QgsRasterLayer(raster_path, os.path.basename(raster_path))
    if not layer.isValid:
        raise Exception('Layer is not valid.')

    monkey_patch_keywords(layer)

    return layer


def remove_vector_temp_file(file_path):
    """Helper function that removes temp file created during test.

    Also its keywords file will be removed.

    :param file_path: File path to be removed.
    :type file_path: str
    """
    file_path = file_path[:-4]
    extensions = ['.shp', '.shx', '.dbf', '.prj', '.xml']
    extensions.extend(['.prj', '.sld', 'qml'])
    for ext in extensions:
        if os.path.exists(file_path + ext):
            os.remove(file_path + ext)


class FakeLayer():

    """A Mock layer.

    :param source:
    """

    def __init__(self, source=None):
        self.layer_source = source

    def source(self):
        """Get the sources as defined in init

        :return: sources
        """
        return self.layer_source


def get_control_text(file_name):
    """Helper to get control text for string compares.

    :param file_name: filename
    :type file_name: str

    :returns: A string containing the contents of the file.
    """
    control_file_path = standard_data_path(
        'control',
        'files',
        file_name
    )
    expected_result = codecs.open(
        control_file_path,
        mode='r',
        encoding='utf-8').readlines()
    return expected_result
