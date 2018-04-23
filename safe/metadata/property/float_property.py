# -*- coding: utf-8 -*-

"""Float property."""


NoneType = type(None)

from safe.common.exceptions import MetadataCastError
from safe.metadata.property import BaseProperty

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class FloatProperty(BaseProperty):

    """A property that accepts float input."""

    # if you edit this you need to adapt accordingly xml_value and is_valid
    _allowed_python_types = [float, NoneType]

    def __init__(self, name, value, xml_path):
        super(FloatProperty, self).__init__(
            name, value, xml_path, self._allowed_python_types)

    @classmethod
    def is_valid(cls, value):
        return True

    def cast_from_str(self, value):
        try:
            return float(value)
        except ValueError as e:
            raise MetadataCastError(e)

    @property
    def xml_value(self):
        if self.python_type is float:
            return str(self.value)
        elif self.python_type is NoneType:
            return ''
        else:
            raise RuntimeError('self._allowed_python_types and self.xml_value'
                               'are out of sync. This should never happen')
