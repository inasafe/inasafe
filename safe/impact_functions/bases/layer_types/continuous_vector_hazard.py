# coding=utf-8
from builtins import object
from safe.common.exceptions import NoAttributeInLayerError
from safe.impact_functions.bases.utilities import check_attribute_exist

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/05/15'


class ContinuousVectorHazardMixin(object):

    def __init__(self):
        self._hazard_value_attribute = None
        self._hazard_threshold = None

    @property
    def hazard_value_attribute(self):
        return self._hazard_value_attribute

    @hazard_value_attribute.setter
    def hazard_value_attribute(self, value):
        # self.hazard is from IF base class.
        hazard_layer = self.hazard.qgis_vector_layer()
        if hazard_layer and check_attribute_exist(hazard_layer, value):
            self._hazard_value_attribute = value
        else:
            message = ('The attribute "%s" does not exist in the hazard '
                       'layer.') % value
            raise NoAttributeInLayerError(message)

    @property
    def hazard_threshold(self):
        return self._hazard_threshold

    @hazard_threshold.setter
    def hazard_threshold(self, value):
        self._hazard_threshold = value
