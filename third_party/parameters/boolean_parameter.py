# coding=utf-8
"""Boolean Parameter."""
from generic_parameter import GenericParameter


class BooleanParameter(GenericParameter):
    """A subclass of generic parameter that accepts boolean only.

    .. versionadded:: 2.2
    """

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter. If none
            is specified one will be generated using python hash. This guid
            will be used when storing parameters in the registry.
        :type guid: str
        """
        super(BooleanParameter, self).__init__(guid)
        self.expected_type = bool
