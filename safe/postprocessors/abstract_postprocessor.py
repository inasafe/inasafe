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

from safe.common.exceptions import PostprocessorError
from safe.common.utilities import get_defaults

from third_party.odict import OrderedDict

LOGGER = logging.getLogger('InaSAFE')


class AbstractPostprocessor():
    """
    Abstract postprocessor class, do not instantiate directly.
    but instantiate the PostprocessorFactory class which will take care of
    setting up many prostprocessors. Alternatively you can as well instantiate
    directly a sub class of AbstractPostprocessor.

    Each subclass has to overload the process method and call its parent
    like this: AbstractPostprocessor.process(self)
    if a postprocessor needs parmeters, then it should override the setup and
    clear methods as well and call respectively
    AbstractPostprocessor.setup(self) and AbstractPostprocessor.clear(self).

    for implementation examples see AgePostprocessor which uses mandatory and
    optional parameters
    """

    NO_DATA_TEXT = get_defaults('NO_DATA')

    def __init__(self):
        """
        Constructor for abstract postprocessor class, do not instantiate
        directly. It takes care of defining self._results
        Needs to be called from the concrete implementation with
        AbstractPostprocessor.__init__(self)
        """
        self._results = None

    def setup(self, params):
        """Abstract method to be called from the concrete implementation
         with AbstractPostprocessor.setup(self, None) it takes care of results
        being initialized

        Args:
            params: dict of parameters to pass to the post processor
        Returns:
            None
        Raises:
            None
        """
        del params
        if self._results is not None:
            self._raise_error('clear needs to be called before setup')
        self._results = OrderedDict()

    def process(self):
        """Abstract method to be called from the concrete implementation
         with AbstractPostprocessor.process(self) it takes care of results
        being initialized

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        if self._results is None:
            self._raise_error('setup needs to be called before process')

    def clear(self):
        """Abstract method to be called from the concrete implementation
         with AbstractPostprocessor.process(self) it takes care of results
        being cleared

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        self._results = None

    def results(self):
        """Returns the postprocessors results

        Args:
            None
        Returns:
            Odict of results
        Raises:
            None
        """
        return self._results

    def _raise_error(self, message=None):
        """internal method to be used by the postprocessors to raise an error

        Args:
            None
        Returns:
            None
        Raises:
            PostprocessorError
        """
        if message is None:
            message = 'Postprocessor error'
        raise PostprocessorError(message)

    def _log_message(self, message):
        """internal method to be used by the postprocessors to log a message

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        LOGGER.debug(message)

    def _append_result(self, name, result, metadata=None):
        """add an indicator results to the postprocessors result.

        internal method to be used by the postprocessors to add an indicator
        results to the postprocessors result

        Args:
            * name: str the name of the indicator
            * result the value calculated by the indicator
            * metadata Dict of metadata
        Returns:
            None
        Raises:
            None
        """
        if metadata is None:
            metadata = dict()
        self._results[name] = {'value': result,
                                 'metadata': metadata}
