# -*- coding: utf-8 -*-

"""Tools for metadata encoding."""

import json
from datetime import datetime, date

from PyQt4.QtCore import QDate, Qt, QDateTime, QUrl

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'encoder.py'
__date__ = '2/18/16'
__copyright__ = 'imajimatika@gmail.com'


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
