

from qgis.core import (
    QgsMapLayer,
    QgsCoordinateReferenceSystem,
    QgsRectangle)

from safe.common.exceptions import InvalidExtentError, InvalidLayerError
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


__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'impact_function'
__date__ = '8/16/16'
__copyright__ = 'imajimatika@gmail.com'


class ImpactFunction(object):
    """Impact Function."""

    def __init__(self):
        self._hazard = None
        self._exposure = None
        self._aggregation = None
        # Requested extent to use
        self._requested_extent = None
        # Requested extent's CRS
        self._requested_extent_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        # The current viewport extent of the map canvas
        self._viewport_extent = None
        # Actual extent to use - Read Only
        # For 'old-style' IF we do some manipulation to the requested extent
        self._actual_extent = None
        # Actual extent's CRS - Read Only
        self._actual_extent_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        # set this to a gui call back / web callback etc as needed.
        self._callback = self.console_progress_callback

        self.algorithm = None
        self.impact_layer = None
        self._hazard_field = 'hazard'
        self._aggregation_field = 'agg_area'

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
            message = tr('Hazard layer should be SafeLayer or QgsMapLayer')
            raise InvalidLayerError(message)

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
        :type layer: SafeLayer, QgsMapLayer
        """
        if isinstance(layer, SafeLayer):
            self._exposure = layer
        elif isinstance(layer, QgsMapLayer):
            self._exposure = SafeLayer(layer)
        else:
            message = tr('Exposure layer should be SafeLayer or QgsMapLayer')
            raise InvalidLayerError(message)

        if self._exposure.is_qgsvectorlayer():
            # Update the affected field to a non-conflicting one
            self.hazard_field = get_non_conflicting_attribute_name(
                self.hazard_field,
                self._exposure.layer.dataProvider().fieldNameMap().keys()
            )

            # Update the aggregation field to a non-conflicting one
            self.aggregation_field = get_non_conflicting_attribute_name(
                self.aggregation_field,
                (self._exposure.layer.dataProvider().fieldNameMap().keys()
                 + [self.hazard_field])
            )
        self.set_algorithm()

    @property
    def aggregation(self):
        """Property for the aggregation layer to be used for the analysis.

        :returns: A map layer.
        :rtype: SafeLayer
        """
        return self._exposure

    @aggregation.setter
    def aggregation(self, layer):
        """Setter for aggregation layer property.

        :param layer: aggregation layer to be used for the analysis.
        :type layer: SafeLayer, QgsMapLayer
        """
        if isinstance(layer, SafeLayer):
            self._aggregation = layer
        elif isinstance(layer, QgsMapLayer):
            self._aggregation = SafeLayer(layer)
        else:
            message = tr(
                'Aggregation layer should be SafeLayer or QgsMapLayer')
            raise InvalidLayerError(message)

    @property
    def hazard_field(self):
        """Property for the affected_field of the impact layer.

        :returns: The affected_field in the impact layer in case it's a vector.
        :rtype: unicode, str
        """
        return self._hazard_field

    @hazard_field.setter
    def hazard_field(self, affected_field):
        """Setter for the affected_field of the impact layer.

        :param affected_field: Field name.
        :type affected_field: str
        """
        self._hazard_field = affected_field

    @property
    def aggregation_field(self):
        """Property for the aggregation_field of the impact layer.

        :returns: The aggregation_field in the impact layer
        :rtype: unicode, str
        """
        return self._aggregation_field

    @aggregation_field.setter
    def aggregation_field(self, aggregation_field):
        """Setter for the aggregation_field of the impact layer.

        :param aggregation_field: Field name.
        :type aggregation_field: str
        """
        self._aggregation_field = aggregation_field

    @property
    def requested_extent(self):
        """Property for the extent of impact function analysis.

        :returns: A QgsRectangle.
        :rtype: QgsRectangle
        """
        return self._requested_extent

    @requested_extent.setter
    def requested_extent(self, extent):
        """Setter for extent property.

        :param extent: Analysis boundaries expressed as a QgsRectangle.
        The extent CRS should match the extent_crs property of this IF instance.
        :type extent: QgsRectangle
        """
        if isinstance(extent, QgsRectangle):
            self._requested_extent = extent
        else:
            raise InvalidExtentError('%s is not a valid extent.' % extent)

    @property
    def requested_extent_crs(self):
        """Property for the extent CRS of impact function analysis.

        :return crs: The coordinate reference system for the analysis boundary.
        :rtype: QgsCoordinateReferenceSystem
        """
        return self._requested_extent_crs

    @requested_extent_crs.setter
    def requested_extent_crs(self, crs):
        """Setter for extent_crs property.

        :param crs: The coordinate reference system for the analysis boundary.
        :type crs: QgsCoordinateReferenceSystem
        """
        self._requested_extent_crs = crs

    @property
    def actual_extent(self):
        """Property for the actual extent of impact function analysis.

        :returns: A QgsRectangle.
        :rtype: QgsRectangle
        """
        return self._actual_extent

    @property
    def actual_extent_crs(self):
        """Property for the actual extent crs for analysis.

        :returns: The CRS for the actual extent.
        :rtype: QgsCoordinateReferenceSystem
        """
        return self._actual_extent_crs

    @property
    def viewport_extent(self):
        """Property for the viewport extent of the map canvas.

        :returns: A QgsRectangle.
        :rtype: QgsRectangle
        """
        return self._viewport_extent

    @viewport_extent.setter
    def viewport_extent(self, viewport_extent):
        """Setter for the viewport extent of the map canvas.

        :param viewport_extent: Analysis boundaries expressed as a
        QgsRectangle. The extent CRS should match the extent_crs property of
        this IF instance.
        :type viewport_extent: QgsRectangle
        """
        self._viewport_extent = viewport_extent

    @property
    def callback(self):
        """Property for the callback used to relay processing progress.

        :returns: A callback function. The callback function will have the
            following parameter requirements.

            progress_callback(current, maximum, message=None)

        :rtype: function

        .. seealso:: console_progress_callback
        """
        return self._callback

    @callback.setter
    def callback(self, callback):
        """Setter for callback property.

        :param callback: A callback function reference that provides the
            following signature:

            progress_callback(current, maximum, message=None)

        :type callback: function
        """
        self._callback = callback

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
        # Clipping
        pass

    def run_algorithm(self):
        #TODO(IS) : Think how we can pass the affected field and aggregation
        # field
        algorithm_instance = self.algorithm(
            self.hazard.layer,
            self.exposure.layer,
            self.aggregation.layer,
            self.actual_extent
        )
        self.impact_layer = algorithm_instance.run()
        # Add impact keywords after this


    def post_process(self):
        """"""
        pass

    def run(self):
        pass

    @staticmethod
    def console_progress_callback(current, maximum, message=None):
        """Simple console based callback implementation for tests.

        :param current: Current progress.
        :type current: int

        :param maximum: Maximum range (point at which task is complete.
        :type maximum: int

        :param message: Optional message to display in the progress bar
        :type message: str, QString
        """
        # noinspection PyChainedComparisons
        if maximum > 1000 and current % 1000 != 0 and current != maximum:
            return
        if message is not None:
            print message
        print 'Task progress: %i of %i' % (current, maximum)
