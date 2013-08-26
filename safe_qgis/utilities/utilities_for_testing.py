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
from os.path import join
from itertools import izip

from PyQt4 import QtGui, QtCore
from qgis.core import (
    QgsApplication,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsMapLayerRegistry)
from qgis.gui import QgsMapCanvas
from safe_qgis.test.qgis_interface import QgisInterface

# For testing and demoing
from safe_qgis.safe_interface import (
    read_file_keywords,
    unique_filename,
    temp_dir,
    TESTDATA,
    UNITDATA)

from safe_qgis.safe_interface import HAZDATA, EXPDATA


YOGYA2006_title = 'An earthquake in Yogyakarta like in 2006'
PADANG2009_title = 'An earthquake in Padang like in 2009'

TEST_FILES_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../test/test_data/test_files'))

SCENARIO_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../test/test_data/test_scenarios'))


LOGGER = logging.getLogger('InaSAFE')

QGISAPP = None  # Static vainasafele used to hold hand to running QGis app
CANVAS = None
PARENT = None
IFACE = None
GEOCRS = 4326  # constant for EPSG:GEOCRS Geographic CRS id
GOOGLECRS = 900913  # constant for EPSG:GOOGLECRS Google Mercator id
DEVNULL = open(os.devnull, 'w')
CONTROL_IMAGE_DIR = os.path.join(
    os.path.dirname(__file__),
    '../test/test_data/test_images')


def assert_hashes_for_file(hashes, filename):
    """Assert that a files has matches one of a list of expected hashes
    :param filename: the filename
    :param hashes: the hash of the file
    """
    myHash = hash_for_file(filename)
    myMessage = ('Unexpected hash'
                 '\nGot: %s'
                 '\nExpected: %s'
                 '\nPlease check graphics %s visually '
                 'and add to list of expected hashes '
                 'if it is OK on this platform.' % (myHash, hashes, filename))
    assert myHash in hashes, myMessage


def assert_hash_for_file(hash_string, filename):
    """Assert that a files has matches its expected hash
    :param filename:
    :param hash_string:
    """
    myHash = hash_for_file(filename)
    myMessage = ('Unexpected hash'
                 '\nGot: %s'
                 '\nExpected: %s' % (myHash, hash_string))
    assert myHash == hash_string, myMessage


def hash_for_file(filename):
    """Return an md5 checksum for a file
    :param filename:
    """
    myPath = filename
    myData = file(myPath, 'rb').read()
    myHash = hashlib.md5()
    myHash.update(myData)
    myHash = myHash.hexdigest()
    return myHash


def get_qgis_app():
    """ Start one QGis application to test against

    Input
        NIL

    Output
        handle to qgis app


    If QGis is already running the handle to that app will be returned
    """

    global QGISAPP  # pylint: disable=W0603

    if QGISAPP is None:
        myGuiFlag = True  # All test will run qgis in safe_qgis mode
        QGISAPP = QgsApplication(sys.argv, myGuiFlag)

        # Note: This block is not needed for  QGIS > 1.8 which will
        # automatically check the QGIS_PREFIX_PATH var so it is here
        # for backwards compatibility only
        if 'QGIS_PREFIX_PATH' in os.environ:
            myPath = os.environ['QGIS_PREFIX_PATH']
            myUseDefaultPathFlag = True
            QGISAPP.setPrefixPath(myPath, myUseDefaultPathFlag)

        QGISAPP.initQgis()
        s = QGISAPP.showSettings()
        LOGGER.debug(s)

    global PARENT  # pylint: disable=W0603
    if PARENT is None:
        PARENT = QtGui.QWidget()

    global CANVAS  # pylint: disable=W0603
    if CANVAS is None:
        CANVAS = QgsMapCanvas(PARENT)
        CANVAS.resize(QtCore.QSize(400, 400))

    global IFACE  # pylint: disable=W0603
    if IFACE is None:
        # QgisInterface is a stub implementation of the QGIS plugin interface
        IFACE = QgisInterface(CANVAS)

    return QGISAPP, CANVAS, IFACE, PARENT


def test_data_path(subdirectory=None):
    """Return the absolute path to the InaSAFE unit test data dir.

    :type subdirectory: Additional subdir to add to the path - typically
        'hazard' or 'exposure'.
    :param subdirectory:

    .. note:: This is not the same thing as the GIT inasafe_data dir. Rather
       this is a new dataset where the test datasets are all tiny for fast
       testing and the datasets live in the same repo as the code.

    """
    myPath = UNITDATA

    if subdirectory is not None:
        myPath = os.path.abspath(os.path.join(myPath,
                                              subdirectory))
    return myPath


def load_layer(layer_file, directory=TESTDATA):
    """Helper to load and return a single QGIS layer

    :param layer_file: Path name to raster or vector file.
    :type layer_file: str
    :param directory: Optional parent dir. If None, path name is assumed
        to be absolute.
    :type directory: str, None

    :returns: tuple containing layer and its category.
    :rtype: (QgsMapLayer, str)

    """

    # Extract basename and absolute path
    myFilename = os.path.split(layer_file)[-1]  # In case path was absolute
    myBaseName, myExt = os.path.splitext(myFilename)
    if directory is None:
        myPath = layer_file
    else:
        myPath = os.path.join(directory, layer_file)
    myKeywordPath = myPath[:-4] + '.keywords'

    # Determine if layer is hazard or exposure
    myKeywords = read_file_keywords(myKeywordPath)
    myCategory = 'undefined'
    if 'category' in myKeywords:
        myCategory = myKeywords['category']
    myMessage = 'Could not read %s' % myKeywordPath
    assert myKeywords is not None, myMessage

    # Create QGis Layer Instance
    if myExt in ['.asc', '.tif']:
        myLayer = QgsRasterLayer(myPath, myBaseName)
    elif myExt in ['.shp']:
        myLayer = QgsVectorLayer(myPath, myBaseName, 'ogr')
    else:
        myMessage = 'File %s had illegal extension' % myPath
        raise Exception(myMessage)

    myMessage = 'Layer "%s" is not valid' % str(myLayer.source())
    assert myLayer.isValid(), myMessage
    return myLayer, myCategory


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
    myCrs = QgsCoordinateReferenceSystem()
    myCrs.createFromSrid(epsg_id)

    # Reproject all layers to WGS84 geographic CRS
    CANVAS.mapRenderer().setDestinationCrs(myCrs)


def set_padang_extent():
    """Zoom to an area occupied by both both Padang layers."""
    myRect = QgsRectangle(100.21, -1.05, 100.63, -0.84)
    CANVAS.setExtent(myRect)


def set_jakarta_extent():
    """Zoom to an area occupied by both Jakarta layers in Geo."""
    myRect = QgsRectangle(106.52, -6.38, 107.14, -6.07)
    CANVAS.setExtent(myRect)


def set_jakarta_google_extent():
    """Zoom to an area occupied by both Jakarta layers in 900913 crs."""
    myRect = QgsRectangle(11873524, -695798, 11913804, -675295)
    CANVAS.setExtent(myRect)


def set_batemans_bay_extent():
    """Zoom to an area occupied by both Batemans Bay layers in geo crs."""
    myRect = QgsRectangle(150.152, -35.710, 150.187, -35.7013)
    CANVAS.setExtent(myRect)


def set_yogya_extent():
    """Zoom to an area occupied by both Jakarta layers in Geo."""
    myRect = QgsRectangle(110.348, -7.732, 110.368, -7.716)
    CANVAS.setExtent(myRect)


def set_small_jakarta_extent():
    """Zoom to an area occupied by both Jakarta layers in Geo."""
    myRect = QgsRectangle(106.7767, -6.1260, 106.7817, -6.1216)
    CANVAS.setExtent(myRect)


def set_geo_extent(bounding_box):
    """Zoom to an area specified given bounding box.

    :param bounding_box: List containing [xmin, ymin, xmax, ymax]
    :type bounding_box: list
    """
    myRect = QgsRectangle(*bounding_box)
    CANVAS.setExtent(myRect)


def check_images(control_image, test_image_path, tolerance=1000):
    r"""Compare a test image against a collection of known good images.

    :param tolerance: How many pixels may be different between the
        two images.
    :type tolerance: int

    :param test_image_path: The Image being checked (must have same dimensions
        as the control image). Must be full path to image.
    :type test_image_path: str

    :param control_image: The basename for the control image. The .png
        extension will automatically be added and the test image path
        (CONTROL_IMAGE_DIR) will be prepended. e.g.
        addClassToLegend will cause the control image of
        test\/test_data\/test_images\/addClassToLegend.png to be used.
    :type control_image: str

    :returns: Success or failure indicator, message providing analysis,
        comparison notes
    :rtype: bool, str
    """
    myMessages = ''
    myPlatform = platform_name()
    myBase, myExt = os.path.splitext(control_image)
    myPlatformImage = os.path.join(CONTROL_IMAGE_DIR, '%s-variant%s%s.png' % (
        myBase, myPlatform, myExt))
    myMessages += 'Checking for platform specific variant...\n'
    myMessages += test_image_path + '\n'
    myMessages += myPlatformImage + '\n'
    # It the platform image exists, we should test only that!
    if os.path.exists(myPlatformImage):
        myFlag, myMessage = check_image(
            myPlatformImage, test_image_path, tolerance)
        myMessages += myMessage + '\n'
        return myFlag, myMessages

    myMessages += (
        '\nNo platform specific control image could be found,\n'
        'testing against all control images. Try adding %s in\n '
        'the file name if you want it to be detected for this\n'
        'platform which will speed up image comparison tests.\n' %
        myPlatform)

    # Ok there is no specific platform match so go ahead and match to any of
    # the control image and its variants...
    myControlImages = glob.glob('%s/%s*%s' % (
        CONTROL_IMAGE_DIR, myBase, myExt))
    myFlag = False

    for myControlImage in myControlImages:
        myFullPath = os.path.join(
            CONTROL_IMAGE_DIR, myControlImage)
        myFlag, myMessage = check_image(
            myFullPath, test_image_path, tolerance)
        myMessages += myMessage
        # As soon as one passes we are done!
        if myFlag:
            print 'match with: ', myControlImage
            break
        LOGGER.debug('No match for control image %s' % myControlImage)

    return myFlag, myMessages


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
        myTestImage = QtGui.QImage(test_image_path)
    except OSError:
        myMessage = 'Test image:\n{0:s}\ncould not be loaded'.format(
            test_image_path)
        return False, myMessage

    try:
        if not os.path.exists(control_image_path):
            LOGGER.debug('checkImage: Control image does not exist:\n%s' %
                         control_image_path)
            raise OSError
        myControlImage = QtGui.QImage(control_image_path)
    except OSError:
        myMessage = 'Control image:\n{0:s}\ncould not be loaded.\n'
        return False, myMessage

    if (myControlImage.width() != myTestImage.width()
            or myControlImage.height() != myTestImage.height()):
        myMessage = ('Control and test images are different sizes.\n'
                     'Control image   : %s (%i x %i)\n'
                     'Test image      : %s (%i x %i)\n'
                     'If this test has failed look at the above images '
                     'to try to determine what may have change or '
                     'adjust the tolerance if needed.' %
                     (control_image_path,
                      myControlImage.width(),
                      myControlImage.height(),
                      test_image_path,
                      myTestImage.width(),
                      myTestImage.height()))
        LOGGER.debug(myMessage)
        return False, myMessage

    myImageWidth = myControlImage.width()
    myImageHeight = myControlImage.height()
    myMismatchCount = 0

    myDifferenceImage = QtGui.QImage(myImageWidth,
                                     myImageHeight,
                                     QtGui.QImage.Format_ARGB32_Premultiplied)
    myDifferenceImage.fill(152 + 219 * 256 + 249 * 256 * 256)

    for myY in range(myImageHeight):
        for myX in range(myImageWidth):
            myControlPixel = myControlImage.pixel(myX, myY)
            myTestPixel = myTestImage.pixel(myX, myY)
            if myControlPixel != myTestPixel:
                myMismatchCount += 1
                myDifferenceImage.setPixel(myX, myY, QtGui.qRgb(255, 0, 0))
    myDifferenceFilePath = unique_filename(
        prefix='difference-%s' % os.path.basename(control_image_path),
        suffix='.png',
        dir=temp_dir('test'))
    LOGGER.debug('Saving difference image as: %s' % myDifferenceFilePath)
    myDifferenceImage.save(myDifferenceFilePath, "PNG")

    # allow pixel deviation of 1 percent
    myPixelCount = myImageWidth * myImageHeight
    # FIXME (Ole): Use relative error i.e. mismatchcount/total pixels
    if myMismatchCount > tolerance:
        mySuccessFlag = False
    else:
        mySuccessFlag = True
    myMessage = ('%i of %i pixels are mismatched. Tolerance is %i.\n'
                 'Control image   : %s\n'
                 'Test image      : %s\n'
                 'Difference image: %s\n'
                 'If this test has failed look at the above images '
                 'to try to determine what may have change or '
                 'adjust the tolerance if needed.' %
                 (myMismatchCount,
                  myPixelCount,
                  tolerance,
                  control_image_path,
                  test_image_path,
                  myDifferenceFilePath))
    return mySuccessFlag, myMessage


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


def platform_name():
    """Get a platform name for this host.

        e.g OSX10.8
        Windows7-SP1-AMD64
        LinuxMint-14-x86_64
    """
    my_platform_system = platform.system()
    if my_platform_system == 'Darwin':
        myName = 'OSX'
        myName += '.'.join(platform.mac_ver()[0].split('.')[0:2])
        return myName
    elif my_platform_system == 'Linux':
        myName = '-'.join(platform.dist()[:-1]) + '-' + platform.machine()
        return myName
    elif my_platform_system == 'Windows':
        myName = 'Windows'
        myWin32Version = platform.win32_ver()
        myPlatformMachine = platform.machine()
        myName += myWin32Version[0] + '-' + myWin32Version[2]
        myName += '-' + myPlatformMachine
        return myName
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

    myHazard = str(dock.cboHazard.currentText())
    myExposure = str(dock.cboExposure.currentText())
    myImpactFunctionTitle = str(dock.cboFunction.currentText())
    myImpactFunctionId = dock.get_function_id()
    myRunButton = dock.pbnRunStop.isEnabled()

    return {'Hazard': myHazard,
            'Exposure': myExposure,
            'Impact Function Title': myImpactFunctionTitle,
            'Impact Function Id': myImpactFunctionId,
            'Run Button Enabled': myRunButton}


def formatted_list(layer_list):
    """Return a string representing a list of layers

    :param layer_list: A list of layers.
    :type layer_list: list

    :returns: The returned string will list layers in correct order but
        formatted with line breaks between each entry.
    :rtype: str
    """
    myListString = ''
    for myItem in layer_list:
        myListString += myItem + '\n'
    return myListString


def canvas_list():
    """Return a string representing the list of canvas layers.

    :returns: The returned string will list layers in correct order but
        formatted with line breaks between each entry.
    :rtype: str
    """
    myListString = ''
    for myLayer in CANVAS.layers():
        myListString += str(myLayer.name()) + '\n'
    return myListString


def combos_to_string(dock):
    """Helper to return a string showing the state of all combos.

    :param dock: A dock instance to get the state of combos from.
    :type dock: Dock

    :returns: A descriptive list of the contents of each combo with the
        active combo item highlighted with a >> symbol.
    :rtype: str
    """

    myString = 'Hazard Layers\n'
    myString += '-------------------------\n'
    myCurrentId = dock.cboHazard.currentIndex()
    for myCount in range(0, dock.cboHazard.count()):
        myItemText = dock.cboHazard.itemText(myCount)
        if myCount == myCurrentId:
            myString += '>> '
        else:
            myString += '   '
        myString += str(myItemText) + '\n'
    myString += '\n'
    myString += 'Exposure Layers\n'
    myString += '-------------------------\n'
    myCurrentId = dock.cboExposure.currentIndex()
    for myCount in range(0, dock.cboExposure.count()):
        myItemText = dock.cboExposure.itemText(myCount)
        if myCount == myCurrentId:
            myString += '>> '
        else:
            myString += '   '
        myString += str(myItemText) + '\n'

    myString += '\n'
    myString += 'Functions\n'
    myString += '-------------------------\n'
    myCurrentId = dock.cboFunction.currentIndex()
    for myCount in range(0, dock.cboFunction.count()):
        myItemText = dock.cboFunction.itemText(myCount)
        if myCount == myCurrentId:
            myString += '>> '
        else:
            myString += '   '
        myString += '%s (Function ID: %s)\n' % (
            str(myItemText), dock.get_function_id(myCurrentId))

    myString += '\n'
    myString += 'Aggregation Layers\n'
    myString += '-------------------------\n'
    myCurrentId = dock.cboAggregation.currentIndex()
    for myCount in range(0, dock.cboAggregation.count()):
        myItemText = dock.cboAggregation.itemText(myCount)
        if myCount == myCurrentId:
            myString += '>> '
        else:
            myString += '   '
        myString += str(myItemText) + '\n'

    myString += '\n\n >> means combo item is selected'
    return myString


def setup_scenario(
        dock,
        hazard,
        exposure,
        function,
        function_id,
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
        myIndex = dock.cboHazard.findText(hazard)
        myMessage = ('\nHazard Layer Not Found: %s\n Combo State:\n%s' %
                     (hazard, combos_to_string(dock)))
        if myIndex == -1:
            return False, myMessage
        dock.cboHazard.setCurrentIndex(myIndex)

    if exposure is not None:
        myIndex = dock.cboExposure.findText(exposure)
        myMessage = ('\nExposure Layer Not Found: %s\n Combo State:\n%s' %
                     (exposure, combos_to_string(dock)))
        if myIndex == -1:
            return False, myMessage
        dock.cboExposure.setCurrentIndex(myIndex)

    if function is not None:
        myIndex = dock.cboFunction.findText(function)
        myMessage = ('\nImpact Function Not Found: %s\n Combo State:\n%s' %
                     (function, combos_to_string(dock)))
        if myIndex == -1:
            return False, myMessage
        dock.cboFunction.setCurrentIndex(myIndex)

    if aggregation_layer is not None:
        myIndex = dock.cboAggregation.findText(aggregation_layer)
        myMessage = ('Aggregation layer Not Found: %s\n Combo State:\n%s' %
                     (aggregation_layer, combos_to_string(dock)))
        if myIndex == -1:
            return False, myMessage
        dock.cboAggregation.setCurrentIndex(myIndex)

    if aggregation_enabled_flag is not None:
        if dock.cboAggregation.isEnabled() != aggregation_enabled_flag:
            myMessage = (
                'The aggregation combobox should be %s' %
                ('enabled' if aggregation_enabled_flag else 'disabled'))
            return False, myMessage

    # Check that layers and impact function are correct
    myDict = get_ui_state(dock)

    myExpectedDict = {'Run Button Enabled': ok_button_flag,
                      'Impact Function Title': function,
                      'Impact Function Id': function_id,
                      'Hazard': hazard,
                      'Exposure': exposure}

    myMessage = 'Expected versus Actual State\n'
    myMessage += '--------------------------------------------------------\n'

    for myKey in myExpectedDict.keys():
        myMessage += 'Expected %s: %s\n' % (myKey, myExpectedDict[myKey])
        myMessage += 'Actual   %s: %s\n' % (myKey, myDict[myKey])
        myMessage += '----\n'
    myMessage += '--------------------------------------------------------\n'
    myMessage += combos_to_string(dock)

    if myDict != myExpectedDict:
        return False, myMessage

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
    # WARNING: Please keep test_data/test/loadStandardLayers.qgs in sync with
    # myFileList
    myFileList = [join(TESTDATA, 'Padang_WGS84.shp'),
                  join(EXPDATA, 'glp10ag.asc'),
                  join(HAZDATA, 'Shakemap_Padang_2009.asc'),
                  join(TESTDATA, 'tsunami_max_inundation_depth_utm56s.tif'),
                  join(TESTDATA, 'tsunami_building_exposure.shp'),
                  join(HAZDATA, 'Flood_Current_Depth_Jakarta_geographic.asc'),
                  join(TESTDATA, 'Population_Jakarta_geographic.asc'),
                  join(HAZDATA, 'eq_yogya_2006.asc'),
                  join(HAZDATA, 'Jakarta_RW_2007flood.shp'),
                  join(TESTDATA, 'OSM_building_polygons_20110905.shp'),
                  join(EXPDATA, 'DKI_buildings.shp'),
                  join(HAZDATA, 'jakarta_flood_category_123.asc'),
                  join(TESTDATA, 'roads_Maumere.shp'),
                  join(TESTDATA, 'donut.shp'),
                  join(TESTDATA, 'Merapi_alert.shp'),
                  join(TESTDATA, 'kabupaten_jakarta_singlepart.shp')]
    myHazardLayerCount, myExposureLayerCount = load_layers(
        myFileList, data_directory=None, dock=dock)
    #FIXME (MB) -1 is until we add the aggregation category because of
    # kabupaten_jakarta_singlepart not being either hazard nor exposure layer

    assert myHazardLayerCount + myExposureLayerCount == len(myFileList) - 1

    return myHazardLayerCount, myExposureLayerCount


def load_layers(
        layer_list,
        clear_flag=True,
        data_directory=TESTDATA,
        dock=None):
    """Helper function to load layers as defined in a python list.

    :param dock: A valid dock instance.
    :type dock: Dock

    :param data_directory: Path to where data should be loaded from. Defaults
        to TESTDATA directory.
    :type data_directory: str, None

    :param clear_flag: Whether to clear currently loaded layers before loading
        the new layers.
    :type clear_flag: bool

    :param layer_list: A list of layers to load.
    :type layer_list: list(str)
    """
    # First unload any layers that may already be loaded
    if clear_flag:
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().removeAllMapLayers()

    # Now go ahead and load our layers
    myExposureLayerCount = 0
    myHazardLayerCount = 0
    map_layer_list = []
    # Now create our new layers
    for myFile in layer_list:

        myLayer, myType = load_layer(myFile, data_directory)
        if myType == 'hazard':
            myHazardLayerCount += 1
        elif myType == 'exposure':
            myExposureLayerCount += 1

        # Add layer to the registry (that QGis knows about) a slot
        # in qgis_interface will also ensure it gets added to the canvas

        # noinspection PyArgumentList
        map_layer_list.append(myLayer)

    # noinspection PyArgumentList
    QgsMapLayerRegistry.instance().addMapLayers(map_layer_list)

    if dock is not None:
        dock.get_layers()

    # Add MCL's to the CANVAS
    return myHazardLayerCount, myExposureLayerCount


def compareWkt(a, b, tol=0.000001):
    """ Helper function to compare WKT geometries with given tolerance
    Taken from QGIS test suite

    :param a: Input WKT geometry
    :type a: str

    :param b: Expected WKT geometry
    :type b: str

    :param tol: compare tolerance
    :type tol: float

    :return: True on success, False on failure
    :rtype bool
    """
    r = re.compile('-?\d+(?:\.\d+)?(?:[eE]\d+)?')

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
