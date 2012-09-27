"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**ISImpactCalculator.**

The module provides a high level interface for running SAFE scenarios.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com, ole.moller.nielsen@gmail.com'
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '11/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from PyQt4.QtCore import QObject

#Do not import any QGIS or SAFE modules in this module!
from safe_qgis.impact_calculator_thread import ImpactCalculatorThread
from safe_qgis.exceptions import InsufficientParametersException
from safe_qgis.safe_interface import (readSafeLayer,
                                   getSafeImpactFunctions)


class ImpactCalculator(QObject):
    """A class to compute an impact scenario. We inherit from QObject
    so that we can use Qt translation self.tr calls."""

    def __init__(self):
        """Constructor for the impact calculator."""
        QObject.__init__(self)
        self._hazardLayer = None
        self._exposureLayer = None
        self._function = None
        self._filename = None
        self._result = None

    def exposureLayer(self):
        """Accessor for the exposure layer.

        Args:
            None
        Returns:
            A QgsMapLayer or None depending on if the layer is set
        Raises:
            None
        """
        return self._exposureLayer

    def setExposureLayer(self, theLayerPath):
        """Mutator for Exposure layer property (e.g. buildings or
        features that will be affected).

        Args:
            theLayerPath - This should be a string representing a
            path to a file which can be loaded as a SAFE readlayer instance.
        Returns:
            None
        Raises:
            None
        """
        if theLayerPath is None:
            self._exposureLayer = None
        else:
            self._exposureLayer = str(theLayerPath)

    def hazardLayer(self):
        """Accessor for the hazard layer.

        Args:
            None
        Returns:
            A QgsMapLayer or None depending on if the layer is set
        Raises:
            None
        """
        return self._hazardLayer

    def setHazardLayer(self, theLayerPath):
        """Mutator: hazard layer. Hazard layer property  (e.g. a flood depth
        raster). This should be a SAFE readlayer instance.

        Args:
            theLayerPath - This should be a string representing a
            path to a file which can be loaded as a SAFE readlayer instance.
        Returns:
            None
        Raises:
            None
        """
        if theLayerPath is None:
            self._hazardLayer = None
        else:
            self._hazardLayer = str(theLayerPath)

    def function(self):
        """Accessor for the function layer.

        Args:
            None
        Returns:
            An inasafe function or None depending on if the layer is set
        Raises:
            None
        """
        return self._function

    def setFunction(self, theFunctionName):
        """Mutator: function layer. Function property (specifies which
        inasafe function to use to process the hazard and exposure
        layers with.

        Args:
            theFunctionName - This should be a string containing the name of a
            valid SAFE impact_function.
        Returns:
            None
        Raises:
            None
        """
        self._function = str(theFunctionName)

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
        self._filename = None
        self._result = None
        if self._hazardLayer is None or self._hazardLayer == '':
            myMessage = self.tr('Error: Hazard layer not set.')
            raise InsufficientParametersException(myMessage)

        if self._exposureLayer is None or self._exposureLayer == '':
            myMessage = self.tr('Error: Exposure layer not set.')
            raise InsufficientParametersException(myMessage)

        if self._function is None or self._function == '':
            myMessage = self.tr('Error: Function not set.')
            raise InsufficientParametersException(myMessage)

        # Call impact calculation engine
        try:
            myHazardLayer = readSafeLayer(self._hazardLayer)
            myExposureLayer = readSafeLayer(self._exposureLayer)
        except:
            raise

        myFunctions = getSafeImpactFunctions(self._function)
        myFunction = myFunctions[0][self._function]
        return ImpactCalculatorThread(myHazardLayer,
                                      myExposureLayer,
                                      myFunction)
