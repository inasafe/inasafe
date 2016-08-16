__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'impact_function'
__date__ = '8/16/16'
__copyright__ = 'imajimatika@gmail.com'

from qgis.core import QgsMapLayer

from safe.utilities.i18n import tr
from safe.common.utilities import get_non_conflicting_attribute_name
from safe.storage.safe_layer import SafeLayer

from safe.new_impact_function.algorithm.line import LineAlgorithm
from safe.new_impact_function.algorithm.point import PointAlgorithm
from safe.new_impact_function.algorithm.polygon import PolygonAlgorithm
from safe.new_impact_function.algorithm.raster import RasterAlgorithm
from safe.new_impact_function.algorithm.indivisible_polygon import (
    IndivisiblePolygonAlgorithm
)


class ImpactFunction(object):
    """Impact Function."""

    def __init__(self):
        self._hazard = None
        self._exposure = None
        self._aggregation = None
        self._extent = None

        self.algorithm = None
        self.impact_layer = None
        self._target_field = 'affected'

    @property
    def hazard(self):
        """Property for the hazard layer to be used for the analysis.

        :returns: A map layer.
        :rtype: SafeLayer
        """
        return self._hazard

    @hazard.setter
    def hazard(self, layer):
        """Setter for hazard layer property.

        :param layer: Hazard layer to be used for the analysis.
        :type layer: SafeLayer, QgsMapLayer
        """
        if isinstance(layer, SafeLayer):
            self._hazard = layer
        elif isinstance(layer, QgsMapLayer):
            self._hazard = SafeLayer(layer)
        else:
            message = tr('Layer should be SafeLayer or QgsMapLayer')
            raise Exception(message)

        # Update the target field to a non-conflicting one
        if self._hazard.is_qgsvectorlayer():
            self.target_field = get_non_conflicting_attribute_name(
                self.target_field,
                self._hazard.layer.dataProvider().fieldNameMap().keys()
            )
        self.set_algorithm()

    @property
    def exposure(self):
        """Property for the exposure layer to be used for the analysis.

        :returns: A map layer.
        :rtype: SafeLayer
        """
        return self._exposure

    @exposure.setter
    def exposure(self, layer):
        """Setter for exposure layer property.

        :param layer: exposure layer to be used for the analysis.
        :type layer: SafeLayer
        """
        if isinstance(layer, SafeLayer):
            self._exposure = layer
        elif isinstance(layer, QgsMapLayer):
            self._exposure = SafeLayer(layer)
        else:
            message = tr('Layer should be SafeLayer or QgsMapLayer')
            raise Exception(message)

        # Update the target field to a non-conflicting one
        if self._exposure.is_qgsvectorlayer():
            self.target_field = get_non_conflicting_attribute_name(
                self.target_field,
                self._exposure.layer.dataProvider().fieldNameMap().keys()
            )
        self.set_algorithm()

    @property
    def target_field(self):
        """Property for the target_field of the impact layer.

        :returns: The target field in the impact layer in case it's a vector.
        :rtype: unicode, str
        """
        return self._target_field

    @target_field.setter
    def target_field(self, target_field):
        """Setter for the target_field of the impact layer.

        :param target_field: Field name.
        :type target_field: str
        """
        self._target_field = target_field

    def set_algorithm(self):
        if self.exposure.keyword('layer_geometry') == 'raster':
            self.algorithm = RasterAlgorithm
        elif self.exposure.keyword('layer_geometry') == 'point':
            self.algorithm = PointAlgorithm
        elif self.exposure.keyword('exposure') == 'structure':
            self.algorithm = IndivisiblePolygonAlgorithm
        elif self.exposure.keyword('layer_geometry') == 'line':
            self.algorithm = LineAlgorithm
        else:
            self.algorithm = PolygonAlgorithm

    def preprocess(self):
        """"""
        pass

    def run_algorithm(self):
        algorithm_instance = self.algorithm(
            self.hazard.layer,
            self.exposure.layer,
            self.aggregation.layer,
            self.extent
        )
        self.impact_layer = algorithm_instance.run()
        # Add impact keywords after this


    def post_process(self):
        """"""
        pass

    def run(self):
        pass