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
__version__ = '0.3.1'
__date__ = '11/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
from is_safe_interface import calculateSafeImpact
from is_utilities import getExceptionWithStacktrace
import threading
from PyQt4.QtCore import (QObject,
                          pyqtSignal)
from is_exceptions import InsufficientParametersException


class ISImpactCalculatorThread(threading.Thread, QObject):
    """A threaded class to compute an impact scenario. Under
       python a thread can only be run once, so the instances
       based on this class are designed to be short lived.
       We inherit from QObject so that we can use Qt translation self.tr
       calls and emit signals.

       .. todo:: implement this class using QThread as a base class since it
          supports thread termination which python threading doesnt seem to do.
          Also see the techbase article below for emitting signals across
          threads using Qt.QueuedConnection.
          http://techbase.kde.org/Development/Tutorials/
          Python_introduction_to_signals_and_slots
    """
    done = pyqtSignal()
    """Users of this of this class can listen for signals indicating
       when processing is done. For example::

         from is_impact_calculator_trhead import ISImpactCalculatorThread
         n = ISImpactCalculatorThread()
         n.done.connect(n.showMessage)
         n.done.emit()

       Prints 'hello' to the console

       .. seealso::
          http://techbase.kde.org/Development/Tutorials/
          Python_introduction_to_signals_and_slots

          for an alternative (maybe nicer?) approach.
       """

    def showMessage(self):
        """For testing only"""
        print 'hello'

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
        QObject.__init__(self)
        self._hazardLayer = theHazardLayer
        self._exposureLayer = theExposureLayer
        self._function = theFunction
        self._impactLayer = None
        self._result = None

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
        if (self._hazardLayer is None or self._exposureLayer is None
            or self._function is None):
            myMessage = self.tr('Ensure that hazard, exposure and function '
                                'are all set before trying to run the '
                                'analysis.')
            raise InsufficientParametersException(myMessage)
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
