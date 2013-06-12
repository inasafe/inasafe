"""Helper module for gui test suite
"""

import os
import sys
import hashlib
import logging
import platform
import glob
from os.path import join

from PyQt4 import QtGui, QtCore
from qgis.core import (
    QgsApplication,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsMapLayerRegistry)
from qgis.gui import QgsMapCanvas
from qgis_interface import QgisInterface

# For testing and demoing
from safe_qgis.safe_interface import (
    readKeywordsFromFile,
    unique_filename,
    temp_dir,
    TESTDATA,
    UNITDATA)

from safe_interface import HAZDATA, EXPDATA

from safe_qgis.utilities import qgisVersion


YOGYA2006_title = 'An earthquake in Yogyakarta like in 2006'
PADANG2009_title = 'An earthquake in Padang like in 2009'

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__),
                              'test_data/test_files')

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
    'test_data/test_images')


def assertHashesForFile(theHashes, theFilename):
    """Assert that a files has matches one of a list of expected hashes"""
    myHash = hashForFile(theFilename)
    myMessage = ('Unexpected hash'
                 '\nGot: %s'
                 '\nExpected: %s'
                 '\nPlease check graphics %s visually '
                 'and add to list of expected hashes '
                 'if it is OK on this platform.' % (myHash,
                                                    theHashes,
                                                    theFilename))
    assert myHash in theHashes, myMessage


def assertHashForFile(theHash, theFilename):
    """Assert that a files has matches its expected hash"""
    myHash = hashForFile(theFilename)
    myMessage = ('Unexpected hash'
                 '\nGot: %s'
                 '\nExpected: %s' % (myHash, theHash))
    assert myHash == theHash, myMessage


def hashForFile(theFilename):
    """Return an md5 checksum for a file"""
    myPath = theFilename
    myData = file(myPath, 'rb').read()
    myHash = hashlib.md5()
    myHash.update(myData)
    myHash = myHash.hexdigest()
    return myHash


def getQgisTestApp():
    """ Start one QGis application to test agaist

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


def unitTestDataPath(theSubdir=None):
    """Return the absolute path to the InaSAFE unit test data dir.

    .. note:: This is not the same thing as the SVN inasafe_data dir. Rather
       this is a new dataset where the test datasets are all tiny for fast
       testing and the datasets live in the same repo as the code.

    Args:
       * theSubdir: (Optional) Additional subdir to add to the path - typically
         'hazard' or 'exposure'.
    """
    myPath = UNITDATA

    if theSubdir is not None:
        myPath = os.path.abspath(os.path.join(myPath,
                                              theSubdir))
    return myPath


def loadLayer(theLayerFile, theDirectory=TESTDATA):
    """Helper to load and return a single QGIS layer

    Args:
        theLayerFile: Pathname to raster or vector file
        DIR: Optional parameter stating the parent dir. If None,
             pathname is assumed to be absolute

    Returns: QgsMapLayer, str (for layer type)

    """

    # Extract basename and absolute path
    myFilename = os.path.split(theLayerFile)[-1]  # In case path was absolute
    myBaseName, myExt = os.path.splitext(myFilename)
    if theDirectory is None:
        myPath = theLayerFile
    else:
        myPath = os.path.join(theDirectory, theLayerFile)
    myKeywordPath = myPath[:-4] + '.keywords'

    # Determine if layer is hazard or exposure
    myKeywords = readKeywordsFromFile(myKeywordPath)
    myType = 'undefined'
    if 'category' in myKeywords:
        myType = myKeywords['category']
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
    return myLayer, myType


def setCanvasCrs(theEpsgId, theOtfpFlag=False):
    """Helper to set the crs for the CANVAS before a test is run.

    Args:

        * theEpsgId  - Valid EPSG identifier (int)
        * theOtfpFlag - whether on the fly projections should be enabled
                        on the CANVAS. Default to False.
    """
        # Enable on-the-fly reprojection
    CANVAS.mapRenderer().setProjectionsEnabled(theOtfpFlag)

    # Create CRS Instance
    myCrs = QgsCoordinateReferenceSystem()
    myCrs.createFromId(theEpsgId, QgsCoordinateReferenceSystem.EpsgCrsId)

    # Reproject all layers to WGS84 geographic CRS
    CANVAS.mapRenderer().setDestinationCrs(myCrs)


def setPadangGeoExtent():
    """Zoom to an area occupied by both both Padang layers"""
    myRect = QgsRectangle(100.21, -1.05, 100.63, -0.84)
    CANVAS.setExtent(myRect)


def setJakartaGeoExtent():
    """Zoom to an area occupied by both Jakarta layers in Geo"""
    myRect = QgsRectangle(106.52, -6.38, 107.14, -6.07)
    CANVAS.setExtent(myRect)


def setJakartaGoogleExtent():
    """Zoom to an area occupied by both Jakarta layers in 900913 crs
    """
    myRect = QgsRectangle(11873524, -695798, 11913804, -675295)
    CANVAS.setExtent(myRect)


def setBatemansBayGeoExtent():
    """Zoom to an area occupied by both Batemans Bay
     layers in geo crs"""
    myRect = QgsRectangle(150.152, -35.710, 150.187, -35.7013)
    CANVAS.setExtent(myRect)


def setYogyaGeoExtent():
    """Zoom to an area occupied by both Jakarta layers in Geo"""
    myRect = QgsRectangle(110.348, -7.732, 110.368, -7.716)
    CANVAS.setExtent(myRect)


def setGeoExtent(theBoundingBox):
    """Zoom to an area specified given bounding box (list)"""
    myRect = QgsRectangle(*theBoundingBox)
    CANVAS.setExtent(myRect)


def checkImages(theControlImage, theTestImagePath, theTolerance=1000):
    """Compare a test image against a collection of known good images.

    Args:
        * theControlImagePath: str file names. Give only the basename +ext
            as the test image path (CONTROL_IMAGE_DIR) will be prepended. e.g.
            addClassToLegend.png
        * theTestImagePath: The Image being checked (must have same dimensions
            as the control image). Must be full path to image.
        * theTolerance: How many pixels may be different between the
            two images.

    Returns:
        (bool, str, str) where:
        * bool is success or failure indicator
        * str is the file path of the resulting difference image
        * str is a message providing analysis comparison notes

    Raises:
        None
    """
    myMessages = ''
    myPlatform = platformName()
    myBase, myExt = os.path.splitext(theControlImage)
    myPlatformImage = os.path.join(CONTROL_IMAGE_DIR, '%s-variant%s%s.png' % (
        myBase, myPlatform, myExt))
    myMessages += 'Checking for platform specific variant...\n'
    myMessages += theTestImagePath + '\n'
    myMessages += myPlatformImage + '\n'
    # It the platform image exists, we should test only that!
    if os.path.exists(myPlatformImage):
        myFlag, myMessage = checkImage(
            myPlatformImage, theTestImagePath, theTolerance)
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
        myFlag, myMessage = checkImage(
            myFullPath, theTestImagePath, theTolerance)
        myMessages += myMessage
        # As soon as one passes we are done!
        if myFlag:
            print 'match with: ', myControlImage
            break
        LOGGER.debug('No match for control image %s' % myControlImage)

    return myFlag, myMessages


def checkImage(theControlImagePath, theTestImagePath, theTolerance=1000):
    """Compare a test image against a known good image.

    Args:
        * theControlImagePath: The image representing expected output
        * theTestImagePath: The Image being checked (must have same dimensions
            as the control image).
        * theTolerance: How many pixels may be different between the
            two images.

    Returns:
        (bool, str, str) where:
        * bool is success or failure indicator
        * str is a message providing analysis comparison notes

    Raises:
        None
    """

    try:
        if not os.path.exists(theTestImagePath):
            LOGGER.debug('checkImage: Test image does not exist:\n%s' %
                         theTestImagePath)
            raise OSError
        myTestImage = QtGui.QImage(theTestImagePath)
    except OSError:
        myMessage = 'Test image:\n%s\ncould not be loaded' % theTestImagePath
        return False, myMessage

    try:
        if not os.path.exists(theControlImagePath):
            LOGGER.debug('checkImage: Control image does not exist:\n%s' %
                         theControlImagePath)
            raise OSError
        myControlImage = QtGui.QImage(theControlImagePath)
    except OSError:
        myMessage = ('Control image:\n%s\ncould not be loaded.\n'
                     'Test image is:\n%s\n' % (
                         theControlImagePath,
                         theTestImagePath))
        return False, myMessage

    if (myControlImage.width() != myTestImage.width()
            or myControlImage.height() != myTestImage.height()):
        myMessage = ('Control and test images are different sizes.\n'
                     'Control image   : %s (%i x %i)\n'
                     'Test image      : %s (%i x %i)\n'
                     'If this test has failed look at the above images '
                     'to try to determine what may have change or '
                     'adjust the tolerance if needed.' %
                     (theControlImagePath,
                      myControlImage.width(),
                      myControlImage.height(),
                      theTestImagePath,
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
        prefix='difference-%s' % os.path.basename(theControlImagePath),
        suffix='.png',
        dir=temp_dir('test'))
    LOGGER.debug('Saving difference image as: %s' % myDifferenceFilePath)
    myDifferenceImage.save(myDifferenceFilePath, "PNG")

    #allow pixel deviation of 1 percent
    myPixelCount = myImageWidth * myImageHeight
    # FIXME (Ole): Use relative error i.e. mismatchcount/total pixels
    if myMismatchCount > theTolerance:
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
                  theTolerance,
                  theControlImagePath,
                  theTestImagePath,
                  myDifferenceFilePath))
    return mySuccessFlag, myMessage


class RedirectStdStreams(object):
    """Context manager for redirection of stdout and stderr

    This is from
    http://stackoverflow.com/questions/6796492/
    python-temporarily-redirect-stdout-stderr

    In this context, the class is used to get rid of QGIS
    output in the test suite - BUT IT DOESN'T WORK (Maybe
    because QGIS starts its providers in a different process?)

    Usage:

    devnull = open(os.devnull, 'w')
    print('Fubar')

    with RedirectStdStreams(stdout=devnull, stderr=devnull):
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


def platformName():
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


def getUiState(theDock):
    """Get state of the 3 combos on the DOCK theDock. This method is purely for
    testing and not to be confused with the saveState and restoreState methods
    of inasafedock.
    """

    myHazard = str(theDock.cboHazard.currentText())
    myExposure = str(theDock.cboExposure.currentText())
    myImpactFunctionTitle = str(theDock.cboFunction.currentText())
    myImpactFunctionId = theDock.getFunctionID()
    myRunButton = theDock.pbnRunStop.isEnabled()

    return {'Hazard': myHazard,
            'Exposure': myExposure,
            'Impact Function Title': myImpactFunctionTitle,
            'Impact Function Id': myImpactFunctionId,
            'Run Button Enabled': myRunButton}


def formattedList(theList):
    """Return a string representing a list of layers (in correct order)
    but formatted with line breaks between each entry."""
    myListString = ''
    for myItem in theList:
        myListString += myItem + '\n'
    return myListString


def canvasList():
    """Return a string representing the list of canvas layers (in correct
    order) but formatted with line breaks between each entry."""
    myListString = ''
    for myLayer in CANVAS.layers():
        myListString += str(myLayer.name()) + '\n'
    return myListString


def combosToString(theDock):
    """Helper to return a string showing the state of all combos (all their
    entries"""

    myString = 'Hazard Layers\n'
    myString += '-------------------------\n'
    myCurrentId = theDock.cboHazard.currentIndex()
    for myCount in range(0, theDock.cboHazard.count()):
        myItemText = theDock.cboHazard.itemText(myCount)
        if myCount == myCurrentId:
            myString += '>> '
        else:
            myString += '   '
        myString += str(myItemText) + '\n'
    myString += '\n'
    myString += 'Exposure Layers\n'
    myString += '-------------------------\n'
    myCurrentId = theDock.cboExposure.currentIndex()
    for myCount in range(0, theDock.cboExposure.count()):
        myItemText = theDock.cboExposure.itemText(myCount)
        if myCount == myCurrentId:
            myString += '>> '
        else:
            myString += '   '
        myString += str(myItemText) + '\n'

    myString += '\n'
    myString += 'Functions\n'
    myString += '-------------------------\n'
    myCurrentId = theDock.cboFunction.currentIndex()
    for myCount in range(0, theDock.cboFunction.count()):
        myItemText = theDock.cboFunction.itemText(myCount)
        if myCount == myCurrentId:
            myString += '>> '
        else:
            myString += '   '
        myString += '%s (Function ID: %s)\n' % (
            str(myItemText), theDock.getFunctionID(myCurrentId))

    myString += '\n'
    myString += 'Aggregation Layers\n'
    myString += '-------------------------\n'
    myCurrentId = theDock.cboAggregation.currentIndex()
    for myCount in range(0, theDock.cboAggregation.count()):
        myItemText = theDock.cboAggregation.itemText(myCount)
        if myCount == myCurrentId:
            myString += '>> '
        else:
            myString += '   '
        myString += str(myItemText) + '\n'

    myString += '\n\n >> means combo item is selected'
    return myString


def setupScenario(
        theDock,
        theHazard,
        theExposure,
        theFunction,
        theFunctionId,
        theOkButtonFlag=True,
        theAggregationLayer=None,
        theAggregationEnabledFlag=None):
    """Helper function to set the gui state to a given scenario.

    Args:
        * theDock Dock- (Required) dock instance.
        * theHazard str - (Required) name of the hazard combo entry to set.
        * theExposure str - (Required) name of exposure combo entry to set.
        * theFunction - (Required) name of the function combo entry to set.
        * theFunctionId - (Required) impact function id that should be used.
        * theOkButtonFlag - (Optional) Whether the ok button should be enabled
            after this scenario is set up.
        * theAggregationLayer - (Optional) which layer should be used for
            aggregation
        * theAggregationEnabledFlag - (Optional) whether it is expected that
            aggregation should be enabled when the scenario is loaded.

    We require both theFunction and theFunctionId because safe allows for
    multiple functions with the same name but different id's so we need to be
    sure we have the right one.

    .. note:: Layers are not actually loaded - the calling function is
        responsible for that.

    Returns: bool - Indicating if the setup was successful
            str - A message indicating why it may have failed.

    Raises: None
    """
    if theHazard is not None:
        myIndex = theDock.cboHazard.findText(theHazard)
        myMessage = ('\nHazard Layer Not Found: %s\n Combo State:\n%s' %
                     (theHazard, combosToString(theDock)))
        if myIndex == -1:
            return False, myMessage
        theDock.cboHazard.setCurrentIndex(myIndex)

    if theExposure is not None:
        myIndex = theDock.cboExposure.findText(theExposure)
        myMessage = ('\nExposure Layer Not Found: %s\n Combo State:\n%s' %
                     (theExposure, combosToString(theDock)))
        if myIndex == -1:
            return False, myMessage
        theDock.cboExposure.setCurrentIndex(myIndex)

    if theFunction is not None:
        myIndex = theDock.cboFunction.findText(theFunction)
        myMessage = ('\nImpact Function Not Found: %s\n Combo State:\n%s' %
                     (theFunction, combosToString(theDock)))
        if myIndex == -1:
            return False, myMessage
        theDock.cboFunction.setCurrentIndex(myIndex)

    if theAggregationLayer is not None:
        myIndex = theDock.cboAggregation.findText(theAggregationLayer)
        myMessage = ('Aggregation layer Not Found: %s\n Combo State:\n%s' %
                     (theAggregationLayer, combosToString(theDock)))
        if myIndex == -1:
            return False, myMessage
        theDock.cboAggregation.setCurrentIndex(myIndex)

    if theAggregationEnabledFlag is not None:
        if theDock.cboAggregation.isEnabled() != theAggregationEnabledFlag:
            myMessage = (
                'The aggregation combobox should be %s' %
                ('enabled' if theAggregationEnabledFlag else 'disabled'))
            return False, myMessage

    # Check that layers and impact function are correct
    myDict = getUiState(theDock)

    myExpectedDict = {'Run Button Enabled': theOkButtonFlag,
                      'Impact Function Title': theFunction,
                      'Impact Function Id': theFunctionId,
                      'Hazard': theHazard,
                      'Exposure': theExposure}

    myMessage = 'Expected versus Actual State\n'
    myMessage += '--------------------------------------------------------\n'

    for myKey in myExpectedDict.keys():
        myMessage += 'Expected %s: %s\n' % (myKey, myExpectedDict[myKey])
        myMessage += 'Actual   %s: %s\n' % (myKey, myDict[myKey])
        myMessage += '----\n'
    myMessage += '--------------------------------------------------------\n'
    myMessage += combosToString(theDock)

    if myDict != myExpectedDict:
        return False, myMessage

    return True, 'Matched ok.'


def populatemyDock(theDock):
    """A helper function to populate the DOCK and set it to a valid state.
    """
    loadStandardLayers(theDock)
    theDock.cboHazard.setCurrentIndex(0)
    theDock.cboExposure.setCurrentIndex(0)
    #QTest.mouseClick(myHazardItem, Qt.LeftButton)
    #QTest.mouseClick(myExposureItem, Qt.LeftButton)


def loadStandardLayers(theDock=None):
    """Helper function to load standard layers into the dialog."""
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
    myHazardLayerCount, myExposureLayerCount = loadLayers(
        myFileList, theDataDirectory=None, theDock=theDock)
    #FIXME (MB) -1 is untill we add the aggregation category because of
    # kabupaten_jakarta_singlepart not being either hazard nor exposure layer

    assert myHazardLayerCount + myExposureLayerCount == len(myFileList) - 1

    return myHazardLayerCount, myExposureLayerCount


def loadLayers(
        theLayerList,
        theClearFlag=True,
        theDataDirectory=TESTDATA,
        theDock=None):
    """Helper function to load layers as defined in a python list."""
    # First unload any layers that may already be loaded
    if theClearFlag:
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().removeAllMapLayers()

    # Now go ahead and load our layers
    myExposureLayerCount = 0
    myHazardLayerCount = 0

    # Now create our new layers
    for myFile in theLayerList:

        myLayer, myType = loadLayer(myFile, theDataDirectory)
        if myType == 'hazard':
            myHazardLayerCount += 1
        elif myType == 'exposure':
            myExposureLayerCount += 1
            # Add layer to the registry (that QGis knows about) a slot
        # in qgis_interface will also ensure it gets added to the canvas
        if qgisVersion() >= 10800:  # 1.8 or newer
            # noinspection PyArgumentList
            QgsMapLayerRegistry.instance().addMapLayers([myLayer])
        else:
            # noinspection PyArgumentList
            QgsMapLayerRegistry.instance().addMapLayer(myLayer)

    if theDock is not None:
        theDock.getLayers()

    # Add MCL's to the CANVAS
    return myHazardLayerCount, myExposureLayerCount
