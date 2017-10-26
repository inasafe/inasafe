# coding=utf-8
"""Default Select Parameter."""

from parameters.select_parameter import SelectParameter

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class DefaultSelectParameter(SelectParameter):
    """Parameter that represent a select parameter with default."""

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter.
            If none is specified one will be generated using python
            hash. This guid will be used when storing parameters in
            the registry.
        :type guid: str
        """

        super(DefaultSelectParameter, self).__init__(guid)
        self.expected_type = object
        self.element_type = object

        # Store option for default labels
        self._default_labels = None
        # Store option for default values
        self._default_values = None
        # Store selected default value
        self._default_value = None
        # Minimum and maximum for custom value
        self._min_value = None
        self._max_value = None

    @property
    def default_labels(self):
        """Property for default_labels"""
        return self._default_labels

    @default_labels.setter
    def default_labels(self, default_labels):
        """Setter for default_labels.

        :param default_labels: The default_labels values.
        :type default_labels: list
        """
        self._default_labels = default_labels

    @property
    def default_values(self):
        """Property for default_values"""
        return self._default_values

    @default_values.setter
    def default_values(self, default_values):
        """Setter for default_values.

        :param default_values: The default values.
        :type default_values: list
        """
        self._default_values = default_values

    @property
    def minimum(self):
        """Property for minimum value."""
        return self._min_value

    @minimum.setter
    def minimum(self, minimum):
        """Setter for minimum value.

        :param minimum: The minimum value.
        :type minimum: int or float
        """
        self._min_value = minimum

    @property
    def maximum(self):
        """Property for maximum value."""
        return self._max_value

    @maximum.setter
    def maximum(self, maximum):
        """Setter for maximum value.

        :param maximum: The maximum value.
        :type maximum: int or float
        """
        self._max_value = maximum

    @property
    def default_value(self):
        """Property for default_value"""
        return self._default_value

    @default_value.setter
    def default_value(self, default_value):
        """Setter for default_value.

        :param default_value: The default value.
        :type default_value: object
        """
        # For custom value
        if default_value not in self.default_values:
            if len(self.default_labels) == len(self.default_values):
                self.default_values[-1] = default_value
            else:
                self.default_values.append(default_value)

        self._default_value = default_value
