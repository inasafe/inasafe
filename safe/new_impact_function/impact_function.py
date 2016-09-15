# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid -
  *Impact Function.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""

from qgis.core import (
    QgsMapLayer,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsVectorLayer,
    QgsGeometry,
    QgsFeature
)

from safe.definitions import post_processors
from safe.defaults import get_defaults
from safe.common.exceptions import InvalidExtentError
from safe.utilities.i18n import tr
from safe.common.utilities import get_non_conflicting_attribute_name
from safe.utilities.keyword_io import KeywordIO


__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'impact_function'
__date__ = '8/16/16'
__copyright__ = 'imajimatika@gmail.com'


class ImpactFunction(object):
    """Impact Function."""

    def __init__(self):
        self._hazard = None
        self._hazard_keyword = {}

        self._exposure = None
        self._exposure_keyword = {}

        self._aggregation = None
        self._aggregation_keyword = {}

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

        self._name = None  # e.g. Flood Raster on Building Polygon
        self._title = None  # be affected

    @property
    def hazard(self):
        """Property for the hazard layer to be used for the analysis.

        :returns: A map layer.
        :rtype: QgsMapLayer
        """
        return self._hazard

    @hazard.setter
    def hazard(self, layer):
        """Setter for hazard layer property.

        :param layer: Hazard layer to be used for the analysis.
        :type layer: QgsMapLayer
        """
        self._hazard = layer
        self._hazard_keyword = KeywordIO().read_keywords(layer)

        self.setup_impact_function()

    @property
    def hazard_keyword(self):
        """Keyword for the hazard layer to be used for the analysis.

        :returns: A dictionary or string
        :rtype: dict, str
        """
        return self._hazard_keyword

    @hazard_keyword.setter
    def hazard_keyword(self, keyword):
        """Setter for hazard layer keyword.

        :param keyword: Dictionary of keyword
        :type keyword: dict
        """
        self._hazard_keyword = keyword

    @property
    def exposure(self):
        """Property for the exposure layer to be used for the analysis.

        :returns: A map layer.
        :rtype: QgsMapLayer
        """
        return self._exposure

    @exposure.setter
    def exposure(self, layer):
        """Setter for exposure layer property.

        :param layer: exposure layer to be used for the analysis.
        :type layer: QgsMapLayer
        """
        self._exposure = layer
        self._exposure_keyword = KeywordIO().read_keywords(layer)

        if layer.type() == QgsMapLayer.VectorLayer:
            # Update the affected field to a non-conflicting one
            self.hazard_field = get_non_conflicting_attribute_name(
                self.hazard_field,
                self._exposure.dataProvider().fieldNameMap().keys()
            )

            # Update the aggregation field to a non-conflicting one
            self.aggregation_field = get_non_conflicting_attribute_name(
                self.aggregation_field,
                (self._exposure.dataProvider().fieldNameMap().keys()
                 + [self.hazard_field])
            )
        self.setup_impact_function()

    @property
    def exposure_keyword(self, keyword=None):
        """Keyword for the exposure layer to be used for the analysis.

        :returns: A dictionary or string
        :rtype: dict, str
        """
        if keyword:
            return self._exposure_keyword.get(keyword)
        else:
            return self._exposure_keyword

    @exposure_keyword.setter
    def exposure_keyword(self, keyword):
        """Setter for exposure layer keyword.

        :param keyword: Dictionary of keyword
        :type keyword: dict
        """
        self._exposure_keyword = keyword

    @property
    def aggregation(self):
        """Property for the aggregation layer to be used for the analysis.

        :returns: A map layer.
        :rtype: QgsMapLayer
        """
        return self._aggregation

    @aggregation.setter
    def aggregation(self, layer):
        """Setter for aggregation layer property.

        :param layer: aggregation layer to be used for the analysis.
        :type layer: QgsMapLayer
        """
        self._aggregation = layer
        self._aggregation_keyword = KeywordIO().read_keywords(layer)

    @property
    def aggregation_keyword(self, keyword=None):
        """Keyword for the aggregation layer to be used for the analysis.

        :returns: A dictionary or string
        :rtype: dict, str
        """
        if keyword:
            return self._aggregation_keyword.get(keyword)
        else:
            return self._aggregation_keyword

    @aggregation_keyword.setter
    def aggregation_keyword(self, keyword):
        """Setter for aggregation layer keyword.

        :param keyword: Dictionary of keyword
        :type keyword: dict
        """
        self._aggregation_keyword = keyword

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
    def name(self):
        """The name of the impact function

        :returns: The name.
        :rtype: basestring
        """
        return self._name

    @property
    def title(self):
        """The title of the impact function

        :returns: The title.
        :rtype: basestring
        """
        return self._title

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

    def setup_impact_function(self):
        """Automatically called when the hazard or exposure is changed.
        """
        if not self.hazard or not self.exposure:
            return

        # Set the algorithm
        self.set_algorithm()

        # Set the name
        self._name = '%s %s on %s %s' % (
            self.hazard_keyword.get('hazard').title(),
            self.hazard_keyword.get('layer_geometry').title(),
            self.exposure_keyword.get('exposure').title(),
            self.exposure_keyword.get('layer_geometry').title(),
        )

        # Set the title
        if self.exposure_keyword.get('exposure') == 'population':
            self._title = tr('need evacuation')
        else:
            self._title = tr('be affected')

    def set_algorithm(self):
        if self.exposure_keyword.get('layer_geometry') == 'raster':
            # Special case for Raster Earthquake hazard.
            if self.hazard_keyword('hazard') == 'earthquake':
                pass
            else:
                self.algorithm = self.raster_algorithm
        elif self.exposure_keyword.get('layer_geometry') == 'point':
            self.algorithm = self.point_algorithm
        elif self.exposure_keyword.get('exposure') == 'structure':
            self.algorithm = self.indivisible_polygon_algorithm
        elif self.exposure_keyword.get('layer_geometry') == 'line':
            self.algorithm = self.line_algorithm
        else:
            self.algorithm = self.polygon_algorithm

    def preprocess(self):
        """Run process before running the main work / algorithm"""
        # Clipping
        # Convert hazard to classified vector
        # Aggregation if needed
        pass

    def run_algorithm(self):
        """Run the algorithm
        """
        algorithm_instance = self.algorithm(
            hazard=self.hazard.layer,
            exposure=self.exposure.layer,
            # aggregation=self.aggregation.layer,
            extent=self.actual_extent,
            hazard_field=self.hazard_field,
            aggregation_field=self.aggregation_field,
            original_hazard_field=self.hazard.keyword('field'),
            # original_aggregation_field=self.aggregation.keyword(
            #     'aggregation_attribute')
        )
        self.impact_layer = algorithm_instance.run()
        # Add impact keywords after this

    def post_process(self):
        """More process after getting the impact layer with data."""
        # Post processor (gender, age, building type, etc)
        # Notes, action
        pass

    def run(self):
        self.preprocess()
        self.run_algorithm()
        self.post_process()

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

    def indivisible_polygon_algorithm(self):
        pass

    def line_algorithm(self):
        pass

    def point_algorithm(self):
        pass

    def polygon_algorithm(self):
        pass

    def raster_algorithm(self):
        pass

    def is_divisible_exposure(self):
        """Check if an exposure has divisible feature.
        :returns: True if divisible, else False
        :rtype: bool
        """
        if self.exposure_keyword.get('layer_geometry') == 'point':
            return False
        elif self.exposure_keyword.get('layer_geometry') == 'line':
            return True
        elif self.exposure_keyword.get('layer_geometry') == 'polygon':
            if self.exposure_keyword.get('layer_geometry') == 'structure':
                return False
            else:
                return True
        else:
            return True

    def create_virtual_aggregation(self):
        """Function to create aggregation layer based on extent

        :returns: A polygon layer with exposure's crs.
        :rtype: QgsVectorLayer
        """
        exposure_crs = self.exposure.crs().authid()
        aggregation_layer = QgsVectorLayer(
            "Polygon?crs=%s" % exposure_crs, "aggregation", "memory")
        data_provider = aggregation_layer.dataProvider()

        feature = QgsFeature()
        # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
        feature.setGeometry(QgsGeometry.fromRect(self.actual_extent))
        data_provider.addFeatures([feature])

        return aggregation_layer

    def flow(self):
        impact_function_state = {
            'hazard': {
                'process': []
            },
            'exposure': {
                'process': []
            },
            'aggregation': {
                'process': []
            },
            'impact function': {
                'process': []

            },
            'post_processor': {
                'process': []

            }
        }

        # Aggregation Preparation
        if not self.aggregation:
            impact_function_state['aggregation']['provided'] = False
            if not self.actual_extent:
                self._actual_extent = self.exposure.extent()

            self.aggregation = self.create_virtual_aggregation()

            # Generate aggregation keywords
            aggregation_keyword = get_defaults()
            self.aggregation_keyword = aggregation_keyword

        else:
            impact_function_state['aggregation']['provided'] = True

        impact_function_state['aggregation']['process'].append(
            'Project aggregation CRS to exposure CRS')

        # Hazard Preparation
        if self.hazard.type() == QgsMapLayer.VectorLayer:
            if self.hazard_keyword.get('layer_mode') == 'continuous':
                impact_function_state['hazard']['process'].append(
                    'classify continuous hazard and assign class name')
                if self.hazard_keyword.get('layer_geometry') != 'polygon':
                    impact_function_state['hazard']['process'].append(
                        'Buffering')
            else:
                if self.hazard_keyword.get('layer_geometry') != 'polygon':
                    impact_function_state['hazard']['process'].append(
                        'Buffering')
                impact_function_state['hazard']['process'].append(
                    'Assign classes based on value map')

        elif self.hazard.type() == QgsMapLayer.RasterLayer:
            if self.hazard_keyword.get('layer_mode') == 'continuous':
                impact_function_state['hazard']['process'].append(
                    'classify continuous raster hazard')
            impact_function_state['hazard']['process'].append(
                'polygonise classified raster hazard')
            impact_function_state['hazard']['process'].append(
                'assign class name based on class id')
        else:
            raise tr('Unsupported hazard layer type')

        impact_function_state['hazard']['process'].append(
            'Classified polygon hazard with keywords')
        impact_function_state['hazard']['process'].append(
            'Project hazard CRS to exposure CRS')

        impact_function_state['hazard']['process'].append(
            'Vector clip and mask hazard to aggregation')
        impact_function_state['hazard']['process'].append(
            'Intersect hazard polygons with aggregation areas and assign '
            'hazard class')

        # Exposure Preparation
        if self.exposure.type() == QgsMapLayer.RasterLayer:
            if self.exposure_keyword.get('exposure_unit') == 'density':
                impact_function_state['exposure']['process'].append(
                    'Calculate counts per cell')
            impact_function_state['exposure']['process'].append(
                'Raster clip and mask exposure to aggregation')
            impact_function_state['exposure']['process'].append(
                'Zonal stats on intersected hazard / aggregation data')
            impact_function_state['exposure']['process'].append(
                'Intersect aggregate hazard layer with divisible polygon')
        elif self.exposure.type() == QgsMapLayer.VectorLayer:
            impact_function_state['exposure']['process'].append(
                'Vector clip and mask exposure to aggregation')
            if self.is_divisible_exposure():
                pass
            elif self.exposure_keyword.get('layer_geometry') == 'line':
                impact_function_state['exposure']['process'].append(
                    'Intersect line with aggregation hazard areas')
            else:
                impact_function_state['exposure']['process'].append(
                    'Intersect aggregate hazard layer with divisible polygon')
        else:
            raise tr('Unsupported exposure layer type')

        # Running Impact Function
        impact_function_state['impact function']['process'].append(
            'Run impact function')

        if self.exposure_keyword.get('layer_geometry') == 'raster':
            # Special case for Raster Earthquake hazard.
            if self.hazard_keyword('hazard') == 'earthquake':
                pass
            else:
                impact_function_state['impact function']['algorithm'] = \
                    'raster'
        elif self.exposure_keyword.get('layer_geometry') == 'point':
            impact_function_state['impact function']['algorithm'] = 'point'
        elif self.exposure_keyword.get('exposure') == 'structure':
            impact_function_state['impact function']['algorithm'] = \
                'indivisible polygon'
        elif self.exposure_keyword.get('layer_geometry') == 'line':
            impact_function_state['impact function']['algorithm'] = 'line'
        else:
            impact_function_state['impact function']['algorithm'] = 'polygon'

        if self.is_divisible_exposure():
            impact_function_state['impact function']['process'].append(
                'Highest class of hazard is assigned when more than one '
                'overlaps')
        else:
            impact_function_state['impact function']['process'].append(
                'Assign by location aggregation and hazard areas to exposure '
                'features')

        # Post Processor
        # TODO (Ismail) Add new keyword for post processor in exposure layer
        post_processor_parameters = post_processors
        for post_processor in post_processor_parameters:
            impact_function_state['post_processor']['process'].append(
                'Post processor for %s.' % post_processor['name'])

        return impact_function_state
