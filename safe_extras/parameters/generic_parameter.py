# coding=utf-8
"""Generic Parameter."""
import uuid


class GenericParameter(object):
    """A generic base class for all parameters."""

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter. If none
            is specified one will be generated using python hash. This guid
            will be used when storing parameters in the registry.
        :type guid: str, None
        """
        self.guid = None
        if guid is None:
            self._guid = uuid.uuid4()
        else:
            self._guid = guid
        self._name = None
        self._expected_type = None
        self._required = None
        self._help_text = None
        self._description = None
        self._value = None
        # Defaults to _required
        self._is_required = True

    @property
    def guid(self):
        """Unique identifier property for a parameter.

        :returns: A globally unique identifier for the parameter.
        :rtype: str
        """
        return self._guid

    @guid.setter
    def guid(self, guid):
        """Assign a unique identifier to the parameter instance.

        :param guid: A globally unique identified (never translated).
        :type guid: str

        Perhaps it should set the _guid itself?
        """
        self._guid = guid

    @property
    def name(self):
        """Name property for the parameter.

        :returns: The name for this parameter.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Set the name for the parameter.

        :param name: The _name for the parameters. This will be used in the UI,
            and can be translated)
        :type name: str
        """
        self._name = name

    @property
    def expected_type(self):
        """Property for the expected type for this parameter.

        :returns: The expected type for this parameter.
        :rtype: str
        """
        return self._expected_type

    @expected_type.setter
    def expected_type(self, expected_type):
        """Define what type of input is _required.

        :param expected_type: ?????
        :type expected_type: ????

        """
        # TODO some validation here...
        # I think validation should be in set_value
        self._expected_type = expected_type

    @property
    def is_required(self):
        """Property indicating whether the parameter is required.

        :returns: bool
        """
        return self._is_required

    @is_required.setter
    def is_required(self, required):
        """Define if this is a required parameter or not.

        :param required: A _required to indicate if a parameter is _required.
        :type required: bool
        """
        self._is_required = required

    @property
    def help_text(self):
        """Property containing help text for the parameter.

        :returns: A short help sentence for the parameter.
        :rtype: str
        """
        return self._help_text

    @help_text.setter
    def help_text(self, help_text):
        """Define the help _help_text for this parameter.

        :param help_text: A short (i.e. one line) explanation of the parameter.
        :type help_text: str
        """
        self._help_text = help_text

    @property
    def description(self):
        """Property for the description of the parameter.

        :returns: A detailed description for the parameter.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Define the _description for this parameter.

        :param description: A detailed _description of the parameter
        :type description: str
        """
        self._description = description

    def _check_type(self, value):
        # Checking that the type of _value is the same as the expected _value
        # or same as one type in list of type
        message = (
            'The type of the _value [%s] does match with the expected '
            'type of the parameter [%s].' % (
                str(type(value)), str(self._expected_type)))

        if (type(self._expected_type) is type and type(value) is not
                self._expected_type):
            raise TypeError(message)
        if (type(self._expected_type) is list and type(value) not in
                self._expected_type):
            raise TypeError(message)

    @property
    def value(self):
        """Property for the parameter value.

        :returns: The parameter value. The return type depends on the
            subclass of GenericParameter.
        """
        return self._value

    @value.setter
    def value(self, value):
        """Define the current _value for the parameter.

        .. note:: Subclasses may want to overload this function to do parameter
            type specific checks.

        :param value: The _value of the parameter itself.
        :type value: str, bool, integer, float, list, dict

        :raises: TypeError
        """
        # self._check_type(value)
        self._value = value

    def serialize(self):
        """Convert the parameter into a dictionary.

        :return: The parameter dictionary.
        :rtype: dict
        """
        # noinspection PyDictCreation
        pickle = {}
        pickle['guid'] = '%s' % self.guid
        pickle['name'] = self.name
        if type(self.expected_type) == list:
            pickle['expected_type'] = ['%s' % t for t in self.expected_type]
        else:
            pickle['expected_type'] = '%s' % self.expected_type
        pickle['is_required'] = self.is_required
        pickle['help_text'] = self.help_text
        pickle['description'] = self.description
        pickle['value'] = self.value
        return pickle
