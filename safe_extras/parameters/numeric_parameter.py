# coding=utf-8

"""Integer Parameter."""
from generic_parameter import GenericParameter
from parameter_exceptions import (
    InvalidMaximumError, InvalidMinimumError, ValueOutOfBounds)


class NumericParameter(GenericParameter):
    """A subclass of generic parameter that accepts float or integer only.

    Known issue : You should set the minimum and the maximum value explicitly.
    See https://github.com/inasafe/inasafe/issues/2468#issuecomment-171124507

    .. versionadded:: 2.2
    """

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter. If none
            is specified one will be generated using python hash. This guid
            will be used when storing parameters in the registry.
        :type guid: str
        """
        super(NumericParameter, self).__init__(guid)
        self._minimum_allowed_value = None
        self._maximum_allowed_value = None
        self._unit = None
        self._allowed_units = []

    @property
    def minimum_allowed_value(self):
        """Property for the minimum allowed value for the parameter.

        :returns: The minimum allowed value.
        :rtype: float, int
        """
        return self._minimum_allowed_value

    @minimum_allowed_value.setter
    def minimum_allowed_value(self, value):
        """Setter for the minimum allowed value for the parameter.

        :param value: The minimum allowed value.
        :type value: float, int

        :raises: InvalidMinimumError, TypeError
        """
        self._check_type(value)
        # If maximum is not set, we can set minimum regardless
        if self._maximum_allowed_value is None:
            self._minimum_allowed_value = value
            return
        # Otherwise it must be less than maximum
        if value <= self._maximum_allowed_value:
            self._minimum_allowed_value = value
            return

        raise InvalidMinimumError('Minimum must be less than maximum')

    @property
    def maximum_allowed_value(self):
        """Property for the maximum allowed value for the parameter.

        :returns: The maximum allowed value.
        :rtype: float, int
        """
        return self._maximum_allowed_value

    @maximum_allowed_value.setter
    def maximum_allowed_value(self, value):
        """Setter for the maximum allowed value for the parameter.

        :param value: The maximum allowed value.
        :type value: float, int

        :raises: InvalidMaximumError, TypeError
        """
        self._check_type(value)
        # If minimum is not set, we can set maximum regardless
        if self._minimum_allowed_value is None:
            self._maximum_allowed_value = value
            return
        # Otherwise it must be more than the minimum
        if value >= self._minimum_allowed_value:
            self._maximum_allowed_value = value
            return

        raise InvalidMaximumError('Maximum must be greater than minimum')

    @property
    def unit(self):
        """Property for the unit for the parameter.

        :returns: The unit of the parameter.
        :rtype: Unit

        """
        return self._unit

    @unit.setter
    def unit(self, unit):
        """Setter for unit for the parameter.

        :param unit: Unit for parameter
        :type unit: Unit

        """
        self._unit = unit

    @property
    def allowed_units(self):
        """Property for the allowed_units for the parameter.

        :returns: The list of allowed unit of the parameter.
        :rtype: list

        """
        return self._allowed_units

    @allowed_units.setter
    def allowed_units(self, allowed_units):
        """Setter for allowed_units for the parameter.

        :param allowed_units: The list of allowed unit of the parameter.
        :type allowed_units: list

        """
        self._allowed_units = allowed_units

    @GenericParameter.value.setter
    def value(self, value):
        """Define the current _value for the parameter.

        .. note:: Overloads the setting in GenericParameter

        :param value: The _value of the parameter itself.
        :type value: str, bool, integer, float, list, dict

        :raises: TypeError
        """
        self._check_type(value)
        if self._minimum_allowed_value <= value <= self._maximum_allowed_value:
            self._value = value
        else:
            raise ValueOutOfBounds(
                'Value (%s) must be greater than %s and less than %s' % (
                    value,
                    self._minimum_allowed_value,
                    self._maximum_allowed_value))

    def serialize(self):
        """Convert the parameter into a dictionary.

        :return: The parameter dictionary.
        :rtype: dict
        """
        pickle = super(NumericParameter, self).serialize()
        pickle['minimum_allowed_value'] = self.minimum_allowed_value
        pickle['maximum_allowed_value'] = self.maximum_allowed_value
        pickle['unit'] = self.unit
        pickle['allowed_units'] = [unit.name for unit in self.allowed_units]
        return pickle
