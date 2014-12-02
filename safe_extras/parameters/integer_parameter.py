# coding=utf-8

"""Integer Parameter."""
import sys

from numeric_parameter import NumericParameter


class IntegerParameter(NumericParameter):
    """A subclass of numeric parameter that accepts integer only.

    .. note:: By default the min and max allowed values will be
        the platform specific largest and smallest int numbers.

    .. versionadded:: 2.2
    """

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter. If none
            is specified one will be generated using python hash. This guid
            will be used when storing parameters in the registry.
        :type guid: str
        """
        super(IntegerParameter, self).__init__(guid)
        self.expected_type = int
        self._minimum_allowed_value = - sys.maxint - 1
        self._maximum_allowed_value = sys.maxint
        self._unit = ''
