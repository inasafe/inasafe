# coding=utf-8
"""Tools for metadata encoding."""

import json
from datetime import datetime, date

from PyQt4.QtCore import QDate, Qt, QDateTime, QUrl

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class MetadataEncoder(json.JSONEncoder):

    """Metadata Encoder."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.date().isoformat()
        elif isinstance(obj, QDate):
            return obj.toString(Qt.ISODate)
        elif isinstance(obj, QDateTime):
            return obj.toString(Qt.ISODate)
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, QUrl):
            return obj.toString()

        return json.JSONEncoder.default(self, obj)
