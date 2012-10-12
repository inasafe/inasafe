"""
InaSAFE Disaster risk assessment tool developed by AusAid - **GUI Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from safe.common.utilities import ugettext as tr # pylint: disable=W0611

from safe.common.exceptions import PostprocessorError


class AbstractPostprocessor():
    def __init__(self):
        self._results = None

    def setup(self):
        if self._results is not None:
            self.raise_error('clear needs to be called before setup')
        self._results = {}

    def process(self):
        if self._results is None:
            self.raise_error('setup needs to be called before process')

    def results(self):
        return self._results

    def clear(self):
        self._results = None

    def raise_error(self, message=None):
        if message is None:
            message = 'Postprocessor error'
        raise PostprocessorError(message)

    def _append_result(self, name, result, metadata=None):
        if metadata is None:
            metadata = dict()
        self._results[name] = {'value': result,
                                 'metadata': metadata}

