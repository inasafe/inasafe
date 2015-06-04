# coding=utf-8
"""Dictionary Parameter."""
from collection_parameter import CollectionParameter


class DictParameter(CollectionParameter):
    """A subclass of parameter that allows the user to select from a dict.

    .. versionadded:: 2.2
    """

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter. If none
            is specified one will be generated using python hash. This guid
            will be used when storing parameters in the registry.
        :type guid: str
        """
        super(DictParameter, self).__init__(guid)
        self.expected_type = dict

    def __setitem__(self, key, value):
        """Helper method to make DictParameter behave like dict"""
        self._value[key] = value

    def __getitem__(self, key):
        """Helper method to make DictParameter behave like dict"""
        return self._value[key]

    def keys(self):
        """Helper method to make DictParameter behave like dict"""
        return self._value.keys()

    @property
    def value(self):
        """Property for value of this parameter."""
        return self._value

    @value.setter
    def value(self, value):
        """Define the current value for the parameter.

        Need to check the type of each element isdict.

        :param value: The collection of values set for this parameter.
        :type value: dict

        :raises: TypeError
        """
        self.check_types(value)
        self.check_length(value)
        self._value = value
