# coding=utf-8
from builtins import object
from safe.common.exceptions import NoAttributeInLayerError
from safe.impact_functions.bases.utilities import check_attribute_exist

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/05/15'


class ClassifiedVectorHazardMixin(object):

    def __init__(self):
        self._hazard_class_attribute = None
        self._hazard_class_mapping = None

    @property
    def hazard_class_attribute(self):
        return self._hazard_class_attribute

    @hazard_class_attribute.setter
    def hazard_class_attribute(self, value):
        # self.hazard is from IF base class.
        hazard_layer = self.hazard.qgis_vector_layer()
        if hazard_layer and check_attribute_exist(hazard_layer, value):
            self._hazard_class_attribute = value
        else:
            message = ('The attribute "%s" does not exist in the hazard '
                       'layer.') % value
            raise NoAttributeInLayerError(message)

    @property
    def hazard_class_mapping(self):
        return self._hazard_class_mapping

    @hazard_class_mapping.setter
    def hazard_class_mapping(self, value):
        self._hazard_class_mapping = value
