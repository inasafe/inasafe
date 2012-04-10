"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**ISImpactCalculatorThread.**

The module provides a high level interface for running SAFE scenarios.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com, ole.moller.nielsen@gmail.com'
__version__ = '0.3.0'
__date__ = '11/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
from is_safe_interface import calculateSafeImpact
from is_utilities import getExceptionWithStacktrace
import threading
from PyQt4.QtCore import (QObject,
                          pyqtSignal)


class ISImpactCalculatorThread(QObject, threading.Thread):
    """A threaded class to compute an impact scenario. Under
        python a thread can only be run once, so the instances
        based on this class are designed to be short lived.
        We inherit from QObject so that we can use Qt translation self.tr
        calls and emit signals."""

    #def tr(theText):
    #    """We define a tr() alias here since the ISImpactCalculatorThread
    #     implementation below is not a class and does not inherit from QObject
    ##    .. note:: see http://tinyurl.com/pyqt-differences
    #    Args:
    #       theText - string to be translated
    #    Returns:
    #       Translated version of the given string if available, otherwise
    #       the original string.
    ##    """
    #    myContext = "ISImpactCalculatorThread"
    #    return QCoreApplication.translate(myContext, theText)

    done = pyqtSignal()
    """so that we can emit a signal when processing is done."""

    def __init__(self, theHazardLayer, theExposureLayer,
                 theFunction):
        """Constructor for the impact calculator thread.

        Args:

          * Hazard layer: InaSAFE read_layer object containing the Hazard data.
          * Exposure layer: InaSAFE read_layer object containing the Exposure
            data.
          * Function: a InaSAFE function that defines how the Hazard assessment
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
        self._impactLayer = None
        self._result = None

    def notifier(self):
        """Return a qobject that will emit a 'done' signal when the
        thread completes."""
        return self._notifier

    def impactLayer(self):
        """Return the InaSAFE layer instance which is the output from the
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

          calculator = ISImpactCalculator()
          rasterPath = os.path.join(TESTDATA, 'xxx.asc')
          vectorPath = os.path.join(TESTDATA, 'xxx.shp')
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
            self._impactLayer = calculateSafeImpact(theLayers=myLayers,
                                        theFunction=self._function)
        except Exception, e:
            myMessage = self.tr('Calculation error encountered:\n')
            myMessage += getExceptionWithStacktrace(e, html=True)
            print myMessage
            self._result = myMessage
        else:
            self._result = self.tr('Calculation completed successfully.')

        #  Let any listening slots know we are done
        self.done.emit()
