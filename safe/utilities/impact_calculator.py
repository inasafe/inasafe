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

__author__ = 'tim@kartoza.com, ole.moller.nielsen@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '11/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4.QtCore import QObject

# Do not import any QGIS or SAFE modules in this module!
from safe.utilities.impact_calculator_thread import ImpactCalculatorThread
from safe.utilities.qgis_layer_wrapper import QgisWrapper
from safe.common.exceptions import (
    InsufficientParametersError,
    InvalidParameterError)
from safe.utilities.gis import convert_to_safe_layer
from safe.impact_functions.impact_function_manager import ImpactFunctionManager


class ImpactCalculator(QObject):
    """A class to compute an impact scenario."""

    # DK: I think it should be only one module that uses information about
    # function style:
    #  ImpactCalculator
    #     gets layers
    #     checks style of the impact function
    #     informs about layer clipping (is the clipping requires?)

    def __init__(self):
        """Constructor for the impact calculator."""
        QObject.__init__(self)
        self.impact_function_manager = ImpactFunctionManager()
        self._hazard_layer = None
        self._exposure_layer = None
        self._impact_function = None
        self._filename = None
        self._result = None
        self._extent = None

    def _get_layer(self, layer):
        """Analyze style of self._function and return appropriate
            class of the layer.

        :param layer: A layer.
        :type layer:  QgsMapLayer or SAFE layer.

        :returns:   The layer of appropriate type
        :rtype:     SAFE or QgisWrapper

        :raises: InsufficientParametersError if self._function is not set,
                 InvalidParameterError if style of self._function is not
                     in ('old-style', 'qgis2.0')
                 Any exceptions raised by other libraries will be propagated.
        """
        if self._impact_function is None:
            message = self.tr('Error: Impact Function not set.')
            raise InsufficientParametersError(message)

        # Get type of the impact function (old-style or new-style)
        try:
            impact_function_type = \
                self.impact_function_manager.get_function_type(
                    self._impact_function)
            if impact_function_type == 'old-style':
                return convert_to_safe_layer(layer)
            elif impact_function_type == 'qgis2.0':
                # convert for new style impact function
                return QgisWrapper(layer)
            else:
                message = self.tr('Error: Impact Function has unknown style.')
                raise InvalidParameterError(message)
        except:
            raise

    def exposure_layer(self):
        """Accessor for the exposure layer.

        :returns: The exposure layer.
        :rtype: read_layer
        """
        return self._get_layer(self._exposure_layer)

    def set_exposure_layer(self, layer):
        """Mutator for Exposure layer property.

        e.g. buildings or features that will be affected.

        :param layer: An exposure layer.
        :type layer:  QgsMapLayer or SAFE layer.
        """
        if layer is None:
            self._exposure_layer = None
        else:
            self._exposure_layer = layer

    def hazard_layer(self):
        """Accessor for the hazard layer.

        :returns: The hazard layer.
        :rtype:   QgsMapLayer or SAFE layer.

        """
        return self._get_layer(self._hazard_layer)

    def set_hazard_layer(self, layer):
        """Mutator for hazard layer property.

        e.g. buildings or features that will be affected.

        :param layer: A hazard layer.
        :type layer: QgsMapLayer or SAFE layer.
        """
        if layer is None:
            self._hazard_layer = None
        else:
            self._hazard_layer = layer

    def set_function(self, impact_function):
        """Mutator for the impact function.

        The function property specifies which inasafe function to use to
        process the hazard and exposure layers with.

        :param impact_function: The identifier of a valid SAFE impact_function.
        :type impact_function: str

        """
        if isinstance(impact_function, str):
            self._impact_function = self.impact_function_manager\
                .get(impact_function)
        else:
            self._impact_function = impact_function

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
        if self._hazard_layer is None:
            message = self.tr('Error: Hazard layer not set.')
            raise InsufficientParametersError(message)

        if self._exposure_layer is None:
            message = self.tr('Error: Exposure layer not set.')
            raise InsufficientParametersError(message)

        if self._impact_function is None:
            message = self.tr('Error: Function not set.')
            raise InsufficientParametersError(message)

        # Call impact calculation engine
        hazard_layer = self.hazard_layer()
        exposure_layer = self.exposure_layer()

        return ImpactCalculatorThread(
            hazard_layer,
            exposure_layer,
            self._impact_function,
            extent=self.extent(),
            check_integrity=self.requires_clipping())

    def function(self):
        """Accessor for the impact function.

        :returns: An InaSAFE impact function or None depending on if it is set.
        :rtype: safe.impact_functions.base.ImpactFunction, None
        """
        return self._impact_function

    def requires_clipping(self):
        """Check to clip or not to clip layers.

        If self._function is a 'new-style' impact function, then
        return False -- clipping is unnecessary, else return True

        :returns:   To clip or not to clip.
        :rtype:     bool

        :raises: InsufficientParametersError if function parameter is not set.
                 InvalidParameterError if the function has unknown style.
        """
        if self._impact_function is None:
            message = self.tr('Error: Impact Function is not provided.')
            raise InsufficientParametersError(message)

        impact_function_type = \
            self.impact_function_manager.get_function_type(
                self._impact_function)
        if impact_function_type == 'old-style':
            return True
        elif impact_function_type == 'qgis2.0':
            return False
        else:
            message = self.tr('Error: Impact Function has unknown style.')
            raise InvalidParameterError(message)

    def set_extent(self, extent):
        """Mutator for the extent property.

        Set extent that can be used as bounding box of the
            calculator's working region.

        :param extent:  Bounding box [xmin, ymin, xmax, ymax]
            of the working region.
        :type extent: list, None

        """
        self._extent = extent

    def extent(self):
        """Accessor for the extent property.

        :returns: Bounding box [xmin, ymin, xmax, ymax] of the working region.
        :rtype: list, None
        """
        return self._extent
