# coding=utf-8
from safe.common.exceptions import NoAttributeInLayerError
from safe.impact_functions.bases.utilities import get_qgis_vector_layer, \
    check_attribute_exist

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/05/15'


class ClassifiedVectorHazardMixin(object):

    def __init__(self):
        self._hazard_class_attribute = None
        self._hazard_class_mapping = None
        self._hazard_layer = None

    def set_up_hazard_layer(self, hazard):
        """Set up the hazard value.

        :param hazard: QgsVectorLayer or Vector data types
        :type hazard: QgsVectorLayer, Vector
        """
        self._hazard_layer = hazard

    @property
    def hazard_class_attribute(self):
        return self._hazard_class_attribute

    @hazard_class_attribute.setter
    def hazard_class_attribute(self, value):
        hazard_layer = get_qgis_vector_layer(self._hazard_layer)
        if hazard_layer and check_attribute_exist(self._hazard_layer, value):
            self._hazard_class_attribute = value
        else:
            message = ('The attribute "%s" is not exists in the hazard '
                       'layer.') % value
            raise NoAttributeInLayerError(message)

    @property
    def hazard_class_mapping(self):
        return self._hazard_class_mapping

    @hazard_class_mapping.setter
    def hazard_class_mapping(self, value):
        self._hazard_class_mapping = value
