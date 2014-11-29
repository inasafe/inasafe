# coding=utf-8
"""Docstring for this file."""
__author__ = 'Christian Christelis'
__project_name = 'parameters'
__filename = 'resource_parameter'
__date__ = '11/11/14'
__copyright__ = 'kartoza.com'
__doc__ = ''

from float_parameter import FloatParameter
from unit import Unit


class ResourceParameter(FloatParameter):
    """A parameter handling specifically the resources used in InaSAFE
    minimum needs.

    :param guid: The unique reference to use when addressing this value.
    :type guid: str, None
    """
    def __init__(self, guid=None):
        super(ResourceParameter, self).__init__(guid)
        self._frequency = ''
        self._unit = Unit()

    @property
    def frequency(self):
        """The frequency that the resource needs to be supplied getter.

        :returns: The frequency.
        :rtype: str
        """
        return self._frequency

    @frequency.setter
    def frequency(self, frequency):
        """Set the frequency that the resource needs to be supplied.

        :param frequency: The frequency of the resource.
        :type frequency: str

        """
        self._frequency = frequency

    def serialize(self):
        """Convert the parameter into a dictionary.

        :return: The parameter dictionary.
        :rtype: dict
        """
        pickle = super(ResourceParameter, self).serialize()
        pickle['frequency'] = self.frequency
        pickle['unit'] = self._unit.serialize()
        return pickle

    @property
    def unit(self):
        """Property for the unit for the parameter.

        :returns: The unit of the parameter.
        :rtype: Unit

        """
        return self._unit

    @unit.setter
    def unit(self, unit):
        """Setter for unit for the parameter.

        :param unit: Unit for parameter
        :type unit: Unit

        """
        self._unit.name = unit
