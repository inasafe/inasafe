# coding=utf-8

"""Collection Parameter abstract base class0."""
import abc

from generic_parameter import GenericParameter
from parameter_exceptions import (
    CollectionLengthError, InvalidMinimumError, InvalidMaximumError)


class CollectionParameter(GenericParameter):
    """A subclass of generic parameter that accepts collections only.

    This is a base class for List, Dict etc. parameters which share some
    functionality.

    .. versionadded:: 2.2
    """
    # Indicate that this is an abstract base class
    __metaclass__ = abc.ABCMeta

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter. If none
            is specified one will be generated using python hash. This guid
            will be used when storing parameters in the registry.
        :type guid: str
        """
        super(CollectionParameter, self).__init__(guid)
        self._minimum_item_count = None
        self._maximum_item_count = None
        self._element_type = None

    @property
    def minimum_item_count(self):
        """Property for minimum allowed item count."""
        return self._minimum_item_count

    @minimum_item_count.setter
    def minimum_item_count(self, minimum_count):
        """Define the minimum number of item in the parameter.

        :param minimum_count: Minimum number of items that may be
            selected. Defaults to 1.
        :type minimum_count: int
        """
        # If maximum is not set, we can set minimum regardless
        if self._maximum_item_count is None:
            self._minimum_item_count = minimum_count
            return
        # Otherwise it must be less than maximum
        if minimum_count <= self._maximum_item_count:
            self._minimum_item_count = minimum_count
            return

        self._minimum_item_count = minimum_count
        raise InvalidMinimumError(
            'Minimum item count must be no more than maximum')

    @property
    def maximum_item_count(self):
        """Property for maximum allowed item count."""
        return self._maximum_item_count

    @maximum_item_count.setter
    def maximum_item_count(self, maximum_count):
        """Define the maximum allowed number of items that can be selected.

        :param maximum_count: Maximum number of items that may be selected.
            Defaults to 1.
        :type maximum_count: int
        """
        # If maximum is not set, we can set minimum regardless
        if self._maximum_item_count is None:
            self._maximum_item_count = maximum_count
            return
        # Otherwise it must be less than maximum
        if maximum_count >= self._minimum_item_count:
            self._maximum_item_count = maximum_count
            return
        raise InvalidMaximumError('Maximum must be greater than minimum')

    def count(self):
        """Obtain the number of element in the list.

        :returns: The number of elements.
        :rtype: int
        """
        return len(self._value)

    @property
    def element_type(self):
        """Property for the allowed type for elements in the list.

        The element type determines if the list should be composed of strings,
        ints, floats etc.

        """
        return self._element_type

    @element_type.setter
    def element_type(self, element_type):
        """Define the allowed type for elements in the list.

        :param element_type: The element type determines if the list should be
            composed of strings, ints, floats etc.
        :type element_type: string, int, float
        """
        self._element_type = element_type

    def check_types(self, value):
        """
        Helper to check the type of the value and its elements.

        :param value: The list of values set for this parameter.
        :type value: str, bool, integer, float, list, dict

        :raises: TypeError
        """
        # Checking that the type of _value is the same as the expected _value
        if not isinstance(value, self.expected_type):
            message = (
                'The type of the value is [%s] but a [%s] is expected.' % (
                    str(type(value)), str(self.expected_type)))
            raise TypeError(message)

        if isinstance(value, dict):
            inspected_values = [value[key] for key in value.keys()]
        elif isinstance(value, list):
            inspected_values = value
        else:
            message = 'The value type is not a collection type'
            raise TypeError(message)

        self._check_sub_values(inspected_values)

    def _check_sub_values(self, values):
        for element in values:
            if isinstance(element, dict) or isinstance(element, list):
                self._check_sub_values(element)
            elif not isinstance(element, self.element_type):
                message = (
                    'The type of the element is [%s] but an [%s] is expected.'
                    % (str(type(element)), str(self.element_type)))
                raise TypeError(message)

    def check_length(self, value):
        """Check if the supplied container is within acceptable length limits.

        :raises: CollectionLengthError
        """

        if (self._maximum_item_count is None and
                self._minimum_item_count is None):
            return

        length = len(value)
        minimum = self.minimum_item_count
        maximum = self.maximum_item_count
        message = (
            '%i elements were found in the collection%s, there should be '
            'at least %i element(s) and no more than %i element(s).' %
            (
                length,
                '' if self.name is None else ' "' + self.name + '"',
                0 if minimum is None else minimum,
                999 if maximum is None else maximum
            ))
        # If maximum is not set, we can set minimum regardless
        if length > maximum:
            raise CollectionLengthError(message)
        # Also it must not be less than minimum
        if length < minimum:
            raise CollectionLengthError(message)

    @property
    def value(self):
        """Property for value of this parameter."""
        if self._value is None:
            self._value = []
        return self._value

    @value.setter
    def value(self, value):
        """Define the current value for the parameter.

        Need to check the type of each element.

        :param value: The collection of values set for this parameter.
        :type value: dict, list

        :raises: TypeError, CollectionLengthError
        """
        self.check_types(value)
        self.check_length(value)
        self._value = value

    def __len__(self):
        return self.value.__len__()

    def __getitem__(self, i):
        return self.value[i]

    def __setitem__(self, i, val):
        return self.value.__setitem__(i, val)
