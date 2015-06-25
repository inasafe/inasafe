# -*- coding: utf-8 -*-

from qgis.networkanalysis import QgsArcProperter


class MultiplyProperty(QgsArcProperter):
    """Strategy for the cost using a coefficient."""

    def __init__(self, attribute_id):
        """Constructor."""
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
