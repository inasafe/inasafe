# coding=utf-8
"""String Parameter."""

from generic_parameter import GenericParameter


class StringParameter(GenericParameter):
    """A subclass of generic parameter that accepts string only.

    .. versionadded:: 2.2
    """

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter. If none
            is specified one will be generated using python hash. This guid
            will be used when storing parameters in the registry.
        :type guid: str, None
        """
        super(StringParameter, self).__init__(guid)
        self.expected_type = [str, unicode]
