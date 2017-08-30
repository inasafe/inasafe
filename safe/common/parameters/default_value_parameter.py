# coding=utf-8
"""Default Value Parameter."""

from parameters.generic_parameter import GenericParameter

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class DefaultValueParameter(GenericParameter):

    """Parameter that represent a selection of default value."""

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter.
            If none is specified one will be generated using python
            hash. This guid will be used when storing parameters in
            the registry.
        :type guid: str
        """

        super(DefaultValueParameter, self).__init__(guid)
        self.expected_type = object
        self.element_type = object

        # Store for labels
        self._labels = None
        # Store option
        self._options = None

    @property
    def labels(self):
        """Property for labels."""
        return self._labels

    @labels.setter
    def labels(self, labels):
        """Setter for labels.

        :param labels: The labels values.
        :type labels: list
        """
        self._labels = labels

    @property
    def options(self):
        """Property for options."""
        return self._options

    @options.setter
    def options(self, options):
        """Setter for default_values.

        :param options: The Options.
        :type options: list
        """
        self._options = options

    @property
    def value(self):
        """Property for default_value."""
        return self._value

    @value.setter
    def value(self, value):
        """Setter for value.

        :param value: The value.
        :type value: object
        """
        # For custom value
        if value not in self.options:
            if len(self.labels) == len(self.options):
                self.options[-1] = value
            else:
                self.options.append(value)

        self._value = value
