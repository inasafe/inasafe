# coding=utf-8
from safe.common.exceptions import NoAttributeInLayerError
from safe.impact_functions.bases.utilities import get_qgis_vector_layer, \
    check_attribute_exist

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '08/05/15'


class ClassifiedVectorExposureMixin(object):

    def __init__(self):
        self._exposure_class_attribute = None
        self._exposure_layer = None

    def set_up_exposure_layer(self, exposure):
        """Set up the hazard value
        :param exposure: QgsVectorLayer or Vector data types
        :type exposure: QgsVectorLayer, Vector
        """
        self._exposure_layer = exposure

    @property
    def exposure_class_attribute(self):
        return self._exposure_class_attribute

    @exposure_class_attribute.setter
    def exposure_class_attribute(self, value):
        exposure_layer = get_qgis_vector_layer(self._exposure_layer)
        if (exposure_layer and
                check_attribute_exist(self._exposure_layer, value)):
            self._exposure_class_attribute = value
        else:
            message = ('The attribute "%s" is not exists in the exposure '
                       'layer.') % value
            raise NoAttributeInLayerError(message)
