# coding=utf-8

"""
Multi-exposure wrapper.

This class will manage how to launch and optimize a multi exposure analysis.
"""

import getpass
import logging
from copy import deepcopy
from datetime import datetime
from os import makedirs
from os.path import join, exists
from socket import gethostname

from osgeo import gdal
from qgis.core import (
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsMapLayer,
    QgsVectorLayer,
    QgsProject,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer)
from qgis.utils import iface
from PyQt4.Qt import PYQT_VERSION_STR
from PyQt4.QtCore import QDir, QT_VERSION_STR

from safe import messaging as m
from safe.common.exceptions import InvalidExtentError
from safe.common.utilities import temp_dir
from safe.common.version import get_version
from safe.datastore.datastore import DataStore
from safe.datastore.folder import Folder
from safe.definitions.constants import (
    PREPARE_SUCCESS,
    PREPARE_FAILED_BAD_INPUT,
    ANALYSIS_FAILED_BAD_INPUT,
    ANALYSIS_SUCCESS,
    MULTI_EXPOSURE_ANALYSIS_FLAG)
from safe.definitions.layer_purposes import (
    layer_purpose_analysis_impacted,
    layer_purpose_aggregation_summary,
    layer_purpose_exposure_summary)
from safe.definitions.provenance import (
    provenance_aggregation_keywords,
    provenance_aggregation_layer,
    provenance_aggregation_layer_id,
    provenance_analysis_extent,
    provenance_crs,
    provenance_data_store_uri,
    provenance_duration,
    provenance_end_datetime,
    provenance_gdal_version,
    provenance_multi_exposure_keywords,
    provenance_multi_exposure_layers,
    provenance_multi_exposure_layers_id,
    provenance_hazard_keywords,
    provenance_hazard_layer,
    provenance_hazard_layer_id,
    provenance_host_name,
    provenance_impact_function_name,
    provenance_inasafe_version,
    provenance_os,
    provenance_pyqt_version,
    provenance_qgis_version,
    provenance_qt_version,
    provenance_start_datetime,
    provenance_user,
    provenance_layer_aggregation_summary,
    provenance_layer_analysis_impacted,
    provenance_layer_aggregation_summary_id,
    provenance_layer_analysis_impacted_id,
    provenance_debug_mode,
    provenance_map_title,
    provenance_multi_exposure_summary_layers)
from safe.definitions.reports.components import (
    standard_impact_report_metadata_pdf, infographic_report)
from safe.definitions.styles import (
    aggregation_color,
    aggregation_width,
    analysis_color,
    analysis_width,
)
from safe.definitions.utilities import (
    get_name,
    get_provenance,
    set_provenance,
)
from safe.gis.tools import (
    geometry_type, load_layer_from_registry, full_layer_uri)
from safe.gis.vector.prepare_vector_layer import prepare_vector_layer
from safe.gis.vector.summary_5_multi_exposure import (
    multi_exposure_analysis_summary,
    multi_exposure_aggregation_summary,
)
from safe.gui.widgets.message import generate_input_error_message
from safe.impact_function.create_extra_layers import (
    create_analysis_layer, create_virtual_aggregation)
from safe.impact_function.impact_function import ImpactFunction
from safe.impact_function.impact_function_utilities import (
    check_input_layer, FROM_CANVAS)
from safe.impact_function.style import simple_polygon_without_brush
from safe.report.impact_report import ImpactReport
from safe.report.report_metadata import ReportMetadata
from safe.utilities.gis import clone_layer
from safe.utilities.i18n import tr
from safe.utilities.gis import qgis_version
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.metadata import (
    copy_layer_keywords,
    write_iso19115_metadata,
    append_ISO19115_keywords,
)
from safe.utilities.settings import setting
from safe.utilities.unicode import get_unicode, byteify
from safe.utilities.utilities import (
    replace_accentuated_characters,
    readable_os_version,
)

LOGGER = logging.getLogger('InaSAFE')
IFACE = iface

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class MultiExposureImpactFunction(object):

    """Multi-exposure wrapper.

    .. versionadded:: 4.3
    """

    def __init__(self):
        """Constructor."""
        # Input layers
        self._hazard = None
        self._aggregation = None

        # Exposures, it's now a list of layers. One for each exposure maximum.
        self._exposures = []

        # For now, we have many IF running.
        self._impact_functions = []
        self._current_impact_function = None

        # The current extent defined by the impact function. Read-only.
        # The CRS is the aggregation CRS or the crs property if no
        # aggregation.
        self._analysis_extent = None
        self._crs = None

        # Datastore when to save layers specific to the multi-exposure.
        # Individual IF will have the default datatstore provided by the IF.
        self._datastore = None

        # Layers
        self._aggregation_summary = None
        self._analysis_summary = None

        # Use debug to store intermediate results
        self.debug_mode = False

        # Metadata
        self.callback = None
        self.debug = False
        self.use_selected_features_only = False
        self._name = None
        self._unique_name = None
        self._is_ready = False
        self._start_datetime = None
        self._end_datetime = None
        self._duration = 0
        self._output_layer_expected = None
        self._output_layers_ordered = None
        self._provenance_ready = False
        self._provenance = {}

        # Impact Report
        self._impact_report = None
        self._report_metadata = []

        # Environment
        set_provenance(self._provenance, provenance_host_name, gethostname())
        set_provenance(self._provenance, provenance_user, getpass.getuser())
        set_provenance(
            self._provenance, provenance_qgis_version, qgis_version())
        set_provenance(
            self._provenance, provenance_gdal_version, gdal.__version__)
        set_provenance(self._provenance, provenance_qt_version, QT_VERSION_STR)
        set_provenance(
            self._provenance, provenance_pyqt_version, PYQT_VERSION_STR)
        set_provenance(
            self._provenance, provenance_os, readable_os_version())
        set_provenance(
            self._provenance, provenance_inasafe_version, get_version())

    @property
    def name(self):
        """The name of the impact function.

        :returns: The name.
        :rtype: basestring
        """
        return self._name

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
    def crs(self):
        """Property for the extent CRS of impact function analysis.

        This property must be null if we use an aggregation layer.
        Otherwise, this parameter must be set. It will be the analysis CRS.

        :return crs: The coordinate reference system for the analysis boundary.
        :rtype: QgsCoordinateReferenceSystem
        """
        return self._crs

    @crs.setter
    def crs(self, crs):
        """Setter for extent_crs property.

        :param crs: The coordinate reference system for the analysis boundary.
        :type crs: QgsCoordinateReferenceSystem
        """
        if isinstance(crs, QgsCoordinateReferenceSystem):
            self._crs = crs
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
    def outputs(self):
        """List of layers containing outputs from the multi exposure IF.

        :returns: A list of vector layers.
        :rtype: list
        """
        outputs = [
            self._aggregation_summary,
            self._analysis_summary
        ]
        return outputs

    @property
    def aggregation_summary(self):
        """Property for the aggregation summary.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._aggregation_summary

    @property
    def analysis_impacted(self):
        """Property for the analysis summary.

        :returns: A vector layer.
        :rtype: QgsVectorLayer
        """
        return self._analysis_summary

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
    def exposures(self):
        """Property for exposure layers to be used for the analysis.

        :returns: List of map layers.
        :rtype: list(QgsMapLayer)
        """
        return self._exposures

    @exposures.setter
    def exposures(self, layers):
        """Setter for exposure layers property.

        :param layers: List of exposure layers to be used for the analysis.
        :type layers: list(QgsMapLayer)
        """
        self._exposures = layers
        self._is_ready = False

    def add_exposure(self, layer):
        """Add an exposure layer in the analysis.

        :param layer: An exposure layer to be used for the analysis.
        :type layer: QgsMapLayer
        """
        self._exposures.append(layer)
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
    def impact_functions(self):
        """Return the list of impact functions which have been used.

        :return: List of impact functions.
        :rtype: list(ImpactFunction)
        """
        return self._impact_functions

    @property
    def current_impact_function(self):
        """Return the current IF being processed.

        :return: Impact function.
        :rtype: ImpactFunction
        """
        return self._current_impact_function

    @property
    def output_layers_ordered(self):
        """Return the custom order input from user.

        :return: List of layer order tuples.
        :rtype: list
        """
        return self._output_layers_ordered

    @output_layers_ordered.setter
    def output_layers_ordered(self, layers):
        """Setter for custom layer order property.

        :param layers: List of layer order tuples.
        :type layers: list
        """
        self._output_layers_ordered = layers

    @property
    def impact_report(self):
        """Property for an impact report.

        :return: An impact report object.
        :rtype: ImpactReport
        """
        return self._impact_report

    @impact_report.setter
    def impact_report(self, impact_report):
        """Setter for the impact report.

        :param impact_report: The impact report object.
        :type impact_report: ImpactReport
        """
        self._impact_report = impact_report

    @property
    def report_metadata(self):
        """Property for report metadata generated by this ImpactFunction.

        :return: A list of ReportMetadata object.
        :rtype: list
        """
        return self._report_metadata

    def output_layers_expected(self):
        """Compute the output layers expected that the IF will produce.

        You must call this function between the `prepare` and the `run`.
        Otherwise you will get an empty dictionary.

        Result:
        {
            'multi_exposure_name': [aggregation_summary, analysis_summary]
            'impact_function_1_name: [impact_layer, aggregate_hazard, ...]
            'impact_function_2_name: [impact_layer, aggregate_hazard, ...]
            ...
        }

        :return: Tree of expected layers.
        :rtype: dictionary
        """
        if not self._is_ready:
            return {}
        else:
            return self._output_layer_expected

    def _compute_output_layer_expected(self):
        """Compute output layers expected that the IF will produce.

        Be careful when you call this function. It's a private function, better
        to use the public function `output_layers_expected()`.

        :return: List of expected layer keys.
        :rtype: list
        """
        results = {
            self._name: [
                layer_purpose_aggregation_summary['key'],
                layer_purpose_analysis_impacted['key']
            ]
        }
        for analysis in self._impact_functions:
            results[analysis.name] = analysis.output_layers_expected()
        return results

    @property
    def provenance(self):
        """Helper method to gather provenance for aggregation summary layer.

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
        # InaSAFE
        set_provenance(
            self._provenance, provenance_impact_function_name, self.name)

        set_provenance(
            self._provenance,
            provenance_analysis_extent,
            self._analysis_extent.exportToWkt())

        set_provenance(
            self._provenance,
            provenance_data_store_uri,
            self.datastore.uri_path)

        # Map title
        set_provenance(self._provenance, provenance_map_title, self.name)

        # CRS
        set_provenance(
            self._provenance, provenance_crs, self._crs.authid())

        # Debug mode
        set_provenance(
            self._provenance, provenance_debug_mode, self.debug_mode)

        self._provenance_ready = True

    def __eq__(self, other):
        """Operator overloading for equal (=).

        :param other: Other Impact Function to be compared.
        :type other: ImpactFunction

        :returns: True if both are the same IF, other wise False.
        :rtype: bool
        """
        return self.is_equal(other)[0]

    def is_equal(self, other):
        """Equality checker with message

        :param other: Other Impact Function to be compared.
        :type other: ImpactFunction

        :returns: True if both are the same IF, other wise False and the
            message.
        :rtype: bool, str
        """
        def check_qgs_map_layers(layer_a, layer_b, if_property):
            """Internal function to check two layers

            :param layer_a: Layer A
            :type layer_a: QgsMapLayer
            :param layer_b: Layer B
            :type layer_b: QgsMapLayer

            :param if_property: Property currently checked
            :type if_property: basestring

            :return: Tuple with bool and error message if needed
            :rtype: (bool, basestring)
            """
            if byteify(layer_a.keywords) != byteify(
                    layer_b.keywords):
                message = (
                    'Keyword Layer is not equal is %s' % if_property)
                return False, message
            if isinstance(layer_a, QgsVectorLayer):
                fields_a = [f.name() for f in layer_a.fields()]
                fields_b = [f.name() for f in layer_b.fields()]
                if fields_a != fields_b:
                    message = (
                        'Layer fields is not equal for %s' %
                        if_property)
                    return False, message
                if (layer_a.featureCount() !=
                        layer_b.featureCount()):
                    message = (
                        'Feature count is not equal for %s' %
                        if_property)
                    return False, message
            return True, None

        properties = [
            'debug_mode',
            'crs',
            'analysis_extent',
            'datastore',
            'name',
            'start_datetime',
            'end_datetime',
            'duration',
            'hazard',
            'aggregation',
            'exposures',
            'aggregation_summary',
            'analysis_impacted',
            # 'impact_functions'
        ]
        for if_property in properties:
            try:
                property_a = getattr(self, if_property)
                property_b = getattr(other, if_property)
                if type(property_a) != type(property_b):
                    message = (
                        'Different type of property %s.\nA: %s\nB: %s' % (
                            if_property, type(property_a), type(property_b)))
                    return False, message
                if isinstance(property_a, QgsMapLayer):
                    status, message = check_qgs_map_layers(
                        property_a, property_b, if_property)
                    if not status:
                        return status, message
                elif isinstance(property_a, QgsGeometry):
                    if not property_a.equals(property_b):
                        string_a = property_a.exportToWkt()
                        string_b = property_b.exportToWkt()
                        message = (
                            '[Non Layer] The not equal property is %s.\n'
                            'A: %s\nB: %s' % (if_property, string_a, string_b))
                        return False, message
                elif isinstance(property_a, DataStore):
                    if property_a.uri_path != property_b.uri_path:
                        string_a = property_a.uri_path
                        string_b = property_b.uri_path
                        message = (
                            '[Non Layer] The not equal property is %s.\n'
                            'A: %s\nB: %s' % (if_property, string_a, string_b))
                        return False, message
                elif (isinstance(property_a, tuple) or
                        isinstance(property_a, list)):
                    if len(property_a) == len(property_b) == 0:
                        continue
                    elif len(property_a) and \
                            isinstance(property_a[0], QgsMapLayer):
                        for layer_a, layer_b in zip(property_a, property_b):
                            status, message = check_qgs_map_layers(
                                layer_a, layer_b, if_property)
                            if not status:
                                return status, message
                    elif len(property_a) and \
                            isinstance(property_a[0], ImpactFunction):
                        # Need to check if it's necessary
                        pass
                    else:
                        message = (
                            '[Non Layer] The not equal property is %s.\n'
                            'A: %s\nB: %s' % (
                                if_property, property_a, property_b))
                        return False, message
                else:
                    if property_a != property_b:
                        string_a = get_unicode(property_a)
                        string_b = get_unicode(property_b)
                        message = (
                            '[Non Layer] The not equal property is %s.\n'
                            'A: %s\nB: %s' % (if_property, string_a, string_b))
                        return False, message
            except AttributeError as e:
                message = (
                    'Property %s is not found. The exception is %s' % (
                        if_property, e))
                return False, message
            except IndexError as e:
                if if_property == 'impact':
                    continue
                else:
                    message = (
                        'Property %s is out of index. The exception is %s' % (
                            if_property, e))
                    return False, message
            except Exception as e:
                message = (
                    'Error on %s with error message %s' % (if_property, e))
                return False, message

        return True, ''

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
        if len(self._exposures) < 2:  # 2 layers minimum.
            message = generate_input_error_message(
                tr('Not enough exposure layer'),
                m.Paragraph(tr('You need to provide at least two exposures.')))
            self._is_ready = False
            return PREPARE_FAILED_BAD_INPUT, message

        existing_exposure = []
        for exposure in self._exposures:
            status, message = check_input_layer(exposure, 'exposure')
            if status != PREPARE_SUCCESS:
                return status, message

            if exposure.keywords['exposure'] in existing_exposure:
                message = generate_input_error_message(
                    tr('Same exposure'),
                    m.Paragraph(tr('Not the same exposure')))
                self._is_ready = False
                return PREPARE_FAILED_BAD_INPUT, message
            else:
                existing_exposure.append(exposure.keywords['exposure'])

        status, message = check_input_layer(self.hazard, 'hazard')
        if status != PREPARE_SUCCESS:
            return status, message

        if self.aggregation:
            status, message = check_input_layer(
                self.aggregation, 'aggregation')
            if status != PREPARE_SUCCESS:
                return status, message

            if self._crs:
                message = generate_input_error_message(
                    tr('Error with the requested CRS'),
                    m.Paragraph(tr(
                        'Requested CRS must be null when an '
                        'aggregation is provided in the multiexposure '
                        'analysis.'))
                )
                return PREPARE_FAILED_BAD_INPUT, message
        else:
            if not self._crs:
                message = generate_input_error_message(
                    tr('Error with the requested CRS'),
                    m.Paragraph(tr(
                        'CRS must be set when you don\'t use an '
                        'aggregation layer. It will be used for the '
                        'analysis CRS in the multiexposue analysis..'))
                )
                return PREPARE_FAILED_BAD_INPUT, message

        # We let other checks like extent,... to the first single exposure IF.
        # The prepare step will fail if needed and the stop the multiexposure.

        self._impact_functions = []

        # We delegate the prepare to the main IF for each exposure
        for exposure in self._exposures:
            impact_function = ImpactFunction()
            impact_function.debug_mode = self.debug_mode
            impact_function.hazard = clone_layer(self._hazard)
            impact_function.exposure = exposure
            impact_function.debug_mode = self.debug
            if self.callback:
                impact_function.callback = self.callback
            if self._aggregation:
                impact_function.aggregation = clone_layer(
                    self._aggregation)
                impact_function.use_selected_features_only = (
                    self.use_selected_features_only)
            else:
                impact_function.crs = self._crs

            code, message = impact_function.prepare()
            if code != PREPARE_SUCCESS:
                return code, message

            self._impact_functions.append(impact_function)

        hazard_name = get_name(self.hazard.keywords.get('hazard'))
        hazard_geometry_name = get_name(geometry_type(self.hazard))
        self._name = (
            u'Multi exposure {hazard_type} {hazard_geometry} On '.format(
                hazard_type=hazard_name, hazard_geometry=hazard_geometry_name))
        exposures_strings = []
        for exposure in self.exposures:
            exposure_name = get_name(exposure.keywords.get('exposure'))
            exposure_geometry_name = get_name(geometry_type(exposure))
            exposures_strings.append(
                u'{exposure_type} {exposure_geometry}'.format(
                    exposure_type=exposure_name,
                    exposure_geometry=exposure_geometry_name))
        self._name += ', '.join(exposures_strings)

        self._output_layer_expected = self._compute_output_layer_expected()

        # Set provenance
        set_provenance(
            self._provenance,
            provenance_multi_exposure_layers,
            [l.source() for l in self._exposures])
        # reference to original layer being used
        set_provenance(
            self._provenance,
            provenance_multi_exposure_layers_id,
            [l.id() for l in self._exposures])
        set_provenance(
            self._provenance,
            provenance_multi_exposure_keywords,
            {l.keywords['exposure']: copy_layer_keywords(l.keywords)
                for l in self.exposures})
        set_provenance(
            self._provenance,
            provenance_hazard_layer,
            self.hazard.publicSource())
        # reference to original layer being used
        set_provenance(
            self._provenance,
            provenance_hazard_layer_id,
            self.hazard.id())
        set_provenance(
            self._provenance,
            provenance_hazard_keywords,
            copy_layer_keywords(self.hazard.keywords))
        # reference to original layer being used
        if self.aggregation:
            set_provenance(
                self._provenance,
                provenance_aggregation_layer_id,
                self.aggregation.id())
            set_provenance(
                self._provenance,
                provenance_aggregation_layer,
                self.aggregation.source())
            set_provenance(
                self._provenance,
                provenance_aggregation_keywords,
                copy_layer_keywords(self.aggregation.keywords))
        else:
            set_provenance(
                self._provenance,
                provenance_aggregation_layer_id,
                None)
            set_provenance(
                self._provenance,
                provenance_aggregation_layer,
                None)
            set_provenance(
                self._provenance,
                provenance_aggregation_keywords,
                None)

        self._is_ready = True
        return PREPARE_SUCCESS, None

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
            message = generate_input_error_message(
                tr('You need to run `prepare` first.'),
                m.Paragraph(tr(
                    'In order to run the analysis, you need to call '
                    '"prepare" before this function.')))
            return ANALYSIS_FAILED_BAD_INPUT, message

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

            default_user_directory = setting('defaultUserDirectory')
            if default_user_directory:
                path = join(default_user_directory, self._unique_name)
                if not exists(path):
                    makedirs(path)
                self._datastore = Folder(path)
            else:
                self._datastore = Folder(temp_dir(sub_dir=self._unique_name))

            self._datastore.default_vector_format = 'geojson'
        LOGGER.info('Datastore : %s' % self.datastore.uri_path)

        if self._aggregation:
            self._crs = self.aggregation.crs()
            self._aggregation_summary = prepare_vector_layer(self.aggregation)

        analysis_layers = []
        aggregation_layers = []
        list_geometries = []
        list_of_analysis_path = []

        for i, impact_function in enumerate(self._impact_functions):
            self._current_impact_function = impact_function
            LOGGER.info('Running %s' % impact_function.name)
            if isinstance(self._datastore, Folder):
                # We can include this analysis in the parent datastore.
                # We can't do that with a geopackage.
                current_name = impact_function.name.replace(' ', '')
                current_name = replace_accentuated_characters(current_name)
                folder = temp_dir(join(self._datastore.uri_path, current_name))
                if not exists(folder):
                    makedirs(folder)
                impact_function.datastore = Folder(folder)
                impact_function.datastore.default_vector_format = 'geojson'

            code, message = impact_function.run()
            if code != ANALYSIS_SUCCESS:
                return code, message

            if (self._aggregation and i == 1) or not self._aggregation:
                list_geometries.append(impact_function.analysis_extent)

            analysis_layers.append(impact_function.analysis_impacted)
            aggregation_layers.append(impact_function.aggregation_summary)
            list_of_analysis_path.append(
                full_layer_uri(impact_function.analysis_impacted))

        set_provenance(
            self._provenance,
            provenance_multi_exposure_summary_layers,
            list_of_analysis_path)

        self._current_impact_function = None
        self._analysis_extent = QgsGeometry.unaryUnion(list_geometries)

        if not self._aggregation:
            self._aggregation_summary = create_virtual_aggregation(
                self._analysis_extent, self._crs)

        self._analysis_summary = create_analysis_layer(
            self._analysis_extent, self._crs, self._name)

        # Sum up layers
        self._aggregation_summary = multi_exposure_aggregation_summary(
            self._aggregation_summary, aggregation_layers)
        self._analysis_summary = multi_exposure_analysis_summary(
            self._analysis_summary, analysis_layers)

        # End of the impact function
        self._end_datetime = datetime.now()
        set_provenance(
            self._provenance, provenance_start_datetime, self.start_datetime)
        set_provenance(
            self._provenance, provenance_end_datetime, self.end_datetime)
        set_provenance(
            self._provenance, provenance_duration, self.duration)

        self._generate_provenance()

        output_layer_provenance = {}

        # Add all layers to the datastore
        # Aggregation summary
        self._aggregation_summary.keywords['provenance_data'] = self.provenance
        append_ISO19115_keywords(self._aggregation_summary.keywords)
        result, name = self._datastore.add_layer(
            self._aggregation_summary,
            layer_purpose_aggregation_summary['key'])
        if not result:
            raise Exception(
                tr('Something went wrong with the datastore : '
                   '{error_message}').format(error_message=name))
        self._aggregation_summary = self.datastore.layer(name)
        output_layer_provenance[provenance_layer_aggregation_summary[
            'provenance_key']] = self._aggregation_summary.source()
        output_layer_provenance[provenance_layer_aggregation_summary_id[
            'provenance_key']] = self._aggregation_summary.id()

        # Analysis summary
        self._analysis_summary.keywords['provenance_data'] = self.provenance
        append_ISO19115_keywords(self._analysis_summary.keywords)
        result, name = self._datastore.add_layer(
            self._analysis_summary, layer_purpose_analysis_impacted['key'])
        if not result:
            raise Exception(
                tr('Something went wrong with the datastore : '
                   '{error_message}').format(error_message=name))
        self._analysis_summary = self.datastore.layer(name)
        output_layer_provenance[provenance_layer_analysis_impacted[
            'provenance_key']] = self._analysis_summary.source()
        output_layer_provenance[provenance_layer_analysis_impacted_id[
            'provenance_key']] = self._analysis_summary.id()
        self._provenance.update(output_layer_provenance)

        # Update provenance data with output layers URI
        self._provenance.update(output_layer_provenance)
        self._aggregation_summary.keywords['provenance_data'] = self.provenance
        write_iso19115_metadata(
            self._aggregation_summary.source(),
            self._aggregation_summary.keywords)
        self._analysis_summary.keywords['provenance_data'] = self.provenance
        write_iso19115_metadata(
            self._analysis_summary.source(),
            self._analysis_summary.keywords)

        # Quick style
        simple_polygon_without_brush(
            self._aggregation_summary, aggregation_width, aggregation_color)
        simple_polygon_without_brush(
            self._analysis_summary, analysis_width, analysis_color)

        # Set back input layers.
        self.hazard = load_layer_from_registry(
            get_provenance(self.provenance, provenance_hazard_layer))
        exposures = get_provenance(
            self.provenance, provenance_multi_exposure_layers)
        self._exposures = []
        for exposure in exposures:
            self.add_exposure(load_layer_from_registry(exposure))
        aggregation_path = get_provenance(
            self.provenance, provenance_aggregation_layer)
        if aggregation_path:
            self.aggregation = load_layer_from_registry(aggregation_path)
        else:
            self.aggregation = None

        return ANALYSIS_SUCCESS, None

    def generate_report(self, components, output_folder=None, iface=None):
        """Generate Impact Report independently by the Impact Function.

        :param components: Report components to be generated.
        :type components: list

        :param output_folder: The output folder.
        :type output_folder: str

        :param iface: A QGIS App interface
        :type iface: QgsInterface

        :returns: Tuple of error code and message
        :type: tuple

        .. versionadded:: 4.3
        """
        # iface set up, in case IF run from test
        if not iface:
            iface = IFACE

        error_code = None
        message = None

        generated_components = deepcopy(components)
        # remove unnecessary components
        if standard_impact_report_metadata_pdf in generated_components:
            generated_components.remove(standard_impact_report_metadata_pdf)
        if infographic_report in generated_components:
            generated_components.remove(infographic_report)

        # Define the extra layers because multi-exposure IF has its own
        # layer order, whether it's coming from the user custom layer order
        # or not.
        extra_layers = []
        if self._output_layers_ordered:
            for layer_definition in self.output_layers_ordered:
                if layer_definition[0] == FROM_CANVAS['key']:
                    layer_path = layer_definition[2]
                    extra_layer = load_layer_from_registry(layer_path)
                else:
                    if layer_definition[2] == self.name:
                        for layer in self.outputs:
                            if layer.keywords['layer_purpose'] == (
                                    layer_definition[1]):
                                extra_layer = layer
                                break
                    else:
                        for sub_impact_function in self.impact_functions:
                            # Iterate over each sub impact function used in the
                            # multi exposure analysis.
                            if sub_impact_function.name == layer_definition[2]:
                                for layer in sub_impact_function.outputs:
                                    purpose = layer_definition[1]
                                    if layer.keywords['layer_purpose'] == (
                                            purpose):
                                        extra_layer = layer
                                        break
                extra_layers.append(extra_layer)

        if not extra_layers:
            # We need to find out about the layers order manually.
            layer_tree_root = QgsProject.instance().layerTreeRoot()
            all_groups = [
                child for child in layer_tree_root.children() if (
                    isinstance(child, QgsLayerTreeGroup))]
            multi_exposure_group = None
            for group in all_groups:
                if group.customProperty(MULTI_EXPOSURE_ANALYSIS_FLAG):
                    multi_exposure_group = group
                    break

            if multi_exposure_group:
                multi_exposure_tree_layers = [
                    child for child in multi_exposure_group.children() if (
                        isinstance(child, QgsLayerTreeLayer))]
                exposure_groups = [
                    child for child in multi_exposure_group.children() if (
                        isinstance(child, QgsLayerTreeGroup))]

                if exposure_groups:
                    extra_layers = []
                    for exposure_group in exposure_groups:
                        tree_layers = [
                            child for child in exposure_group.children() if (
                                isinstance(child, QgsLayerTreeLayer))]
                        for tree_layer in tree_layers:
                            layer_purpose = KeywordIO.read_keywords(
                                tree_layer.layer(), 'layer_purpose')
                            if layer_purpose == (
                                    layer_purpose_exposure_summary['key']):
                                extra_layers.append(tree_layer.layer())
                else:
                    extra_layers = [
                        tree_layer.layer() for tree_layer in (
                            multi_exposure_tree_layers)]

        for component in generated_components:

            report_metadata = ReportMetadata(
                metadata_dict=component)

            self._report_metadata.append(report_metadata)
            self._impact_report = ImpactReport(
                iface,
                report_metadata,
                multi_exposure_impact_function=self,
                analysis=self.analysis_impacted,
                extra_layers=extra_layers)

            # generate report folder

            # no other option for now
            # TODO: retrieve the information from data store
            if isinstance(self.datastore.uri, QDir):
                layer_dir = self.datastore.uri.absolutePath()
            else:
                # No other way for now
                return

            # We will generate it on the fly without storing it after datastore
            # supports
            if output_folder:
                self._impact_report.output_folder = output_folder
            else:
                self._impact_report.output_folder = join(layer_dir, 'output')

            error_code, message = self._impact_report.process_components()
            if error_code == ImpactReport.REPORT_GENERATION_FAILED:
                break

        return error_code, message

    @staticmethod
    def load_from_output_metadata(output_metadata):
        """Set Impact Function based on an output of an analysis's metadata.

        If possible, we will try to use layers already in the legend and to not
        recreating new ones. We will keep the style for instance.

        :param output_metadata: Metadata from an output layer.
        :type output_metadata: OutputLayerMetadata

        :returns: Impact Function based on the metadata.
        :rtype: ImpactFunction
        """
        impact_function = MultiExposureImpactFunction()
        provenance = output_metadata['provenance_data']
        # Set provenance data
        impact_function._provenance = provenance

        # Set exposure layer
        paths = get_provenance(provenance, provenance_multi_exposure_layers)
        if paths:
            for path in paths:
                impact_function.add_exposure(load_layer_from_registry(path))

        # Set hazard layer
        path = get_provenance(provenance, provenance_hazard_layer)
        if path:
            impact_function.hazard = load_layer_from_registry(path)

        # Set aggregation layer
        path = get_provenance(provenance, provenance_aggregation_layer)
        if path:
            impact_function.aggregation = load_layer_from_registry(path)

        # Analysis extent
        extent = get_provenance(provenance, provenance_analysis_extent)
        if extent:
            impact_function._analysis_extent = QgsGeometry.fromWkt(extent)

        # Data store
        data_store_uri = get_provenance(provenance, provenance_data_store_uri)
        if data_store_uri:
            impact_function.datastore = Folder(data_store_uri)

        # Name
        name = get_provenance(provenance, provenance_impact_function_name)
        impact_function._name = name

        # Start date time
        start_datetime = get_provenance(provenance, provenance_start_datetime)
        impact_function._start_datetime = start_datetime

        # End date time
        end_datetime = get_provenance(provenance, provenance_end_datetime)
        impact_function._end_datetime = end_datetime

        # Duration
        duration = get_provenance(provenance, provenance_duration)
        impact_function._duration = duration

        # Debug mode
        debug_mode = get_provenance(provenance, provenance_debug_mode)
        impact_function.debug_mode = debug_mode

        # Output layers
        # aggregation_summary
        path = get_provenance(provenance, provenance_layer_aggregation_summary)
        if path:
            impact_function._aggregation_summary = load_layer_from_registry(
                path)

        # analysis_impacted
        path = get_provenance(provenance, provenance_layer_analysis_impacted)
        if path:
            impact_function._analysis_summary = load_layer_from_registry(path)

        list_of_exposure_summary = get_provenance(
            provenance, provenance_multi_exposure_summary_layers)
        for exposure_summary in list_of_exposure_summary:
            layer = load_layer_from_registry(exposure_summary)
            keywords = KeywordIO.read_keywords(layer)
            serialized_impact_function = (
                ImpactFunction.load_from_output_metadata(keywords))
            impact_function._impact_functions.append(
                serialized_impact_function)

        impact_function._output_layer_expected = \
            impact_function._compute_output_layer_expected()

        # crs
        crs = get_provenance(provenance, provenance_crs)
        if crs:
            impact_function._crs = QgsCoordinateReferenceSystem(crs)

        impact_function._provenance_ready = True

        return impact_function
