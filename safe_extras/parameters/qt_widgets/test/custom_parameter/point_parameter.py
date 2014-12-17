# coding=utf-8
"""Docstring for this file."""
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'point_parameter'
__date__ = '12/15/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''


from generic_parameter import GenericParameter


class PointParameter(GenericParameter):
    """Parameter that represent a point."""

    def __init__(self, guid=None):
        """Constructor.

        :param guid: Optional unique identifier for this parameter.
            If none is specified one will be generated using python
            hash. This guid will be used when storing parameters in
            the registry.
        :type guid: str
        """
        super(PointParameter, self).__init__(guid)
        self.expected_type = tuple
