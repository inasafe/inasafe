"""Helper module for gui test suite
"""

import os
import sys
import hashlib
import logging

from PyQt4 import QtGui, QtCore

from qgis.core import (QgsApplication,
                      QgsVectorLayer,
                      QgsRasterLayer,
                      QgsRectangle,
                      QgsCoordinateReferenceSystem)
from qgis.gui import QgsMapCanvas
from qgis_interface import QgisInterface

# For testing and demoing
from safe.common.testing import TESTDATA
from safe_qgis.safe_interface import (readKeywordsFromFile,
                                      temp_dir,
                                      unique_filename)
LOGGER = logging.getLogger('InaSAFE')

QGISAPP = None  # Static vainasafele used to hold hand to running QGis app
CANVAS = None
PARENT = None
IFACE = None
GEOCRS = 4326  # constant for EPSG:GEOCRS Geographic CRS id
GOOGLECRS = 900913  # constant for EPSG:GOOGLECRS Google Mercator id
DEVNULL = open(os.devnull, 'w')
CONTROL_IMAGE_DIR = os.path.join(os.path.dirname(__file__),
    'test_data/test_images')


def assertHashesForFile(theHashes, theFilename):
    """Assert that a files has matches one of a list of expected hashes"""
    myHash = hashForFile(theFilename)
    myMessage = ('Unexpected hash'
                 '\nGot: %s'
                 '\nExpected: %s'
                 '\nPlease check graphics %s visually '
                 'and add to list of expected hashes '
                 'if it is OK on this platform.'
                  % (myHash, theHashes, theFilename))
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
    from safe.common.testing import UNITDATA

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


def checkImages(theControlImages, theTestImagePath, theTolerance=1000):
    """Compare a test image against a collection of known good images.

    Args:
        * theControlImagePath: list of file names. Give only the basename +ext
            as the test image path (CONTROL_IMAGE_DIR) will be prepended.
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
    for myControlImage in theControlImages:
        myFullPath = os.path.join(CONTROL_IMAGE_DIR,
                                      myControlImage)
        myFlag, myMessage = checkImage(myFullPath,
                                          theTestImagePath,
                                          theTolerance)
        myMessages += myMessage
        # As soon as one passes we are done!
        if myFlag:
            break

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
            raise OSError
        myTestImage = QtGui.QImage(theTestImagePath)
    except OSError:
        myMessage = 'Test image:\n%s\ncould not be loaded' % theTestImagePath
        return False, myMessage

    try:
        if not os.path.exists(theControlImagePath):
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
                     'Control image   : %s\n'
                     'Test image      : %s\n'
                     'Difference image: %s\n'
                     'If this test has failed look at the above images '
                     'to try to determine what may have change or '
                     'adjust the tolerance if needed.' %
                     (theTolerance,
                      theControlImagePath,
                      theTestImagePath))
        return False, myMessage

    myImageWidth = myControlImage.width()
    myImageHeight = myControlImage.height()
    myMismatchCount = 0

    myDifferenceImage = QtGui.QImage(myImageWidth,
                                     myImageHeight,
                                     QtGui.QImage.Format_ARGB32_Premultiplied)
    myDifferenceImage.fill(QtGui.qRgb(152, 219, 249))

    myControlPixel = QtGui.QColor().rgb()
    myTestPixel = QtGui.QColor().rgb()
    for myY in range(myImageHeight):
        for myX in range(myImageWidth):
            myControlPixel = myControlImage.pixel(myX, myY)
            myTestPixel = myTestImage.pixel(myX, myY)
            if (myControlPixel != myTestPixel):
                myMismatchCount = myMismatchCount + 1
                myDifferenceImage.setPixel(myX, myY, QtGui.qRgb(255, 0, 0))
    myDifferenceFilePath = unique_filename(prefix='difference',
                                           suffix='.png',
                                           dir=temp_dir('test'))
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
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush()
        self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush()
        self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
