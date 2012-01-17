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


class ImpactCalculator:
    """A class to compute an impact scenario."""

    def __init__(self):
        """Constructor for the impact calculator."""
        self._hazard_layer = None
        self._exposure_layer = None
        self._function = None

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

        Args:
           None.
        Returns:
           A two tuple containing:

           * a raster output layer's path
           * a string (probably in html markup) containing reporting
             information summarising the analysis result

        Raises:
           InsufficientParametersException if not all parameters are
           set.
        """

        if not self.__hazard_layer:
            msg = 'Error: Hazard layer not set.'
            raise InsufficientParametersException(msg)

        if not self.__exposure_layer:
            msg = 'Error: Exposure layer not set.'
            raise InsufficientParametersException(msg)

        if not self.__function:
            msg = 'Error: Function not set.'
            raise InsufficientParametersException(msg)

        # Call impact calculation engine
        myHazardLayer = read_layer(self.make_ascii(self.__hazard_layer))
        myExposureLayer = read_layer(self.make_ascii(self.__exposure_layer))
        myLayers = [myHazardLayer, myExposureLayer]
        myFunctions = get_plugins(self.make_ascii(self.__function))
        myFunction = myFunctions[0][self.make_ascii(self.__function)]
        myFilename = calculate_impact(layers=myLayers,
                                      impact_fcn=myFunction)
        return myFilename
