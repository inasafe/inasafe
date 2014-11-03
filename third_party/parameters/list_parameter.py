"""List Parameter."""

from collection_parameter import CollectionParameter


class ListParameter(CollectionParameter):
    """A subclass of paramter that allows the user to select from a list.

    .. versionadded:: 2.2
    """

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter. If none
            is specified one will be generated using python hash. This guid
            will be used when storing parameters in the registry.
        :type guid: str
        """
        super(ListParameter, self).__init__(guid)
        self.expected_type = list

