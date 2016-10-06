# coding=utf-8
"""Select Parameter."""

from collection_parameter import CollectionParameter
from parameter_exceptions import ValueNotAllowedException

__author__ = 'ismailsunni'
__project_name__ = 'parameters'
__filename__ = 'select_parameter'
__date__ = '05/10/2016'
__copyright__ = 'imajimatika@gmail.com'


class SelectParameter(CollectionParameter):
    """A subclass of parameter that allows the user to select from a list.

    """

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter. If none
            is specified one will be generated using python hash. This guid
            will be used when storing parameters in the registry.
        :type guid: str
        """
        super(SelectParameter, self).__init__(guid)
        self.expected_type = object
        self._options_list = None
        self._is_editable = False

        self._minimum_item_count = 1
        self._maximum_item_count = 1

    @property
    def is_editable(self):
        """Flag to determine that the list items is editable"""
        return self._is_editable

    @is_editable.setter
    def is_editable(self, value):
        self._is_editable = value

    @property
    def options_list(self):
        """Stores the list of options the value can take"""
        return self._options_list

    @options_list.setter
    def options_list(self, value):
        # the options type must be the same as the value type
        self.check_types(value)
        self._options_list = value

    @property
    def value(self):
        if self._value is None:
            self._value = None
        return self._value

    @value.setter
    def value(self, value):
        """Define the current value for the parameter.

        Need to check the type of each element.

        :param value: The collection of values set for this parameter.
        :type value: dict, list

        :raises: TypeError, CollectionLengthError
        """
        # self.check_types(value)
        # self.check_length(value)
        self.check_value_in_options(value)
        self._value = value

    def check_value_in_options(self, value):
        """Check items of value assigned is a subset of options_list

        :param value: The collection of values checked
        :type value: object

        :raise: ValueNotAllowedException
        """
        message = 'The value %s doesn\'t exists on the allowed options list.'
        if value not in self.options_list:
            message = message % value
            raise ValueNotAllowedException(message)
