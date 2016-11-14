# coding=utf-8
"""
Impact function
"""
from datetime import datetime
from os.path import join, exists
from os import makedirs
from collections import OrderedDict

from PyQt4.QtCore import QSettings
from qgis.core import (
    QgsMapLayer,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsVectorLayer,
    QGis,
)

import logging

from safe.common.utilities import temp_dir
from safe.datastore.folder import Folder
from safe.datastore.datastore import DataStore
from safe.gisv4.vector.prepare_vector_layer import prepare_vector_layer
from safe.gisv4.vector.reproject import reproject
from safe.gisv4.vector.assign_highest_value import assign_highest_value
from safe.gisv4.vector.reclassify import reclassify as reclassify_vector
from safe.gisv4.vector.union import union
from safe.gisv4.vector.clip import clip
from safe.gisv4.vector.smart_clip import smart_clip
from safe.gisv4.vector.summary_1_aggregate_hazard import (
    aggregate_hazard_summary)
from safe.gisv4.vector.summary_2_aggregation import aggregation_summary
from safe.gisv4.vector.summary_3_analysis import analysis_summary
from safe.gisv4.vector.summary_4_exposure_breakdown import (
    exposure_type_breakdown)
from safe.gisv4.vector.recompute_counts import recompute_counts
from safe.gisv4.vector.update_value_map import update_value_map
from safe.gisv4.raster.reclassify import reclassify as reclassify_raster
from safe.gisv4.raster.polygonize import polygonize
from safe.gisv4.raster.zonal_statistics import zonal_stats
from safe.definitionsv4.post_processors import post_processors
from safe.definitionsv4.analysis_steps import analysis_steps
from safe.definitionsv4.utilities import definition
from safe.definitionsv4.exposure import indivisible_exposure
from safe.definitionsv4.fields import (
    size_field, exposure_class_field, hazard_class_field)
from safe.definitionsv4.constants import inasafe_keyword_version_key
from safe.definitionsv4.versions import inasafe_keyword_version
from safe.common.exceptions import (
    InvalidExtentError,
    InvalidLayerError,
    InvalidAggregationKeywords,
    InvalidHazardKeywords,
    InvalidExposureKeywords,
)
from safe.impact_function_v4.postprocessors import (
    run_single_post_processor, enough_input)
from safe.impact_function_v4.create_extra_layers import (
    create_analysis_layer, create_virtual_aggregation, create_profile_layer)
from safe.impact_function_v4.style import (
    hazard_class_style,
    simple_polygon_without_brush,
)
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import replace_accentuated_characters
from safe.utilities.profiling import (
    profile, clear_prof_data, profiling_log)
from safe.test.utilities import check_inasafe_fields
from safe import messaging as m

LOGGER = logging.getLogger('InaSAFE')


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class ImpactFunction(object):
    """Impact Function."""

    def __init__(self):

        # Input layers
        self._hazard = None
        self._exposure = None
        self._aggregation = None

        # Output layers
        self._exposure_impacted = None
        self._aggregate_hazard_impacted = None
        self._aggregation_impacted = None
        self._analysis_impacted = None
        self._exposure_breakdown = None
        self._profiling_table = None

        # Use debug to store intermediate results
        self.debug_mode = False

        # Requested extent to use
        self._requested_extent = None
        # Requested extent's CRS
        self._requested_extent_crs = None

        # The current viewport extent of the map canvas
        self._viewport_extent = None
        # Current viewport extent's CRS
        self._viewport_extent_crs = None

        # set this to a gui call back / web callback etc as needed.
        self._callback = self.console_progress_callback

        # Names
        self._name = None  # e.g. Flood Raster on Building Polygon
        self._title = None  # be affected
        self._unique_name = None  # EXP + On + Haz + DDMMMMYYYY + HHhMM.SS

        # Datastore when to save layers
        self._datastore = None

        # Metadata on the IF
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
        row.add(m.Cell(tr('Time')), header_flag=True)
        table.add(row)

        if self.performance_log is None:
            message.add(table)
            return message

        indent = -1

        def display_tree(tree, space):
            space += 1
            new_row = m.Row()

            # This is a kind of hack to display the tree with indentation
            text = '|'
            text += '*' * space

            if tree.children:
                text += '\ '
            else:
                text += '| '
            text += tree.__str__()

            new_row.add(m.Cell(text))
            new_row.add(m.Cell(tree.elapsed_time))
            table.add(new_row)
            if tree.children:
                for child in tree.children:
                    display_tree(child, space)
            space -= 1

        # noinspection PyTypeChecker
        display_tree(self.performance_log, indent)
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

        version = keywords.get(inasafe_keyword_version_key)
        if version != inasafe_keyword_version:
            parameters = {
                'version': inasafe_keyword_version,
                'source': layer.source()
            }
            raise InvalidHazardKeywords(
                tr('The layer {source} must be updated to {version}.'.format(
                    **parameters)))

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

        version = keywords.get(inasafe_keyword_version_key)
        if version != inasafe_keyword_version:
            parameters = {
                'version': inasafe_keyword_version,
                'source': layer.source()
            }
            raise InvalidHazardKeywords(
                tr('The layer {source} must be updated to {version}.'.format(
                    **parameters)))

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

        version = keywords.get(inasafe_keyword_version_key)
        if version != inasafe_keyword_version:
            parameters = {
                'version': inasafe_keyword_version,
                'source': layer.source()
            }
            raise InvalidHazardKeywords(
                tr('The layer {source} must be updated to {version}.'.format(
                    **parameters)))

        self._aggregation = layer
        self._aggregation.keywords = keywords

    @property
    def outputs(self):
        """List of layers containing outputs from the IF.

        :returns: A list of vector layers.
        :rtype: list
        """
        layers = [
            self._exposure_impacted,
            self._aggregate_hazard_impacted,
            self._aggregation_impacted,
            self._analysis_impacted,
            self._exposure_breakdown,
        ]

        # Remove layers which are not set.
        layers = filter(None, layers)
        return layers

    @property
    def impact(self):
        """Property for the most detailed output.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self.outputs[0]

    @property
    def exposure_impacted(self):
        """Property for the exposure impacted.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._exposure_impacted

    @property
    def aggregate_hazard_impacted(self):
        """Property for the aggregate hazard impacted.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._aggregate_hazard_impacted

    @property
    def aggregation_impacted(self):
        """Property for the aggregation impacted.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._aggregation_impacted

    @property
    def analysis_impacted(self):
        """Property for the analysis layer.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._analysis_impacted

    @property
    def exposure_breakdown(self):
        """Return the exposure breakdown if available.

        It's a QgsVectorLayer without geometry.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._exposure_breakdown

    @property
    def profiling(self):
        """Return the profiling layer.

        It's a QgsVectorLayer without geometry.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._profiling_table

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
        if isinstance(crs, QgsCoordinateReferenceSystem):
            self._requested_extent_crs = crs
        else:
            raise InvalidExtentError('%s is not a valid CRS object.' % crs)

    @property
    def viewport_extent(self):
        """Property for the viewport extent of the map canvas.

        :returns: A QgsRectangle.
        :rtype: QgsRectangle
        """
        return self._viewport_extent

    @viewport_extent.setter
    def viewport_extent(self, extent):
        """Setter for the viewport extent of the map canvas.

        :param extent: Analysis boundaries expressed as a
        QgsRectangle. The extent CRS should match the extent_crs property of
        this IF instance.
        :type extent: QgsRectangle
        """
        self._viewport_extent = extent
        if isinstance(extent, QgsRectangle):
            self._viewport_extent = extent
        else:
            raise InvalidExtentError('%s is not a valid extent.' % extent)

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
        if isinstance(datastore, DataStore):
            self._datastore = datastore
        else:
            raise Exception('%s is not a valid datastore.' % datastore)

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

            self.progress_callback(current, maximum, message=None)

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

        :param message: Optional message dictionary to containing content
            we can display to the user. See safe.definitions.analysis_steps
            for an example of the expected format
        :type message: dict
        """
        # noinspection PyChainedComparisons
        if maximum > 1000 and current % 1000 != 0 and current != maximum:
            return
        if message is not None:
            LOGGER.info(message['description'])
        LOGGER.info('Task progress: %i of %i' % (current, maximum))

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
        LOGGER.debug('%s: %s: %s' % (context, key, value))
        self.state[context]["info"][key] = value

    def validate(self):
        """Method to check if the impact function can be run."""
        if not self.exposure:
            raise InvalidLayerError(tr('The exposure layer is compulsory.'))

        if not self.hazard:
            raise InvalidLayerError(tr('The hazard layer is compulsory.'))

        if self.aggregation:
            if self.requested_extent:
                raise InvalidExtentError(
                    tr('Requested Extent must be null when an aggregation is '
                       'provided.'))
            if self.requested_extent_crs:
                raise InvalidExtentError(
                    tr('Requested Extent CRS must be null when an aggregation '
                       'is provided.'))
            if self._viewport_extent:
                raise InvalidExtentError(
                    tr('Viewport Extent must be null when an aggregation is '
                       'provided.'))
            if self._viewport_extent_crs:
                raise InvalidExtentError(
                    tr('Viewport CRS must be null when an aggregation is '
                       'provided.'))

    def debug_layer(self, layer, check_fields=True):
        """Write the layer produced to the datastore if debug mode is on.

        :param layer: The QGIS layer to check and save.
        :type layer: QgsMapLayer

        :param check_fields: Boolean to check or not inasafe_fields
        :type check_fields: bool
        """
        name = self.datastore.add_layer(layer, layer.keywords['title'])

        if isinstance(layer, QgsVectorLayer) and check_fields:
            check_inasafe_fields(layer)

        return name

    def run(self):
        """Run the whole impact function."""

        self.validate()

        self.reset_state()
        clear_prof_data()
        self._run()

        # Get the profiling log
        self._performance_log = profiling_log()
        self.callback(8, 8, analysis_steps['profiling'])

        if self.debug_mode:
            self._profiling_table = create_profile_layer(
                self.performance_log_message())
            _, name = self.debug_layer(self._profiling_table)
            self._profiling_table = self.datastore.layer(name)
            check_inasafe_fields(self._profiling_table)

        # Later, we should move this call.
        self.style()

        return self.state

    @profile
    def _run(self):
        """Internal function to run the impact function with profiling."""
        step_count = len(analysis_steps)
        self.callback(0, step_count, analysis_steps['initialisation'])

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
            self.callback(1, step_count, analysis_steps['data_store'])

            settings = QSettings()
            default_user_directory = settings.value(
                'inasafe/defaultUserDirectory', defaultValue='')
            if default_user_directory:
                path = join(default_user_directory, self._unique_name)
                if not exists(path):
                    makedirs(path)
                self._datastore = Folder(path)
            else:
                self._datastore = Folder(temp_dir(sub_dir=self._unique_name))

            self._datastore.default_vector_format = 'geojson'
            if self.debug_mode:
                print 'Temporary datastore'
                print self.datastore.uri.absolutePath()

            LOGGER.debug('Datastore : %s' % self.datastore.uri.absolutePath())

        if self.debug_mode:
            self._datastore.use_index = True

            self.datastore.add_layer(self.exposure, 'exposure')
            self.datastore.add_layer(self.hazard, 'hazard')
            if self.aggregation:
                self.datastore.add_layer(self.aggregation, 'aggregation')

        # Special case for Raster Earthquake hazard on Raster population.
        if self.hazard.type() == QgsMapLayer.RasterLayer:
            if self.hazard.keywords.get('hazard') == 'earthquake':
                if self.exposure.type() == QgsMapLayer.RasterLayer:
                    if self.exposure.keywords.get('exposure') == 'population':
                        # return self.state()

                        # These layers are not generated.
                        self._exposure_impacted = None
                        self._aggregate_hazard_impacted = None
                        return

        self._performance_log = profiling_log()
        self.callback(2, step_count, analysis_steps['hazard_preparation'])
        self.hazard_preparation()

        self._performance_log = profiling_log()
        self.callback(3, step_count, analysis_steps['aggregation_preparation'])
        self.aggregation_preparation()

        self._performance_log = profiling_log()
        self.callback(
            4, step_count, analysis_steps['aggregate_hazard_preparation'])
        self.aggregate_hazard_preparation()

        self._performance_log = profiling_log()
        self.callback(5, step_count, analysis_steps['exposure_preparation'])
        self.exposure_preparation()

        self._performance_log = profiling_log()
        self.callback(6, step_count, analysis_steps['combine_hazard_exposure'])
        self.intersect_exposure_and_aggregate_hazard()

        self._performance_log = profiling_log()
        self.callback(7, step_count, analysis_steps['post_processing'])
        if self._exposure_impacted:
            self._performance_log = profiling_log()
            # We post process the exposure impacted
            self.post_process(self._exposure_impacted)
        else:
            if self._aggregate_hazard_impacted:
                # We post process the aggregate hazard.
                # Raster continuous exposure.
                self.post_process(self._aggregate_hazard_impacted)
            else:
                # We post process the aggregation.
                # Earthquake raster on population raster.
                self.post_process(self._aggregation_impacted)

        self._performance_log = profiling_log()
        self.callback(8, step_count, analysis_steps['summary_calculation'])
        self.summary_calculation()

        # End of the impact function, we can add layers to the datastore.
        # We replace memory layers by the real layer from the datastore.
        if self._exposure_impacted:
            _, name = self.datastore.add_layer(
                self._exposure_impacted, 'exposure_impacted')
            self._exposure_impacted = self.datastore.layer(name)
            if self.debug_mode:
                check_inasafe_fields(self._exposure_impacted)

        if self.aggregate_hazard_impacted:
            _, name = self.datastore.add_layer(
                self._aggregate_hazard_impacted, 'aggregate_hazard_impacted')
            self._aggregate_hazard = self.datastore.layer(name)
            if self.debug_mode:
                check_inasafe_fields(self._aggregate_hazard)

            if self._exposure.keywords.get('classification'):
                _, name = self.datastore.add_layer(
                    self._exposure_breakdown, 'exposure_breakdown')
                self._exposure_breakdown = self.datastore.layer(name)
                if self.debug_mode:
                    check_inasafe_fields(self._exposure_breakdown)

        _, name = self.datastore.add_layer(
            self._aggregation_impacted, 'aggregation_impacted')
        self._aggregation_impacted = self.datastore.layer(name)
        if self.debug_mode:
            check_inasafe_fields(self._aggregation_impacted)

        _, name = self.datastore.add_layer(self._analysis_impacted, 'analysis')
        self._analysis_impacted = self.datastore.layer(name)
        if self.debug_mode:
            check_inasafe_fields(self._analysis_impacted)

    @profile
    def hazard_preparation(self):
        """This function is doing the hazard preparation."""

        if self.hazard.type() == QgsMapLayer.RasterLayer:

            if self.hazard.keywords.get('layer_mode') == 'continuous':

                self.set_state_process(
                    'hazard', 'Classify continuous raster hazard')
                # noinspection PyTypeChecker
                self.hazard = reclassify_raster(self.hazard)
                if self.debug_mode:
                    self.debug_layer(self.hazard)

            self.set_state_process(
                'hazard', 'Polygonize classified raster hazard')
            # noinspection PyTypeChecker
            self.hazard = polygonize(self.hazard)
            if self.debug_mode:
                self.debug_layer(self.hazard)

        self.set_state_process(
            'hazard',
            'Cleaning the vector hazard attribute table')
        # noinspection PyTypeChecker
        self.hazard = prepare_vector_layer(self.hazard)
        if self.debug_mode:
            self.debug_layer(self.hazard)

        if self.hazard.keywords.get('layer_mode') == 'continuous':
            self.set_state_process(
                'hazard',
                'Classify continuous hazard and assign class names')
            self.hazard = reclassify_vector(self.hazard)
            if self.debug_mode:
                self.debug_layer(self.hazard)

        self.set_state_process(
            'hazard', 'Assign classes based on value map')
        self.hazard = update_value_map(self.hazard)
        if self.debug_mode:
            self.debug_layer(self.hazard)

        self.set_state_process(
            'hazard', 'Classified polygon hazard with keywords')

        if self.hazard.crs().authid() != self.exposure.crs().authid():
            self.set_state_process(
                'hazard',
                'Reproject hazard layer to exposure CRS')
            # noinspection PyTypeChecker
            self.hazard = reproject(
                self.hazard, self.exposure.crs())
            if self.debug_mode:
                self.debug_layer(self.hazard)

        self.set_state_process(
            'hazard', 'Vector clip and mask hazard to aggregation')

    @profile
    def aggregation_preparation(self):
        """This function is doing the aggregation preparation."""
        if not self.aggregation:
            self.set_state_info('aggregation', 'provided', False)

            self.set_state_process(
                'aggregation',
                'Convert bbox aggregation to polygon layer with keywords')
            self.aggregation = create_virtual_aggregation(
                self.exposure.extent(), self.exposure.crs())
            if self.debug_mode:
                self.debug_layer(self.aggregation)

        else:
            self.set_state_info('aggregation', 'provided', True)

            self.set_state_process(
                'aggregation', 'Cleaning the aggregation layer')
            # noinspection PyTypeChecker
            self.aggregation = prepare_vector_layer(self.aggregation)
            if self.debug_mode:
                self.debug_layer(self.aggregation)

            if self.aggregation.crs().authid() != self.exposure.crs().authid():
                self.set_state_process(
                    'aggregation',
                    'Reproject aggregation layer to exposure CRS')
                # noinspection PyTypeChecker
                self.aggregation = reproject(
                    self.aggregation, self.exposure.crs())
                if self.debug_mode:
                    self.debug_layer(self.aggregation)

            else:
                self.set_state_process(
                    'aggregation',
                    'Aggregation layer already in exposure CRS')

        self.set_state_process(
            'aggregation',
            'Convert the aggregation layer to the analysis layer')
        self._analysis_impacted = create_analysis_layer(
            self.aggregation, self.exposure.crs(), self.name)
        if self.debug_mode:
            self.debug_layer(self._analysis_impacted)

    @profile
    def aggregate_hazard_preparation(self):
        """This function is doing the aggregate hazard layer.

        It will prepare the aggregate layer and intersect hazard polygons with
        aggregation areas and assign hazard class.
        """
        self.set_state_process(
            'hazard',
            'Clip and mask hazard polygons with the analysis layer')
        self.hazard = clip(self.hazard, self._analysis_impacted)
        if self.debug_mode:
            self.debug_layer(self.hazard)

        self.set_state_process(
            'aggregation',
            'Union hazard polygons with aggregation areas and assign '
            'hazard class')
        self._aggregate_hazard_impacted = union(self.hazard, self.aggregation)
        if self.debug_mode:
            self.debug_layer(self._aggregate_hazard_impacted)

    @profile
    def exposure_preparation(self):
        """This function is doing the exposure preparation."""
        if self.exposure.type() == QgsMapLayer.RasterLayer:
            if self.exposure.keywords.get('layer_mode') == 'continuous':
                if self.exposure.keywords.get('exposure_unit') == 'density':
                    self.set_state_process(
                        'exposure', 'Calculate counts per cell')
                    # Todo, Need to write this algorithm.

                # We don't do any other process to a continuous raster.
                return

            else:
                self.set_state_process(
                    'exposure', 'Polygonise classified raster exposure')
                # noinspection PyTypeChecker
                self.exposure = polygonize(self.exposure)
                if self.debug_mode:
                    self.debug_layer(self.exposure)

        self.set_state_process(
            'exposure',
            'Cleaning the vector exposure attribute table')
        # noinspection PyTypeChecker
        self.exposure = prepare_vector_layer(self.exposure)
        if self.debug_mode:
            self.debug_layer(self.exposure)

        fields = self.exposure.keywords['inasafe_fields']
        if exposure_class_field['key'] not in fields:
            self.set_state_process(
                'exposure', 'Assign classes based on value map')
            self.exposure = update_value_map(self.exposure)
            if self.debug_mode:
                self.debug_layer(self.exposure)

        exposure = self.exposure.keywords.get('exposure')
        indivisible_keys = [f['key'] for f in indivisible_exposure]
        geometry = self.exposure.geometryType()
        if exposure in indivisible_keys and geometry != QGis.Point:
            self.set_state_process(
                'exposure',
                'Smart clip')
            self.exposure = smart_clip(
                self.exposure, self._analysis_impacted)
        else:
            self.set_state_process(
                'exposure',
                'Clip the exposure layer with the analysis layer')
            self.exposure = clip(self.exposure, self._analysis_impacted)

        if self.debug_mode:
            self.debug_layer(self.exposure)

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
            self._aggregate_hazard_impacted = zonal_stats(
                self.exposure, self._aggregate_hazard_impacted)
            if self.debug_mode:
                self.debug_layer(self._aggregate_hazard_impacted)

            # I know it's redundant, it's just to be sure that we don't have
            # any impact layer for that IF.
            self._exposure_impacted = None

        else:
            exposure = self.exposure.keywords.get('exposure')
            indivisible_keys = [f['key'] for f in indivisible_exposure]
            geometry = self.exposure.geometryType()
            if exposure in indivisible_keys and geometry != QGis.Point:
                self.set_state_process(
                    'impact function',
                    'Highest class of hazard is assigned when more than one '
                    'overlaps')
                self._exposure_impacted = assign_highest_value(
                    self.exposure, self._aggregate_hazard_impacted)

            else:
                self.set_state_process(
                    'impact function',
                    'Union exposure features to the aggregate hazard')
                self._exposure_impacted = union(
                    self.exposure, self._aggregate_hazard_impacted)

                # If the layer has the size field, it means we need to
                # recompute counts based on the old and new size.
                fields = self.exposure.keywords['inasafe_fields']
                if size_field['key'] in fields:
                    self.set_state_process(
                        'exposure',
                        'Recompute counts')
                    self._exposure_impacted = recompute_counts(
                        self._exposure_impacted)

            if self.debug_mode:
                self.debug_layer(self._exposure_impacted)

        if self._exposure_impacted:
            self._exposure_impacted.keywords['title'] = 'exposure_impacted'

    @profile
    def post_process(self, layer):
        """More process after getting the impact layer with data.

        :param layer: The vector layer to use for post processing.
        :type layer: QgsVectorLayer
        """
        # Post processor (gender, age, building type, etc)
        # Notes, action

        for post_processor in post_processors:
            valid, message = enough_input(layer, post_processor['input'])

            if valid:
                valid, message = run_single_post_processor(
                    layer, post_processor)
                if valid:
                    msg = str('Post processor for %s' % post_processor['name'])
                    self.set_state_process('post_processor', msg)
                    LOGGER.info(msg)
                else:
                    LOGGER.info(message)
            else:
                LOGGER.info(message)

    def summary_calculation(self):
        """Do the summary calculation."""

        if self._exposure_impacted:
            self.set_state_process(
                'impact function',
                'Aggregate the impact summary')
            self._aggregate_hazard_impacted = aggregate_hazard_summary(
                self.exposure_impacted, self._aggregate_hazard_impacted)

        if self._aggregate_hazard_impacted:
            self.set_state_process(
                'impact function',
                'Aggregate the aggregation summary')
            self._aggregation_impacted = aggregation_summary(
                self._aggregate_hazard_impacted, self.aggregation)

            self.set_state_process(
                'impact function',
                'Aggregate the analysis summary')
            self._analysis_impacted = analysis_summary(
                self._aggregate_hazard_impacted, self._analysis_impacted)

            if self._exposure.keywords.get('classification'):
                self.set_state_process(
                    'impact function',
                    'Build the exposure breakdown')
                self._exposure_breakdown = exposure_type_breakdown(
                    self._aggregate_hazard_impacted)

    def style(self):
        """Function to apply some styles to the layers."""
        # Let's style the hazard class in each layers.
        classification = self.hazard.keywords['classification']
        classification = definition(classification)

        classes = OrderedDict()
        for f in reversed(classification['classes']):
            classes[f['key']] = (f['color'], f['name'])

        # Let's style layers which have a geometry and have hazard_class
        hazard_class = hazard_class_field['key']
        for layer in self.outputs:
            if layer.geometryType() != QGis.NoGeometry:
                if layer.keywords['inasafe_fields'].get(hazard_class):
                    hazard_class_style(layer, classes)

        # Let's style the aggregation and analysis layer.
        simple_polygon_without_brush(self.aggregation_impacted)
        simple_polygon_without_brush(self.analysis_impacted)
