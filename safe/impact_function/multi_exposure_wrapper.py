# coding=utf-8

"""
Multi-exposure wrapper.

This class will manage how to launch and optimize a multi exposure analysis.
"""

import logging
from datetime import datetime

from safe import messaging as m
from safe.definitions.constants import (
    PREPARE_SUCCESS,
    PREPARE_FAILED_BAD_INPUT,
    ANALYSIS_FAILED_BAD_INPUT,
    ANALYSIS_SUCCESS,
)
from safe.gui.widgets.message import generate_input_error_message
from safe.impact_function.impact_function import ImpactFunction
from safe.impact_function.impact_function_utilities import check_input_layer
from safe.utilities.gis import deep_duplicate_layer
from safe.utilities.i18n import tr

LOGGER = logging.getLogger('InaSAFE')


class MultiExposureImpactFunction(object):

    """Multi-exposure wrapper."""

    def __init__(self):
        """Constructor."""
        # Input layers
        self._hazard = None
        self._aggregation = None

        # Exposures, it's now a list of layers. One for each exposure maximum.
        self._exposures = []

        # For now, we have many IF running.
        self._impact_functions = []
        self._current_impact_function = None

        # Metadata
        self.callback = None
        self.debug = False
        self._is_ready = False
        self._start_datetime = None
        self._end_datetime = None
        self._duration = 0

    @property
    def hazard(self):
        """Property for the hazard layer to be used for the analysis.

        :returns: A map layer.
        :rtype: QgsMapLayer
        """
        return self._hazard

    @hazard.setter
    def hazard(self, layer):
        """Setter for hazard layer property.

        :param layer: Hazard layer to be used for the analysis.
        :type layer: QgsMapLayer
        """
        self._hazard = layer
        self._is_ready = False

    @property
    def exposures(self):
        """Property for exposure layers to be used for the analysis.

        :returns: List of map layers.
        :rtype: list(QgsMapLayer)
        """
        return self._exposures

    @exposures.setter
    def exposures(self, layers):
        """Setter for exposure layers property.

        :param layers: List of exposure layers to be used for the analysis.
        :type layers: list(QgsMapLayer)
        """
        self._exposures = layers
        self._is_ready = False

    @property
    def aggregation(self):
        """Property for the aggregation layer to be used for the analysis.

        :returns: A map layer.
        :rtype: QgsVectorLayer
        """
        return self._aggregation

    @aggregation.setter
    def aggregation(self, layer):
        """Setter for aggregation layer property.

        :param layer: aggregation layer to be used for the analysis.
        :type layer: QgsVectorLayer
        """
        self._aggregation = layer
        self._is_ready = False

    @property
    def impact_functions(self):
        """Return the list of impact functions which have been used.

        :return: List of impact functions.
        :rtype: list(ImpactFunction)
        """
        return self._impact_functions

    @property
    def current_impact_function(self):
        """Return the current IF being processed.

        :return: Impact function.
        :rtype: ImpactFunction
        """
        return self._current_impact_function

    def prepare(self):
        """Method to check if the impact function can be run.

        :return: A tuple with the status of the IF and an error message if
            needed.
            The status is PREPARE_SUCCESS if everything was fine.
            The status is PREPARE_FAILED_BAD_INPUT if the client should fix
                something.
            The status is PREPARE_FAILED_INSUFFICIENT_OVERLAP if the client
                should fix the analysis extent.
            The status is PREPARE_FAILED_BAD_CODE if something went wrong
                from the code.
        :rtype: (int, m.Message)
        """
        if len(self._exposures) < 1:
            message = generate_input_error_message(
                tr('No exposure layer provided'),
                m.Paragraph(tr('You need to provide at least one exposure.')))
            self._is_ready = False
            return PREPARE_FAILED_BAD_INPUT, message

        existing_exposure = []
        for exposure in self._exposures:
            status, message = check_input_layer(exposure, 'exposure')
            if status != PREPARE_SUCCESS:
                return status, message

            if exposure.keywords['exposure'] in existing_exposure:
                message = generate_input_error_message(
                    tr('Same exposure'),
                    m.Paragraph(tr('Not the same exposure')))
                self._is_ready = False
                return PREPARE_FAILED_BAD_INPUT, message
            else:
                existing_exposure.append(exposure.keywords['exposure'])

        status, message = check_input_layer(self.hazard, 'hazard')
        if status != PREPARE_SUCCESS:
            return status, message

        if self.aggregation:
            status, message = check_input_layer(
                self.aggregation, 'aggregation')
            if status != PREPARE_SUCCESS:
                return status, message

        self._impact_functions = []

        # We delegate the prepare to the main IF for each exposure
        for exposure in self._exposures:
            impact_function = ImpactFunction()
            impact_function.hazard = deep_duplicate_layer(self._hazard)
            impact_function.exposure = exposure
            impact_function.debug_mode = self.debug
            if self.callback:
                impact_function.callback = self.callback
            if self._aggregation:
                impact_function.aggregation = deep_duplicate_layer(
                    self._aggregation)
            else:
                # TODO
                pass

            code, message = impact_function.prepare()
            if code != PREPARE_SUCCESS:
                return code, message

            self._impact_functions.append(impact_function)

        self._is_ready = True
        return PREPARE_SUCCESS, None

    def run(self):
        """Run the whole impact function.

        :return: A tuple with the status of the IF and an error message if
            needed.
            The status is ANALYSIS_SUCCESS if everything was fine.
            The status is ANALYSIS_FAILED_BAD_INPUT if the client should fix
                something.
            The status is ANALYSIS_FAILED_BAD_CODE if something went wrong
                from the code.
        :rtype: (int, m.Message)
        """
        self._start_datetime = datetime.now()
        if not self._is_ready:
            message = tr('You need to run `prepare` first.')
            return ANALYSIS_FAILED_BAD_INPUT, message

        for impact_function in self._impact_functions:
            self._current_impact_function = impact_function
            LOGGER.info('Running %s' % impact_function.name)
            code, message = impact_function.run()
            if code != ANALYSIS_SUCCESS:
                return code, message

        return ANALYSIS_SUCCESS, None
