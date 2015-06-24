# -*- coding: utf-8 -*-
from processing.core.AlgorithmProvider import AlgorithmProvider
from PyQt4.QtGui import QIcon

from safe.utilities.resources import resources_path


class InaSafeProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)

        self.activate = True

        self.alglist = [
        ]

        for alg in self.alglist:
            alg.provider = self

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)

    def unload(self):
        AlgorithmProvider.unload(self)

    def getName(self):
        return 'InaSAFE'

    def getDescription(self):
        return 'InaSAFE'

    def getIcon(self):
        icon = resources_path('img', 'icons', 'icon.svg')
        return QIcon(icon)

    def _loadAlgorithms(self):
        self.algs = self.alglist

    def getSupportedOutputTableExtensions(self):
        return ['csv']
