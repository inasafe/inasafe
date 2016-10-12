# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid -
  *Impact Function.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""
from PyQt4.QtCore import QVariant

from qgis.core import (
    QgsMapLayer,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsVectorLayer,
    QgsGeometry,
    QgsFeature,
    QgsField,
    QgsDistanceArea,
    QGis,
    QgsFeatureRequest,
)

import logging

from safe.gisv4.vector.tools import create_memory_layer
from safe.definitionsv4.post_processors import post_processors
from safe.defaults import get_defaults
from safe.common.exceptions import (
    InvalidExtentError,
    InvalidLayerError,
    InvalidAggregationKeywords,
    InvalidHazardKeywords,
    InvalidExposureKeywords,
)
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO

LOGGER = logging.getLogger('InaSAFE')


__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'impact_function'
__date__ = '8/16/16'
__copyright__ = 'imajimatika@gmail.com'


def evaluate_formula(formula, variables):
    """Very simple formula evaluator. Beware the security.
    :param formula: A simple formula.
    :type formula: str

    :param variables: A collection of variable (key and value).
    :type variables: dict

    :returns: The result of the formula execution.
    :rtype: float, int
    """
    for key, value in variables.items():
        formula = formula.replace(key, str(value))
    return eval(formula)


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
        self._actual_extent = None
        # Actual extent's CRS - Read Only
        self._actual_extent_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        # set this to a gui call back / web callback etc as needed.
        self._callback = self.console_progress_callback

        self.algorithm = None
        self.impact = None

        self._name = None  # e.g. Flood Raster on Building Polygon
        self._title = None  # be affected

        self.state = {}
        self.reset_state()

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

        :raise: NoKeywordsFoundError if no keywords has been found.
        :raise: InvalidHazardKeywords if the layer is not an hazard layer.
        """
        try:
            # The layer might have monkey patching already.
            keywords = layer.keywords
        except AttributeError:
            # Or we should read it using KeywordIO
            # but NoKeywordsFoundError might be raised.
            keywords = KeywordIO().read_keywords(layer)

        if keywords.get('layer_purpose') != 'hazard':
            raise InvalidHazardKeywords

        self._hazard = layer
        self._hazard.keywords = keywords

        self.setup_impact_function()

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

        :raise: NoKeywordsFoundError if no keywords has been found.
        :raise: InvalidExposureKeywords if the layer is not an exposure layer.
        """
        try:
            # The layer might have monkey patching already.
            keywords = layer.keywords
        except AttributeError:
            # Or we should read it using KeywordIO
            # but NoKeywordsFoundError might be raised.
            keywords = KeywordIO().read_keywords(layer)

        if keywords.get('layer_purpose') != 'exposure':
            raise InvalidExposureKeywords

        self._exposure = layer
        self._exposure.keywords = keywords

        self.setup_impact_function()

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

        :raise: NoKeywordsFoundError if no keywords has been found.
        :raise: InvalidExposureKeywords if the layer isn't an aggregation layer
        """
        try:
            # The layer might have monkey patching already.
            keywords = layer.keywords
        except AttributeError:
            # Or we should read it using KeywordIO
            # but NoKeywordsFoundError might be raised.
            keywords = KeywordIO().read_keywords(layer)

        if keywords.get('layer_purpose') != 'aggregation':
            raise InvalidAggregationKeywords

        self._aggregation = layer
        self._aggregation.keywords = keywords

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
            The extent CRS should match the extent_crs property of this IF
            instance.
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

        # Set the name
        self._name = '%s %s on %s %s' % (
            self.hazard.keywords.get('hazard').title(),
            self.hazard.keywords.get('layer_geometry').title(),
            self.exposure.keywords.get('exposure').title(),
            self.exposure.keywords.get('layer_geometry').title(),
        )

        # Set the title
        if self.exposure.keywords.get('exposure') == 'population':
            self._title = tr('need evacuation')
        else:
            self._title = tr('be affected')

    def post_process(self):
        """More process after getting the impact layer with data."""
        # Post processor (gender, age, building type, etc)
        # Notes, action

        for post_processor in post_processors:
            post_processor_output = self.run_single_post_processor(
                post_processor)
            self.set_state_process(
                'post_processor',
                'Post processor for %s %s.' % (
                    post_processor['name'], post_processor_output))

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

    def is_divisible_exposure(self):
        """Check if an exposure has divisible feature.

        :returns: True if divisible, else False.
        :rtype: bool
        """
        if self.exposure.keywords.get('layer_geometry') == 'point':
            return False
        elif self.exposure.keywords.get('layer_geometry') == 'line':
            return True
        elif self.exposure.keywords.get('layer_geometry') == 'polygon':
            if self.exposure.keywords.get('exposure') == 'structure':
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
        aggregation_layer = create_memory_layer(
            'aggregation', QGis.Polygon, self.exposure.crs())

        aggregation_layer.startEditing()

        feature = QgsFeature()
        # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
        feature.setGeometry(QgsGeometry.fromRect(self.actual_extent))
        aggregation_layer.addFeature(feature)
        aggregation_layer.commitChanges()

        # Generate aggregation keywords
        aggregation_layer.keywords = get_defaults()
        aggregation_layer.keywords['layer_purpose'] = 'aggregation'

        return aggregation_layer

    def reset_state(self):
        """Method to reset the state of the impact function.
        """
        self.state = {
            'hazard': {
                'process': [],
                'info': {}
            },
            'exposure': {
                'process': [],
                'info': {}
            },
            'aggregation': {
                'process': [],
                'info': {}
            },
            'impact function': {
                'process': [],
                'info': {}
            },
            'post_processor': {
                'process': [],
                'info': {}
            }
        }

    def set_state_process(self, context, process):
        """Method to append process for a context in the IF state.

        :param context: It can be a layer purpose or a section (impact
            function, post processor).
        :type context: str, unicode

        :param process: A text explain the process.
        :type process: str, unicode
        """
        self.state[context]["process"].append(process)

    def set_state_info(self, context, key, value):
        """Method to add information for a context in the IF state.

        :param context: It can be a layer purpose or a section (impact
            function, post processor).
        :type context: str, unicode

        :param key: A key for the information, e.g. algorithm.
        :type key: str, unicode

        :param value: The value of the information. E.g point
        :type value: str, unicode, int, float, bool, list, dict
        """
        self.state[context]["info"][key] = value

    def run(self):
        """Run the whole impact function."""
        self.reset_state()

        # Hazard Preparation
        if self.hazard.type() == QgsMapLayer.VectorLayer:
            if self.hazard.keywords.get('layer_geometry') == 'polygon':
                if self.hazard.keywords.get('layer_mode') == 'continuous':
                    self.set_state_process(
                        'hazard',
                        'Classify continuous hazard and assign class names')
                else:
                    self.set_state_process(
                        'hazard', 'Assign classes based on value map')
            else:
                self.set_state_process('hazard', 'Buffering')
                self.set_state_process(
                    'hazard', 'Assign classes based on value map')

        elif self.hazard.type() == QgsMapLayer.RasterLayer:
            if self.hazard.keywords.get('layer_mode') == 'continuous':
                self.set_state_process(
                    'hazard', 'Classify continuous raster hazard')
            self.set_state_process(
                'hazard', 'Polygonise classified raster hazard')
            self.set_state_process(
                'hazard', 'Assign class names based on class id')
        else:
            raise InvalidLayerError(tr('Unsupported hazard layer type'))
        self.set_state_process(
            'hazard', 'Classified polygon hazard with keywords')
        self.set_state_process(
            'hazard', 'Project hazard CRS to exposure CRS')

        self.set_state_process(
            'hazard', 'Vector clip and mask hazard to aggregation')

        # Aggregation Preparation
        if not self.aggregation:
            self.set_state_info('aggregation', 'provided', False)
            if not self.actual_extent:
                self._actual_extent = self.exposure.extent()

            self.set_state_process(
                'aggregation',
                'Convert bbox aggregation to polygon layer with keywords')

            self.aggregation = self.create_virtual_aggregation()

        else:
            self.set_state_info('aggregation', 'provided', True)

        self.set_state_process(
            'aggregation', 'Project aggregation CRS to exposure CRS')
        self.set_state_process(
            'aggregation',
            'Intersect hazard polygons with aggregation areas and assign '
            'hazard class')

        # Exposure Preparation
        if self.exposure.type() == QgsMapLayer.RasterLayer:
            if self.exposure.keywords.get('layer_mode') == 'continuous':
                if self.exposure.keywords.get('exposure_unit') == 'density':
                    self.set_state_process(
                        'exposure', 'Calculate counts per cell')
                self.set_state_process(
                    'exposure',
                    'Raster clip and mask exposure to aggregate hazard')
                self.set_state_process(
                    'exposure',
                    'Zonal stats on intersected hazard / aggregation data')
            else:
                self.set_state_process(
                    'exposure', 'Polygonise classified raster hazard')
                self.set_state_process(
                    'exposure',
                    'Intersect aggregate hazard layer with divisible polygon')
                self.set_state_process(
                    'exposure',
                    'Recalculate population based on new polygonise size')

        elif self.exposure.type() == QgsMapLayer.VectorLayer:
            self.set_state_process(
                'exposure', 'Classified exposure with keywords')
            if self.is_divisible_exposure():
                if self.exposure.keywords.get('layer_geometry') == 'line':
                    self.set_state_process(
                        'exposure',
                        'Intersect with aggregate hazard and exclude roads '
                        'outside')
                else:
                    self.set_state_process(
                        'exposure',
                        'Intersect aggregate hazard layer with divisible '
                        'polygon')
                    self.set_state_process(
                        'exposure',
                        'Recalculate population based on new polygonise size')
            else:
                self.set_state_process(
                    'exposure',
                    'Exclude all polygons not intersecting aggregate hazard')
        else:
            raise InvalidLayerError(tr('Unsupported exposure layer type'))

        # Running Impact Function
        self.set_state_process('impact function', 'Run impact function')

        if self.exposure.type() == QgsMapLayer.RasterLayer:
            # Special case for Raster Earthquake hazard.
            if self.hazard.keywords('hazard') == 'earthquake':
                pass
            else:
                self.set_state_info('impact function', 'algorithm', 'raster')
                self.state['impact function']['info']['algorithm'] = \
                    'raster'
        elif self.exposure.keywords.get('layer_geometry') == 'point':
            self.set_state_info('impact function', 'algorithm', 'point')
        elif self.exposure.keywords.get('exposure') == 'structure':
            self.set_state_info(
                'impact function', 'algorithm', 'indivisible polygon')
        elif self.exposure.keywords.get('layer_geometry') == 'line':
            self.set_state_info('impact function', 'algorithm', 'line')
        else:
            self.set_state_info('impact function', 'algorithm', 'polygon')

        if self.is_divisible_exposure():
            self.set_state_process(
                'impact function',
                'Highest class of hazard is assigned when more than one '
                'overlaps')
        else:
            self.set_state_process(
                'impact function',
                'Assign by location aggregation and hazard areas to exposure '
                'features')

        # Post Processor
        # Disable post processor for now (IS)
        # self.post_process()

        # Disable writing impact keyword until implementing all helper methods
        # KeywordIO().write_keywords(
        #     self.impact, self.impact.keywords)

        return self.state

    def run_single_post_processor(self, post_processor):
        """Run single post processor.

        If the impact layer has the output field, it will pass the post
        processor calculation.

        :param post_processor: A post processor definition.
        :type post_processor: dict

        :returns: Tuple with True if success, else False with an error message.
        :rtype: (bool, str)
        """
        valid, message = self.enough_input(post_processor['input'])
        if valid:

            # Turn on the editing mode.
            if not self.impact.startEditing():
                msg = tr('The impact layer could not start the editing mode.')
                return False, msg

            # Calculate based on formula
            # Iterate all possible output
            for output_key, output_value in post_processor['output'].items():

                # Get output attribute name
                output_field_name = output_value['value']['field_name']

                # If there is already the output field, don't proceed
                if self.impact.fieldNameIndex(output_field_name) > -1:
                    msg = tr(
                        'The field name %s already exists.'
                        % output_field_name)
                    return False, msg

                # Add output attribute name to the layer
                result = self.impact.addAttribute(
                    QgsField(
                        output_field_name,
                        output_value['value']['type'])
                )
                if not result:
                    msg = tr(
                        'Error while creating the field %s.'
                        % output_field_name)
                    return False, msg

                # Get the index of output attribute
                output_field_index = self.impact.fieldNameIndex(
                    output_field_name)

                if self.impact.fieldNameIndex(output_field_name) == -1:
                    msg = tr(
                        'The field name %s has not been created.'
                        % output_field_name)
                    return False, msg

                # Get the input field's indexes for input
                input_indexes = {}
                # Store the indexes that will be deleted.
                temporary_indexes = []
                for key, value in post_processor['input'].items():

                    if value['type'] == 'field':
                        inasafe_fields = self.impact.keywords['inasafe_fields']
                        name_field = inasafe_fields.get(value['value']['key'])

                        if not name_field:
                            msg = tr(
                                '%s has not been found in inasafe fields.'
                                % value['value']['key'])
                            return False, msg

                        index = self.impact.fieldNameIndex(name_field)

                        if index == -1:
                            fields = self.impact.fields().toList()
                            msg = tr(
                                'The field name %s has not been found in %s'
                                % (
                                    name_field,
                                    [f.name() for f in fields]
                                ))
                            return False, msg

                        input_indexes[key] = index

                    # For geometry, create new field that contain the value
                    elif value['type'] == 'geometry_property':
                        if value['value'] == 'size':
                            input_indexes[key] = self.add_size_field()
                            temporary_indexes.append(input_indexes[key])

                # Create iterator for feature
                request = QgsFeatureRequest().setSubsetOfAttributes(
                    input_indexes.values())
                iterator = self.impact.getFeatures(request)
                # Iterate all feature
                for feature in iterator:
                    attributes = feature.attributes()

                    # Create dictionary to store the input
                    parameters = {}

                    # Fill up the input from fields
                    for key, value in input_indexes.items():
                        parameters[key] = attributes[value]
                    # Fill up the input from geometry property

                    # Evaluate the formula
                    post_processor_result = evaluate_formula(
                        output_value['formula'], parameters)

                    self.impact.changeAttributeValue(
                        feature.id(),
                        output_field_index,
                        post_processor_result
                    )

                # Delete temporary indexes
                self.impact.deleteAttributes(temporary_indexes)

            self.impact.commitChanges()
            LOGGER.debug(self.impact.source())
            return True, None
        else:
            return False, message

    def enough_input(self, post_processor_input):
        """Check if the input from impact_fields in enough.

        :param post_processor_input: Collection of post processor input
            requirements.
        :type post_processor_input: dict

        :returns: Tuple with True if success, else False with an error message.
        :rtype: (bool, str)
        """
        impact_fields = self.impact.keywords['inasafe_fields'].keys()
        for input_key, input_value in post_processor_input.items():
            if input_value['type'] == 'field':
                key = input_value['value']['key']
                if key in impact_fields:
                    continue
                else:
                    msg = 'Key %s is missing in fields %s' % (
                        key, impact_fields)
                    return False, msg
        return True, None

    def add_size_field(self):
        """Add size field in to impact layer.

        If polygon, size will be area in square meter.
        If line, size will be length in meter.

        :returns: Index of the size field.
        :rtype: int
        """
        # Create QgsDistanceArea object
        size_calculator = QgsDistanceArea()
        size_calculator.setSourceCrs(self.impact.crs())
        size_calculator.setEllipsoid('WGS84')
        size_calculator.setEllipsoidalMode(True)

        # Add new field, size
        self.impact.addAttribute(QgsField('size', QVariant.Double))

        # Get index
        size_field_index = self.impact.fieldNameIndex('size')

        # Iterate through all features
        request = QgsFeatureRequest().setSubsetOfAttributes([])
        features = self.impact.getFeatures(request)
        for feature in features:
            self.impact.changeAttributeValue(
                feature.id(),
                size_field_index,
                size_calculator.measure(feature.geometry())
            )
        return size_field_index
