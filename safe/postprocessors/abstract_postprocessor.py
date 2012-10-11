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

from PyQt4.QtCore import QCoreApplication

from safe_qgis.exceptions import PostprocessorError


class AbstractPostprocessor():
    def __init__(self):
        self.results = None

    def setup(self):
        if self.results is not None:
            self.raiseError('clear needs to be called before setup')
        self.results = {}

    def process(self):
        if self.results is None:
            self.raiseError('setup needs to be called before process')

    def getResults(self):
        return self.results

    def clear(self):
        self.results = None

    def raiseError(self, theMessage=None):
        if theMessage is None:
            theMessage = 'Postprocessor error'
        raise PostprocessorError(theMessage)

    def _appendResult(self, theName, theResult, theMetadata={}):
        self.results[theName] = {'value': theResult,
                                 'metadata': theMetadata}

    def tr(self, theString):
        """We implement this ourself since we do not inherit QObject.

        Args:
           theString - string for translation.
        Returns:
           Translated version of theString.
        Raises:
           no exceptions explicitly raised.
        """
        return QCoreApplication.translate('Plugin', theString)
