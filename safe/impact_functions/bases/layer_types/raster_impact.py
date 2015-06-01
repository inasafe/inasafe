# coding=utf-8
__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '28/05/15'


class RasterImpactMixin(object):

    def __init__(self):
        self._impact_attribute = None
        self._impact_layer = None

    def set_up_impact_layer(self, impact):
        """Set up the hazard value.

        :param impact: QgsVectorLayer or Vector data types
        :type impact: QgsVectorLayer, Vector
        """
        self._impact_layer = impact

    @property
    def impact_attribute(self):
        return self._impact_attribute

    @impact_attribute.setter
    def impact_attribute(self, value):
        self._impact_attribute = value
