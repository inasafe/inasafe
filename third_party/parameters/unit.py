# coding=utf-8
"""Docstring for this file."""
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'unit'
__date__ = '8/25/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

import uuid


class Unit(object):
    """Class for representing unit."""
    def __init__(self, guid=None):
        """Constructor

        :param guid: Optional unique identifier for this unit. If none
            is specified one will be generated using python hash. This guid
            will be used when storing unit in the registry.
        :type guid: str, None

        """
        self.guid = None
        if guid is None:
            self._guid = uuid.uuid4()
        else:
            self._guid = guid
        self._name = None
        self._help_text = None
        self._description = None
        self._plural = None
        self._abbreviation = None

    @property
    def guid(self):
        """Unique identifier property for a unit.

        :returns: A globally unique identifier for the unit.
        :rtype: str
        """
        return self._guid

    @guid.setter
    def guid(self, guid):
        """Assign a unique identifier to the unit instance.

        :param guid: A globally unique identified (never translated).
        :type guid: str

        Perhaps it should set the guid itself?
        """
        self._guid = guid

    @property
    def name(self):
        """Name property for the unit.

        :returns: The name for this unit.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Set the name for the unit.

        :param name: The name for the units. This will be used in the UI,
            and can be translated)
        :type name: str
        """
        self._name = name

    @property
    def plural(self):
        """The plural name property of the unit.

        :returns: The plural name for this unit.
        :rtype: str
        """
        return self._plural

    @plural.setter
    def plural(self, plural):
        """Set the plural name for the unit.

        :param plural: The plural name for this unit.
        :type plural: str
        """
        self._plural = plural

    @property
    def abbreviation(self):
        """The abbreviated name property of the unit.

        :returns: The abbreviated name for this unit.
        :rtype: str
        """
        return self._abbreviation

    @abbreviation.setter
    def abbreviation(self, abbreviation):
        """Set the abbreviated name for the unit.

        :param abbreviation: The abbreviated name for this unit.
        :type abbreviation: str
        """
        self._abbreviation = abbreviation

    @property
    def help_text(self):
        """Property containing help text for the parameter.

        It will be used as tooltip in the UI..

        :returns: A short help sentence for the parameter.
        :rtype: str
        """
        return self._help_text

    @help_text.setter
    def help_text(self, help_text):
        """Define the help help_text for this parameter.

        :param help_text: A short (i.e. one line) explanation of the parameter.
        :type help_text: str
        """
        self._help_text = help_text

    @property
    def description(self):
        """Property for the description of the unit.

        :returns: A detailed description for the unit.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Define the description for this unit.

        :param description: A detailed description of the unit
        :type description: str
        """
        self._description = description

    def load_dictionary(self, unit_dictionary):
        """Load from unit dictionary to initialize unit object

        :param unit_dictionary: Unit dictionary, the same in the metadata.py
        :type unit_dictionary: dict

        """
        name = unit_dictionary.get('name', '')
        help_text = unit_dictionary.get('help_text', '')
        description = unit_dictionary.get('description', '')

        if name:
            self.name = name
        if help_text:
            self.help_text = help_text
        if description:
            self.description = description

    def serialize(self):
        """Serialize the unit.

        :returns: The unit content in a dict format
        :rtype: dict
        """
        return {
            'name': self.name,
            'plural': self.plural,
            'abbreviation': self.abbreviation
        }

    def __str__(self):
        return self.name
