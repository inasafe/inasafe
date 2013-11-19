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
from safe_qgis.exceptions import (
    InsufficientParametersError,
    InvalidParameterError)
from safe_qgis.safe_interface import (
    convertToSafeLayer,
    getSafeImpactFunctions,
    getSafeImpactFunctionType)


class ImpactCalculator(QObject):
    """A class to compute an impact scenario. We inherit from QObject
    so that we can use Qt translation self.tr calls."""

    # DK: I think it should be only one module that uses information about function style:
    #  ImpactCalculator
    #     gets layers
    #     checks style of the impact function
    #     clips layers if the function is old-style


    def __init__(self):
        """Constructor for the impact calculator."""
        QObject.__init__(self)
        self._hazardLayer = None
        self._exposureLayer = None
        self._function = None
        self._filename = None
        self._result = None

    def _convert_layer(self, layer):
        """Analyze style of self._function and return appropriate
            class of the layer.

        :param layer: A layer.
        :type layer:  QgsMapLayer or SAFE layer.

        :returns:   The layer of appropriate type
        :rtype:     convertToSafeLayer

        :raises: InsufficientParametersError if self._function is not set,
                 InvalidParameterError if style of self._function is not
                     in ('old-style', 'qgis2.0')
                 Any exceptions raised by other libraries will be propogated.
        """

        # FIXME (DK): I'm not sure that it is good place for the
        #   converting function. May be safe_qgis.safe_interface is better.
        #   But I don't like pass information about function style to other
        #   modules: I prefer keep only one place of function style analysis

        if self._function is None or self._function == '':
            myMessage = self.tr('Error: Function not set.')
            raise InsufficientParametersError(myMessage)

        # Get type of the impact function (old-style or new-style)
        try:
            func_type = getSafeImpactFunctionType(self._function)
            if func_type == 'old-style':
                return convertToSafeLayer(layer)
            elif func_type == 'qgis2.0':
                # TODO (DK): convert for new style impact function
                return convertToSafeLayer(layer)
            else:
                myMessage = self.tr('Error: Function has unknown style.')
                raise InvalidParameterError(myMessage)
        except:
            raise

    def exposure_layer(self):
        """Accessor for the exposure layer.

        :returns: The exposure layer.
        :rtype: read_layer
        """
        return self._convert_layer(self._exposureLayer)

    def set_exposure_layer(self, layer):
        """Mutator for Exposure layer property.

        e.g. buildings or features that will be affected.

        :param layer: An exposure layer.
        :type layer:  QgsMapLayer or SAFE layer.
        """
        if layer is None:
            self._exposureLayer = None
        else:
            self._exposureLayer = layer

    def hazard_layer(self):
        """Accessor for the hazard layer.

        :returns: The hazard layer.
        :rtype:   QgsMapLayer or SAFE layer.

        """
        return self._convert_layer(self._hazardLayer)

    def set_hazard_layer(self, layer):
        """Mutator for hazard layer property.

        e.g. buildings or features that will be affected.

        :param layer: A hazard layer.
        :type layer_path: QgsMapLayer or SAFE layer.
        """
        if layer is None:
            self._hazardLayer = None
        else:
            self._hazardLayer = layer

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
        if self._hazardLayer is None:
            myMessage = self.tr('Error: Hazard layer not set.')
            raise InsufficientParametersError(myMessage)

        if self._exposureLayer is None:
            myMessage = self.tr('Error: Exposure layer not set.')
            raise InsufficientParametersError(myMessage)

        if self._function is None or self._function == '':
            myMessage = self.tr('Error: Function not set.')
            raise InsufficientParametersError(myMessage)

        # Call impact calculation engine
        myHazardLayer = self.hazard_layer()
        myExposureLayer = self.exposure_layer()

        myFunctions = getSafeImpactFunctions(self._function)
        myFunction = myFunctions[0][self._function]
        return ImpactCalculatorThread(
            myHazardLayer,
            myExposureLayer,
            myFunction)

    def need_clip(self):
        """Check to clip or not to clip layers.

        If self._function is a 'new-style' impact function, then
            return False -- clipping is unnecessary, else return True

        :returns:   To clip or not to clip.
        :rtype:     bool

        :raises: InsufficientParametersError if function parameter is not set.
                 InvalidParameterError if the function has unknown style.
        """
        f = self.function()
        if f is None:
            myMessage = self.tr('Error: Function is not provided.')
            raise InsufficientParametersError(myMessage)

        style = getSafeImpactFunctionType(f)
        if style == 'old-style':
            return True
        elif style == 'qgis2.0':
            return False
        else:
            myMessage = self.tr('Error: Function has unknown style.')
            raise InvalidParameterError(myMessage)
