# coding=utf-8
"""This is the concrete Minimum Needs class that contains the logic to load
the minimum needs to and from the QSettings"""
__author__ = 'christian'

from PyQt4.QtCore import QSettings
from safe.common.minimum_needs import MinimumNeeds


class QMinimumNeeds(MinimumNeeds):
    """The concrete MinimumNeeds class to be used in a QGis environment.

    In the case where we assume QGis we use the QSettings object to store the
    minimum needs.
    """

    def __init__(self):
        self.settings = QSettings()
        self.load()

    def load(self):
        """Load the minimum needs from the QSettings object.
        """
        minimum_needs = self.settings.value('minimum_needs')
        if minimum_needs is None:
            minimum_needs = self._defaults()
        self.minimum_needs = minimum_needs

    def save(self):
        """Save teh minimum needs to the QSettings object.
        """
        self.settings.setValue('minimum_needs', self.minimum_needs)

