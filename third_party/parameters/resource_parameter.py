# coding=utf-8
from float_parameter import FloatParameter


class ResourceParameter(FloatParameter):
    """A parameter handling specifically the resources used in InaSAFE
    minimum needs.

    :param guid: The unique reference to use when addressing this value.
    :type guid: str, None
    """
    def __init__(self, guid=None):
        super(ResourceParameter, self).__init__(guid)
        self._frequency = ''

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
        return pickle
