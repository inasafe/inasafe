# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**ImpactCalculator.**

The module provides a high level interface for running SAFE scenarios.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com, ole.moller.nielsen@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '11/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from PyQt4.QtCore import QObject

#Do not import any QGIS or SAFE modules in this module!
from safe_qgis.utilities.impact_calculator_thread import ImpactCalculatorThread
from safe_qgis.exceptions import InsufficientParametersError
from safe_qgis.safe_interface import readSafeLayer, getSafeImpactFunctions


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

    def exposure_layer(self):
        """Accessor for the exposure layer.

        :returns: The exposure layer.
        :rtype: read_layer
        """
        return self._exposureLayer

    def set_exposure_layer(self, layer_path):
        """Mutator for Exposure layer property.

        e.g. buildings or features that will be affected.

        :param layer_path: Path to a file which can be loaded as a SAFE
            read_layer instance.
        :type layer_path: str
        """
        if layer_path is None:
            self._exposureLayer = None
        else:
            self._exposureLayer = str(layer_path)

    def hazard_layer(self):
        """Accessor for the hazard layer.

        :returns: Path for the hazard layer.
        :rtype: str

        """
        return self._hazardLayer

    def set_hazard_layer(self, layer_path):
        """Mutator for hazard layer property.

        e.g. buildings or features that will be affected.

        :param layer_path: Path to a file which can be loaded as a SAFE
            read_layer instance.
        :type layer_path: str
        """
        if layer_path is None:
            self._hazardLayer = None
        else:
            self._hazardLayer = str(layer_path)

    def function(self):
        """Accessor for the impact function.

        :returns: An InaSAFE impact function or None depending on if it is set.
        :rtype: FunctionProvider, None
        """
        return self._function

    def set_function(self, function_id):
        """Mutator for the impact function.

        The function property specifies which inasafe function to use to
        process the hazard and exposure layers with.

        :param function_id: The identifier of a valid SAFE impact_function.
        :type function_id: str

        """
        self._function = str(function_id)

    def get_runner(self):
        """ Factory to create a new runner thread.

        Requires three parameters to be set before execution can take place:

        * Hazard layer - a path to a raster (string)
        * Exposure layer - a path to a vector hazard layer (string).
        * Function - a function name that defines how the Hazard assessment
          will be computed (string).

        :returns: An impact calculator thread instance.
        :rtype: ImpactCalculatorThread

        :raises: InsufficientParametersError if not all parameters are set.
        """
        self._filename = None
        self._result = None
        if self._hazardLayer is None or self._hazardLayer == '':
            myMessage = self.tr('Error: Hazard layer not set.')
            raise InsufficientParametersError(myMessage)

        if self._exposureLayer is None or self._exposureLayer == '':
            myMessage = self.tr('Error: Exposure layer not set.')
            raise InsufficientParametersError(myMessage)

        if self._function is None or self._function == '':
            myMessage = self.tr('Error: Function not set.')
            raise InsufficientParametersError(myMessage)

        # Call impact calculation engine
        try:
            myHazardLayer = readSafeLayer(self._hazardLayer)
            myExposureLayer = readSafeLayer(self._exposureLayer)
        except:
            raise

        myFunctions = getSafeImpactFunctions(self._function)
        myFunction = myFunctions[0][self._function]
        return ImpactCalculatorThread(
            myHazardLayer,
            myExposureLayer,
            myFunction)
