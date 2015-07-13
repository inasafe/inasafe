# coding=utf-8
"""List Parameter."""

from collection_parameter import CollectionParameter
from generic_parameter import GenericParameter


class GroupParameter(CollectionParameter):
    """A subclass of parameter that allows the user to select from a list.

    .. versionadded:: 2.2
    """

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter. If none
            is specified one will be generated using python hash. This guid
            will be used when storing parameters in the registry.
        :type guid: str
        """
        super(GroupParameter, self).__init__(guid)
        self.expected_type = list
        self.element_type = GenericParameter
        self.is_required = False
        self._enable_parameter = True
        self._custom_validator = None
        self._must_scroll = True

    @property
    def enable_parameter(self):
        return self._enable_parameter

    @enable_parameter.setter
    def enable_parameter(self, value):
        self._enable_parameter = value

    @property
    def must_scroll(self):
        return self._must_scroll

    @must_scroll.setter
    def must_scroll(self, value):
        self._must_scroll = value

    @property
    def custom_validator(self):
        return self._custom_validator

    @custom_validator.setter
    def custom_validator(self, value):
        """
        :param value: function object with one argument for the parameter
        :type value: (list[Parameter]) -> None
        """
        self._custom_validator = value

    def validate(self):
        if self.custom_validator:
            self.custom_validator(self.value)
