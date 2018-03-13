# coding=utf-8
"""Group Select Parameter."""

from collections import OrderedDict

from parameters.generic_parameter import GenericParameter

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class GroupSelectParameter(GenericParameter):

    """Parameter that represent a select parameter with group option."""

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter.
            If none is specified one will be generated using python
            hash. This guid will be used when storing parameters in
            the registry.
        :type guid: str
        """
        super(GroupSelectParameter, self).__init__(guid)
        self.expected_type = OrderedDict

        # Store options, with label, type, and value
        # Example:
        # Options = {
        #     'do not report':
        #         {
        #             'label': 'Do not report',
        #             'value': None,
        #             'type': 'static',
        #             'constraint': {}
        #         },
        #     'global default':
        #         {
        #             'label': 'Global default',
        #             'value': 0.5,
        #             'type': 'static',
        #             'constraint': {}
        #         },
        #     'custom value':
        #         {
        #             'label': 'Custom',
        #             'value': 0.5,  # Taken from keywords / recent value
        #             'type': 'single dynamic',
        #             'constraint':
        #                 {
        #                     'min': 0,
        #                     'max': 1
        #                 }
        #         },
        #     'ratio fields':
        #         {
        #             'label': 'Ratio fields',
        #             'value': [],  # Taken from keywords
        #             'type': 'multiple dynamic',
        #             'constraint': {}
        #         }
        # }
        self._options = {}
        self._selected_key = None

    @property
    def options(self):
        """Property for options."""
        return self._options

    @options.setter
    def options(self, options):
        """Setter for options.

        :param options: The options values.
        :type options: dict
        """
        self._options = options

    @property
    def selected(self):
        """Property for selected."""
        return self._selected_key

    @selected.setter
    def selected(self, selected):
        """Setter selected.

        :param key: The key of the options to be selected.
        :type key: basestring
        """
        if selected in self.options:
            self._selected_key = selected

    @property
    def value(self):
        """Property for the parameter value.

        :returns: The parameter value.
        :rtype: dict
        """
        return self.options.get(self._selected_key, {}).get('value')

    def set_value_for_key(self, key, value):
        """Set the value of key to value.

        :param key: The key.
        :type key: str

        :param value: The value to be assigned.
        :type value: list, float, int
        """
        if key in self.options:
            self.options[key]['value'] = value

    def selected_option_type(self):
        """Helper to get the type of selected options."""
        if self.selected:
            return self.options[self.selected]['type']
