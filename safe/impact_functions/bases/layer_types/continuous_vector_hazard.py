# coding=utf-8
from safe.common.exceptions import NoAttributeInLayerError
from safe.impact_functions.bases.utilities import get_qgis_vector_layer, \
    check_attribute_exist

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/05/15'


class ContinuousVectorHazardMixin(object):

    def __init__(self):
        self._hazard_value_attribute = None
        self._hazard_threshold = None
        self._hazard_layer = None

    def set_up_hazard_layer(self, hazard):
        """Set up the hazard value.
        
        :param hazard: QgsVectorLayer or Vector data types
        :type hazard: QgsVectorLayer, Vector
        """
        self._hazard_layer = hazard

    @property
    def hazard_value_attribute(self):
        return self._hazard_value_attribute

    @hazard_value_attribute.setter
    def hazard_value_attribute(self, value):
        hazard_layer = get_qgis_vector_layer(self._hazard_layer)
        if hazard_layer and check_attribute_exist(self._hazard_layer, value):
            self._hazard_value_attribute = value
        else:
            message = ('The attribute "%s" is not exists in the hazard '
                       'layer.') % value
            raise NoAttributeInLayerError(message)

    @property
    def hazard_threshold(self):
        return self._hazard_threshold

    @hazard_threshold.setter
    def hazard_threshold(self, value):
        self._hazard_threshold = value
