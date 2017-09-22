# coding=utf-8

"""Impact Function."""

import getpass
from datetime import datetime
from os.path import join, exists
from os import makedirs
from collections import OrderedDict
from socket import gethostname

from PyQt4.QtCore import QT_VERSION_STR, QSettings
from PyQt4.Qt import PYQT_VERSION_STR
from osgeo import gdal
from qgis.core import (
    QgsMapLayer,
    QgsGeometry,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsVectorLayer,
    QGis
)

import logging

from safe.common.utilities import temp_dir
from safe.common.version import get_version
from safe.datastore.folder import Folder
from safe.datastore.datastore import DataStore
from safe.gis.sanity_check import check_inasafe_fields, check_layer
from safe.gis.vector.tools import remove_fields
from safe.gis.vector.from_counts_to_ratios import from_counts_to_ratios
from safe.gis.vector.prepare_vector_layer import prepare_vector_layer
from safe.gis.vector.clean_geometry import clean_layer
from safe.gis.vector.reproject import reproject
from safe.gis.vector.assign_highest_value import assign_highest_value
from safe.gis.vector.default_values import add_default_values
from safe.gis.vector.reclassify import reclassify as reclassify_vector
from safe.gis.vector.union import union
from safe.gis.vector.clip import clip
from safe.gis.vector.smart_clip import smart_clip
from safe.gis.vector.intersection import intersection
from safe.gis.vector.summary_1_aggregate_hazard import (
    aggregate_hazard_summary)
from safe.gis.vector.summary_2_aggregation import aggregation_summary
from safe.gis.vector.summary_3_analysis import analysis_summary
from safe.gis.vector.summary_4_exposure_summary_table import (
    exposure_summary_table)
from safe.gis.vector.recompute_counts import recompute_counts
from safe.gis.vector.update_value_map import update_value_map
from safe.gis.raster.clip_bounding_box import clip_by_extent
from safe.gis.raster.reclassify import reclassify as reclassify_raster
from safe.gis.raster.polygonize import polygonize
from safe.gis.raster.zonal_statistics import zonal_stats
from safe.definitions.analysis_steps import analysis_steps
from safe.definitions.utilities import (
    definition,
    get_non_compulsory_fields,
    get_name,
    set_provenance
)
from safe.definitions.exposure import indivisible_exposure
from safe.definitions.fields import (
    size_field,
    exposure_class_field,
    hazard_class_field,
)
from safe.definitions import count_ratio_mapping, post_processors
from safe.definitions.layer_purposes import (
    layer_purpose_exposure,
    layer_purpose_exposure_summary,
    layer_purpose_aggregate_hazard_impacted,
    layer_purpose_aggregation_summary,
    layer_purpose_analysis_impacted,
    layer_purpose_exposure_summary_table,
    layer_purpose_profiling,
)
from safe.definitions.styles import (
    aggregation_color,
    aggregation_width,
    analysis_color,
    analysis_width)

from safe.definitions.provenance import (
    provenance_action_checklist,
    provenance_aggregation_keywords,
    provenance_aggregation_layer,
    provenance_aggregation_layer_id,
    provenance_analysis_extent,
    provenance_analysis_question,
    provenance_data_store_uri,
    provenance_duration,
    provenance_end_datetime,
    provenance_exposure_keywords,
    provenance_exposure_layer,
    provenance_exposure_layer_id,
    provenance_gdal_version,
    provenance_hazard_keywords,
    provenance_hazard_layer,
    provenance_hazard_layer_id,
    provenance_host_name,
    provenance_impact_function_name,
    provenance_impact_function_title,
    provenance_inasafe_version,
    provenance_map_legend_title,
    provenance_map_title,
    provenance_notes,
    provenance_os,
    provenance_pyqt_version,
    provenance_qgis_version,
    provenance_qt_version,
    provenance_requested_extent,
    provenance_start_datetime,
    provenance_user,
    provenance_layer_exposure_summary,
    provenance_layer_aggregate_hazard_impacted,
    provenance_layer_aggregation_summary,
    provenance_layer_analysis_impacted,
    provenance_layer_exposure_summary_table,
    provenance_layer_aggregate_hazard_impacted_id,
    provenance_layer_aggregation_summary_id,
    provenance_layer_exposure_summary_table_id,
    provenance_layer_profiling_id,
    provenance_layer_analysis_impacted_id,
    provenance_layer_exposure_summary_id,
    provenance_crs)
from safe.impact_function.provenance_utilities import (
    get_map_title, get_analysis_question)

from safe.definitions.constants import (
    inasafe_keyword_version_key,
    GLOBAL,
    ANALYSIS_SUCCESS,
    ANALYSIS_FAILED_BAD_INPUT,
    ANALYSIS_FAILED_BAD_CODE,
    PREPARE_SUCCESS,
    PREPARE_FAILED_BAD_INPUT,
    PREPARE_FAILED_INSUFFICIENT_OVERLAP,
    PREPARE_FAILED_INSUFFICIENT_OVERLAP_REQUESTED_EXTENT,
    PREPARE_FAILED_BAD_LAYER,
    PREPARE_FAILED_BAD_CODE)
from safe.definitions.hazard_exposure_specifications import (
    specific_actions, specific_notes)
from safe.definitions.versions import inasafe_keyword_version
from safe.common.exceptions import (
    InaSAFEError,
    InvalidExtentError,
    InvalidLayerError,
    WrongEarthquakeFunction,
    NoKeywordsFoundError,
    NoFeaturesInExtentError,
    ProcessingInstallationError,
)
from safe.definitions.earthquake import EARTHQUAKE_FUNCTIONS
from safe.impact_function.postprocessors import (
    run_single_post_processor, enough_input)
from safe.impact_function.create_extra_layers import (
    create_analysis_layer,
    create_virtual_aggregation,
    create_profile_layer,
    create_valid_aggregation,
)
from safe.impact_function.style import (
    layer_title,
    generate_classified_legend,
    hazard_class_style,
    simple_polygon_without_brush,
)
from safe.utilities.gis import is_vector_layer, is_raster_layer
from safe.utilities.i18n import tr
from safe.utilities.default_values import get_inasafe_default_value_qsetting
from safe.utilities.unicode import get_unicode
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.metadata import (
    active_thresholds_value_maps, copy_layer_keywords, write_iso19115_metadata)
from safe.utilities.utilities import (
    replace_accentuated_characters,
    get_error_message,
    is_keyword_version_supported,
    readable_os_version)
from safe.utilities.profiling import (
    profile, clear_prof_data, profiling_log)
from safe.utilities.gis import qgis_version
from safe.utilities.settings import setting
from safe import messaging as m
from safe.messaging import styles
from safe.gui.widgets.message import generate_input_error_message

SUGGESTION_STYLE = styles.GREEN_LEVEL_4_STYLE
WARNING_STYLE = styles.RED_LEVEL_4_STYLE

LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class ImpactFunction(object):

    """Impact Function."""

    def __init__(self):
        """Constructor."""
        # Input layers
        self._hazard = None
        self._exposure = None
        self._aggregation = None

        # If there is an aggregation layer provided, do we use selected
        # features only ?
        self.use_selected_features_only = False

        # Output layers
        self._exposure_summary = None
        self._aggregate_hazard_impacted = None
        self._aggregation_summary = None
        self._analysis_impacted = None
        self._exposure_summary_table = None
        self._profiling_table = None

        # Use debug to store intermediate results
        self.debug_mode = False

        # Requested extent to use
        self._requested_extent = None
        # Requested extent's CRS
        self._requested_extent_crs = None
        # Use exposure view only
        self.use_exposure_view_only = False

        # The current extent defined by the impact function. Read-only.
        # The CRS is the exposure CRS.
        self._analysis_extent = None

        # set this to a gui call back / web callback etc as needed.
        self._callback = self.console_progress_callback

        # Names
        self._name = None  # e.g. Flood Raster on Building Polygon
        self._title = None  # be affected
        self._unique_name = None  # EXP + On + Haz + DDMMMMYYYY + HHhMM.SS.ms

        # Datastore when to save layers
        self._datastore = None

        # Metadata on the IF
        self.state = {}
        self._performance_log = None
        self.reset_state()
        self._is_ready = False
        self._provenance_ready = False
        self._start_datetime = None
        self._end_datetime = None
        self._duration = 0
        self._provenance = {}
        # Environment
        set_provenance(self._provenance, provenance_host_name, gethostname())
        set_provenance(self._provenance, provenance_user, getpass.getuser())
        set_provenance(
            self._provenance, provenance_qgis_version, QGis.QGIS_VERSION)
        set_provenance(
            self._provenance, provenance_gdal_version, gdal.__version__)
        set_provenance(self._provenance, provenance_qt_version, QT_VERSION_STR)
        set_provenance(
            self._provenance, provenance_pyqt_version, PYQT_VERSION_STR)
        set_provenance(
            self._provenance, provenance_os, readable_os_version())
        set_provenance(
            self._provenance, provenance_inasafe_version, get_version())

        # Earthquake function
        value = setting(
            'earthquake_function', EARTHQUAKE_FUNCTIONS[0]['key'], str)
        if value not in [model['key'] for model in EARTHQUAKE_FUNCTIONS]:
            raise WrongEarthquakeFunction
        self._earthquake_function = value

    @property
    def performance_log(self):
        """Property for the performance log that can be used for benchmarking.

        :returns: A dict containing benchmarking data.
        :rtype: dict
        """
        return self._performance_log

    def performance_log_message(self):
        """Return the profiling log as a message."""
        message = m.Message()
        table = m.Table(style_class='table table-condensed table-striped')
        row = m.Row()
        row.add(m.Cell(tr('Function'), header=True))
        row.add(m.Cell(tr('Time'), header=True))
        if setting(key='memory_profile', expected_type=bool):
            row.add(m.Cell(tr('Memory'), header=True))
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

            busy = tr('Busy')
            new_row.add(m.Cell(text))
            time = tree.elapsed_time
            if time is None:
                time = busy
            new_row.add(m.Cell(time))
            if setting(key='memory_profile', expected_type=bool):
                memory_used = tree.memory_used
                if memory_used is None:
                    memory_used = busy
                new_row.add(m.Cell(memory_used))
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
        """
        self._hazard = layer
        self._is_ready = False

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
        self._is_ready = False

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
        """
        self._aggregation = layer
        self._is_ready = False

    @property
    def is_ready(self):
        """Property to know if the impact function is ready.

        :return: If the impact function is ready.
        :rtype: bool
        """
        return self._is_ready

    @property
    def outputs(self):
        """List of layers containing outputs from the IF.

        :returns: A list of vector layers.
        :rtype: list
        """
        layers = OrderedDict()
        layers[layer_purpose_exposure_summary['key']] = (
            self._exposure_summary)
        layers[layer_purpose_aggregate_hazard_impacted['key']] = (
            self._aggregate_hazard_impacted)
        layers[layer_purpose_aggregation_summary['key']] = (
            self._aggregation_summary)
        layers[layer_purpose_analysis_impacted['key']] = (
            self._analysis_impacted)
        layers[layer_purpose_exposure_summary_table['key']] = (
            self._exposure_summary_table)
        layers[layer_purpose_profiling['key']] = self._profiling_table

        for expected_purpose, layer in layers.iteritems():
            if layer:
                purpose = layer.keywords['layer_purpose']
                if purpose != expected_purpose:
                    # ET 18/11/16
                    # I'm disabling this check. If an exception is raised in
                    # the IF, this exception might be raised and will hide the
                    # other one.
                    # raise Exception('Wrong layer purpose : %s != %s' % (
                    #     purpose, expected_purpose))
                    pass

        # Remove layers which are not set.
        layers = [layer for layer in layers.values() if layer]
        return layers

    @property
    def impact(self):
        """Property for the most detailed output vector layer.

        :returns: A vector layer.
        :rtype: QgsMapLayer
        """
        return self.outputs[0]

    @property
    def exposure_summary(self):
        """Property for the exposure summary.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._exposure_summary

    @property
    def aggregate_hazard_impacted(self):
        """Property for the aggregate hazard impacted.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._aggregate_hazard_impacted

    @property
    def aggregation_summary(self):
        """Property for the aggregation summary.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._aggregation_summary

    @property
    def analysis_impacted(self):
        """Property for the analysis layer.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._analysis_impacted

    @property
    def exposure_summary_table(self):
        """Return the exposure summary table if available.

        It's a QgsVectorLayer without geometry.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._exposure_summary_table

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
        """Property for the extent requested by the user.

        It can be the extent from the map canvas, a bookmark or bbox ...

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
            self._is_ready = False
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
            self._is_ready = False
        else:
            raise InvalidExtentError('%s is not a valid CRS object.' % crs)

    @property
    def analysis_extent(self):
        """Property for the analysis extent.

        :returns: A polygon.
        :rtype: QgsGeometry
        """
        return self._analysis_extent

    @property
    def datastore(self):
        """Return the current datastore.

        :return: The datastore.
        :rtype: Datastore.Datastore
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
        """The name of the impact function.

        :returns: The name.
        :rtype: basestring
        """
        return self._name

    @property
    def title(self):
        """The title of the impact function.

        :returns: The title.
        :rtype: basestring
        """
        return self._title

    @property
    def start_datetime(self):
        """The timestamp when the impact function start to run.

        :return: The start timestamp.
        :rtype: datetime
        """
        return self._start_datetime

    @property
    def end_datetime(self):
        """The timestamp when the impact function finish the run process.

        :return: The start timestamp.
        :rtype: datetime
        """
        return self._end_datetime

    @property
    def duration(self):
        """The duration of running the impact function in seconds.

        Return 0 if the start or end datetime is None.

        :return: The duration.
        :rtype: float
        """
        if self.end_datetime is None or self.start_datetime is None:
            return 0
        return (self.end_datetime - self.start_datetime).total_seconds()

    @property
    def earthquake_function(self):
        """The current earthquake function to use.

        There is not setter for the earthquake fatality function. You need to
        use the key inasafe/earthquake_function in QSettings.

        :return: The earthquake function.
        :rtype: str
        """
        return self._earthquake_function

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
        """Method to reset the state of the impact function."""
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
        LOGGER.info('%s: %s' % (context, process))
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
        LOGGER.info('%s: %s: %s' % (context, key, value))
        self.state[context]["info"][key] = value

    @staticmethod
    def _check_layer(layer, purpose):
        """Private function to check if the layer is valid.

        The function will also set the monkey patching if needed.

        :param layer: The layer to test.
        :type layer: QgsMapLayer

        :param purpose: The expected purpose of the layer.
        :type purpose: basestring

        :return: A tuple with the status of the layer and an error message if
            needed.
            The status is 0 if everything was fine.
            The status is 1 if the client should fix something.
        :rtype: (int, m.Message)
        """
        if not layer.isValid():
            title = tr(
                'The {purpose} layer is invalid').format(purpose=purpose)
            content = tr(
                'The impact function needs a {exposure} layer to run. '
                'You must provide a valid {exposure} layer.').format(
                purpose=purpose)
            message = generate_input_error_message(
                title, m.Paragraph(content))
            return PREPARE_FAILED_BAD_INPUT, message

        # We should read it using KeywordIO for the very beginning. To avoid
        # get the modified keywords in the patching.
        try:
            keywords = KeywordIO().read_keywords(layer)
        except NoKeywordsFoundError:

            title = tr(
                'The {purpose} layer does not have keywords.').format(
                purpose=purpose)
            content = tr(
                'The {purpose} layer does not have keywords. Use the wizard '
                'to assign keywords to the layer.').format(purpose=purpose)
            message = generate_input_error_message(
                title, m.Paragraph(content))
            return PREPARE_FAILED_BAD_INPUT, message

        if keywords.get('layer_purpose') != purpose:
            title = tr('The expected {purpose} layer is not an {purpose}.')\
                .format(purpose=purpose)
            content = tr('The expected {purpose} layer is not an {purpose}.')\
                .format(purpose=purpose)
            message = generate_input_error_message(
                title, m.Paragraph(content))
            return PREPARE_FAILED_BAD_INPUT, message

        version = keywords.get(inasafe_keyword_version_key)
        supported = is_keyword_version_supported(version)
        if not supported:
            parameters = {
                'version': inasafe_keyword_version,
                'source': layer.publicSource()
            }
            title = tr('The {purpose} layer is not up to date.').format(
                purpose=purpose)
            content = tr(
                'The layer {source} must be updated to {version}.').format(
                    **parameters)
            message = generate_input_error_message(
                title, m.Paragraph(content))
            return PREPARE_FAILED_BAD_INPUT, message

        layer.keywords = keywords

        if is_vector_layer(layer):
            try:
                check_inasafe_fields(layer, keywords_only=True)
            except InvalidLayerError:
                title = tr('The {purpose} layer is not up to date.').format(
                    purpose=purpose)
                content = tr(
                    'The layer {source} must be updated with the keyword '
                    'wizard. Your fields which have been set in the keywords '
                    'previously are not matching your layer.').format(
                    source=layer.publicSource())
                message = generate_input_error_message(
                    title, m.Paragraph(content))
                del layer.keywords
                return PREPARE_FAILED_BAD_INPUT, message

        return PREPARE_SUCCESS, None

    def prepare(self):
        """Method to check if the impact function can be run.

        :return: A tuple with the status of the IF and an error message if
            needed.
            The status is PREPARE_SUCCESS if everything was fine.
            The status is PREPARE_FAILED_BAD_INPUT if the client should fix
                something.
            The status is PREPARE_FAILED_INSUFFICIENT_OVERLAP if the client
                should fix the analysis extent.
            The status is PREPARE_FAILED_BAD_CODE if something went wrong
                from the code.
        :rtype: (int, m.Message)
        """
        self._provenance_ready = False
        # save layer reference before preparing.
        # used to display it in maps
        original_exposure = self.exposure
        original_hazard = self.hazard
        original_aggregation = self.aggregation
        try:
            if not self.exposure:
                message = generate_input_error_message(
                    tr('The exposure layer is compulsory'),
                    m.Paragraph(tr(
                        'The impact function needs an exposure layer to run. '
                        'You must provide it.'))
                )
                return PREPARE_FAILED_BAD_INPUT, message

            status, message = self._check_layer(self.exposure, 'exposure')

            if status != PREPARE_SUCCESS:
                return status, message

            if not self.hazard:
                message = generate_input_error_message(
                    tr('The hazard layer is compulsory'),
                    m.Paragraph(tr(
                        'The impact function needs a hazard layer to run. '
                        'You must provide it.'))
                )
                return PREPARE_FAILED_BAD_INPUT, message

            status, message = self._check_layer(self.hazard, 'hazard')

            if status != PREPARE_SUCCESS:
                return status, message

            if self.aggregation:
                if self._requested_extent:
                    message = generate_input_error_message(
                        tr('Error with the requested extent'),
                        m.Paragraph(tr(
                            'Requested Extent must be null when an '
                            'aggregation is provided.'))
                    )
                    return PREPARE_FAILED_BAD_INPUT, message

                if self._requested_extent_crs:
                    message = generate_input_error_message(
                        tr('Error with the requested extent'),
                        m.Paragraph(tr(
                            'Requested Extent CRS must be null when an '
                            'aggregation is provided.'))
                    )
                    return PREPARE_FAILED_BAD_INPUT, message

                if self.use_exposure_view_only:
                    message = generate_input_error_message(
                        tr('Error with the requested extent'),
                        m.Paragraph(tr(
                            'Use exposure view only can not be set to True if '
                            'you use an aggregation layer.'))
                    )
                    return PREPARE_FAILED_BAD_INPUT, message

                status, message = self._check_layer(
                    self.aggregation, 'aggregation')
                aggregation_source = self.aggregation.publicSource()
                aggregation_keywords = copy_layer_keywords(
                    self.aggregation.keywords)

                if status != PREPARE_SUCCESS:
                    return status, message
            else:
                aggregation_source = None
                aggregation_keywords = None
                if self.requested_extent and not self.requested_extent_crs:
                    message = generate_input_error_message(
                        tr('Error with the requested extent'),
                        m.Paragraph(tr(
                            'Requested Extent CRS must be set when requested '
                            'is not null.'))
                    )
                    return PREPARE_FAILED_BAD_INPUT, message

                if self.requested_extent and self.use_exposure_view_only:
                    message = generate_input_error_message(
                        tr('Error with the requested extent'),
                        m.Paragraph(tr(
                            'Requested Extent must be null when you use the '
                            'exposure view only.'))
                    )
                    return PREPARE_FAILED_BAD_INPUT, message

            # We need to check if the hazard is OK to run on the exposure.
            hazard_keywords = self.hazard.keywords
            exposure_key = self.exposure.keywords['exposure']
            if not active_thresholds_value_maps(hazard_keywords, exposure_key):
                warning_heading = m.Heading(
                    tr('Incompatible exposure/hazard'), **WARNING_STYLE)
                warning_message = tr(
                    'The hazard layer is not set up for this kind of '
                    'exposure. In InaSAFE, you need to define keywords in the '
                    'hazard layer for each exposure type that you want to use '
                    'with the hazard.')
                suggestion_heading = m.Heading(
                    tr('Suggestion'), **SUGGESTION_STYLE)
                suggestion = tr(
                    'Please select the hazard layer in the legend and then '
                    'run the keyword wizard to define the needed keywords for '
                    '{exposure_type} exposure.').format(
                        exposure_type=exposure_key)

                message = m.Message()
                message.add(warning_heading)
                message.add(warning_message)
                message.add(suggestion_heading)
                message.add(suggestion)
                return PREPARE_FAILED_BAD_INPUT, message

            status, message = self._compute_analysis_extent()
            if status != PREPARE_SUCCESS:
                return status, message

            # Set the name
            hazard_name = get_name(self.hazard.keywords.get('hazard'))
            exposure_name = get_name(self.exposure.keywords.get('exposure'))
            hazard_geometry_name = get_name(
                self.hazard.keywords.get('layer_geometry'))
            exposure_geometry_name = get_name(
                self.exposure.keywords.get('layer_geometry'))
            self._name = tr(
                '{hazard_type} {hazard_geometry} On {exposure_type} '
                '{exposure_geometry}').format(
                hazard_type=hazard_name,
                hazard_geometry=hazard_geometry_name,
                exposure_type=exposure_name,
                exposure_geometry=exposure_geometry_name
            ).title()

            # Set the title
            if self.exposure.keywords.get('exposure') == 'population':
                self._title = tr('need evacuation')
            else:
                self._title = tr('be affected')

        except Exception as e:
            if self.debug_mode:
                # We run in debug mode, we do not want to catch the exception.
                # You should download the First Aid plugin for instance.
                raise
            else:
                message = get_error_message(e)
                return PREPARE_FAILED_BAD_CODE, message
        else:
            # Everything was fine.
            self._is_ready = True
            set_provenance(
                self._provenance,
                provenance_exposure_layer,
                self.exposure.publicSource())
            # reference to original layer being used
            set_provenance(
                self._provenance,
                provenance_exposure_layer_id,
                original_exposure.id())
            set_provenance(
                self._provenance,
                provenance_exposure_keywords,
                copy_layer_keywords(self.exposure.keywords))
            set_provenance(
                self._provenance,
                provenance_hazard_layer,
                self.hazard.publicSource())
            # reference to original layer being used
            set_provenance(
                self._provenance,
                provenance_hazard_layer_id,
                original_hazard.id())
            set_provenance(
                self._provenance,
                provenance_hazard_keywords,
                copy_layer_keywords(self.hazard.keywords))
            # reference to original layer being used
            if original_aggregation:
                set_provenance(
                    self._provenance,
                    provenance_aggregation_layer_id,
                    original_aggregation.id())
            else:
                set_provenance(
                    self._provenance,
                    provenance_aggregation_layer_id,
                    None)
            set_provenance(
                self._provenance,
                provenance_aggregation_layer,
                aggregation_source)
            set_provenance(
                self._provenance,
                provenance_aggregation_keywords,
                aggregation_keywords)

            return PREPARE_SUCCESS, None

    def _compute_analysis_extent(self):
        """Compute the minimum extent between layers.

        This function will set the self._analysis_extent geometry using
        exposure CRS.

        :return: A tuple with the status of the IF and an error message if
            needed.
            The status is PREPARE_SUCCESS if everything was fine.
            The status is PREPARE_FAILED_INSUFFICIENT_OVERLAP if the client
                should fix the analysis extent.
            The status is PREPARE_FAILED_BAD_CODE if something went wrong
                from the code.
        :rtype: (int, m.Message)
        """
        exposure_extent = QgsGeometry.fromRect(self.exposure.extent())
        hazard_extent = QgsGeometry.fromRect(self.hazard.extent())

        if self.hazard.crs().authid() != self.exposure.crs().authid():
            crs_transform = QgsCoordinateTransform(
                self.hazard.crs(), self.exposure.crs())
            hazard_extent.transform(crs_transform)

        # We check if the hazard and the exposure overlap.
        if not exposure_extent.intersects(hazard_extent):
            message = generate_input_error_message(
                tr('Layers need to overlap.'),
                m.Paragraph(tr(
                    'The exposure and the hazard layer need to overlap.'))
            )
            return PREPARE_FAILED_INSUFFICIENT_OVERLAP, message
        else:
            hazard_exposure = exposure_extent.intersection(hazard_extent)

        if not self.aggregation:
            if self.requested_extent and self.requested_extent_crs:
                user_bounding_box = QgsGeometry.fromRect(self.requested_extent)

                if self.requested_extent_crs != self.exposure.crs():
                    crs_transform = QgsCoordinateTransform(
                        self.requested_extent_crs, self.exposure.crs())
                    user_bounding_box.transform(crs_transform)

                if not hazard_exposure.intersects(user_bounding_box):
                    message = generate_input_error_message(
                        tr('The bounding box need to overlap layers.'),
                        m.Paragraph(tr(
                            'The requested analysis extent is not overlaping '
                            'the exposure and the hazard.'))
                    )
                    return (
                        PREPARE_FAILED_INSUFFICIENT_OVERLAP_REQUESTED_EXTENT,
                        message)
                else:
                    self._analysis_extent = hazard_exposure.intersection(
                        user_bounding_box)

            elif self.use_exposure_view_only:
                self._analysis_extent = exposure_extent

            else:
                self._analysis_extent = hazard_exposure

        else:
            # We monkey patch if we use selected features only.
            self.aggregation.use_selected_features_only = (
                self.use_selected_features_only)
            self.aggregation = create_valid_aggregation(self.aggregation)
            list_geometry = []
            for area in self.aggregation.getFeatures():
                list_geometry.append(QgsGeometry(area.geometry()))

            geometry = QgsGeometry.unaryUnion(list_geometry)
            if geometry.isMultipart():
                multi_polygon = geometry.asMultiPolygon()
                for polygon in multi_polygon:
                    for ring in polygon[1:]:
                        polygon.remove(ring)
                self._analysis_extent = QgsGeometry.fromMultiPolygon(
                    multi_polygon)

            else:
                polygon = geometry.asPolygon()
                for ring in polygon[1:]:
                    polygon.remove(ring)
                self._analysis_extent = QgsGeometry.fromPolygon(polygon)
            is_empty = self._analysis_extent.isGeosEmpty()
            is_invalid = not self._analysis_extent.isGeosValid()
            if is_empty or is_invalid:
                message = generate_input_error_message(
                    tr('There is a problem with the aggregation layer.'),
                    m.Paragraph(tr(
                        'The aggregation layer seems to have a problem. '
                        'Some features might be invalid. You should check the '
                        'validity of this layer or use a selection within '
                        'this layer.'))
                )
                return PREPARE_FAILED_BAD_LAYER, message

            if self.aggregation.crs().authid() != self.exposure.crs().authid():
                crs_transform = QgsCoordinateTransform(
                    self.aggregation.crs(), self.exposure.crs())
                self._analysis_extent.transform(crs_transform)

        return PREPARE_SUCCESS, None

    def debug_layer(self, layer, check_fields=True, add_to_datastore=None):
        """Write the layer produced to the datastore if debug mode is on.

        :param layer: The QGIS layer to check and save.
        :type layer: QgsMapLayer

        :param check_fields: Boolean to check or not inasafe_fields.
            By default, it's true.
        :type check_fields: bool

        :param add_to_datastore: Boolean if we need to store the layer. This
            parameter will overwrite the debug mode behaviour. Default to None,
            we usually let debug mode choose for us.
        :param add_to_datastore: bool

        :return: The name of the layer added in the datastore.
        :rtype: basestring
        """
        # This one checks the memory layer.
        check_layer(layer, has_geometry=None)

        if isinstance(layer, QgsVectorLayer) and check_fields:
            check_inasafe_fields(layer)

        # Be careful, add_to_datastore can be None, True or False.
        # None means we let debug_mode to choose for us.
        # If add_to_datastore is not None, we do not care about debug_mode.
        if isinstance(add_to_datastore, bool) and add_to_datastore:
            save_layer = True
        elif isinstance(add_to_datastore, bool) and not add_to_datastore:
            save_layer = False
        elif self.debug_mode:
            save_layer = True
        else:
            save_layer = False

        if save_layer:
            result, name = self.datastore.add_layer(
                layer, layer.keywords['title'])
            if not result:
                raise Exception(
                    'Something went wrong with the datastore : {error_message}'
                    .format(error_message=name))
            if self.debug_mode:
                # This one checks the GeoJSON file. We noticed some difference
                # between checking a memory layer and a file based layer.
                check_layer(self.datastore.layer(name))

            return name

    def run(self):
        """Run the whole impact function.

        :return: A tuple with the status of the IF and an error message if
            needed.
            The status is ANALYSIS_SUCCESS if everything was fine.
            The status is ANALYSIS_FAILED_BAD_INPUT if the client should fix
                something.
            The status is ANALYSIS_FAILED_BAD_CODE if something went wrong
                from the code.
        :rtype: (int, m.Message)
        """
        self._start_datetime = datetime.now()
        if not self._is_ready:
            message = tr('You need to run `prepare` first.')
            return ANALYSIS_FAILED_BAD_INPUT, message

        try:
            self.reset_state()
            clear_prof_data()
            self._run()

            # Get the profiling log
            self._performance_log = profiling_log()
            self.callback(8, 8, analysis_steps['profiling'])

            self._profiling_table = create_profile_layer(
                self.performance_log_message())
            result, name = self.datastore.add_layer(
                self._profiling_table, self._profiling_table.keywords['title'])
            if not result:
                raise Exception(
                    'Something went wrong with the datastore : {error_message}'
                    .format(error_message=name))
            self._profiling_table = self.datastore.layer(name)

            # Later, we should move this call.
            self.style()

            # End of the impact function. We need to set this IF not ready.
            self._is_ready = False

        except NoFeaturesInExtentError:
            warning_heading = m.Heading(
                tr('No features in the extent'), **WARNING_STYLE)
            warning_message = tr(
                'There are no features in the analysis extent.')
            suggestion_heading = m.Heading(
                tr('Suggestion'), **SUGGESTION_STYLE)
            suggestion = tr(
                'Try zooming in to a bigger area or check your features ('
                'geometry and attribute table). For instance, an empty '
                'geometry or an hazard without value are removed during the '
                'process.')

            message = m.Message()
            message.add(warning_heading)
            message.add(warning_message)
            message.add(suggestion_heading)
            message.add(suggestion)
            return ANALYSIS_FAILED_BAD_INPUT, message

        except ProcessingInstallationError:
            warning_heading = m.Heading(
                tr('Configuration issue'), **WARNING_STYLE)
            warning_message = tr(
                'There is a problem with the Processing plugin.')
            suggestion_heading = m.Heading(
                tr('Suggestion'), **SUGGESTION_STYLE)
            suggestion = tr(
                'InaSAFE depends on the QGIS Processing plugin. This is a '
                'core plugin that ships with QGIS. It used to be possible to '
                'install the processing plugin from the QGIS Plugin Manager, '
                'however we advise you not to use these version since the '
                'Plugin Manager version may be incompatible with the '
                'version needed by InaSAFE. To resolve this issue, check in '
                'your .qgis2/python/plugins directory if you have a '
                'processing folder. If you do, remove the processing folder '
                'and then restart QGIS. If this issue persists, please '
                'report the problem to the InaSAFE team.')
            message = m.Message()
            message.add(warning_heading)
            message.add(warning_message)
            message.add(suggestion_heading)
            message.add(suggestion)
            return ANALYSIS_FAILED_BAD_INPUT, message

        except InaSAFEError as e:
            message = get_error_message(e)
            return ANALYSIS_FAILED_BAD_CODE, message

        except MemoryError:
            warning_heading = m.Heading(tr('Memory issue'), **WARNING_STYLE)
            warning_message = tr(
                'There is not enough free memory to run this analysis.')
            suggestion_heading = m.Heading(
                tr('Suggestion'), **SUGGESTION_STYLE)
            suggestion = tr(
                'Try zooming in to a smaller area or using a raster layer '
                'with a coarser resolution to speed up execution and reduce '
                'memory requirements. You could also try adding more RAM to '
                'your computer.')

            message = m.Message()
            message.add(warning_heading)
            message.add(warning_message)
            message.add(suggestion_heading)
            message.add(suggestion)
            return ANALYSIS_FAILED_BAD_INPUT, message

        except Exception as e:
            if self.debug_mode:
                # We run in debug mode, we do not want to catch the exception.
                # You should download the First Aid plugin for instance.
                raise
            else:
                message = get_error_message(e)
                return ANALYSIS_FAILED_BAD_CODE, message

        else:
            return ANALYSIS_SUCCESS, None

    @profile
    def _run(self):
        """Internal function to run the impact function with profiling."""
        LOGGER.info('ANALYSIS : The impact function is starting.')
        step_count = len(analysis_steps)
        self.callback(0, step_count, analysis_steps['initialisation'])

        # Set a unique name for this impact
        self._unique_name = self._name.replace(' ', '')
        self._unique_name = replace_accentuated_characters(self._unique_name)
        now = datetime.now()
        date = now.strftime('%d%B%Y').decode('utf8')
        # We need to add milliseconds to be sure to have a unique name.
        # Some tests are executed in less than a second.
        time = now.strftime('%Hh%M-%S.%f').decode('utf8')
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
        LOGGER.info('Datastore : %s' % self.datastore.uri_path)

        if self.debug_mode:
            self._datastore.use_index = True

            self.datastore.add_layer(self.exposure, 'exposure')
            self.datastore.add_layer(self.hazard, 'hazard')
            if self.aggregation:
                self.datastore.add_layer(self.aggregation, 'aggregation')

        self._performance_log = profiling_log()
        self.callback(2, step_count, analysis_steps['aggregation_preparation'])
        self.aggregation_preparation()

        # Special case for earthquake hazard on population. We need to remove
        # the fatality model.
        earthquake_on_population = False
        if self.hazard.keywords.get('hazard') == 'earthquake':
            if self.exposure.keywords.get('exposure') == 'population':
                earthquake_on_population = True
        if not earthquake_on_population:
            # This is not a EQ raster on raster population. We need to set it
            # to None as we don't want notes specific to EQ raster on
            # population.
            self._earthquake_function = None

        step_count = len(analysis_steps)

        self._performance_log = profiling_log()
        self.callback(3, step_count, analysis_steps['hazard_preparation'])
        self.hazard_preparation()

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
        if is_vector_layer(self._exposure_summary):
            # We post process the exposure summary
            self.post_process(self._exposure_summary)
        else:
            # We post process the aggregate hazard.
            # Raster continuous exposure.
            self.post_process(self._aggregate_hazard_impacted)

        self._performance_log = profiling_log()
        self.callback(8, step_count, analysis_steps['summary_calculation'])
        self.summary_calculation()

        self._end_datetime = datetime.now()
        set_provenance(
            self._provenance, provenance_start_datetime, self.start_datetime)
        set_provenance(
            self._provenance, provenance_end_datetime, self.end_datetime)
        set_provenance(
            self._provenance, provenance_duration, self.duration)
        self._generate_provenance()

        # Update provenance with output layer path
        output_layer_provenance = {
            provenance_layer_exposure_summary[
                'provenance_key']: None,
            provenance_layer_aggregate_hazard_impacted[
                'provenance_key']: None,
            provenance_layer_aggregation_summary[
                'provenance_key']: None,
            provenance_layer_analysis_impacted[
                'provenance_key']: None,
            provenance_layer_exposure_summary_table[
                'provenance_key']: None,
            provenance_layer_exposure_summary_id['provenance_key']: None,
            provenance_layer_aggregate_hazard_impacted_id[
                'provenance_key']: None,
            provenance_layer_aggregation_summary_id['provenance_key']: None,
            provenance_layer_analysis_impacted_id['provenance_key']: None,
            provenance_layer_exposure_summary_table_id['provenance_key']: None,
        }

        # End of the impact function, we can add layers to the datastore.
        # We replace memory layers by the real layer from the datastore.

        # Exposure summary
        if self._exposure_summary:
            self._exposure_summary.keywords[
                'provenance_data'] = self.provenance
            self.append_ISO19115_keywords(
                self._exposure_summary.keywords)
            result, name = self.datastore.add_layer(
                self._exposure_summary,
                layer_purpose_exposure_summary['key'])
            if not result:
                raise Exception(
                    tr('Something went wrong with the datastore : '
                       '{error_message}').format(error_message=name))
            self._exposure_summary = self.datastore.layer(name)
            self.debug_layer(self._exposure_summary, add_to_datastore=False)

            output_layer_provenance[provenance_layer_exposure_summary[
                'provenance_key']] = self._exposure_summary.publicSource()
            output_layer_provenance[provenance_layer_exposure_summary_id[
                'provenance_key']] = self._exposure_summary.id()

        # Aggregate hazard impacted
        if self.aggregate_hazard_impacted:
            self.aggregate_hazard_impacted.keywords[
                'provenance_data'] = self.provenance
            self.append_ISO19115_keywords(
                self.aggregate_hazard_impacted.keywords)
            result, name = self.datastore.add_layer(
                self._aggregate_hazard_impacted,
                layer_purpose_aggregate_hazard_impacted['key'])
            if not result:
                raise Exception(
                    tr('Something went wrong with the datastore : '
                       '{error_message}').format(error_message=name))
            self._aggregate_hazard_impacted = self.datastore.layer(name)
            self.debug_layer(
                self._aggregate_hazard_impacted, add_to_datastore=False)

            output_layer_provenance[
                provenance_layer_aggregate_hazard_impacted['provenance_key']
            ] = self.aggregate_hazard_impacted.publicSource()
            output_layer_provenance[
                provenance_layer_aggregate_hazard_impacted_id['provenance_key']
            ] = self.aggregate_hazard_impacted.id()

        # Exposure summary table
        if self._exposure.keywords.get('classification'):
            self._exposure_summary_table.keywords[
                'provenance_data'] = self.provenance
            self.append_ISO19115_keywords(
                self._exposure_summary_table.keywords)
            result, name = self.datastore.add_layer(
                self._exposure_summary_table,
                layer_purpose_exposure_summary_table['key'])
            if not result:
                raise Exception(
                    tr('Something went wrong with the datastore : '
                       '{error_message}').format(error_message=name))
            self._exposure_summary_table = self.datastore.layer(name)
            self.debug_layer(
                self._exposure_summary_table, add_to_datastore=False)

            output_layer_provenance[
                provenance_layer_exposure_summary_table['provenance_key']
            ] = self._exposure_summary_table.publicSource()
            output_layer_provenance[
                provenance_layer_exposure_summary_table_id['provenance_key']
            ] = self._exposure_summary_table.id()

        # Aggregation summary
        self.aggregation_summary.keywords['provenance_data'] = self.provenance
        self.append_ISO19115_keywords(self.aggregation_summary.keywords)
        result, name = self.datastore.add_layer(
            self._aggregation_summary,
            layer_purpose_aggregation_summary['key'])
        if not result:
            raise Exception(
                tr('Something went wrong with the datastore : '
                   '{error_message}').format(error_message=name))
        self._aggregation_summary = self.datastore.layer(name)
        self.debug_layer(self._aggregation_summary, add_to_datastore=False)

        output_layer_provenance[provenance_layer_aggregation_summary[
            'provenance_key']] = self._aggregation_summary.publicSource()
        output_layer_provenance[provenance_layer_aggregation_summary_id[
            'provenance_key']] = self._aggregation_summary.id()

        # Analysis impacted
        self.analysis_impacted.keywords['provenance_data'] = self.provenance
        self.append_ISO19115_keywords(self.analysis_impacted.keywords)
        result, name = self.datastore.add_layer(
            self._analysis_impacted, layer_purpose_analysis_impacted['key'])
        if not result:
            raise Exception(
                tr('Something went wrong with the datastore : '
                   '{error_message}').format(error_message=name))
        self._analysis_impacted = self.datastore.layer(name)
        self.debug_layer(self._analysis_impacted, add_to_datastore=False)
        output_layer_provenance[provenance_layer_analysis_impacted[
            'provenance_key']] = self._analysis_impacted.publicSource()
        output_layer_provenance[provenance_layer_analysis_impacted_id[
            'provenance_key']] = self._analysis_impacted.id()

        # Update provenance data with output layers URI
        self._provenance.update(output_layer_provenance)
        if self._exposure_summary:
            self._exposure_summary.keywords[
                'provenance_data'] = self.provenance
            write_iso19115_metadata(
                self._exposure_summary.publicSource(),
                self._exposure_summary.keywords)
        if self._aggregate_hazard_impacted:
            self._aggregate_hazard_impacted.keywords[
                'provenance_data'] = self.provenance
            write_iso19115_metadata(
                self._aggregate_hazard_impacted.publicSource(),
                self._aggregate_hazard_impacted.keywords)
        if self._exposure_summary_table:
            self._exposure_summary_table.keywords[
                'provenance_data'] = self.provenance
            write_iso19115_metadata(
                self._exposure_summary_table.publicSource(),
                self._exposure_summary_table.keywords)

        self.aggregation_summary.keywords['provenance_data'] = self.provenance
        write_iso19115_metadata(
            self.aggregation_summary.publicSource(),
            self.aggregation_summary.keywords)

        self.analysis_impacted.keywords['provenance_data'] = self.provenance
        write_iso19115_metadata(
            self.analysis_impacted.publicSource(),
            self.analysis_impacted.keywords)

    @profile
    def aggregation_preparation(self):
        """This function is doing the aggregation preparation."""
        LOGGER.info('ANALYSIS : Aggregation preparation')
        if not self.aggregation:
            self.set_state_info('aggregation', 'provided', False)
            LOGGER.info(
                'The aggregation layer is not provided. We are going to '
                'create it from the analysis extent.')

            self.set_state_process(
                'aggregation',
                'Convert bbox aggregation to polygon layer with keywords')
            self.aggregation = create_virtual_aggregation(
                self.analysis_extent, self.exposure.crs())
            self.debug_layer(self.aggregation)

            exposure = definition(self.exposure.keywords['exposure'])
            keywords = self.exposure.keywords

            # inasafe_default_values will not exist as we can't use
            # default in the exposure layer.
            keywords['inasafe_default_values'] = {}

            if is_vector_layer(self.exposure):
                LOGGER.info(
                    'The exposure is a vector layer. According to the kind of '
                    'exposure, we need to check if the exposure has some '
                    'counts before adding some default ratios.')
                non_compulsory_fields = get_non_compulsory_fields(
                    layer_purpose_exposure['key'], exposure['key'])
                for count_field in non_compulsory_fields:
                    count_key = count_field['key']
                    if count_key in count_ratio_mapping.keys():
                        ratio_field = count_ratio_mapping[count_key]
                        if count_key not in keywords['inasafe_fields']:
                            # The exposure hasn't a count field, we should add
                            # it.
                            default_value = get_inasafe_default_value_qsetting(
                                    QSettings(), GLOBAL, ratio_field)
                            keywords['inasafe_default_values'][ratio_field] = (
                                default_value)
                            LOGGER.info(
                                'The exposure do not have field {count}, we '
                                'can add {ratio} = {value} to the exposure '
                                'default values.'.format(
                                    count=count_key,
                                    ratio=ratio_field,
                                    value=default_value))
                        else:
                            LOGGER.info(
                                'The exposure layer has the count field '
                                '{count}, we skip the ratio '
                                '{ratio}.'.format(
                                    count=count_key, ratio=ratio_field))

            else:
                LOGGER.info(
                    'The exposure is a raster layer. The exposure can not '
                    'have some counts. We add every global defaults to the '
                    'exposure layer related to the exposure.')

                non_compulsory_fields = get_non_compulsory_fields(
                    layer_purpose_exposure['key'], exposure['key'])
                for count_field in non_compulsory_fields:
                    count_key = count_field['key']
                    if count_key in count_ratio_mapping.keys():
                        ratio_field = count_ratio_mapping[count_key]
                        default_value = get_inasafe_default_value_qsetting(
                            QSettings(), GLOBAL, ratio_field)
                        keywords['inasafe_default_values'][ratio_field] = (
                            default_value)
                        LOGGER.info(
                            'We are adding {ratio} = {value} to the exposure '
                            'default values.'.format(
                                count=count_key,
                                ratio=ratio_field,
                                value=default_value))

        else:
            self.set_state_info('aggregation', 'provided', True)

            self.set_state_process(
                'aggregation', 'Cleaning the aggregation layer')
            self.aggregation = prepare_vector_layer(self.aggregation)
            self.debug_layer(self.aggregation)

            if self.aggregation.crs().authid() != self.exposure.crs().authid():
                self.set_state_process(
                    'aggregation',
                    'Reproject aggregation layer to exposure CRS')
                # noinspection PyTypeChecker
                self.aggregation = reproject(
                    self.aggregation, self.exposure.crs())
                self.debug_layer(self.aggregation)

            else:
                self.set_state_process(
                    'aggregation',
                    'Aggregation layer already in exposure CRS')

            # We need to check if we can add default ratios to the exposure
            # by looking also in the aggregation layer.
            exposure_keywords = self.exposure.keywords
            # The exposure might be a raster so without inasafe_fields.
            exposure_fields = exposure_keywords.get('inasafe_fields', {})
            exposure = definition(exposure_keywords['exposure'])
            exposure_keywords['inasafe_default_values'] = {}
            exposure_defaults = exposure_keywords['inasafe_default_values']
            aggregation_keywords = self.aggregation.keywords
            aggregation_fields = aggregation_keywords['inasafe_fields']
            if not aggregation_keywords.get('inasafe_default_values'):
                aggregation_keywords['inasafe_default_values'] = {}
            aggregation_default_fields = aggregation_keywords.get(
                'inasafe_default_values')
            non_compulsory_fields = get_non_compulsory_fields(
                layer_purpose_exposure['key'], exposure['key'])
            for count_field in non_compulsory_fields:
                if count_field['key'] in count_ratio_mapping.keys():
                    ratio_field = count_ratio_mapping[count_field['key']]
                    if count_field['key'] not in exposure_fields:
                        # The exposure layer can be vector or a raster.

                        ratio_is_a_field = ratio_field in aggregation_fields
                        ratio_is_a_constant = (
                            ratio_field in aggregation_default_fields)

                        if ratio_is_a_constant and ratio_is_a_field:
                            # This should of course never happen! It would
                            # be an error from the wizard. See #3809.
                            # Let's raise an exception.
                            raise Exception

                        if ratio_is_a_field and not ratio_is_a_constant:
                            # The ratio is a field, we do nothing here.
                            # The ratio will be propagated to the
                            # aggregate_hazard layer.
                            # Let's skip to the next field.
                            if is_vector_layer(self.exposure):
                                LOGGER.info(
                                    '{ratio} field detected in the '
                                    'aggregation layer AND the equivalent '
                                    'count has not been detected in the '
                                    'exposure layer. We will propagate this '
                                    'ratio to the exposure layer later when '
                                    'we combine these two layers.'.format(
                                        ratio=ratio_field))
                                continue
                            else:
                                LOGGER.info(
                                    '{ratio} field detected in the '
                                    'aggregation layer. The exposure is a '
                                    'raster so without the equivalent count. '
                                    'We will propagate this ratio to the '
                                    'exposure layer later when we combine '
                                    'these two layers.'.format(
                                        ratio=ratio_field))

                        if ratio_is_a_constant and not ratio_is_a_field:
                            # It's a constant. We need to add to the exposure.
                            value = aggregation_default_fields[ratio_field]
                            exposure_defaults[ratio_field] = value
                            if is_vector_layer(self.exposure):
                                LOGGER.info(
                                    '{ratio} = {value} constant detected in '
                                    'the aggregation layer AND the equivalent '
                                    'count has not been detected in the '
                                    'exposure layer. We are adding this ratio '
                                    'to the exposure layer.'.format(
                                        ratio=ratio_field, value=value))
                            else:
                                LOGGER.info(
                                    '{ratio} = {value} constant detected in '
                                    'the aggregation layer. The exposure is a '
                                    'raster so without the equivalent count.'
                                    'We are adding this ratio to the exposure '
                                    'layer.'.format(
                                        ratio=ratio_field, value=value))

                        if not ratio_is_a_constant and not ratio_is_a_field:
                            if is_vector_layer(self.exposure):
                                LOGGER.info(
                                    '{ratio_field} is neither a constant nor '
                                    'a field in the aggregation layer AND the '
                                    'equivalent count has not been detected '
                                    'in the exposure layer. We will do '
                                    'nothing about it.'.format(
                                        ratio_field=ratio_field))
                            else:
                                LOGGER.info(
                                    '{ratio_field} is neither a constant nor '
                                    'a field in the aggregation layer. The '
                                    'exposure is a raster so without the '
                                    'equivalent count. We will do '
                                    'nothing about it.'.format(
                                        ratio_field=ratio_field))

                    else:
                        # The exposure layer is a vector layer only.
                        if ratio_field in aggregation_fields:
                            # The count field is in the exposure and the ratio
                            # is in the aggregation. We need to remove it from
                            # the aggregation. We remove the keyword too.
                            remove_fields(
                                self.aggregation,
                                [aggregation_fields[ratio_field]])
                            del aggregation_fields[ratio_field]
                            LOGGER.info(
                                '{ratio_field} is detected in the aggregation '
                                'layer AND {count_field} is detected in the '
                                'exposure layer. We remove the ratio from the '
                                'aggregation.'.format(
                                    ratio_field=ratio_field,
                                    count_field=count_field['key']))

                        else:
                            LOGGER.info(
                                '{ratio_field} is not in the detected in the '
                                'aggregation layer AND {count_field} is '
                                'detected in the exposure layer. We do '
                                'nothing in this step.'.format(
                                    ratio_field=ratio_field,
                                    count_field=count_field['key']))

        self.set_state_process(
            'aggregation',
            'Convert the aggregation layer to the analysis layer')
        self._analysis_impacted = create_analysis_layer(
            self.analysis_extent, self.exposure.crs(), self.name)
        self.debug_layer(self._analysis_impacted)

    @profile
    def hazard_preparation(self):
        """This function is doing the hazard preparation."""
        LOGGER.info('ANALYSIS : Hazard preparation')

        use_same_projection = (
            self.hazard.crs().authid() == self.exposure.crs().authid())
        self.set_state_info(
            'hazard', 'use_same_projection', use_same_projection)

        if is_raster_layer(self.hazard):

            extent = self.analysis_impacted.extent()
            if not use_same_projection:
                transform = QgsCoordinateTransform(
                    self.analysis_impacted.crs(), self.hazard.crs())
                extent = transform.transform(self.analysis_impacted.extent())

            self.set_state_process(
                'hazard', 'Clip raster by analysis bounding box')
            # noinspection PyTypeChecker
            self.hazard = clip_by_extent(self.hazard, extent)
            self.debug_layer(self.hazard)

            if self.hazard.keywords.get('layer_mode') == 'continuous':
                self.set_state_process(
                    'hazard', 'Classify continuous raster hazard')
                # noinspection PyTypeChecker
                self.hazard = reclassify_raster(
                    self.hazard, self.exposure.keywords['exposure'])
                self.debug_layer(self.hazard)

            self.set_state_process(
                'hazard', 'Polygonize classified raster hazard')
            # noinspection PyTypeChecker
            self.hazard = polygonize(self.hazard)
            self.debug_layer(self.hazard)

        if self.hazard.crs().authid() != self.exposure.crs().authid():
            self.set_state_process(
                'hazard',
                'Reproject hazard layer to exposure CRS')
            # noinspection PyTypeChecker
            self.hazard = reproject(self.hazard, self.exposure.crs())
            self.debug_layer(self.hazard, check_fields=False)

        self.set_state_process(
            'hazard',
            'Clip and mask hazard polygons with the analysis layer')
        self.hazard = clip(self.hazard, self._analysis_impacted)
        self.debug_layer(self.hazard, check_fields=False)

        self.set_state_process(
            'hazard',
            'Cleaning the vector hazard attribute table')
        # noinspection PyTypeChecker
        self.hazard = prepare_vector_layer(self.hazard)
        self.debug_layer(self.hazard)

        if self.hazard.keywords.get('layer_mode') == 'continuous':
            # If the layer is continuous, we update the original data to the
            # inasafe hazard class.
            self.set_state_process(
                'hazard',
                'Classify continuous hazard and assign class names')
            self.hazard = reclassify_vector(
                self.hazard, self.exposure.keywords['exposure'])
            self.debug_layer(self.hazard)
        else:
            # However, if it's a classified dataset, we only transpose the
            # value map using inasafe hazard classes.
            self.set_state_process(
                'hazard', 'Assign classes based on value map')
            self.hazard = update_value_map(
                self.hazard, self.exposure.keywords['exposure'])
            self.debug_layer(self.hazard)

    @profile
    def aggregate_hazard_preparation(self):
        """This function is doing the aggregate hazard layer.

        It will prepare the aggregate layer and intersect hazard polygons with
        aggregation areas and assign hazard class.
        """
        LOGGER.info('ANALYSIS : Aggregate hazard preparation')
        self.set_state_process('hazard', 'Make hazard layer valid')
        self.hazard = clean_layer(self.hazard)
        self.debug_layer(self.hazard)

        self.set_state_process(
            'aggregation',
            'Union hazard polygons with aggregation areas and assign '
            'hazard class')
        self._aggregate_hazard_impacted = union(self.hazard, self.aggregation)
        self.debug_layer(self._aggregate_hazard_impacted)

    @profile
    def exposure_preparation(self):
        """This function is doing the exposure preparation."""
        LOGGER.info('ANALYSIS : Exposure preparation')
        if is_raster_layer(self.exposure):
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
                self.debug_layer(self.exposure)

        # We may need to add the size of the original feature. So don't want to
        # split the feature yet.
        self.set_state_process('exposure', 'Smart clip')
        self.exposure = smart_clip(
            self.exposure, self._analysis_impacted)
        self.debug_layer(self.exposure, check_fields=False)

        self.set_state_process(
            'exposure',
            'Cleaning the vector exposure attribute table')
        # noinspection PyTypeChecker
        self.exposure = prepare_vector_layer(self.exposure)
        self.debug_layer(self.exposure)

        self.set_state_process('exposure', 'Compute ratios from counts')
        self.exposure = from_counts_to_ratios(self.exposure)
        self.debug_layer(self.exposure)

        exposure = self.exposure.keywords.get('exposure')
        geometry = self.exposure.geometryType()
        indivisible_keys = [f['key'] for f in indivisible_exposure]
        if exposure not in indivisible_keys and geometry != QGis.Point:
            # We can now split features because the `prepare_vector_layer`
            # might have added the size field.
            self.set_state_process(
                'exposure',
                'Clip the exposure layer with the analysis layer')
            self.exposure = clip(self.exposure, self._analysis_impacted)
            self.debug_layer(self.exposure)

        self.set_state_process('exposure', 'Add default values')
        self.exposure = add_default_values(self.exposure)
        self.debug_layer(self.exposure)

        fields = self.exposure.keywords['inasafe_fields']
        if exposure_class_field['key'] not in fields:
            self.set_state_process(
                'exposure', 'Assign classes based on value map')
            self.exposure = update_value_map(self.exposure)
            self.debug_layer(self.exposure)

    @profile
    def intersect_exposure_and_aggregate_hazard(self):
        """This function intersects the exposure with the aggregate hazard.

        If the the exposure is a continuous raster exposure, this function
            will set the aggregate hazard layer.
        However, this function will set the impact layer.
        """
        LOGGER.info('ANALYSIS : Intersect Exposure and Aggregate Hazard')
        if is_raster_layer(self.exposure):
            self.set_state_process(
                'impact function',
                'Zonal stats between exposure and aggregate hazard')
            # noinspection PyTypeChecker
            self._aggregate_hazard_impacted = zonal_stats(
                self.exposure, self._aggregate_hazard_impacted)
            self.debug_layer(self._aggregate_hazard_impacted)

            self.set_state_process('impact function', 'Add default values')
            self._aggregate_hazard_impacted = add_default_values(
                self._aggregate_hazard_impacted)
            self.debug_layer(self._aggregate_hazard_impacted)

            # I know it's redundant, it's just to be sure that we don't have
            # any impact layer for that IF.
            self._exposure_summary = None

        else:
            indivisible_keys = [f['key'] for f in indivisible_exposure]
            geometry = self.exposure.geometryType()
            exposure = self.exposure.keywords.get('exposure')
            is_divisible = exposure not in indivisible_keys

            if geometry in [QGis.Line, QGis.Polygon] and is_divisible:

                self.set_state_process(
                    'exposure', 'Make exposure layer valid')
                self._exposure = clean_layer(self.exposure)
                self.debug_layer(self.exposure)

                self.set_state_process(
                    'impact function', 'Make aggregate hazard layer valid')
                self._aggregate_hazard_impacted = clean_layer(
                    self._aggregate_hazard_impacted)
                self.debug_layer(self._aggregate_hazard_impacted)

                self.set_state_process(
                    'impact function',
                    'Intersect divisible features with the aggregate hazard')
                self._exposure_summary = intersection(
                    self._exposure, self._aggregate_hazard_impacted)
                self.debug_layer(self._exposure_summary)

                # If the layer has the size field, it means we need to
                # recompute counts based on the old and new size.
                fields = self._exposure_summary.keywords['inasafe_fields']
                if size_field['key'] in fields:
                    self.set_state_process(
                        'impact function',
                        'Recompute counts')
                    LOGGER.info(
                        'InaSAFE will not use these counts, as we have ratios '
                        'since the exposure preparation step.')
                    self._exposure_summary = recompute_counts(
                        self._exposure_summary)
                    self.debug_layer(self._exposure_summary)

            else:
                self.set_state_process(
                    'impact function',
                    'Highest class of hazard is assigned to the exposure')
                self._exposure_summary = assign_highest_value(
                    self._exposure, self._aggregate_hazard_impacted)
                self.debug_layer(self._exposure_summary)

            # set title using definition
            # the title will be overwritten anyway by standard title
            # set this as fallback.
            self._exposure_summary.keywords['title'] = (
                layer_purpose_exposure_summary['name'])
            if qgis_version() >= 21800:
                self._exposure_summary.setName(
                    self._exposure_summary.keywords['title'])
            else:
                self._exposure_summary.setLayerName(
                    self._exposure_summary.keywords['title'])

    @profile
    def post_process(self, layer):
        """More process after getting the impact layer with data.

        :param layer: The vector layer to use for post processing.
        :type layer: QgsVectorLayer
        """
        LOGGER.info('ANALYSIS : Post processing')

        # Set the layer title
        purpose = layer.keywords['layer_purpose']
        if purpose != layer_purpose_aggregation_summary['key']:
            # On an aggregation layer, the default title does make any sense.
            layer_title(layer)

        for post_processor in post_processors:
            valid, message = enough_input(layer, post_processor['input'])
            name = get_unicode(post_processor['name'])

            if valid:
                valid, message = run_single_post_processor(
                    layer, post_processor)
                if valid:
                    self.set_state_process('post_processor', name)
                    message = u'{name} : Running'.format(name=name)
                    LOGGER.info(message)

            else:
                # message = u'{name} : Could not run : {reason}'.format(
                #     name=name, reason=message)
                # LOGGER.info(message)
                pass

        self.debug_layer(layer, add_to_datastore=False)

    @profile
    def summary_calculation(self):
        """Do the summary calculation.

        We do not check layers here, we will check them in the next step.
        """
        LOGGER.info('ANALYSIS : Summary calculation')
        if is_vector_layer(self._exposure_summary):
            # With continuous exposure, we don't have an exposure summary layer
            self.set_state_process(
                'impact function',
                'Aggregate the impact summary')
            self._aggregate_hazard_impacted = aggregate_hazard_summary(
                self.exposure_summary, self._aggregate_hazard_impacted)
            self.debug_layer(self._exposure_summary, add_to_datastore=False)

        self.set_state_process(
            'impact function', 'Aggregate the aggregation summary')
        self._aggregation_summary = aggregation_summary(
            self._aggregate_hazard_impacted, self.aggregation)
        self.debug_layer(
            self._aggregation_summary, add_to_datastore=False)

        self.set_state_process(
            'impact function', 'Aggregate the analysis summary')
        self._analysis_impacted = analysis_summary(
            self._aggregate_hazard_impacted, self._analysis_impacted)
        self.debug_layer(self._analysis_impacted)

        if self._exposure.keywords.get('classification'):
            self.set_state_process(
                'impact function', 'Build the exposure summary table')
            self._exposure_summary_table = exposure_summary_table(
                self._aggregate_hazard_impacted, self._exposure_summary)
            self.debug_layer(
                self._exposure_summary_table, add_to_datastore=False)

    def style(self):
        """Function to apply some styles to the layers."""
        LOGGER.info('ANALYSIS : Styling')
        classes = generate_classified_legend(
            self.analysis_impacted,
            self.exposure,
            self.hazard,
            self.debug_mode)

        # Let's style layers which have a geometry and have hazard_class
        hazard_class = hazard_class_field['key']
        for layer in self.outputs:
            without_geometries = [QGis.NoGeometry, QGis.UnknownGeometry]
            if layer.geometryType() not in without_geometries:
                display_not_exposed = False
                if layer == self.impact or self.debug_mode:
                    display_not_exposed = True

                if layer.keywords['inasafe_fields'].get(hazard_class):
                    hazard_class_style(layer, classes, display_not_exposed)

        # Let's style the aggregation and analysis layer.
        simple_polygon_without_brush(
            self.aggregation_summary, aggregation_width, aggregation_color)
        simple_polygon_without_brush(
            self.analysis_impacted, analysis_width, analysis_color)

    @property
    def provenance(self):
        """Helper method to gather provenance for exposure_summary layer.

        If the impact function is not ready (has not called prepare method),
        it will return empty dict to avoid miss information.

        The impact function will call generate_provenance at the end of the IF.

        List of keys (for quick lookup): safe/definitions/provenance.py

        :returns: Dictionary that contains all provenance.
        :rtype: dict
        """
        if self._provenance_ready:
            return self._provenance
        else:
            return {}

    def _generate_provenance(self):
        """Function to generate provenance at the end of the IF."""
        # noinspection PyTypeChecker
        exposure = definition(
            self._provenance['exposure_keywords']['exposure'])

        # noinspection PyTypeChecker
        hazard = definition(
            self._provenance['hazard_keywords']['hazard'])
        # noinspection PyTypeChecker
        hazard_category = definition(self._provenance['hazard_keywords'][
            'hazard_category'])

        # InaSAFE
        set_provenance(
            self._provenance, provenance_impact_function_name, self.name)
        set_provenance(
            self._provenance, provenance_impact_function_title, self.title)

        # Map title
        set_provenance(
            self._provenance,
            provenance_map_title,
            get_map_title(hazard, exposure, hazard_category))

        set_provenance(
            self._provenance,
            provenance_map_legend_title,
            exposure['layer_legend_title'])

        set_provenance(
            self._provenance,
            provenance_analysis_question,
            get_analysis_question(hazard, exposure))

        if self.requested_extent:
            set_provenance(
                self._provenance,
                provenance_requested_extent,
                self.requested_extent.asWktCoordinates())
        else:
            set_provenance(
                self._provenance,
                provenance_requested_extent,
                None)
        set_provenance(
            self._provenance,
            provenance_analysis_extent,
            self.analysis_extent.exportToWkt())

        set_provenance(
            self._provenance,
            provenance_data_store_uri,
            self.datastore.uri_path)

        # Notes and Action
        set_provenance(self._provenance, provenance_notes, self.notes())
        set_provenance(
            self._provenance,
            provenance_action_checklist,
            self.action_checklist())

        # CRS
        set_provenance(
            self._provenance, provenance_crs, self.impact.crs().authid())

        self._provenance_ready = True

    def exposure_notes(self):
        """Get the exposure specific notes defined in definitions.

        This method will do a lookup in definitions and return the
        exposure definition specific notes dictionary.

        This is a helper function to make it
        easy to get exposure specific notes from the definitions metadata.

        .. versionadded:: 3.5

        :returns: A list like e.g. safe.definitions.exposure_land_cover[
            'notes']
        :rtype: list, None
        """
        notes = []
        exposure = definition(self.exposure.keywords.get('exposure'))
        if 'notes' in exposure:
            notes += exposure['notes']
        if self.exposure.keywords['layer_mode'] == 'classified':
            if 'classified_notes' in exposure:
                notes += exposure['classified_notes']
        if self.exposure.keywords['layer_mode'] == 'continuous':
            if 'continuous_notes' in exposure:
                notes += exposure['continuous_notes']
        return notes

    def hazard_notes(self):
        """Get the hazard specific notes defined in definitions.

        This method will do a lookup in definitions and return the
        hazard definition specific notes dictionary.

        This is a helper function to make it
        easy to get hazard specific notes from the definitions metadata.

        .. versionadded:: 3.5

        :returns: A list like e.g. safe.definitions.hazard_land_cover[
            'notes']
        :rtype: list, None
        """
        notes = []
        hazard = definition(self.hazard.keywords.get('hazard'))

        if 'notes' in hazard:
            notes += hazard['notes']
        if self.hazard.keywords['layer_mode'] == 'classified':
            if 'classified_notes' in hazard:
                notes += hazard['classified_notes']
        if self.hazard.keywords['layer_mode'] == 'continuous':
            if 'continuous_notes' in hazard:
                notes += hazard['continuous_notes']
        if self.hazard.keywords['hazard_category'] == 'single_event':
            if 'single_event_notes' in hazard:
                notes += hazard['single_event_notes']
        if self.hazard.keywords['hazard_category'] == 'multiple_event':
            if 'multi_event_notes' in hazard:
                notes += hazard['multi_event_notes']
        return notes

    def notes(self):
        """Return the notes section of the report.

        .. versionadded:: 3.5

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        fields = []  # Notes still to be defined for ASH
        # include any generic exposure specific notes from definitions
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions
        fields = fields + self.hazard_notes()

        # include any hazard/exposure notes from definitions
        exposure = definition(self.exposure.keywords.get('exposure'))
        hazard = definition(self.hazard.keywords.get('hazard'))
        fields.extend(specific_notes(hazard, exposure))

        if self._earthquake_function is not None:
            # Get notes specific to the fatality model
            for fatality_model in EARTHQUAKE_FUNCTIONS:
                if fatality_model['key'] == self._earthquake_function:
                    fields.extend(fatality_model.get('notes', []))

        return fields

    def action_checklist(self):
        """Return the list of action check list dictionary.

        :return: The list of action check list dictionary.
        :rtype: list
        """
        actions = []
        exposure = definition(self.exposure.keywords.get('exposure'))
        actions.extend(exposure.get('actions'))

        hazard = definition(self.hazard.keywords.get('hazard'))
        actions.extend(hazard.get('actions'))

        actions.extend(specific_actions(hazard, exposure))
        return actions

    # noinspection PyPep8Naming
    @staticmethod
    def append_ISO19115_keywords(keywords):
        """Append ISO19115 from setting to keywords.

        :param keywords: The keywords destination.
        :type keywords: dict
        """
        # Map setting's key and metadata key
        ISO19115_mapping = {
            'ISO19115_ORGANIZATION': 'organisation',
            'ISO19115_URL': 'url',
            'ISO19115_EMAIL': 'email',
            'ISO19115_LICENSE': 'license'
        }
        ISO19115_keywords = {}
        # Getting value from setting.
        for key, value in ISO19115_mapping.items():
            ISO19115_keywords[value] = setting(key, expected_type=str)
        keywords.update(ISO19115_keywords)
