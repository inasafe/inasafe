# coding=utf-8

"""Dictionary property."""

import json
from datetime import datetime
from types import NoneType

from safe.common.exceptions import MetadataCastError
from safe.metadata.property import BaseProperty
from safe.metadata.utilities import serialize_dictionary

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class DictionaryProperty(BaseProperty):

    """A property that accepts dictionary input."""

    # if you edit this you need to adapt accordingly xml_value and is_valid
    _allowed_python_types = [dict, NoneType]

    def __init__(self, name, value, xml_path):
        super(DictionaryProperty, self).__init__(
            name, value, xml_path, self._allowed_python_types)

    @classmethod
    def is_valid(cls, value):
        return True

    def cast_from_str(self, value):
        try:
            value = json.loads(value)
            # Checking if the v is basestring, try to decode if it's json
            for k, v in list(value.items()):
                if isinstance(v, str):
                    try:
                        # Try to get dictionary, if possible.
                        dictionary_value = json.loads(v)
                        if isinstance(dictionary_value, dict):
                            value[k] = dictionary_value
                        else:
                            pass
                    except ValueError:
                        # Try to get time, if possible.
                        try:
                            value[k] = datetime.strptime(
                                v, "%Y-%m-%dT%H:%M:%S.%f")
                        except ValueError:
                            pass
            return value
        except ValueError as e:
            raise MetadataCastError(e)

    @property
    def xml_value(self):
        if self.python_type is dict:
            try:
                return json.dumps(self.value)
            except (TypeError, ValueError):
                string_value = serialize_dictionary(self.value)
                return json.dumps(string_value)

        elif self.python_type is NoneType:
            return ''
        else:
            raise RuntimeError(
                'self._allowed_python_types and self.xml_value are out of '
                'sync. This should never happen')
