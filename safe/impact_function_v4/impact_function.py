# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid -
  *Impact Function.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""
from collections import OrderedDict
from datetime import datetime

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

from safe.common.utilities import temp_dir
from safe.datastore.folder import Folder
from safe.gisv4.vector.tools import create_memory_layer
from safe.gisv4.vector.prepare_vector_layer import prepare_vector_layer
from safe.gisv4.vector.reproject import reproject
from safe.gisv4.vector.assign_highest_value import assign_highest_value
from safe.gisv4.vector.reclassify import reclassify as reclassify_vector
from safe.gisv4.vector.union import union
from safe.gisv4.vector.clip import clip
from safe.gisv4.vector.aggregate_summary import aggregate_summary
from safe.gisv4.vector.assign_inasafe_values import assign_inasafe_values
from safe.gisv4.raster.reclassify import reclassify as reclassify_raster
from safe.gisv4.raster.polygonize import polygonize
from safe.definitionsv4.post_processors import post_processors
from safe.definitionsv4.fields import (
    aggregation_id_field,
    aggregation_name_field,
    size_field
)
from safe.definitionsv4.utilities import definition
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
from safe.utilities.utilities import replace_accentuated_characters
from safe.utilities.profiling import (
    profile, clear_prof_data, profiling_log)
from safe import messaging as m

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

        self._aggregate_hazard = None

        self.debug = False

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

        self.impact = None

        self._name = None  # e.g. Flood Raster on Building Polygon
        self._title = None  # be affected
        self._unique_name = None  # EXP + On + Haz + DDMMMMYYYY + HHhMM.SS

        self._datastore = None

        self.state = {}
        self._performance_log = None
        self.reset_state()

    @property
    def performance_log(self):
        """Property for the performance log that can be used for benchmarking.

        :returns: A dict containing benchmarking data.
        :rtype: dict
        """
        return self._performance_log

    def performance_log_message(self):
        """Return the profiling log as a message"""
        message = m.Message()
        table = m.Table(style_class='table table-condensed table-striped')
        row = m.Row()
        row.add(m.Cell(tr('Function')), header_flag=True)
        row.add(m.Cell(tr('Calls')), header_flag=True)
        row.add(m.Cell(tr('Average (ms)')), header_flag=True)
        row.add(m.Cell(tr('Max (ms)')), header_flag=True)
        table.add(row)
        for function_name, data in self._performance_log.items():
            calls = data[0]
            max_time = max(data[1])
            avg_time = sum(data[1]) / len(data[1])
            row = m.Row()
            row.add(m.Cell(function_name))
            row.add(m.Cell(calls))
            row.add(m.Cell(avg_time))
            row.add(m.Cell(max_time))
            table.add(row)
        message.add(table)
        return message

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
        if not layer.isValid():
            raise InvalidHazardKeywords(tr('The hazard is not valid.'))

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
        if not layer.isValid():
            raise InvalidHazardKeywords(tr('The exposure is not valid.'))

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
        :rtype: QgsVectorLayer
        """
        return self._aggregation

    @aggregation.setter
    def aggregation(self, layer):
        """Setter for aggregation layer property.

        :param layer: aggregation layer to be used for the analysis.
        :type layer: QgsVectorLayer

        :raise: NoKeywordsFoundError if no keywords has been found.
        :raise: InvalidExposureKeywords if the layer isn't an aggregation layer
        """
        if not layer.isValid():
            raise InvalidHazardKeywords(tr('The aggregation is not valid.'))

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
    def aggregate_hazard(self):
        """Property for the aggregate hazard.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._aggregate_hazard

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
    def datastore(self):
        """Return the current datastore.

        :return: The datastore.
        :rtype: Datastore
        """
        return self._datastore

    @datastore.setter
    def datastore(self, datastore):
        """Setter for the datastore.

        :param datastore: The datastore.
        :type datastore: DataStore
        """
        self._datastore = datastore

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

    @profile
    def setup_impact_function(self):
        """Automatically called when the hazard or exposure is changed.
        """
        if not self.hazard or not self.exposure:
            return

        # Set the name
        self._name = tr('%s %s On %s %s' % (
            self.hazard.keywords.get('hazard').title(),
            self.hazard.keywords.get('layer_geometry').title(),
            self.exposure.keywords.get('exposure').title(),
            self.exposure.keywords.get('layer_geometry').title(),
        ))

        # Set the title
        if self.exposure.keywords.get('exposure') == 'population':
            self._title = tr('need evacuation')
        else:
            self._title = tr('be affected')

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

    @profile
    def create_virtual_aggregation(self):
        """Function to create aggregation layer based on extent

        :returns: A polygon layer with exposure's crs.
        :rtype: QgsVectorLayer
        """
        fields = [
            QgsField(
                aggregation_id_field['field_name'],
                aggregation_id_field['type']
            ),
            QgsField(
                aggregation_name_field['field_name'],
                aggregation_name_field['type']
            )
        ]
        aggregation_layer = create_memory_layer(
            'aggregation', QGis.Polygon, self.exposure.crs(), fields)

        aggregation_layer.startEditing()

        feature = QgsFeature()
        # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
        feature.setGeometry(QgsGeometry.fromRect(self.actual_extent))
        feature.setAttributes([1, tr('Entire Area')])
        aggregation_layer.addFeature(feature)
        aggregation_layer.commitChanges()

        # Generate aggregation keywords
        aggregation_layer.keywords = get_defaults()
        aggregation_layer.keywords['layer_purpose'] = 'aggregation'
        aggregation_layer.keywords['inasafe_fields'] = {
            aggregation_id_field['key']: aggregation_id_field['field_name'],
            aggregation_name_field['key']: aggregation_name_field['field_name']
        }

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

    @profile
    def run(self):
        """Run the whole impact function."""
        self.reset_state()
        clear_prof_data()

        # Set a unique name for this impact
        self._unique_name = self._name.replace(' ', '')
        self._unique_name = replace_accentuated_characters(self._unique_name)
        now = datetime.now()
        date = now.strftime('%d%B%Y').decode('utf8')
        time = now.strftime('%Hh%M-%S').decode('utf8')
        self._unique_name = '%s_%s_%s' % (self._unique_name, date, time)

        if not self._datastore:
            # By default, results will go in a temporary folder.
            # Users are free to set their own datastore with the setter.
            self._datastore = Folder(temp_dir(sub_dir=self._unique_name))
            self._datastore.default_vector_format = 'geojson'
            if self.debug:
                print 'Temporary datastore'
                print self.datastore.uri.absolutePath()

        if self.debug:
            self._datastore.use_index = True

            self.datastore.add_layer(self.exposure, 'exposure')
            self.datastore.add_layer(self.hazard, 'hazard')
            if self.aggregation:
                self.datastore.add_layer(self.aggregation, 'aggregation')

        # Special case for Raster Earthquake hazard.
        if self.hazard.type() == QgsMapLayer.RasterLayer:
            if self.hazard.keywords.get('hazard') == 'earthquake':
                # return self.state()
                return

        self.hazard_preparation()

        self.aggregate_hazard_preparation()

        self.exposure_preparation()

        self.intersect_exposure_and_aggregate_hazard()

        # Post Processor
        self.post_process()

        self.datastore.add_layer(self.impact, 'impact')

        self.set_state_process(
            'impact function',
            'Aggregate the impact summary')
        self._aggregate_hazard = aggregate_summary(
            self.aggregate_hazard, self.impact)

        self.datastore.add_layer(self.aggregate_hazard, 'aggregate-hazard')

        # Get the profiling log
        self._performance_log = profiling_log()

        if self.debug:
            print 'Performance log message :'
            print self.performance_log_message().to_text()
        return self.state

    @profile
    def hazard_preparation(self):
        """This function is doing the hazard preparation."""

        if self.hazard.type() == QgsMapLayer.VectorLayer:

            self.set_state_process(
                'hazard',
                'Cleaning the vector hazard attribute table')
            # noinspection PyTypeChecker
            self.hazard = prepare_vector_layer(self.hazard)
            if self.debug:
                self.datastore.add_layer(
                    self.hazard, 'hazard_cleaned')

            if self.hazard.keywords.get('layer_geometry') == 'polygon':

                if self.hazard.keywords.get('layer_mode') == 'continuous':
                    self.set_state_process(
                        'hazard',
                        'Classify continuous hazard and assign class names')
                    # self.hazard = reclassify(self.hazard, ranges)
                    # if self.debug:
                    #     self.datastore.add_layer(
                    #         self.hazard, 'hazard reclassified')

            else:
                self.set_state_process('hazard', 'Buffering')
                self.set_state_process(
                    'hazard', 'Assign classes based on value map')

        elif self.hazard.type() == QgsMapLayer.RasterLayer:

            if self.hazard.keywords.get('layer_mode') == 'continuous':
                self.set_state_process(
                    'hazard', 'Classify continuous raster hazard')
                classifications = self.hazard.keywords.get('classification')
                hazard_classes = definition(classifications)['classes']
                ranges = OrderedDict()
                for hazard_class in reversed(hazard_classes):
                    min_value = hazard_class['numeric_default_min']
                    max_value = hazard_class['numeric_default_max']
                    ranges[hazard_class['value']] = [min_value, max_value]
                self.hazard = reclassify_raster(self.hazard, ranges)
                if self.debug:
                    self.datastore.add_layer(
                        self.hazard, 'hazard_raster_reclassified')

            self.set_state_process(
                'hazard', 'Polygonize classified raster hazard')
            self.hazard = polygonize(self.hazard)
            if self.debug:
                self.datastore.add_layer(
                    self.hazard, 'hazard_polygonized')

            self.set_state_process(
                'hazard',
                'Cleaning the vector hazard attribute table')
            # noinspection PyTypeChecker
            self.hazard = prepare_vector_layer(self.hazard)
            if self.debug:
                self.datastore.add_layer(
                    self.hazard, 'hazard_cleaned')

        else:
            raise InvalidLayerError(tr('Unsupported hazard layer type'))

        self.set_state_process(
            'hazard', 'Assign classes based on value map')
        self.hazard = assign_inasafe_values(self.hazard)
        if self.debug:
            self.datastore.add_layer(
                self.hazard, 'hazard_value_map_to_reclassified')

        self.set_state_process(
            'hazard', 'Classified polygon hazard with keywords')

        if self.hazard.crs().authid() != self.exposure.crs().authid():
            self.set_state_process(
                'hazard',
                'Reproject hazard layer to exposure CRS')
            # noinspection PyTypeChecker
            self.hazard = reproject(
                self.hazard, self.exposure.crs())
            if self.debug:
                self.datastore.add_layer(
                    self.aggregation, 'hazard_reprojected')

        self.set_state_process(
            'hazard', 'Vector clip and mask hazard to aggregation')

    @profile
    def aggregate_hazard_preparation(self):
        """This function is doing the aggregate hazard layer.

        It will prepare the aggregate layer and intersect hazard polygons with
        aggregation areas and assign hazard class.
        """
        if not self.aggregation:
            self.set_state_info('aggregation', 'provided', False)

            if not self.actual_extent:
                self._actual_extent = self.exposure.extent()

            self.set_state_process(
                'aggregation',
                'Convert bbox aggregation to polygon layer with keywords')
            self.aggregation = self.create_virtual_aggregation()
            if self.debug:
                self.datastore.add_layer(self.aggregation, 'aggr_from_bbox')

        else:
            self.set_state_info('aggregation', 'provided', True)

            self.set_state_process(
                'aggregation', 'Cleaning the aggregation layer')
            # noinspection PyTypeChecker
            self.aggregation = prepare_vector_layer(self.aggregation)
            if self.debug:
                self.datastore.add_layer(self.aggregation, 'aggr_prepared')

            if self.aggregation.crs().authid() != self.exposure.crs().authid():
                self.set_state_process(
                    'aggregation',
                    'Reproject aggregation layer to exposure CRS')
                # noinspection PyTypeChecker
                self.aggregation = reproject(
                    self.aggregation, self.exposure.crs())
                if self.debug:
                    self.datastore.add_layer(
                        self.aggregation, 'aggr_reprojected')
            else:
                self.set_state_process(
                    'aggregation',
                    'Aggregation layer already in exposure CRS')

        self.set_state_process(
            'hazard',
            'Clip and mask hazard polygons with aggregation')
        self.hazard = clip(self.hazard, self.aggregation)
        if self.debug:
            self.datastore.add_layer(
                self.hazard, 'hazard_clip_by_aggregation')

        self.set_state_process(
            'aggregation',
            'Union hazard polygons with aggregation areas and assign '
            'hazard class')
        self._aggregate_hazard = union(self.hazard, self.aggregation)
        if self.debug:
            self.datastore.add_layer(
                self._aggregate_hazard, 'aggregate_hazard')

    @profile
    def exposure_preparation(self):
        """This function is doing the exposure preparation."""
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
                'exposure',
                'Cleaning the vector exposure attribute table')
            # noinspection PyTypeChecker
            self.exposure = prepare_vector_layer(self.exposure)
            if self.debug:
                self.datastore.add_layer(
                    self.exposure, 'exposure_cleaned')

            self.set_state_process(
                'exposure', 'Assign classes based on value map')
            self.exposure = assign_inasafe_values(self.exposure)
            if self.debug:
                self.datastore.add_layer(
                    self.exposure, 'exposure_value_map_to_reclassified')

            exposure = self.exposure.keywords.get('exposure')
            geometry = self.exposure.geometryType()
            if exposure == 'structure' and geometry == QGis.Polygon:
                self.set_state_process(
                    'exposure',
                    'Smart clip')
            else:
                self.set_state_process(
                    'exposure',
                    'Clip the exposure layer with the aggregagte hazard')
                self.exposure = clip(self.exposure, self._aggregate_hazard)
                if self.debug:
                    self.datastore.add_layer(
                        self.exposure, 'exposure_clip')

    @profile
    def intersect_exposure_and_aggregate_hazard(self):
        """This function intersects the exposure with the aggregate hazard.

        This function will set the impact layer.
        """
        self.set_state_process('impact function', 'Run impact function')
        exposure = self.exposure.keywords.get('exposure')
        geometry = self.exposure.geometryType()
        if exposure == 'structure' and geometry == QGis.Polygon:
            self.set_state_process(
                'impact function',
                'Highest class of hazard is assigned when more than one '
                'overlaps')
            # self.impact = intersection(self.exposure, self._aggregate_hazard)

        else:
            self.set_state_process(
                'impact function',
                'Union exposure features to the aggregate hazard')
            self.impact = union(self.exposure, self._aggregate_hazard)

        self.datastore.add_layer(self.impact, 'intermediate-impact')

    @profile
    def post_process(self):
        """More process after getting the impact layer with data."""
        # Post processor (gender, age, building type, etc)
        # Notes, action

        for post_processor in post_processors:
            result, post_processor_output = self.run_single_post_processor(
                post_processor)
            if result:
                self.set_state_process(
                    'post_processor',
                    str('Post processor for %s' % post_processor['name']))

    @profile
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

            if not self.impact.editBuffer():

                # Turn on the editing mode.
                if not self.impact.startEditing():
                    msg = tr(
                        'The impact layer could not start the editing mode.')
                    return False, msg

            # Calculate based on formula
            # Iterate all possible output
            for output_key, output_value in post_processor['output'].items():

                # Get output attribute name
                key = output_value['value']['key']
                output_field_name = output_value['value']['field_name']
                self.impact.keywords['inasafe_fields'][key] = output_field_name

                # If there is already the output field, don't proceed
                if self.impact.fieldNameIndex(output_field_name) > -1:
                    msg = tr(
                        'The field name %s already exists.'
                        % output_field_name)
                    self.impact.rollBack()
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
                    self.impact.rollBack()
                    return False, msg

                # Get the index of output attribute
                output_field_index = self.impact.fieldNameIndex(
                    output_field_name)

                if self.impact.fieldNameIndex(output_field_name) == -1:
                    msg = tr(
                        'The field name %s has not been created.'
                        % output_field_name)
                    self.impact.rollBack()
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
                            self.impact.rollBack()
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
                            self.impact.rollBack()
                            return False, msg

                        input_indexes[key] = index

                    # For geometry, create new field that contain the value
                    elif value['type'] == 'geometry_property':
                        if value['value'] == 'size':
                            flag = False
                            # Check if size field is already exist
                            if self.impact.fieldNameIndex(
                                    size_field['field_name']) != -1:
                                flag = True
                                # temporary_indexes.append(input_indexes[key])
                            input_indexes[key] = self.add_size_field()
                            if not flag:
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
            return True, None
        else:
            self.impact.rollBack()
            return False, message

    @profile
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

    @profile
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

        size_field_index = self.impact.fieldNameIndex('size')
        # Check if size field already exist
        if size_field_index == -1:
            # Add new field, size
            self.impact.addAttribute(QgsField(
                size_field['field_name'], size_field['type']))
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
