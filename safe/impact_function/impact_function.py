# coding=utf-8

"""Impact Function."""

import getpass
import platform
from datetime import datetime
from os.path import join, exists
from os import makedirs
from collections import OrderedDict
from copy import deepcopy
from socket import gethostname

from PyQt4.QtCore import QT_VERSION_STR, QSettings
from PyQt4.Qt import PYQT_VERSION_STR
from osgeo import gdal
from qgis.core import (
    QgsMapLayer,
    QgsGeometry,
    QgsCoordinateTransform,
    QgsFeatureRequest,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsVectorLayer,
    QGis,
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
from safe.gis.vector.summary_33_eq_raster_analysis import (
    analysis_eartquake_summary)
from safe.gis.vector.summary_4_exposure_breakdown import (
    exposure_type_breakdown)
from safe.gis.vector.recompute_counts import recompute_counts
from safe.gis.vector.update_value_map import update_value_map
from safe.gis.raster.clip_bounding_box import clip_by_extent
from safe.gis.raster.reclassify import reclassify as reclassify_raster
from safe.gis.raster.polygonize import polygonize
from safe.gis.raster.zonal_statistics import zonal_stats
from safe.gis.raster.align import align_rasters
from safe.gis.raster.rasterize import rasterize_vector_layer
from safe.definitions.post_processors import post_processors
from safe.definitions.analysis_steps import analysis_steps
from safe.definitions.utilities import definition
from safe.definitions.exposure import indivisible_exposure
from safe.definitions.fields import (
    size_field,
    exposure_class_field,
    hazard_class_field,
    count_ratio_mapping,
)
from safe.definitions.layer_purposes import (
    layer_purpose_exposure_impacted,
    layer_purpose_aggregate_hazard_impacted,
    layer_purpose_aggregation_impacted,
    layer_purpose_analysis_impacted,
    layer_purpose_exposure_breakdown,
    layer_purpose_profiling,
)
from safe.impact_function.provenance_utilities import (
    get_map_title,
    get_report_question,
    get_analysis_question
)
from safe.definitions.constants import (
    inasafe_keyword_version_key,
    ANALYSIS_SUCCESS,
    ANALYSIS_FAILED_BAD_INPUT,
    ANALYSIS_FAILED_BAD_CODE,
    PREPARE_SUCCESS,
    PREPARE_FAILED_BAD_INPUT,
    PREPARE_FAILED_INSUFFICIENT_OVERLAP,
    PREPARE_FAILED_INSUFFICIENT_OVERLAP_REQUESTED_EXTENT,
    PREPARE_FAILED_BAD_LAYER,
    PREPARE_FAILED_BAD_CODE)
from safe.definitions.versions import inasafe_keyword_version
from safe.common.exceptions import (
    InaSAFEError,
    InvalidExtentError,
    WrongEarthquakeFunction,
    NoKeywordsFoundError,
    NoFeaturesInExtentError,
    ProcessingInstallationError,
)
from safe.definitions.earthquake import EARTHQUAKE_FUNCTIONS
from safe.impact_function.earthquake import (
    exposed_people_stats,
    make_summary_layer,
)
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
    displaced_people_style,
)
from safe.utilities.gis import is_vector_layer, is_raster_layer
from safe.utilities.i18n import tr
from safe.utilities.unicode import get_unicode
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.metadata import (
    active_thresholds_value_maps, active_classification)
from safe.utilities.utilities import (
    replace_accentuated_characters, get_error_message)
from safe.utilities.profiling import (
    profile, clear_prof_data, profiling_log)
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
        self._datetime = None
        self._provenance = {
            # Environment
            'host_name': gethostname(),
            'user': getpass.getuser(),
            'qgis_version': QGis.QGIS_VERSION,
            'gdal_version': gdal.__version__,
            'qt_version': QT_VERSION_STR,
            'pyqt_version': PYQT_VERSION_STR,
            'os': platform.version(),
            'inasafe_version': get_version(),
        }

        # Earthquake function
        self._earthquake_function = None
        value = setting(
            'earthquake_function', EARTHQUAKE_FUNCTIONS[0]['key'], str)
        self.earthquake_function = value  # Use the setter to check the value.

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
        layers[layer_purpose_exposure_impacted['key']] = (
            self._exposure_impacted)
        layers[layer_purpose_aggregate_hazard_impacted['key']] = (
            self._aggregate_hazard_impacted)
        layers[layer_purpose_aggregation_impacted['key']] = (
            self._aggregation_impacted)
        layers[layer_purpose_analysis_impacted['key']] = (
            self._analysis_impacted)
        layers[layer_purpose_exposure_breakdown['key']] = (
            self._exposure_breakdown)
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
        :rtype: QgsVectorLayer
        """
        if is_vector_layer(self.outputs[0]):
            return self.outputs[0]
        else:
            # In case of EQ raster on population, the exposure impacted is a
            # raster.
            return self.outputs[1]

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
    def datetime(self):
        """The timestamp of the impact function executions.

        :return: The timestamp.
        :rtype: datetime
        """
        return self._datetime

    @property
    def earthquake_function(self):
        """The current earthquake function to use.

        :return: The earthquake function.
        :rtype: str
        """
        return self._earthquake_function

    @earthquake_function.setter
    def earthquake_function(self, function):
        """Set the earthquake function to use.

        :param function: The earthquake function to use.
        :type function: str
        """
        if function not in [model['key'] for model in EARTHQUAKE_FUNCTIONS]:
            raise WrongEarthquakeFunction
        else:
            self._earthquake_function = function

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
            message = generate_input_error_message(
                tr('The %s layer is invalid' % purpose),
                m.Paragraph(tr(
                    'The impact function needs a %s layer to run. '
                    'You must provide a valid %s layer.' % (purpose, purpose)))
            )
            return PREPARE_FAILED_BAD_INPUT, message

        # We should read it using KeywordIO for the very beginning. To avoid
        # get the modified keywords in the patching.
        try:
            keywords = KeywordIO().read_keywords(layer)
        except NoKeywordsFoundError:
            message = generate_input_error_message(
                tr('The %s layer do not have keywords.' % purpose),
                m.Paragraph(tr(
                    'The %s layer do not have keywords. Use the wizard to '
                    'assign keywords to the layer.' % purpose))
            )
            return PREPARE_FAILED_BAD_INPUT, message

        if keywords.get('layer_purpose') != purpose:
            message = generate_input_error_message(
                tr('The %s layer is not an %s.' % (purpose, purpose)),
                m.Paragraph(tr(
                    'The %s layer is not an %s.' % (purpose, purpose)))
            )
            return PREPARE_FAILED_BAD_INPUT, message

        version = keywords.get(inasafe_keyword_version_key)
        if version != inasafe_keyword_version:
            parameters = {
                'version': inasafe_keyword_version,
                'source': layer.source()
            }
            message = generate_input_error_message(
                tr('The %s layer is not up to date.' % purpose),
                m.Paragraph(
                    tr('The layer {source} must be updated to {version}.'
                        .format(**parameters))))
            return PREPARE_FAILED_BAD_INPUT, message

        layer.keywords = keywords
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

                status, message = self._check_layer(
                    self.aggregation, 'aggregation')
                aggregation_source = self.aggregation.source()
                aggregation_keywords = deepcopy(self.aggregation.keywords)

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
            self._provenance['exposure_layer'] = self.exposure.source()
            # reference to original layer being used
            self._provenance['exposure_layer_id'] = original_exposure.id()
            self._provenance['exposure_keywords'] = deepcopy(
                self.exposure.keywords)
            self._provenance['hazard_layer'] = self.hazard.source()
            # reference to original layer being used
            self._provenance['hazard_layer_id'] = original_hazard.id()
            self._provenance['hazard_keywords'] = deepcopy(
                self.hazard.keywords)
            # reference to original layer being used
            if original_aggregation:
                self._provenance['aggregation_layer_id'] = (
                    original_aggregation.id())
            else:
                self._provenance['aggregation_layer_id'] = None
            self._provenance['aggregation_layer'] = aggregation_source
            self._provenance['aggregation_keywords'] = aggregation_keywords

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

            self._analysis_extent = QgsGeometry.unaryUnion(list_geometry)
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
            self._provenance_ready = True
            self._datetime = datetime.now()
            self._provenance['datetime'] = self.datetime
            return ANALYSIS_SUCCESS, None

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

        # Special case for Raster Earthquake hazard on Raster population.
        damage_curve = False
        if is_raster_layer(self.hazard):
            if self.hazard.keywords.get('hazard') == 'earthquake':
                if is_raster_layer(self.exposure):
                    if self.exposure.keywords.get('exposure') == 'population':
                        damage_curve = True

        if damage_curve:
            self.damage_curve_analysis()
        else:
            self.gis_overlay_analysis()

        self._performance_log = profiling_log()
        self.callback(7, step_count, analysis_steps['post_processing'])
        if is_vector_layer(self._exposure_impacted):
            # We post process the exposure impacted
            self.post_process(self._exposure_impacted)
        else:
            if is_vector_layer(self._aggregate_hazard_impacted):
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

        # Exposure impacted
        if self._exposure_impacted:
            self._exposure_impacted.keywords[
                'provenance_data'] = self.provenance
            result, name = self.datastore.add_layer(
                self._exposure_impacted,
                layer_purpose_exposure_impacted['key'])
            if not result:
                raise Exception(
                    tr('Something went wrong with the datastore : '
                       '{error_message}').format(error_message=name))
            self._exposure_impacted = self.datastore.layer(name)
            self.debug_layer(self._exposure_impacted, add_to_datastore=False)

        # Aggregate hazard impacted
        if self.aggregate_hazard_impacted:
            self.aggregate_hazard_impacted.keywords[
                'provenance_data'] = self.provenance
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

        # Exposure breakdown
        if self._exposure.keywords.get('classification'):
            self._exposure_breakdown.keywords[
                'provenance_data'] = self.provenance
            result, name = self.datastore.add_layer(
                self._exposure_breakdown,
                layer_purpose_exposure_breakdown['key'])
            if not result:
                raise Exception(
                    tr('Something went wrong with the datastore : '
                       '{error_message}').format(error_message=name))
            self._exposure_breakdown = self.datastore.layer(name)
            self.debug_layer(self._exposure_breakdown, add_to_datastore=False)

        # Aggregation impacted
        self.aggregation_impacted.keywords['provenance_data'] = self.provenance
        result, name = self.datastore.add_layer(
            self._aggregation_impacted,
            layer_purpose_aggregation_impacted['key'])
        if not result:
            raise Exception(
                tr('Something went wrong with the datastore : '
                   '{error_message}').format(error_message=name))
        self._aggregation_impacted = self.datastore.layer(name)
        self.debug_layer(self._aggregation_impacted, add_to_datastore=False)

        # Analysis impacted
        self.analysis_impacted.keywords['provenance_data'] = self.provenance
        result, name = self.datastore.add_layer(
            self._analysis_impacted, layer_purpose_analysis_impacted['key'])
        if not result:
            raise Exception(
                tr('Something went wrong with the datastore : '
                   '{error_message}').format(error_message=name))
        self._analysis_impacted = self.datastore.layer(name)
        self.debug_layer(self._analysis_impacted, add_to_datastore=False)

    @profile
    def gis_overlay_analysis(self):
        """Perform an overlay analysis between the exposure and the hazard."""
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

    @profile
    def damage_curve_analysis(self):
        """Perform a damage curve analysis."""
        # For now we support only the earthquake raster on population raster.
        self.earthquake_raster_population_raster()

    @profile
    def earthquake_raster_population_raster(self):
        """Perform a damage curve analysis with EQ raster on population raster.
        """
        classification_key = active_classification(
            self.hazard.keywords, 'population')
        thresholds = active_thresholds_value_maps(
            self.hazard.keywords, 'population')
        self.hazard.keywords['classification'] = classification_key
        self.hazard.keywords['thresholds'] = thresholds
        self.aggregation.keywords['hazard_keywords'] = dict(
            self.hazard.keywords)

        fatality_rates = {}
        for model in EARTHQUAKE_FUNCTIONS:
            fatality_rates[model['key']] = model['fatality_rates']
        earthquake_function = fatality_rates[self.earthquake_function]

        self.set_state_process(
            'hazard', 'Align the hazard layer with the exposure')
        self.set_state_process(
            'exposure', 'Align the exposure layer with the hazard')
        self.hazard, self.exposure = align_rasters(
            self.hazard, self.exposure, self.analysis_impacted.extent())
        self.debug_layer(self.hazard)
        self.debug_layer(self.exposure)

        self.set_state_process(
            'aggregation', 'Rasterize the aggregation layer')
        aggregation_aligned = rasterize_vector_layer(
            self.aggregation,
            self.hazard.dataProvider().xSize(),
            self.hazard.dataProvider().ySize(),
            self.hazard.extent())
        self.debug_layer(aggregation_aligned)

        self.set_state_process('exposure', 'Compute exposed people')
        exposed, self._exposure_impacted = exposed_people_stats(
            self.hazard,
            self.exposure,
            aggregation_aligned,
            earthquake_function())
        self.debug_layer(self._exposure_impacted)

        self.set_state_process('impact function', 'Set summaries')
        self._aggregation_impacted = make_summary_layer(
            exposed, self.aggregation, earthquake_function())
        self._aggregation_impacted.keywords['exposure_keywords'] = dict(
            self.exposure_impacted.keywords)
        self._aggregation_impacted.keywords['hazard_keywords'] = dict(
            self.hazard.keywords)
        self.debug_layer(self._aggregation_impacted)

    @profile
    def aggregation_preparation(self):
        """This function is doing the aggregation preparation."""
        if not self.aggregation:
            self.set_state_info('aggregation', 'provided', False)

            self.set_state_process(
                'aggregation',
                'Convert bbox aggregation to polygon layer with keywords')
            self.aggregation = create_virtual_aggregation(
                self.analysis_extent, self.exposure.crs())
            self.debug_layer(self.aggregation)

            if is_vector_layer(self.exposure):
                # We need to check if we can add default ratios to the
                # exposure (only if it's a vector).
                exposure = definition(self.exposure.keywords['exposure'])
                keywords = self.exposure.keywords
                # inasafe_default_values will not exist as we can't use
                # default in the exposure layer.
                keywords['inasafe_default_values'] = {}
                for count_field in exposure['extra_fields']:
                    count_key = count_field['key']
                    if count_key in count_ratio_mapping.keys():
                        if count_key not in keywords['inasafe_fields']:
                            # The exposure hasn't a count field, we should add
                            #  it.
                            ratio_field = count_ratio_mapping[count_key]
                            default = definition(ratio_field)['default_value']
                            keywords['inasafe_default_values'][ratio_field] = (
                                default['default_value'])

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
            aggregation_default_fields = aggregation_keywords.get(
                'inasafe_default_values', {})
            for count_field in exposure['extra_fields']:
                if count_field['key'] in count_ratio_mapping.keys():
                    ratio_field = count_ratio_mapping[count_field['key']]
                    if count_field['key'] not in exposure_fields:

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
                            LOGGER.info(
                                tr('{ratio} field detected, we will propagate '
                                   'it to the exposure layer.').format(
                                        ratio=ratio_field))
                            continue

                        if ratio_is_a_constant and not ratio_is_a_field:
                            # It's a constant. We need to add to the exposure.
                            exposure_defaults[ratio_field] = (
                                aggregation_default_fields[ratio_field])
                            LOGGER.info(
                                tr('{ratio} constant detected, we will add it '
                                   'to the exposure layer.').format(
                                    ratio=ratio_field))

                    else:
                        if ratio_field in aggregation_fields:
                            # The count field is in the exposure and the ratio
                            # is in the aggregation. We need to remove it from
                            # the aggregation. We remove the keyword too.
                            remove_fields(
                                self.aggregation,
                                [aggregation_fields[ratio_field]])
                            del aggregation_fields[ratio_field]

        self.set_state_process(
            'aggregation',
            'Convert the aggregation layer to the analysis layer')
        self._analysis_impacted = create_analysis_layer(
            self.analysis_extent, self.exposure.crs(), self.name)
        self.debug_layer(self._analysis_impacted)

    @profile
    def hazard_preparation(self):
        """This function is doing the hazard preparation."""
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
            self.set_state_process(
                'hazard',
                'Classify continuous hazard and assign class names')
            self.hazard = reclassify_vector(
                self.hazard, self.exposure.keywords['exposure'])
            self.debug_layer(self.hazard)

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
        if is_raster_layer(self.exposure):
            self.set_state_process(
                'impact function',
                'Zonal stats between exposure and aggregate hazard')
            # noinspection PyTypeChecker
            self._aggregate_hazard_impacted = zonal_stats(
                self.exposure, self._aggregate_hazard_impacted)
            self.debug_layer(self._aggregate_hazard_impacted)

            # We can monkey patch keywords here for global defaults.
            keywords = self._aggregate_hazard_impacted.keywords
            keywords['inasafe_default_values'] = {}
            for ratio in count_ratio_mapping.itervalues():
                ratio_field = definition(ratio)
                default = ratio_field['default_value']['default_value']
                key = ratio_field['key']
                keywords['inasafe_default_values'][key] = default
                LOGGER.info(
                    'Adding default {value} for {type} into keywords'.format(
                        value=default, type=key))

            # We add ratios to the agrgegate hazard layer, we do not need them
            # for post processing as we will use the population count. It's
            # easier for user to see this field in the attribute tabler.
            self.set_state_process('impact function', 'Add default values')
            self._aggregate_hazard_impacted = add_default_values(
                self._aggregate_hazard_impacted)
            self.debug_layer(self._aggregate_hazard_impacted)

            # I know it's redundant, it's just to be sure that we don't have
            # any impact layer for that IF.
            self._exposure_impacted = None

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
                self._exposure_impacted = intersection(
                    self._exposure, self._aggregate_hazard_impacted)
                self.debug_layer(self._exposure_impacted)

                # If the layer has the size field, it means we need to
                # recompute counts based on the old and new size.
                fields = self._exposure_impacted.keywords['inasafe_fields']
                if size_field['key'] in fields:
                    self.set_state_process(
                        'impact function',
                        'Recompute counts')
                    self._exposure_impacted = recompute_counts(
                        self._exposure_impacted)
                    self.debug_layer(self._exposure_impacted)

            else:
                self.set_state_process(
                    'impact function',
                    'Highest class of hazard is assigned to the exposure')
                self._exposure_impacted = assign_highest_value(
                    self._exposure, self._aggregate_hazard_impacted)
                self.debug_layer(self._exposure_impacted)

            if self._exposure_impacted:
                self._exposure_impacted.keywords['title'] = (
                    layer_purpose_exposure_impacted['key'])

    @profile
    def post_process(self, layer):
        """More process after getting the impact layer with data.

        :param layer: The vector layer to use for post processing.
        :type layer: QgsVectorLayer
        """
        # Set the layer title
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

            else:
                message = u'{name} : Could not run : {reason}'.format(
                    name=name, reason=message)

            LOGGER.info(message)

        self.debug_layer(layer, add_to_datastore=False)

    @profile
    def summary_calculation(self):
        """Do the summary calculation.

        We do not check layers here, we will check them in the next step.
        """
        if is_vector_layer(self._exposure_impacted):
            # The exposure impacted might be a raster if it's an EQ if.
            self.set_state_process(
                'impact function',
                'Aggregate the impact summary')
            self._aggregate_hazard_impacted = aggregate_hazard_summary(
                self.exposure_impacted, self._aggregate_hazard_impacted)
            self.debug_layer(self._exposure_impacted, add_to_datastore=False)

        if self._aggregate_hazard_impacted:
            self.set_state_process(
                'impact function',
                'Aggregate the aggregation summary')
            self._aggregation_impacted = aggregation_summary(
                self._aggregate_hazard_impacted, self.aggregation)
            self.debug_layer(
                self._aggregation_impacted, add_to_datastore=False)

            self.set_state_process(
                'impact function',
                'Aggregate the analysis summary')
            self._analysis_impacted = analysis_summary(
                self._aggregate_hazard_impacted, self._analysis_impacted)
            self.debug_layer(self._analysis_impacted)

            if self._exposure.keywords.get('classification'):
                self.set_state_process(
                    'impact function',
                    'Build the exposure breakdown')
                self._exposure_breakdown = exposure_type_breakdown(
                    self._aggregate_hazard_impacted)
                self.debug_layer(
                    self._exposure_breakdown, add_to_datastore=False)
        else:
            # We are running EQ raster on population raster.
            self.set_state_process(
                'impact function',
                'Aggregate the earthquake analysis summary')
            self._analysis_impacted = analysis_eartquake_summary(
                self.aggregation_impacted, self.analysis_impacted)
            self.debug_layer(self._analysis_impacted, add_to_datastore=False)

    def style(self):
        """Function to apply some styles to the layers."""
        if self.hazard.keywords.get('classification'):
            classes = generate_classified_legend(
                self.analysis_impacted,
                self.exposure,
                self.hazard,
                self.debug_mode)

            # Let's style layers which have a geometry and have hazard_class
            hazard_class = hazard_class_field['key']
            for layer in self.outputs:
                if is_vector_layer(layer):
                    without_geometries = [
                        QGis.NoGeometry, QGis.UnknownGeometry]
                    if layer.geometryType() not in without_geometries:
                        display_not_exposed = False
                        if layer == self.impact or self.debug_mode:
                            display_not_exposed = True

                        if layer.keywords['inasafe_fields'].get(hazard_class):
                            hazard_class_style(
                                layer, classes, display_not_exposed)
        else:
            # The IF might be EQ on population. There is not a classification.
            pass

            else:
                displaced_people_style(layer)

        # Let's style the aggregation and analysis layer.
        simple_polygon_without_brush(self.aggregation_impacted)
        simple_polygon_without_brush(self.analysis_impacted)

    @property
    def provenance(self):
        """Helper method to gather provenance for exposure_impacted layer.

        If the impact function is not ready (has not called prepare method),
        it will return empty dict to avoid miss information.

        List of keys (for quick lookup):

        [
            'exposure_keywords',
            'hazard_keywords',
            'impact_function_name',
            'impact_function_title',
            'map_title',
            'map_legend_title',
            'analysis_question',
            'report_question',
            'requested_extent',
            'analysis_extent',
            'data_store_uri',
            'notes',
            'action_checklist',
        ]

        :returns: Dictionary that contains all provenance.
        :rtype: dict
        """
        if not self._provenance_ready:
            return {}

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
        self._provenance['impact_function_name'] = self.name
        self._provenance['impact_function_title'] = self.title

        # Map title
        self._provenance['map_title'] = get_map_title(
            hazard, exposure, hazard_category)
        self._provenance['map_legend_title'] = exposure['layer_legend_title']

        self._provenance['analysis_question'] = get_analysis_question(
            hazard, exposure)
        self._provenance['report_question'] = get_report_question(exposure)

        if self.requested_extent:
            self._provenance['requested_extent'] = (
                self.requested_extent.asWktCoordinates()
            )
        else:
            self._provenance['requested_extent'] = None
        self._provenance['analysis_extent'] = (
            self.analysis_extent.exportToWkt()
        )
        self._provenance['data_store_uri'] = self.datastore.uri

        # Notes and Action
        self._provenance['notes'] = self.notes()
        self._provenance['action_checklist'] = self.action_checklist()

        return self._provenance

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
        return fields

    def action_checklist(self):
        """Return the action check list.

        :return: The action check list.
        :rtype: list
        """
        exposure = definition(self.exposure.keywords.get('exposure'))
        hazard = definition(self.hazard.keywords.get('hazard'))

        return exposure.get('actions') + hazard.get('actions')
