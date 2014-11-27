# coding=utf-8
"""Float Parameter."""
import sys

from numeric_parameter import NumericParameter


class FloatParameter(NumericParameter):
    """A subclass of generic parameter that accepts float only.

    .. note:: By default the min and max allowed values will be
        the platform specific largest and smallest float numbers.

    .. versionadded:: 2.2
    """

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter. If none
            is specified one will be generated using python hash. This guid
            will be used when storing parameters in the registry.
        :type guid: str
        """
        super(FloatParameter, self).__init__(guid)
        self.expected_type = [float, int]  # IS:because int is subset of float
        self._minimum_allowed_value = sys.float_info.min
        self._maximum_allowed_value = sys.float_info.max
        self._unit = ''
        # precision means the number of digit after comma that are considered
        self._precision = 2

    @property
    def precision(self):
        """Property for the precision for the parameter.

        :returns: The precision of the value of the parameter.
        :rtype: int
        """
        return self._precision

    @precision.setter
    def precision(self, precision):
        """Setter for the precision for the parameter.

        # precision means the number of digit after comma that are considered

        :param precision: The precision of the value of the parameter.
        :type precision: int

        """
        self._precision = precision

    def serialize(self):
        """Convert the parameter into a dictionary.

        :return: The parameter dictionary.
        :rtype: dict
        """
        pickle = super(FloatParameter, self).serialize()
        pickle['precision'] = self.precision
        return pickle
