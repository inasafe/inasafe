__author__ = 'christian'

from PyQt4.QtCore import QSettings
from safe.common.minimum_needs import MinimumNeeds


class QMinimumNeeds(MinimumNeeds):
    def __init__(self):
        self.settings = QSettings()
        self.load()

    def load(self):
        minimum_needs = self.settings.value('minimum_needs')
        if minimum_needs is None:
            minimum_needs = self._defaults()
        self.minimum_needs = minimum_needs

    def save(self):
        self.settings.setValue('minimum_needs', self.minimum_needs)

