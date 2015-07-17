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

from qgis.networkanalysis import QgsArcProperter


class MultiplyProperty(QgsArcProperter):
    """Strategy for the cost using a coefficient."""

    def __init__(self, attribute_id):
        """Constructor MultiplyProperter."""
        QgsArcProperter.__init__(self)
        self.attribute_id = attribute_id

    def property(self, distance, feature):
        """Compute the cost for a feature.

        :param distance: Distance of the feature.
        :type distance: int

        :param feature: Current feature.
        :type feature: QgsFeature

        :return Cost.
        :rtype float
        """
        attributes = feature.attributes()
        return distance * float(attributes[self.attribute_id])

    def requiredAttributes(self):
        return [self.attribute_id]
