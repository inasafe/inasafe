# coding=utf-8
"""
Impact function
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
    QGis,
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
from safe.gisv4.vector.buffering import buffering
from safe.gisv4.vector.aggregate_summary import aggregate_summary
from safe.gisv4.vector.assign_inasafe_values import assign_inasafe_values
from safe.gisv4.raster.reclassify import reclassify as reclassify_raster
from safe.gisv4.raster.polygonize import polygonize
from safe.gisv4.raster.zonal_statistics import zonal_stats
from safe.definitionsv4.fields import (
    aggregation_id_field,
    aggregation_name_field,
)
from safe.definitionsv4.post_processors import post_processors
from safe.definitionsv4.utilities import definition
from safe.defaults import get_defaults
from safe.common.exceptions import (
    InvalidExtentError,
    InvalidAggregationKeywords,
    InvalidHazardKeywords,
    InvalidExposureKeywords,
)
from safe.impact_function_v4.postprocessors import run_single_post_processor
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import replace_accentuated_characters
from safe.utilities.profiling import (
    profile, clear_prof_data, profiling_log)
from safe import messaging as m

LOGGER = logging.getLogger('InaSAFE')


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


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

        self._impact = None

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
            raise InvalidHazardKeywords(
                tr('The layer is not an hazard layer.'))

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
            raise InvalidExposureKeywords(
                tr('The layer is not an exposure layer.'))

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
            raise InvalidAggregationKeywords(
                tr('The layer is not an aggregation layer.'))

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
    def impact(self):
        """Property for the impact layer.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._impact

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
        if self._impact:
            self.post_process(self._impact)

            self.datastore.add_layer(self._impact, 'impact')

            self.set_state_process(
                'impact function',
                'Aggregate the impact summary')
            self._aggregate_hazard = aggregate_summary(
                self.aggregate_hazard, self._impact)

        self.post_process(self._aggregate_hazard)

        self.datastore.add_layer(self._aggregate_hazard, 'aggregate-hazard')

        # Get the profiling log
        self._performance_log = profiling_log()

        if self.debug:
            print 'Performance log message :'
            print self.performance_log_message().to_text()
        return self.state

    @profile
    def hazard_preparation(self):
        """This function is doing the hazard preparation."""

        if self.hazard.type() == QgsMapLayer.RasterLayer:

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

        if self.hazard.geometryType() == QGis.Polygon:

            if self.hazard.keywords.get('layer_mode') == 'continuous':
                self.set_state_process(
                    'hazard',
                    'Classify continuous hazard and assign class names')
                # self.hazard = reclassify(self.hazard, ranges)
                # if self.debug:
                #     self.datastore.add_layer(
                #         self.hazard, 'hazard reclassified')

            self.set_state_process(
                'hazard', 'Assign classes based on value map')
            self.hazard = assign_inasafe_values(self.hazard)
            if self.debug:
                self.datastore.add_layer(
                    self.hazard, 'hazard_value_map_to_reclassified')

        else:
            self.set_state_process('hazard', 'Buffering')
            classifications = self.hazard.keywords.get('classification')
            hazard_classes = definition(classifications)['classes']
            ranges = OrderedDict()
            for hazard_class in hazard_classes:
                max_value = hazard_class['numeric_default_max']
                ranges[max_value * 1000] = hazard_class['key']
            # noinspection PyTypeChecker
            self.hazard = buffering(self.hazard, ranges)
            if self.debug:
                self.datastore.add_layer(
                    self.hazard, 'buffered-hazard')

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

        If the the exposure is a continuous raster exposure, this function
            will set the aggregate hazard layer.
        However, this function will set the impact layer.
        """
        self.set_state_process('impact function', 'Run impact function')

        if self.exposure.type() == QgsMapLayer.RasterLayer:
            self.set_state_process(
                'impact function',
                'Zonal stats between exposure and aggregate hazard')
            # noinspection PyTypeChecker
            self._aggregate_hazard = zonal_stats(
                self.exposure, self.aggregate_hazard)
            if self.debug:
                self.datastore.add_layer(
                    self._aggregate_hazard, 'zonal_stats')

            # I know it's redundant, it's just to be sure that we don't have
            # any impact layer for that IF.
            self._impact = None

        else:
            exposure = self.exposure.keywords.get('exposure')
            geometry = self.exposure.geometryType()
            if exposure == 'structure' and geometry == QGis.Polygon:
                self.set_state_process(
                    'impact function',
                    'Highest class of hazard is assigned when more than one '
                    'overlaps')
                # self.impact = intersection(
                #     self.exposure, self._aggregate_hazard)

            else:
                self.set_state_process(
                    'impact function',
                    'Union exposure features to the aggregate hazard')
                self._impact = union(self.exposure, self._aggregate_hazard)

            if self.debug:
                self.datastore.add_layer(
                    self._impact, 'intermediate-impact')

    @profile
    def post_process(self, layer):
        """More process after getting the impact layer with data.

        :param layer: The vector layer to use for post processing.
        :type layer: QgsVectorLayer
        """
        # Post processor (gender, age, building type, etc)
        # Notes, action

        for post_processor in post_processors:
            result, post_processor_output = run_single_post_processor(
                layer,
                post_processor)
            if result:
                self.set_state_process(
                    'post_processor',
                    str('Post processor for %s' % post_processor['name']))
