# coding=utf-8
"""List Parameter."""

from collection_parameter import CollectionParameter


class InputListParameter(CollectionParameter):
    """A subclass of parameter that allows the user to select from a list.

    .. versionadded:: 2.2
    """

    NotOrdered = 'NotOrdered'
    AscendingOrder = 'Ascending'
    DescendingOrder = 'Descending'

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter. If none
            is specified one will be generated using python hash. This guid
            will be used when storing parameters in the registry.
        :type guid: str
        """
        super(InputListParameter, self).__init__(guid)
        self.expected_type = list
        self._ordering = InputListParameter.NotOrdered

    @property
    def ordering(self):
        return self._ordering

    @ordering.setter
    def ordering(self, value):
        self._ordering = value

    @property
    def value(self):
        if self._value is None:
            self._value = []
        return self._value

    @value.setter
    def value(self, value):
        self.check_types(value)
        self.check_length(value)
        self._value = value
