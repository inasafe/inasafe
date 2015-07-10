# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid / DFAT -
**New Metadata for SAFE.**

Contact : etienne@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

from PyQt4.QtGui import QIcon
from processing.core.AlgorithmProvider import AlgorithmProvider

from safe.utilities.resources import resources_path
from safe.inasafe_processing.routing.allocate_exits import AllocateExits
from safe.inasafe_processing.routing.allocate_edges import AllocateEdges
from safe.inasafe_processing.geometry_tools.snap_points_project import \
    SnapPointsProject
from safe.inasafe_processing.geometry_tools.snap_points import SnapPoints
from safe.inasafe_processing.geometry_tools.split_poly_to_lines_points import \
    SplitPolygonsToLinesWithPoints
from safe.inasafe_processing.data_management.remove_features import \
    CleaningLayer


class InaSafeProvider(AlgorithmProvider):
    """InaSAFE provides some algorithms through Processing."""

    def __init__(self):
        """Constructor."""
        AlgorithmProvider.__init__(self)

        self.activate = True

        self.alglist = [
            AllocateExits(),
            AllocateEdges(),
            SnapPointsProject(),
            SplitPolygonsToLinesWithPoints(),
            SnapPoints(),
            CleaningLayer(),
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
