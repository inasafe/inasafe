"""
Disaster risk assessment tool developed by AusAid - **impactcalculator.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com, ole.moller.nielsen@gmail.com'
__version__ = '0.0.1'
__date__ = '11/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


import sys
import os
import unicodedata
from riabexceptions import (InsufficientParametersException,
                            KeywordNotFoundException,
                            StyleInfoNotFoundException,
                            InvalidParameterException)

from utilities import get_exception_with_stacktrace
# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(pardir)
from impact_functions import get_admissible_plugins, get_plugins
from engine.core import calculate_impact, get_bounding_boxes
from storage.core import read_layer
from storage.utilities import read_keywords
import threading
from PyQt4.QtCore import QObject, pyqtSignal


def makeAscii(x):
    """Convert QgsString to ASCII"""
    x = unicode(x)
    x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore')
    return x


def getOptimalExtent(hazardPath, exposurePath, desiredViewport):
    """ A helper function to determine what the optimal extent is.
    Optimal extent should be considered as the intersection between
    the three inputs. The riab library will perform various checks
    to ensure that the extent is tenable, includes data from both
    etc.

    This is just a thin wrapper around engine.core.get_bounding_boxes.

    Typically the result of this function will be used to clip
    input layers to a commone extent before processing.

    Args:

       * hazardPath - a string representing a path to a hazard file
         in the file system.
       * exposurePath - a string representing a path to an
         exposure file on the file system.

       ..note:: We do minimal checking as the riab library takes
         care of it for us.

    Returns:
       An array containing an extent in the form [xmin,ymin,xmax,ymax]
       e.g.::

        [100.03, -1.14, 100.81, -0.73]

    Raises:
        Any exceptions raised by the RIAB library will be propogated.
    """
    try:
        # .. note:: The get_bounding_boxes function below assumes that
        #            all inputs are in EPSG:4326
        return get_bounding_boxes(
            makeAscii(hazardPath),
            makeAscii(exposurePath),
            desiredViewport)
    except Exception, e:
        raise e


class ImpactCalculator():
    """A class to compute an impact scenario."""

    def __init__(self):
        """Constructor for the impact calculator."""
        self.__hazard_layer = None
        self.__exposure_layer = None
        self.__function = None

    def getExposureLayer(self):
        """Accessor: exposure layer."""
        return self.__exposure_layer

    def setExposureLayer(self, value):
        """Mutator: exposure layer."""
        self.__exposure_layer = value

    def delExposureLayer(self):
        """Delete: exposure layer."""
        del self.__exposure_layer

    def getHazardLayer(self):
        """Accessor: hazard layer."""
        return self.__hazard_layer

    def setHazardLayer(self, value):
        """Mutator: hazard layer."""
        self.__hazard_layer = value

    def delHazardLayer(self):
        """Delete: hazard layer."""
        del self.__hazard_layer

    def getFunction(self):
        """Accessor: function layer."""
        return self.__function

    def setFunction(self, value):
        """Mutator: function layer."""
        self.__function = value

    def delFunction(self):
        """Delete: function layer."""
        del self.__function

    _hazard_layer = property(getHazardLayer, setHazardLayer,
        delHazardLayer, """Hazard layer property  (e.g. a flood depth
        raster).""")

    _exposure_layer = property(getExposureLayer, setExposureLayer,
        delExposureLayer, """Exposure layer property (e.g. buildings or
        features that will be affected).""")

    _function = property(getFunction, setFunction,
        delFunction, """Function property (specifies which
        riab function to use to process the hazard and exposure
        layers with.""")

    def availableFunctions(self, theKeywordList=None):
        """ Query the riab engine to see what plugins are available.
        Args:

           theKeywordList - an optional parameter which should contain
           a list of 2 dictionaries (the number of items in the list
           is not enforced). The dictionaries should be obtained by using
           getKeywordFromFile e.g.::

               myFile1 = foo.shp
               myFile2 = bar.asc
               myKeywords1 = getKeywordFromFile(myFile1)
               myKeywords2 = getKeywordFromFile(myFile2)
               myList = [myKeywords1, myKeywords2]
               myFunctions = availableFunctions(myList)

        Returns:
           A dictionary of strings where each is a plugin name.
           .. note:: If theKeywordList is not provided, all available
            plugins will be returned in the list.
        Raises:
           NoFunctionsFoundException if no functions are found.
        """
        myDict = get_admissible_plugins(theKeywordList)
        #if len(myDict) < 1:
        #    myMessage = 'No RIAB impact functions could be found'
        #    raise NoFunctionsFoundException(myMessage)

        return myDict

    def getKeywordFromLayer(self, theLayer, keyword):
        """Get metadata from the keywords file associated with a layer.

        .. note:: Requires a riab layer instance as parameter.
        .. see:: getKeywordFromPath

        Args:

           * theLayer - a RIAB layer (vector or raster)
           * keyword - the metadata keyword to retrieve e.g. 'title'

        Returns:
           A string containing the retrieved value for the keyword.

        Raises:
           KeywordNotFoundException if the keyword is not recognised.
        """
        myValue = None
        if theLayer is None:
            raise InvalidParameterException()
        try:
            myValue = theLayer.get_keywords(keyword)
        except Exception, e:
            msg = 'Keyword retrieval failed for %s (%s) \n %s' % (
                    theLayer.get_filename(), keyword, str(e))
            raise KeywordNotFoundException(msg)
        if not myValue or myValue == '':
            msg = 'No value was found for keyword %s in layer %s' % (
                        theLayer.get_filename(), keyword)
            raise KeywordNotFoundException(msg)
        return myValue

    def getKeywordFromFile(self, theLayerPath, keyword=None):
        """Get metadata from the keywords file associated with a layer.

        .. note:: Requires a str representing a file path instance
                  as parameter As opposed to getKeywordFromLayer which
                  takes a riab file object as parameter.

        .. see:: getKeywordFromLayer

        Args:

           * theLayerPath - a string representing a path to a layer
               (e.g. '/tmp/foo.shp', '/tmp/foo.tif')
           * keyword - the metadata keyword to retrieve e.g. 'title'

        Returns:
           A string containing the retrieved value for the keyword if
           the keyword argument is specified, otherwise the
           complete keywords dictionary is returned.

        Raises:
           KeywordNotFoundException if the keyword is not recognised.
        """
        # check the source layer path is valid
        if not os.path.isfile(theLayerPath):
            msg = ('Cannot get keywords from a non-existant file.'
                   '%s does not exist.' % theLayerPath)
            raise InvalidParameterException(msg)

        # check there really is a keywords file for this layer
        myKeywordFilePath = os.path.splitext(theLayerPath)[0]
        myKeywordFilePath += '.keywords'
        if not os.path.isfile(myKeywordFilePath):
            msg = ('No keywords file found for %s' % theLayerPath)
            raise InvalidParameterException(msg)

        #now get the requested keyword using the riab library
        myDictionary = None
        try:
            myDictionary = read_keywords(myKeywordFilePath)
        except Exception, e:
            msg = 'Keyword retrieval failed for %s (%s) \n %s' % (
                    myKeywordFilePath, keyword, str(e))
            raise KeywordNotFoundException(msg)

        # if no keyword was supplied, just return the dict
        if keyword is None:
            return myDictionary
        if not keyword in myDictionary:
            msg = 'No value was found for in file %s in keyword %s' % (
                        myKeywordFilePath, keyword)
            raise KeywordNotFoundException(msg)

        myValue = myDictionary[keyword]

        return myValue

    def getStyleInfo(self, theLayer):
        """Get styleinfo associated with a layer.
        Args:

           * theLayer - RIAB layer (raster or vector)

        Returns:
           A list of dictionaries containing styleinfo info for a layer.

        Raises:

           * StyleInfoNotFoundException if the style is not found.
           * InvalidParameterException if the paramers are not correct.
        """

        if not theLayer:
            raise InvalidParameterException()

        if not hasattr(theLayer, 'get_style_info'):
            msg = ('Argument "%s" was not a valid layer instance' %
                   theLayer)
            raise StyleInfoNotFoundException(msg)

        try:
            myValue = theLayer.get_style_info()
        except Exception, e:
            msg = 'Styleinfo retrieval failed for %s\n %s' % (
                        theLayer.get_filename(), str(e))
            raise StyleInfoNotFoundException(msg)

        if not myValue or myValue == '':
            msg = ('No styleInfo was found for layer %s' % (
                    theLayer.get_filename()))
            raise StyleInfoNotFoundException(msg)

        return myValue

    def getRunner(self):
        """ Factory to create a new runner thread.
        Requires three parameters to be set before execution
        can take place:

        * Hazard layer - a path to a raster (string)
        * Exposure layer - a path to a vector hazard layer (string).
        * Function - a function name that defines how the Hazard assessment
          will be computed (string).

        Args:
           None.
        Returns:
           None
        Raises:
           InsufficientParametersException if not all parameters are
           set.
        """
        self.__filename = None
        self.__result = None
        if not self.__hazard_layer or self.__hazard_layer == '':
            msg = 'Error: Hazard layer not set.'
            raise InsufficientParametersException(msg)

        if not self.__exposure_layer or self.__exposure_layer == '':
            msg = 'Error: Exposure layer not set.'
            raise InsufficientParametersException(msg)

        if not self.__function or self.__function == '':
            msg = 'Error: Function not set.'
            raise InsufficientParametersException(msg)

        # Call impact calculation engine
        myHazardLayer = read_layer(makeAscii(self.__hazard_layer))
        myExposureLayer = read_layer(makeAscii(self.__exposure_layer))
        myFunctions = get_plugins(makeAscii(self.__function))
        myFunction = myFunctions[0][makeAscii(self.__function)]
        return ImpactCalculatorThread(myHazardLayer,
                                      myExposureLayer,
                                      myFunction)


class CalculatorNotifier(QObject):
    """A simple notification class so that we can
    listen for signals indicating when processing is
    done.

    Example::

      from impactcalculator import *
      n = CalculatorNotifier()
      n.done.connect(n.showMessage)
      n.done.emit()

    Prints 'hello' to the console
"""
    done = pyqtSignal()

    def showMessage(self):
        print 'hello'


class ImpactCalculatorThread(threading.Thread):
    """A threaded class to compute an impact scenario. Under
        python a thread can only be run once, so the instances
        based on this class are designed to be short lived.
        """

    def __init__(self, theHazardLayer, theExposureLayer,
                 theFunction):
        """Constructor for the impact calculator thread.

        Args:

          * Hazard layer - a RIAB read_layer object containing the Hazard data.
          * Exposure layer - a RIAB read_layer object containing the Exposure
            data.
          * Function - a RIAB function that defines how the Hazard assessment
            will be computed.

        Returns:
           None
        Raises:
           InsufficientParametersException if not all parameters are
           set.

        Requires three parameters to be set before execution
        can take place:
        """

        threading.Thread.__init__(self)
        self._hazardLayer = theHazardLayer
        self._exposureLayer = theExposureLayer
        self._function = theFunction
        self._notifier = CalculatorNotifier()
        self._impactLayer = None
        self._result = None

    def notifier(self):
        """Return a qobject that will emit a 'done' signal when the
        thread completes."""
        return self._notifier

    def impactLayer(self):
        """Return the RIAB file which is the output from the
        last run."""
        return self._impactLayer

    def result(self):
        """Return the result of the last run."""
        return self._result

    def run(self):
        """ Main function for hazard impact calculation thread.
        Requires three properties to be set before execution
        can take place:

        * Hazard layer - a path to a raster,
        * Exposure layer - a path to a vector points layer.
        * Function - a function that defines how the Hazard assessment
          will be computed.

        After the thread is complete, you can use the filename and
        result accessors to determine what the result of the analysis was::

          calculator = ImpactCalculator()
          myRoot = os.path.dirname(__file__)
          vectorPath = os.path.join(myRoot, 'testdata',
                                     'Jakarta_sekolah.shp')
          rasterPath = os.path.join(myRoot, 'testdata',
                                    'current_flood_depth_jakarta.asc')
          calculator.setHazardLayer(self.rasterPath)
          calculator.setExposureLayer(self.vectorPath)
          calculator.setFunction('Flood Building Impact Function')
          myRunner = calculator.getRunner()
          #wait till completion
          myRunner.join()
          myResult = myRunner.result()
          myFilename = myRunner.filename()


        Args:
           None.
        Returns:
           None
        Raises:
           None
           set.
        """
        try:
            myLayers = [self._hazardLayer, self._exposureLayer]
            self._impactLayer = calculate_impact(layers=myLayers,
                                                 impact_fcn=self._function)
        except Exception, e:
            msg = 'Calculation error encountered:\n'
            msg += get_exception_with_stacktrace(e, html=True)
            print msg
            self._result = msg
        else:
            self._result = 'Calculation completed successfully.'

        #  Let any listending slots know we are done
        self._notifier.done.emit()
