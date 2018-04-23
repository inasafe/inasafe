# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**metadata module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
import json
from datetime import datetime, date

from qgis.PyQt.QtCore import QDate, Qt, QDateTime, QUrl

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
