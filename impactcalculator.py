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
                            NoFunctionsFoundException)

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(pardir)
from impact_functions import get_plugins
from engine.core import calculate_impact
from storage.core import read_layer
import threading
from PyQt4.QtCore import QObject, pyqtSignal


class CalculatorNotifier(QObject):
    """A simple notification class so that we can
    listen for signals indicating when processing is
    done.

    Example:

      from impactcalculator import *
      n = CalculatorNotifier()
      n.done.connect(n.showMessage)
      n.done.emit()

    Prints 'hello' to the console
"""
    done = pyqtSignal()

    def showMessage(self):
        print "hello"


class ImpactCalculator(threading.Thread):
    """A class to compute an impact scenario."""

    def __init__(self):
        """Constructor for the impact calculator."""
        threading.Thread.__init__(self)
        self.__notifier = CalculatorNotifier()
        self.__runningFlag = False
        self.__hazard_layer = None
        self.__exposure_layer = None
        self.__function = None
        self.__filename = None
        self.__result = None

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

    def isRunning(self):
        """Accessor: runningFlag."""
        return self.__runningFlag

    def filename(self):
        """Return the filename of the output from the
        last run."""
        return self.__filename

    def result(self):
        """Return the result of the last run."""
        return self.__result

    def notifier(self):
        """Return a qobject that will emit a 'done' signal when the
        thread completes."""
        return self.__notifier

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

    def availableFunctions(self):
        """ Query the riab engine to see what plugins are available.
        Args:
           None.
        Returns:
           A list of strings where each is a plugin name.
        Raises:
           NoFunctionsFoundException if not all parameters are
           set.
        """
        myList = get_plugins()
        if len(myList) < 1:
            myMessage = 'No RIAB impact functions could be found'
            raise NoFunctionsFoundException(myMessage)

        return myList

    def make_ascii(self, x):
        """Convert QgsString to ASCII"""
        x = unicode(x)
        x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore')
        return x

    def run(self):
        """ Main function for hazard impact calculation.
        Requires three parameters to be set before execution
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
          calculator.run()
          #wait till completion
          calculator.join()
          myResult = calculator.result()
          myFilename = calculator.filename()


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

        self.__runningFlag = True
        # Call impact calculation engine
        myHazardLayer = read_layer(self.make_ascii(self.__hazard_layer))
        myExposureLayer = read_layer(self.make_ascii(self.__exposure_layer))
        myLayers = [myHazardLayer, myExposureLayer]
        myFunctions = get_plugins(self.make_ascii(self.__function))
        myFunction = myFunctions[0][self.make_ascii(self.__function)]
        try:
            self.__filename = calculate_impact(layers=myLayers,
                                      impact_fcn=myFunction)
        except Exception, e:
            self.__running = False
            self.__result = 'Error encountered:\n' + str(e)

        self.__result = 'Completed successfully'
        self.__running = False
        #  let any listending slots know we are done
        self.__notifier.done.emit()
