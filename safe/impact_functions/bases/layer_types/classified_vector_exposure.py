# coding=utf-8
from safe.common.exceptions import NoAttributeInLayerError
from safe.impact_functions.bases.utilities import get_qgis_vector_layer, \
    check_attribute_exist

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '08/05/15'


class ClassifiedVectorExposureMixin(object):

    def __init__(self):
        self._exposure_class_attribute = None
        self._exposure_unique_values = None
        self._exposure_layer = None

    def set_up_exposure_layer(self, exposure):
        """Set up the hazard value.

        :param exposure: QgsVectorLayer or Vector data types
        :type exposure: QgsVectorLayer, Vector
        """
        self._exposure_layer = exposure

    @property
    def exposure_class_attribute(self):
        return self._exposure_class_attribute

    @exposure_class_attribute.setter
    def exposure_class_attribute(self, value):
        exposure_layer = self._exposure_layer.qgis_vector_layer()
        if (exposure_layer and
                check_attribute_exist(exposure_layer, value)):
            self._exposure_class_attribute = value
        else:
            message = ('The attribute "%s" does not exist in the exposure '
                       'layer.') % value
            raise NoAttributeInLayerError(message)

        # finding unique values in layer
        if exposure_layer:
            attr_index = exposure_layer.dataProvider().\
                fieldNameIndex(value)
            unique_list = list()
            for feature in exposure_layer.getFeatures():
                feature_value = feature.attributes()[attr_index]
                if feature_value not in unique_list:
                    unique_list.append(feature_value)

            self.exposure_unique_values = unique_list

    @property
    def exposure_unique_values(self):
        return self._exposure_unique_values

    @exposure_unique_values.setter
    def exposure_unique_values(self, value):
        self._exposure_unique_values = value
