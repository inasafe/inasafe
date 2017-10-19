# -*- coding: utf-8 -*-

"""Integer property."""

from types import NoneType

from safe.common.exceptions import MetadataCastError
from safe.metadata.property import BaseProperty

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class IntegerProperty(BaseProperty):

    """A property that accepts integer input."""

    # if you edit this you need to adapt accordingly xml_value and is_valid
    _allowed_python_types = [int, NoneType]

    def __init__(self, name, value, xml_path):
        super(IntegerProperty, self).__init__(
            name, value, xml_path, self._allowed_python_types)

    @classmethod
    def is_valid(cls, value):
        return True

    def cast_from_str(self, value):
        try:
            return int(value)
        except ValueError as e:
            raise MetadataCastError(e)

    @property
    def xml_value(self):
        if self.python_type is int:
            return str(self.value)
        elif self.python_type is NoneType:
            return ''
        else:
            raise RuntimeError('self._allowed_python_types and self.xml_value'
                               'are out of sync. This should never happen')
