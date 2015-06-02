# coding=utf-8
import sys

from safe.common.exceptions import NoAttributeInLayerError
from safe.impact_functions.bases.utilities import get_qgis_vector_layer, \
    check_attribute_exist

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '08/05/15'


class ContinuousVectorExposureMixin(object):

    def __init__(self):
        self._exposure_value_attribute = None
        self._exposure_min_value = None
        self._exposure_max_value = None
        self._exposure_layer = None

    def set_up_exposure_layer(self, exposure):
        """Set up the hazard value.

        :param exposure: QgsVectorLayer or Vector data types
        :type exposure: QgsVectorLayer, Vector
        """
        self._exposure_layer = exposure

    @property
    def exposure_value_attribute(self):
        return self._exposure_value_attribute

    @exposure_value_attribute.setter
    def exposure_value_attribute(self, value):
        exposure_layer = get_qgis_vector_layer(self._exposure_layer)
        if (exposure_layer and
                check_attribute_exist(exposure_layer, value)):
            self._exposure_value_attribute = value
        else:
            message = ('The attribute "%s" does not exist in the hazard '
                       'layer.') % value
            raise NoAttributeInLayerError(message)

        # finding minima and maxima in a layer
        if exposure_layer:
            attr_index = exposure_layer.dataProvider().\
                fieldNameIndex(value)
            min_val = sys.maxint
            max_val = -sys.maxint - 1
            for feature in exposure_layer.getFeatures():
                try:
                    feature_value = feature.attributes()[attr_index]
                    feature_value = float(feature_value)
                    if feature_value < min_val:
                        min_val = feature_value
                    if feature_value > max_val:
                        max_val = feature_value
                except (ValueError, TypeError):
                    pass

            self.exposure_min_value = min_val
            self.exposure_max_value = max_val

    @property
    def exposure_min_value(self):
        return self._exposure_min_value

    @exposure_min_value.setter
    def exposure_min_value(self, value):
        self._exposure_min_value = value

    @property
    def exposure_max_value(self):
        return self._exposure_max_value

    @exposure_max_value.setter
    def exposure_max_value(self, value):
        self._exposure_max_value = value
