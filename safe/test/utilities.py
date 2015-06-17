# coding=utf-8
"""Helper module for gui test suite
"""

import os
import re
import sys
import hashlib
import logging
import platform
import glob
import shutil
from itertools import izip

from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsMapLayerRegistry)
# noinspection PyPackageRequirements
from PyQt4 import QtGui  # pylint: disable=W0621

# For testing and demoing
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
from safe.gis.numerics import axes_to_points
from safe.impact_functions import register_impact_functions
from safe.utilities.utilities import read_file_keywords
from safe.common.utilities import unique_filename, temp_dir
from safe.common.exceptions import NoKeywordsFoundError
from safe.utilities.clipper import extent_to_geoarray, clip_layer
from safe.utilities.gis import get_wgs84_resolution

QGIS_APP = None  # Static variable used to hold hand to running QGIS app
CANVAS = None
PARENT = None
IFACE = None
YOGYA2006_title = 'An earthquake in Yogyakarta like in 2006'
PADANG2009_title = 'An earthquake in Padang like in 2009'
LOGGER = logging.getLogger('InaSAFE')
GEOCRS = 4326  # constant for EPSG:GEOCRS Geographic CRS id
GOOGLECRS = 3857  # constant for EPSG:GOOGLECRS Google Mercator id
DEVNULL = open(os.devnull, 'w')

# FIXME AG: We are going to remove the usage of all the data from
# inasafe_data and just use data in test_data_path. But until that is done,
# we still keep TESTDATA, HAZDATA, EXPDATA, and BOUNDATA below

# Assuming test data three lvls up
pardir = os.path.abspath(os.path.join(
    os.path.realpath(os.path.dirname(__file__)),
    '..',
    '..',
    '..'))

# Location of test data
DATANAME = 'inasafe_data'
DATADIR = os.path.join(pardir, DATANAME)

# Bundled test data
TESTDATA = os.path.join(DATADIR, 'test')  # Artificial datasets
HAZDATA = os.path.join(DATADIR, 'hazard')  # Real hazard layers
EXPDATA = os.path.join(DATADIR, 'exposure')  # Real exposure layers
BOUNDDATA = os.path.join(DATADIR, 'boundaries')  # Real exposure layers


def get_qgis_app():
    """ Start one QGIS application to test against.

    :returns: Handle to QGIS app, canvas, iface and parent. If there are any
        errors the tuple members will be returned as None.
    :rtype: (QgsApplication, CANVAS, IFACE, PARENT)

    If QGIS is already running the handle to that app will be returned.
    """

    try:
        from qgis.core import QgsApplication
        from qgis.gui import QgsMapCanvas  # pylint: disable=no-name-in-module
        # noinspection PyPackageRequirements
        from PyQt4 import QtGui, QtCore  # pylint: disable=W0621
        # noinspection PyPackageRequirements
        from PyQt4.QtCore import QCoreApplication, QSettings
        from safe.gis.qgis_interface import QgisInterface
    except ImportError:
        return None, None, None, None

    global QGIS_APP  # pylint: disable=W0603

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
        QGIS_APP = QgsApplication(sys.argv, gui_flag)

        # Make sure QGIS_PREFIX_PATH is set in your env if needed!
        QGIS_APP.initQgis()
        s = QGIS_APP.showSettings()
        LOGGER.debug(s)

        # Save some settings
        settings = QSettings()
        settings.setValue('locale/overrideFlag', True)
        settings.setValue('locale/userLocale', 'en_US')

    global PARENT  # pylint: disable=W0603
    if PARENT is None:
        # noinspection PyPep8Naming
        PARENT = QtGui.QWidget()

    global CANVAS  # pylint: disable=W0603
    if CANVAS is None:
        # noinspection PyPep8Naming
        CANVAS = QgsMapCanvas(PARENT)
        CANVAS.resize(QtCore.QSize(400, 400))

    global IFACE  # pylint: disable=W0603
    if IFACE is None:
        # QgisInterface is a stub implementation of the QGIS plugin interface
        # noinspection PyPep8Naming
        IFACE = QgisInterface(CANVAS)
        register_impact_functions()

    return QGIS_APP, CANVAS, IFACE, PARENT


def assert_hashes_for_file(hashes, filename):
    """Assert that a files has matches one of a list of expected hashes
    :param filename: the filename
    :param hashes: the hash of the file
    """
    file_hash = hash_for_file(filename)
    message = (
        'Unexpected hash'
        '\nGot: %s'
        '\nExpected: %s'
        '\nPlease check graphics %s visually '
        'and add to list of expected hashes '
        'if it is OK on this platform.' % (file_hash, hashes, filename))
    if file_hash not in hashes:
        raise Exception(message)


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


def test_data_path(*args):
    """Return the absolute path to the InaSAFE test data or directory path.

    .. versionadded:: 3.0

    :param args: List of path e.g. ['control', 'files',
        'test-error-message.txt'] or ['control', 'scenarios'] to get the path
        to scenarios dir.
    :type args: list

    :return: Absolute path to the test data or dir path.
    :rtype: str

    """
    path = os.path.dirname(__file__)
    path = os.path.abspath(os.path.join(path, 'data'))
    for item in args:
        path = os.path.abspath(os.path.join(path, item))

    return path


def load_layer(layer_path):
    """Helper to load and return a single QGIS layer

    :param layer_path: Path name to raster or vector file.
    :type layer_path: str

    :returns: tuple containing layer and its layer_purpose.
    :rtype: (QgsMapLayer, str)

    """
    # Extract basename and absolute path
    file_name = os.path.split(layer_path)[-1]  # In case path was absolute
    base_name, extension = os.path.splitext(file_name)

    # Determine if layer is hazard or exposure
    layer_purpose = 'undefined'
    try:
        keywords = read_file_keywords(layer_path)
        if 'layer_purpose' in keywords:
            layer_purpose = keywords['layer_purpose']
    except NoKeywordsFoundError:
        pass

    # Create QGis Layer Instance
    if extension in ['.asc', '.tif']:
        layer = QgsRasterLayer(layer_path, base_name)
    elif extension in ['.shp']:
        layer = QgsVectorLayer(layer_path, base_name, 'ogr')
    else:
        message = 'File %s had illegal extension' % layer_path
        raise Exception(message)

    # noinspection PyUnresolvedReferences
    message = 'Layer "%s" is not valid' % layer.source()
    # noinspection PyUnresolvedReferences
    if not layer.isValid():
        print message
    # noinspection PyUnresolvedReferences
    if not layer.isValid():
        raise Exception(message)
    return layer, layer_purpose


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


def set_padang_extent(dock=None):
    """Zoom to an area occupied by both both Padang layers.

    :param dock: A dock widget - if supplied, the extents will also be
        set as the user extent and an appropriate CRS set.
    :type dock: Dock
    """
    rect = QgsRectangle(100.21, -1.05, 100.63, -0.84)
    CANVAS.setExtent(rect)
    if dock is not None:
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        dock.define_user_analysis_extent(rect, crs)


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


def set_batemans_bay_extent(dock=None):
    """Zoom to an area occupied by both Batemans Bay layers in geo crs.

    :param dock: A dock widget - if supplied, the extents will also be
        set as the user extent and an appropriate CRS set.
    :type dock: Dock
    """
    rect = QgsRectangle(150.152, -35.710, 150.187, -35.7013)
    CANVAS.setExtent(rect)
    if dock is not None:
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
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


def set_manila_extent(dock=None):
    """Zoom to an area occupied by both Manila layers in Geo.

    :param dock: A dock widget - if supplied, the extents will also be
        set as the user extent and an appropriate CRS set.
    :type dock: Dock
    """
    rect = QgsRectangle(120.866995, 14.403305, 121.193824, 14.784944)
    CANVAS.setExtent(rect)
    if dock is not None:
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        dock.define_user_analysis_extent(rect, crs)


def set_geo_extent(bounding_box, dock=None):
    """Zoom to an area specified given bounding box.

    :param bounding_box: List containing [xmin, ymin, xmax, ymax]
    :type bounding_box: list

    :param dock: A dock widget - if supplied, the extents will also be
        set as the user extent and an appropriate CRS set.
    :type dock: Dock
    """
    rect = QgsRectangle(*bounding_box)
    CANVAS.setExtent(rect)
    if dock is not None:
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        dock.define_user_analysis_extent(rect, crs)
        print dock.extent.user_extent.toString(), 'set geo extent'


def check_images(control_image, test_image_path, tolerance=1000):
    r"""Compare a test image against a collection of known good images.

    :param tolerance: How many pixels may be different between the
        two images.
    :type tolerance: int

    :param test_image_path: The Image being checked (must have same dimensions
        as the control image). Must be full path to image.
    :type test_image_path: str

    :param control_image: The basename for the control image. The .png
        extension will automatically be added and the test image dir
        (safe/test/data/control/images) will be prepended. e.g.
        addClassToLegend will cause the control image of
        test\/data\/control/images\/addClassToLegend.png to be used.
    :type control_image: str

    :returns: Success or failure indicator, message providing analysis,
        comparison notes
    :rtype: bool, str
    """
    control_image_dir = test_data_path('control', 'images')
    messages = ''
    platform_name = get_platform_name()
    base_name, extension = os.path.splitext(control_image)
    platform_image = os.path.join(control_image_dir, '%s-variant%s%s.png' % (
        base_name, platform_name, extension))
    messages += 'Checking for platform specific variant...\n'
    messages += test_image_path + '\n'
    messages += platform_image + '\n'
    # It the platform image exists, we should test only that!
    if os.path.exists(platform_image):
        flag, message = check_image(
            platform_image, test_image_path, tolerance)
        messages += message + '\n'
        return flag, messages

    messages += (
        '\nNo platform specific control image could be found,\n'
        'testing against all control images. Try adding %s in\n '
        'the file name if you want it to be detected for this\n'
        'platform which will speed up image comparison tests.\n' %
        platform_name)

    # Ok there is no specific platform match so go ahead and match to any of
    # the control image and its variants...
    control_images = glob.glob('%s/%s*%s' % (
        control_image_dir, base_name, extension))
    flag = False

    for control_image in control_images:
        full_path = os.path.join(
            control_image_dir, control_image)
        flag, message = check_image(
            full_path, test_image_path, tolerance)
        messages += message
        # As soon as one passes we are done!
        if flag:
            print 'match with: ', control_image
            break
        LOGGER.debug('No match for control image %s' % control_image)

    return flag, messages


def check_image(control_image_path, test_image_path, tolerance=1000):
    """Compare a test image against a known good image.

    :param tolerance: How many pixels may be different between the two images.
    :type tolerance: int

    :param test_image_path: The Image being checked (must have same dimensions
        as the control image).
    :type test_image_path: str

    :param control_image_path: The image representing expected output.
    :type control_image_path: str

    :returns: Two tuple consisting of success or failure indicator and a
        message providing analysis comparison notes.
    :rtype: (bool, str)
    """

    try:
        if not os.path.exists(test_image_path):
            LOGGER.debug('checkImage: Test image does not exist:\n%s' %
                         test_image_path)
            raise OSError
        test_image = QtGui.QImage(test_image_path)
    except OSError:
        message = 'Test image:\n{0:s}\ncould not be loaded'.format(
            test_image_path)
        return False, message

    try:
        if not os.path.exists(control_image_path):
            LOGGER.debug('checkImage: Control image does not exist:\n%s' %
                         control_image_path)
            raise OSError
        control_image = QtGui.QImage(control_image_path)
    except OSError:
        message = 'Control image:\n{0:s}\ncould not be loaded.\n'
        return False, message

    if (control_image.width() != test_image.width() or
            control_image.height() != test_image.height()):
        message = (
            'Control and test images are different sizes.\n'
            'Control image   : %s (%i x %i)\n'
            'Test image      : %s (%i x %i)\n'
            'If this test has failed look at the above images '
            'to try to determine what may have change or '
            'adjust the tolerance if needed.' %
            (
                control_image_path,
                control_image.width(),
                control_image.height(),
                test_image_path,
                test_image.width(),
                test_image.height()))
        LOGGER.debug(message)
        return False, message

    image_width = control_image.width()
    image_height = control_image.height()
    mismatch_count = 0

    difference_image = QtGui.QImage(
        image_width,
        image_height,
        QtGui.QImage.Format_ARGB32_Premultiplied)
    difference_image.fill(152 + 219 * 256 + 249 * 256 * 256)

    for y in range(image_height):
        for x in range(image_width):
            control_pixel = control_image.pixel(x, y)
            test_pixel = test_image.pixel(x, y)
            if control_pixel != test_pixel:
                mismatch_count += 1
                difference_image.setPixel(x, y, QtGui.qRgb(255, 0, 0))
    difference_path = unique_filename(
        prefix='difference-%s' % os.path.basename(control_image_path),
        suffix='.png',
        dir=temp_dir('test'))
    LOGGER.debug('Saving difference image as: %s' % difference_path)
    difference_image.save(difference_path, "PNG")

    # allow pixel deviation of 1 percent
    pixel_count = image_width * image_height
    # TODO (Ole): Use relative error i.e. mismatch count/total pixels
    if mismatch_count > tolerance:
        success_flag = False
    else:
        success_flag = True
    message = (
        '%i of %i pixels are mismatched. Tolerance is %i.\n'
        'Control image   : %s\n'
        'Test image      : %s\n'
        'Difference image: %s\n'
        'If this test has failed look at the above images '
        'to try to determine what may have change or '
        'adjust the tolerance if needed.' %
        (
            mismatch_count,
            pixel_count,
            tolerance,
            control_image_path,
            test_image_path,
            difference_path))
    return success_flag, message


class RedirectStreams(object):
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


def get_platform_name():
    """Get a platform name for this host.

        e.g OSX10.8
        Windows7-SP1-AMD64
        LinuxMint-14-x86_64
    """
    platform_name = platform.system()
    if platform_name == 'Darwin':
        name = 'OSX'
        name += '.'.join(platform.mac_ver()[0].split('.')[0:2])
        return name
    elif platform_name == 'Linux':
        name = '-'.join(platform.dist()[:-1]) + '-' + platform.machine()
        return name
    elif platform_name == 'Windows':
        name = 'Windows'
        win32_version = platform.win32_ver()
        platform_machine = platform.machine()
        name += win32_version[0] + '-' + win32_version[2]
        name += '-' + platform_machine
        return name
    else:
        return None


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
         'Impact Function Title': 'be affected',
         'Impact Function Id': 'FloodImpactFunction',
         'Run Button Enabled': False}

    """

    hazard = str(dock.cboHazard.currentText())
    exposure = str(dock.cboExposure.currentText())
    impact_function_title = str(dock.cboFunction.currentText())
    impact_function_id = dock.get_function_id()
    run_button = dock.pbnRunStop.isEnabled()

    return {'Hazard': hazard,
            'Exposure': exposure,
            'Impact Function Title': impact_function_title,
            'Impact Function Id': impact_function_id,
            'Run Button Enabled': run_button}


def formatted_list(layer_list):
    """Return a string representing a list of layers

    :param layer_list: A list of layers.
    :type layer_list: list

    :returns: The returned string will list layers in correct order but
        formatted with line breaks between each entry.
    :rtype: str
    """
    list_string = ''
    for item in layer_list:
        list_string += item + '\n'
    return list_string


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

    string = u'Hazard Layers\n'
    string += '-------------------------\n'
    current_id = dock.cboHazard.currentIndex()
    for count in range(0, dock.cboHazard.count()):
        item_text = dock.cboHazard.itemText(count)
        if count == current_id:
            string += '>> '
        else:
            string += '   '
        string += item_text + '\n'
    string += '\n'
    string += 'Exposure Layers\n'
    string += '-------------------------\n'
    current_id = dock.cboExposure.currentIndex()
    for count in range(0, dock.cboExposure.count()):
        item_text = dock.cboExposure.itemText(count)
        if count == current_id:
            string += '>> '
        else:
            string += '   '
        string += item_text + '\n'

    string += '\n'
    string += 'Functions\n'
    string += '-------------------------\n'
    current_id = dock.cboFunction.currentIndex()
    for count in range(0, dock.cboFunction.count()):
        item_text = dock.cboFunction.itemText(count)
        if count == current_id:
            string += '>> '
        else:
            string += '   '
        string += '%s (Function ID: %s)\n' % (
            item_text, dock.get_function_id(current_id))

    string += '\n'
    string += 'Aggregation Layers\n'
    string += '-------------------------\n'
    current_id = dock.cboAggregation.currentIndex()
    for count in range(0, dock.cboAggregation.count()):
        item_text = dock.cboAggregation.itemText(count)
        if count == current_id:
            string += '>> '
        else:
            string += '   '
        string += item_text + '\n'

    string += '\n\n >> means combo item is selected'
    return string


def get_function_index(dock, function_id):
    """Get the combo index for a function given its function_id.

    :param dock: A dock instance.
    :type dock: Dock

    :param function_id: The function id e.g. FloodEvacuationImpactFunction.
    :type function_id: str
    """

    index = -1
    for count in range(dock.cboFunction.count()):
        next_function_id = dock.get_function_id(count)
        if function_id == next_function_id:
            index = count
            break
    return index


def setup_scenario(
        dock,
        hazard,
        exposure,
        function_id,
        function=None,
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
        index = dock.cboHazard.findText(hazard)
        message = ('\nHazard Layer Not Found: %s\n Combo State:\n%s' %
                   (hazard, combos_to_string(dock)))
        if index == -1:
            return False, message
        dock.cboHazard.setCurrentIndex(index)

    if exposure is not None:
        index = dock.cboExposure.findText(exposure)
        message = ('\nExposure Layer Not Found: %s\n Combo State:\n%s' %
                   (exposure, combos_to_string(dock)))
        if index == -1:
            return False, message
        dock.cboExposure.setCurrentIndex(index)

    if function_id is not None:
        index = get_function_index(dock, function_id)
        message = ('\nImpact Function Not Found: %s\n Combo State:\n%s' %
                   (function, combos_to_string(dock)))
        if index == -1:
            return False, message
        dock.cboFunction.setCurrentIndex(index)

    if aggregation_layer is not None:
        index = dock.cboAggregation.findText(aggregation_layer)
        message = ('Aggregation layer Not Found: %s\n Combo State:\n%s' %
                   (aggregation_layer, combos_to_string(dock)))
        if index == -1:
            return False, message
        dock.cboAggregation.setCurrentIndex(index)

    if aggregation_enabled_flag is not None:
        if dock.cboAggregation.isEnabled() != aggregation_enabled_flag:
            message = (
                'The aggregation combobox should be %s' %
                ('enabled' if aggregation_enabled_flag else 'disabled'))
            return False, message

    # Check that layers and impact function are correct
    state = get_ui_state(dock)

    expected_state = {'Run Button Enabled': ok_button_flag,
                      'Impact Function Id': function_id,
                      'Hazard': hazard,
                      'Exposure': exposure}
    if function is not None:
        expected_state['Impact Function Title'] = function
    else:
        state.pop('Impact Function Title')

    message = 'Expected versus Actual State\n'
    message += '--------------------------------------------------------\n'

    for key in expected_state.keys():
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
    dock.cboHazard.setCurrentIndex(0)
    dock.cboExposure.setCurrentIndex(0)


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
        test_data_path('exposure', 'building-points.shp'),
        test_data_path('exposure', 'buildings.shp'),
        test_data_path('hazard', 'volcano_point.shp'),
        test_data_path('exposure', 'roads.shp'),
        test_data_path('hazard', 'flood_multipart_polygons.shp'),
        test_data_path('hazard', 'classified_generic_polygon.shp'),
        test_data_path('hazard', 'volcano_krb.shp'),
        test_data_path('exposure', 'pop_binary_raster_20_20.asc'),
        test_data_path('hazard', 'classified_flood_20_20.asc'),
        test_data_path('hazard', 'continuous_flood_20_20.asc'),
        test_data_path('hazard', 'tsunami_wgs84.tif'),
        test_data_path('hazard', 'earthquake.tif'),
        test_data_path('boundaries', 'district_osm_jakarta.shp'),
    ]
    hazard_layer_count, exposure_layer_count = load_layers(
        file_list, dock=dock)
    # FIXME (MB) -1 is until we add the aggregation category because of
    # kabupaten_jakarta_singlepart not being either hazard nor exposure layer

    if hazard_layer_count + exposure_layer_count != len(file_list) - 1:
        message = (
            'Loading standard layers failed. Expecting layer the number of '
            'hazard_layer and exposure_layer is equals to %d but got %d' % (
                (len(file_list) - 1),
                hazard_layer_count + exposure_layer_count))
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

    for (a1, b1) in izip(a0, b0):
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
        QgsMapLayerRegistry.instance().removeAllMapLayers()

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

        # Add layer to the registry (that QGis knows about) a slot
        # in qgis_interface will also ensure it gets added to the canvas

        # noinspection PyArgumentList
        map_layer_list.append(layer)

    # noinspection PyArgumentList
    QgsMapLayerRegistry.instance().addMapLayers(map_layer_list)

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
        extensions.append('.keywords')
    temp_path = unique_filename(dir=temp_dir(target_directory))
    # copy to temp file
    for ext in extensions:
        src_path = os.path.join(source_directory, name + ext)
        if os.path.exists(src_path):
            target_path = temp_path + ext
            shutil.copy2(src_path, target_path)

    shp_path = '%s.shp' % temp_path
    layer = QgsVectorLayer(shp_path, os.path.basename(shp_path), 'ogr')
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
    extensions = ['.prj', '.sld', 'qml', '.prj', extension]
    if include_keywords:
        extensions.append('.keywords')
    temp_path = unique_filename(dir=temp_dir(target_directory))
    # copy to temp file
    for ext in extensions:
        src_path = os.path.join(source_directory, name + ext)
        if os.path.exists(src_path):
            trg_path = temp_path + ext
            shutil.copy2(src_path, trg_path)

    raster_path = '%s%s' % (temp_path, extension)
    layer = QgsRasterLayer(raster_path, os.path.basename(raster_path))
    return layer


def remove_vector_temp_file(file_path):
    """Helper function that removes temp file created during test.

    Also its keywords file will be removed.

    :param file_path: File path to be removed.
    :type file_path: str
    """
    file_path = file_path[:-4]
    extensions = ['.shp', '.shx', '.dbf', '.prj', '.keywords']
    extensions.extend(['.prj', '.sld', 'qml'])
    for ext in extensions:
        if os.path.exists(file_path + ext):
            os.remove(file_path + ext)


def combine_coordinates(x, y):
    """Make list of all combinations of points for x and y coordinates
    :param x:
    :param y:
    """
    return axes_to_points(x, y)


class FakeLayer(object):
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


def clip_layers(first_layer_path, second_layer_path):
    """Clip and resample layers with the reference to the first layer.

    :param first_layer_path: Path to the first layer path.
    :type first_layer_path: str

    :param second_layer_path: Path to the second layer path.
    :type second_layer_path: str

    :return: Path to the clipped datasets (clipped 1st layer, clipped 2nd
        layer).
    :rtype: tuple(str, str)

    :raise
        FileNotFoundError
    """
    base_name, _ = os.path.splitext(first_layer_path)
    # noinspection PyCallingNonCallable
    first_layer = QgsRasterLayer(first_layer_path, base_name)
    base_name, _ = os.path.splitext(second_layer_path)
    # noinspection PyCallingNonCallable
    second_layer = QgsRasterLayer(second_layer_path, base_name)

    # Get the firs_layer extents as an array in EPSG:4326
    first_layer_geo_extent = extent_to_geoarray(
        first_layer.extent(),
        first_layer.crs())

    first_layer_geo_cell_size, _ = get_wgs84_resolution(first_layer)
    second_layer_geo_cell_size, _ = get_wgs84_resolution(second_layer)

    if first_layer_geo_cell_size < second_layer_geo_cell_size:
        cell_size = first_layer_geo_cell_size
    else:
        cell_size = second_layer_geo_cell_size

    clipped_first_layer = clip_layer(
        layer=first_layer,
        extent=first_layer_geo_extent,
        cell_size=cell_size)

    clipped_second_layer = clip_layer(
        layer=second_layer,
        extent=first_layer_geo_extent,
        cell_size=cell_size)

    return clipped_first_layer, clipped_second_layer
