# coding=utf-8

"""
Multi-exposure wrapper.

This class will manage how to launch and optimize a multi exposure analysis.
"""

import getpass
import logging
from datetime import datetime
from os import makedirs
from os.path import join, exists
from socket import gethostname

from osgeo import gdal
from qgis.utils import iface
from PyQt4.Qt import PYQT_VERSION_STR
from PyQt4.QtCore import QDir, QT_VERSION_STR

from safe import messaging as m
from safe.common.utilities import temp_dir
from safe.common.version import get_version
from safe.datastore.datastore import DataStore
from safe.datastore.folder import Folder
from safe.definitions.constants import (
    PREPARE_SUCCESS,
    PREPARE_FAILED_BAD_INPUT,
    ANALYSIS_FAILED_BAD_INPUT,
    ANALYSIS_SUCCESS,
)
from safe.definitions.layer_purposes import (
    layer_purpose_analysis_impacted,
    layer_purpose_aggregation_summary,
)
from safe.definitions.provenance import (
    provenance_aggregation_keywords,
    provenance_aggregation_layer,
    provenance_aggregation_layer_id,
    provenance_analysis_extent,
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
    provenance_debug_mode)
from safe.definitions.styles import (
    aggregation_color,
    aggregation_width,
    analysis_color,
    analysis_width,
)
from safe.definitions.utilities import (
    get_name,
    set_provenance,
    update_template_component,
)
from safe.gis.tools import geometry_type
from safe.gis.vector.prepare_vector_layer import prepare_vector_layer
from safe.gis.vector.summary_5_multi_exposure import (
    multi_exposure_analysis_summary,
    multi_exposure_aggregation_summary,
)
from safe.gui.widgets.message import generate_input_error_message
from safe.impact_function.create_extra_layers import create_analysis_layer
from safe.impact_function.impact_function import ImpactFunction
from safe.impact_function.impact_function_utilities import check_input_layer
from safe.impact_function.style import simple_polygon_without_brush
from safe.report.impact_report import ImpactReport
from safe.report.report_metadata import ReportMetadata
from safe.utilities.gis import deep_duplicate_layer
from safe.utilities.i18n import tr
from safe.utilities.gis import qgis_version
from safe.utilities.metadata import (
    copy_layer_keywords,
    write_iso19115_metadata,
    append_ISO19115_keywords,
)
from safe.utilities.settings import setting
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
        self.analysis_extent = None
        self._output_layer_expected = None
        self._provenance_ready = False
        self._provenance = {}

        # Impact Report
        self._impact_report = None

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
    def analysis_summary(self):
        """Property for the aggregation summary.

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
            self.analysis_extent.exportToWkt())

        set_provenance(
            self._provenance,
            provenance_data_store_uri,
            self.datastore.uri_path)

        # CRS
        # if self._crs:
        #     set_provenance(
        #         self._provenance, provenance_crs, self._crs.authid())
        # else:
        #     set_provenance(
        #         self._provenance, provenance_crs, self._crs)

        # Debug mode
        set_provenance(
            self._provenance, provenance_debug_mode, self.debug_mode)

        self._provenance_ready = True

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

        self._impact_functions = []

        # We delegate the prepare to the main IF for each exposure
        for exposure in self._exposures:
            impact_function = ImpactFunction()
            impact_function.debug_mode = self.debug_mode
            impact_function.hazard = deep_duplicate_layer(self._hazard)
            impact_function.exposure = exposure
            impact_function.debug_mode = self.debug
            if self.callback:
                impact_function.callback = self.callback
            if self._aggregation:
                impact_function.aggregation = deep_duplicate_layer(
                    self._aggregation)
                impact_function.use_selected_features_only = (
                    self.use_selected_features_only)
            else:
                # TODO
                pass

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
            message = tr('You need to run `prepare` first.')
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

        self._aggregation_summary = prepare_vector_layer(self.aggregation)

        analysis_layers = []
        aggregation_layers = []

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

            if i == 1:
                self.analysis_extent = impact_function.analysis_extent
                self._analysis_summary = create_analysis_layer(
                    self.analysis_extent,
                    impact_function.exposure.crs(),
                    self._name)

            analysis_layers.append(impact_function.analysis_impacted)
            aggregation_layers.append(impact_function.aggregation_summary)

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

        for component in components:

            report_metadata = ReportMetadata(
                metadata_dict=update_template_component(component))

            self._impact_report = ImpactReport(
                iface,
                report_metadata,
                multi_exposure_impact_function=self,
                analysis=self.analysis_summary)

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
