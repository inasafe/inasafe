# -*- coding: utf-8 -*-
"""**Abstract postprocessor class, do not instantiate directly**

"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import logging

from safe.common.utilities import OrderedDict

from safe.defaults import get_defaults
from safe.common.exceptions import PostProcessorError
from safe.common.utilities import (format_int)

LOGGER = logging.getLogger('InaSAFE')


class AbstractPostprocessor(object):
    """
    Abstract postprocessor class, do not instantiate directly.
    but instantiate the PostprocessorFactory class which will take care of
    setting up many prostprocessors. Alternatively you can instantiate
    directly a sub class of AbstractPostprocessor.

    Each subclass has to overload the process method and call its parent
    like this: AbstractPostprocessor.process(self)
    if a postprocessor needs parameters, then it should override the setup and
    clear methods as well and call respectively
    AbstractPostprocessor.setup(self) and AbstractPostprocessor.clear(self).

    for implementation examples see AgePostprocessor which uses mandatory and
    optional parameters
    """

    NO_DATA_TEXT = get_defaults('NO_DATA')

    def __init__(self):
        """
        Constructor.

        Constructor for abstract postprocessor class, do not instantiate
        directly. It takes care of defining self._results
        Needs to be called from the concrete implementation with
        AbstractPostprocessor.__init__(self)
        """
        self._results = None

    def description(self):
        """
        Describe briefly what the post processor does.
        """
        raise NotImplementedError('Please don\'t use this class directly')

    def setup(self, params):
        """
        Setup the post processor.

        Abstract method to be called from the concrete implementation
        with AbstractPostprocessor.setup(self, None) it takes care of results
        being initialized.

        :param params:
        """
        del params
        if self._results is not None:
            self._raise_error('clear needs to be called before setup')
        self._results = OrderedDict()

    def process(self):
        """
        Virtual method to be re-implemented by each post-processor.

        Abstract method to be called from the concrete implementation
        with AbstractPostprocessor.process(self) it takes care of results
        being initialized.
        """
        if self._results is None:
            self._raise_error('setup needs to be called before process')

    def clear(self):
        """
        Clear the existing results.

        Abstract method to be called from the concrete implementation
        with AbstractPostprocessor.process(self) it takes care of results
        being cleared.
        """
        self._results = None

    def results(self):
        """Accessor for the postprocessors results.

        :returns: Results
        :rtype: dict
        """
        return self._results

    def _raise_error(self, message=None):
        """Internal method to be used by the postprocessors to raise an error.

        """
        if message is None:
            message = 'Postprocessor error'
        raise PostProcessorError(message)

    def _log_message(self, message):
        """Internal method to be used by the postprocessors to log a message.
        """
        LOGGER.debug(message)

    def _append_result(self, name, result, metadata=None):
        """add an indicator results to the postprocessors result.

        internal method to be used by the postprocessors to add an indicator
        results to the postprocessors result

        :param name: The name of the indicator.
        :param result: The value calculated by the indicator.
        :param metadata: Dict of metadata.
        """

        if metadata is None:
            metadata = dict()
        # LOGGER.debug('name : ' + str(name) + '\nresult : ' + str(result))
        if result is not None and result != self.NO_DATA_TEXT:
            try:
                result = format_int(result)
            except ValueError as e:
                LOGGER.debug(e)
                result = result
        self._results[name] = {'value': result, 'metadata': metadata}
