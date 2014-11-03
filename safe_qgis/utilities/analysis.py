# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**ImpactCalculator.**

The module provides a high level interface for running full SAFE analysis.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'imajimatika@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '10/20/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# noinspection PyPackageRequirements
from PyQt4 import QtCore
# noinspection PyPackageRequirements
import numpy
import logging
from safe_qgis.utilities.impact_calculator import ImpactCalculator
from safe_qgis.utilities.utilities import (
    get_wgs84_resolution,
    extent_to_geo_array,
    viewport_geo_array,
    get_error_message
)
from safe_qgis.impact_statistics.postprocessor_manager import (
    PostprocessorManager)
from safe_qgis.impact_statistics.aggregator import Aggregator
from safe_qgis.utilities.memory_checker import check_memory_usage
from safe_qgis.safe_interface import (
    get_optimal_extent,
    get_buffered_extent,
    ReadLayerError,
    get_postprocessors,
    get_postprocessor_human_name,
    ZeroImpactException)
from qgis.core import (
    QgsMapLayer,
    QgsCoordinateReferenceSystem,
    QGis)
from safe_qgis.exceptions import (
    KeywordDbError,
    InsufficientOverlapError,
    InvalidLayerError,
    InsufficientParametersError,
    CallGDALError,
    NoFeaturesInExtentError,
    InvalidProjectionError,
    InvalidGeometryError,
    AggregationError,
    UnsupportedProviderError,
    InvalidAggregationKeywords,
    InsufficientMemoryWarning)
from safe_qgis.safe_interface import messaging as m
from safe_qgis.utilities.clipper import clip_layer, adjust_clip_extent

from safe_qgis.safe_interface import styles
from safe_qgis.safe_interface import (
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    ERROR_MESSAGE_SIGNAL,
    BUSY_SIGNAL,
    NOT_BUSY_SIGNAL,
    ANALYSIS_DONE_SIGNAL)
from third_party.pydispatch import dispatcher
from safe_qgis.exceptions import NoValidLayerError


PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
INFO_STYLE = styles.INFO_STYLE
WARNING_STYLE = styles.WARNING_STYLE
KEYWORD_STYLE = styles.KEYWORD_STYLE
SUGGESTION_STYLE = styles.SUGGESTION_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE
LOGO_ELEMENT = m.Image('qrc:/plugins/inasafe/inasafe-logo.png', 'InaSAFE Logo')
LOGGER = logging.getLogger('InaSAFE')


class Analysis(object):
    """Class for running full analysis."""
    def __init__(self):
        """Constructor."""
        # Please set Layers, Impact Functions, and Variables to run Analysis
        # Layers
        self._hazard_layer = None
        self._exposure_layer = None
        self._aggregation_layer = None
        self.hazard_keyword = None
        self.exposure_keyword = None
        self.aggregation_keyword = None

        # Impact Functions
        self.impact_function_id = None
        self.impact_function_parameters = None

        # Variables
        self.clip_hard = None
        self.show_intermediate_layers = None
        self.run_in_thread_flag = None
        self.map_canvas = None
        self.clip_to_viewport = None

        self.force_memory = False

        self.clip_parameters = None
        self.impact_calculator = ImpactCalculator()
        self.runner = None
        self.aggregator = None
        self.postprocessor_manager = None

        self.num_dynamic_signals = 3

    @property
    def hazard_layer(self):
        """Property for hazard layer.

        :returns: Hazard Layer of the analysis.
        :rtype: QgsMapLayer

        """
        return self._hazard_layer

    @hazard_layer.setter
    def hazard_layer(self, hazard_layer):
        """Setter for the hazard layer for the analysis.

        :param hazard_layer: The hazard layer.
        :type hazard_layer: QgsMapLayer

        """
        self._hazard_layer = hazard_layer

    @property
    def exposure_layer(self):
        """Property for exposure layer.

        :returns: Exposure Layer of the analysis.
        :rtype: QgsMapLayer

        """
        return self._exposure_layer

    @exposure_layer.setter
    def exposure_layer(self, exposure_layer):
        """Setter for the exposure layer for the analysis.

        :param exposure_layer: The exposure layer.
        :type exposure_layer: QgsMapLayer

        """
        self._exposure_layer = exposure_layer

    @property
    def aggregation_layer(self):
        """Property for aggregation layer.

        :returns: Aggregation Layer of the analysis.
        :rtype: QgsMapLayer

        """
        return self._aggregation_layer

    @aggregation_layer.setter
    def aggregation_layer(self, aggregation_layer):
        """Setter for the aggregation layer for the analysis.

        :param aggregation_layer: The aggregation layer.
        :type aggregation_layer: QgsMapLayer

        """
        self._aggregation_layer = aggregation_layer

    # noinspection PyMethodMayBeStatic
    def tr(self, string):
        """We implement this since we do not inherit QObject.

        :param string: String for translation.
        :type string: str

        :returns: Translated version of string.
        :rtype: str

        """
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        return QtCore.QCoreApplication.translate('Analysis', string)

    @staticmethod
    def get_layer_title(layer, layer_keyword):
        """Return layer's title from keywords or layer name if not found.

        :param layer: A valid QgsMapLayer
        :type layer: QgsMapLayer

        :param layer_keyword: A keyword for the layer
        :type layer_keyword: dict

        :returns: Layer's title
        :rtype: str
        """
        title = layer_keyword.get('title', str(layer.name()))
        return title

    def get_impact_layer(self):
        """Obtain impact layer from the runner."""
        return self.runner.impact_layer()

    def send_static_message(self, message):
        """Send a static message to the listeners.

        Static messages represents a whole new message. Usually it will
        replace the previous message.

        :param message: An instance of our rich message class.
        :type message: Message

        """
        dispatcher.send(
            signal=STATIC_MESSAGE_SIGNAL,
            sender=self,
            message=message)

    def send_dynamic_message(self, message):
        """Send a dynamic message to the listeners.

        Dynamic messages represents a progres. Usually it will be appended to
        the previous messages.

        :param message: An instance of our rich message class.
        :type message: Message

        """
        dispatcher.send(
            signal=DYNAMIC_MESSAGE_SIGNAL,
            sender=self,
            message=message)

    def send_error_message(self, error_message):
        """Send an error message to the listeners.

        Error messages represents and error. It usually replace the previous
        message since an error has been happened.

        :param error_message: An instance of our rich error message class.
        :type error_message: ErrorMessage
        """
        dispatcher.send(
            signal=ERROR_MESSAGE_SIGNAL,
            sender=self,
            message=error_message)

    def send_busy_signal(self):
        """Send an busy signal to the listeners."""
        dispatcher.send(
            signal=BUSY_SIGNAL,
            sender=self,
            message='')

    def send_not_busy_signal(self):
        """Send an busy signal to the listeners."""
        dispatcher.send(
            signal=NOT_BUSY_SIGNAL,
            sender=self,
            message='')

    def send_analysis_done_signal(self):
        """Send an analysis done signal to the listeners."""
        dispatcher.send(
            signal=ANALYSIS_DONE_SIGNAL,
            sender=self,
            message='')

    def generate_insufficient_overlap_message(
            self,
            e,
            exposure_geoextent,
            exposure_layer,
            hazard_geoextent,
            hazard_layer,
            viewport_geoextent):
        """

        :param e: An exception.
        :param exposure_geoextent: Extent of the exposure layer.
        :param exposure_layer: Exposure layer.
        :param hazard_geoextent: Extent of the hazard layer.
        :param hazard_layer:  Hazard layer instance.
        :param viewport_geoextent: Viewport extents.

        :return: An InaSAFE message object.
        """
        description = self.tr(
            'There was insufficient overlap between the input layers '
            'and / or the layers and the viewable area. Please select two '
            'overlapping layers and zoom or pan to them or disable '
            'viewable area clipping in the options dialog. Full details '
            'follow:')
        message = m.Message(description)
        text = m.Paragraph(
            self.tr('Failed to obtain the optimal extent given:'))
        message.add(text)
        analysis_inputs = m.BulletedList()
        # We must use Qt string interpolators for tr to work properly
        analysis_inputs.add(
            self.tr('Hazard: %s') % (
                hazard_layer.source()))
        analysis_inputs.add(
            self.tr('Exposure: %s') % (
                exposure_layer.source()))
        analysis_inputs.add(
            self.tr('Viewable area Geo Extent: %s') % (
                str(viewport_geoextent)))
        analysis_inputs.add(
            self.tr('Hazard Geo Extent: %s') % (
                str(hazard_geoextent)))
        analysis_inputs.add(
            self.tr('Exposure Geo Extent: %s') % (
                str(exposure_geoextent)))
        analysis_inputs.add(
            self.tr('Viewable area clipping enabled: %s') % (
                str(self.clip_to_viewport)))
        analysis_inputs.add(
            self.tr('Details: %s') % (
                str(e)))
        message.add(analysis_inputs)
        return message

    def get_clip_parameters(self):
        """Calculate the best extents to use for the assessment.

        :returns: A tuple consisting of:

            * extra_exposure_keywords: dict - any additional keywords that
                should be written to the exposure layer. For example if
                rescaling is required for a raster, the original resolution
                can be added to the keywords file.
            * adjusted_geo_extent: list - [xmin, ymin, xmax, ymax] - the best
                extent that can be used given the input datasets and the
                current viewport extents.
            * cell_size: float - the cell size that is the best of the
                hazard and exposure rasters.
            * exposure_layer: QgsMapLayer - layer representing exposure.
            * geo_extent: list - [xmin, ymin, xmax, ymax] - the unbuffered
                intersection of the two input layers extents and the viewport.
            * hazard_layer: QgsMapLayer - layer representing hazard.
        :rtype: dict, QgsRectangle, float,
                QgsMapLayer, QgsRectangle, QgsMapLayer
        :raises: InsufficientOverlapError
        """
        hazard_layer = self.hazard_layer
        exposure_layer = self.exposure_layer
        # Get the current viewport extent as an array in EPSG:4326
        viewport_geoextent = viewport_geo_array(self.map_canvas)
        # Get the Hazard extents as an array in EPSG:4326
        hazard_geoextent = extent_to_geo_array(
            hazard_layer.extent(),
            hazard_layer.crs())
        # Get the Exposure extents as an array in EPSG:4326
        exposure_geoextent = extent_to_geo_array(
            exposure_layer.extent(),
            exposure_layer.crs())

        # Reproject all extents to EPSG:4326 if needed
        geo_crs = QgsCoordinateReferenceSystem()
        geo_crs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
        # Now work out the optimal extent between the two layers and
        # the current view extent. The optimal extent is the intersection
        # between the two layers and the viewport.
        try:
            # Extent is returned as an array [xmin,ymin,xmax,ymax]
            # We will convert it to a QgsRectangle afterwards.
            if self.clip_to_viewport:
                geo_extent = get_optimal_extent(
                    hazard_geoextent,
                    exposure_geoextent,
                    viewport_geoextent)
            else:
                geo_extent = get_optimal_extent(
                    hazard_geoextent,
                    exposure_geoextent)

        except InsufficientOverlapError, e:
            message = self.generate_insufficient_overlap_message(
                e,
                exposure_geoextent,
                exposure_layer,
                hazard_geoextent,
                hazard_layer,
                viewport_geoextent)
            raise InsufficientOverlapError(message)

        # Next work out the ideal spatial resolution for rasters
        # in the analysis. If layers are not native WGS84, we estimate
        # this based on the geographic extents
        # rather than the layers native extents so that we can pass
        # the ideal WGS84 cell size and extents to the layer prep routines
        # and do all preprocessing in a single operation.
        # All this is done in the function getWGS84resolution
        adjusted_geo_extent = geo_extent  # Bbox to use for hazard layer
        cell_size = None
        extra_exposure_keywords = {}
        if hazard_layer.type() == QgsMapLayer.RasterLayer:
            # Hazard layer is raster
            hazard_geo_cell_size, _ = get_wgs84_resolution(hazard_layer)

            if exposure_layer.type() == QgsMapLayer.RasterLayer:
                # In case of two raster layers establish common resolution
                exposure_geo_cell_size, _ = get_wgs84_resolution(
                    exposure_layer)

                # See issue #1008 - the flag below is used to indicate
                # if the user wishes to prevent resampling of exposure data
                keywords = self.exposure_keyword
                allow_resampling_flag = True
                if 'allow_resampling' in keywords:
                    resampling_lower = keywords['allow_resampling'].lower()
                    allow_resampling_flag = resampling_lower == 'true'

                if hazard_geo_cell_size < exposure_geo_cell_size and \
                        allow_resampling_flag:
                    cell_size = hazard_geo_cell_size

                    # Adjust the geo extent to coincide with hazard grids
                    # so gdalwarp can do clipping properly
                    geo_extent = adjust_clip_extent(
                        geo_extent,
                        get_wgs84_resolution(hazard_layer),
                        hazard_geoextent)
                else:
                    cell_size = exposure_geo_cell_size

                    # Adjust extent to coincide with exposure grids
                    # so gdalwarp can do clipping properly
                    geo_extent = adjust_clip_extent(
                        geo_extent,
                        get_wgs84_resolution(exposure_layer),
                        exposure_geoextent)

                adjusted_geo_extent = geo_extent

                # Record native resolution to allow rescaling of exposure data
                if not numpy.allclose(cell_size, exposure_geo_cell_size):
                    extra_exposure_keywords['resolution'] = \
                        exposure_geo_cell_size
            else:
                if exposure_layer.type() != QgsMapLayer.VectorLayer:
                    raise RuntimeError

                # In here we do not set cell_size so that in
                # _clip_raster_layer we can perform gdalwarp without
                # specifying cell size as we still want to have the original
                # pixel size.

                # Adjust the geo extent to be at the edge of the pixel in
                # so gdalwarp can do clipping properly
                geo_extent = adjust_clip_extent(
                    geo_extent,
                    get_wgs84_resolution(hazard_layer),
                    hazard_geoextent)

                # If exposure is vector data grow hazard raster layer to
                # ensure there are enough pixels for points at the edge of
                # the view port to be interpolated correctly. This requires
                # resolution to be available
                adjusted_geo_extent = get_buffered_extent(
                    geo_extent,
                    get_wgs84_resolution(hazard_layer))
        else:
            # Hazard layer is vector

            # In case hazard data is a point data set, we will not clip the
            # exposure data to it. The reason being that points may be used
            # as centers for evacuation circles: See issue #285
            if hazard_layer.geometryType() == QGis.Point:
                geo_extent = exposure_geoextent
                adjusted_geo_extent = geo_extent

        return (
            extra_exposure_keywords,
            adjusted_geo_extent,
            cell_size,
            exposure_layer,
            geo_extent,
            hazard_layer)

    def setup_aggregator(self):
        """Create an aggregator for this analysis run."""
        # Refactor from dock.prepare_aggregator
        if self.clip_parameters is None:
            raise Exception(self.tr('Clip parameters are not set!'))
        buffered_geo_extent = self.clip_parameters[1]

        #setup aggregator to use buffered_geo_extent to deal with #759
        self.aggregator = Aggregator(
            buffered_geo_extent, self.aggregation_layer)

        self.aggregator.show_intermediate_layers = \
            self.show_intermediate_layers

    def setup_analysis(self):
        """Setup analysis so that it will be ready for running."""
        # Refactor from dock.accept()
        title = self.tr('Processing started')
        details = self.tr(
            'Please wait - processing may take a while depending on your '
            'hardware configuration and the analysis extents and data.')

        # trap for issue 706
        try:
            exposure_name = self.get_layer_title(
                self.exposure_layer, self.exposure_keyword)
            hazard_name = self.get_layer_title(
                self.hazard_layer, self.hazard_keyword)
            #aggregation layer could be set to AOI so no check for that
        except AttributeError:
            title = self.tr('No valid layers')
            details = self.tr(
                'Please ensure your hazard and exposure layers are set '
                'in the question area and then press run again.')
            message = m.Message(
                LOGO_ELEMENT,
                m.Heading(title, **WARNING_STYLE),
                m.Paragraph(details))
            raise NoValidLayerError(message)

        text = m.Text(
            self.tr('This analysis will calculate the impact of'),
            m.EmphasizedText(hazard_name),
            self.tr('on'),
            m.EmphasizedText(exposure_name),
        )

        if self.aggregation_layer is not None:
            try:
                aggregation_name = self.get_layer_title(
                    self.aggregation_layer, self.aggregation_keyword)
                # noinspection PyTypeChecker
                text.add(m.Text(
                    self.tr('and bullet_list the results'),
                    m.ImportantText(self.tr('aggregated by')),
                    m.EmphasizedText(aggregation_name))
                )
            except AttributeError:
                pass

        text.add('.')

        message = m.Message(
            LOGO_ELEMENT,
            m.Heading(title, **PROGRESS_UPDATE_STYLE),
            m.Paragraph(details),
            m.Paragraph(text))

        try:
            # add which postprocessors will run when appropriated
            post_processors_names = self.impact_function_parameters[
                'postprocessors']
            # aggregator is not ready yet here so we can't use
            # self.aggregator.aoi_mode
            aoi_mode = self.aggregation_layer is None
            post_processors = get_postprocessors(
                post_processors_names, aoi_mode)
            message.add(m.Paragraph(self.tr(
                'The following postprocessors will be used:')))

            bullet_list = m.BulletedList()

            for name, post_processor in post_processors.iteritems():
                bullet_list.add('%s: %s' % (
                    get_postprocessor_human_name(name),
                    post_processor.description()))
            message.add(bullet_list)

        except (TypeError, KeyError):
            # TypeError is for when function_parameters is none
            # KeyError is for when ['postprocessors'] is unavailable
            pass

        self.send_static_message(message)

        # Find out what the usable extent and cell size are
        try:
            self.clip_parameters = self.get_clip_parameters()
            buffered_geoextent = self.clip_parameters[1]
            cell_size = self.clip_parameters[2]
        except (RuntimeError, InsufficientOverlapError, AttributeError) as e:
            LOGGER.exception('Error calculating extents. %s' % str(e.message))
            context = self.tr(
                'A problem was encountered when trying to determine the '
                'analysis extents.'
            )
            self.analysis_error(e, context)
            raise e

        if not self.force_memory:
            # Ensure there is enough memory
            result = check_memory_usage(buffered_geoextent, cell_size)
            if not result:
                raise InsufficientMemoryWarning

        self.setup_aggregator()

        # go check if our postprocessing layer has any keywords set and if not
        # prompt for them. if a prompt is shown run method is called by the
        # accepted signal of the keywords dialog
        self.aggregator.validate_keywords()
        if self.aggregator.is_valid:
            pass
        else:
            raise InvalidAggregationKeywords

    def analysis_error(self, exception, message):
        """A helper to spawn an error and halt processing.

        An exception will be logged, busy status removed and a message
        displayed.

        :param message: an ErrorMessage to display
        :type message: ErrorMessage, Message

        :param exception: An exception that was raised
        :type exception: Exception
        """
        self.send_not_busy_signal()
        LOGGER.exception(message)
        message = get_error_message(exception, context=message)
        self.send_error_message(message)

    def optimal_clip(self):
        """ A helper function to perform an optimal clip of the input data.
        Optimal extent should be considered as the intersection between
        the three inputs. The InaSAFE library will perform various checks
        to ensure that the extent is tenable, includes data from both
        etc.

        The result of this function will be two layers which are
        clipped and re-sampled if needed, and in the EPSG:4326 geographic
        coordinate reference system.

        :returns: The clipped hazard and exposure layers.
        :rtype: (QgsMapLayer, QgsMapLayer)
        """

        # Get the hazard and exposure layers selected in the combos
        # and other related parameters needed for clipping.
        try:
            extra_exposure_keywords = self.clip_parameters[0]
            buffered_geo_extent = self.clip_parameters[1]
            cell_size = self.clip_parameters[2]
            exposure_layer = self.clip_parameters[3]
            geo_extent = self.clip_parameters[4]
            hazard_layer = self.clip_parameters[5]
        except:
            raise
        # Make sure that we have EPSG:4326 versions of the input layers
        # that are clipped and (in the case of two raster inputs) resampled to
        # the best resolution.
        title = self.tr('Preparing hazard data')
        detail = self.tr(
            'We are resampling and clipping the hazard layer to match the '
            'intersection of the exposure layer and the current view extents.')
        message = m.Message(
            m.Heading(title, **PROGRESS_UPDATE_STYLE),
            m.Paragraph(detail))
        self.send_dynamic_message(message)
        try:
            clipped_hazard = clip_layer(
                layer=hazard_layer,
                extent=buffered_geo_extent,
                cell_size=cell_size,
                hard_clip_flag=self.clip_hard)
        except CallGDALError, e:
            raise e
        except IOError, e:
            raise e

        title = self.tr('Preparing exposure data')
        detail = self.tr(
            'We are resampling and clipping the exposure layer to match the '
            'intersection of the hazard layer and the current view extents.')
        message = m.Message(
            m.Heading(title, **PROGRESS_UPDATE_STYLE),
            m.Paragraph(detail))
        self.send_dynamic_message(message)

        clipped_exposure = clip_layer(
            layer=exposure_layer,
            extent=geo_extent,
            cell_size=cell_size,
            extra_keywords=extra_exposure_keywords,
            hard_clip_flag=self.clip_hard)
        return clipped_hazard, clipped_exposure

    def setup_impact_calculator(self):
        """Initialise ImpactCalculator based on the current state of the ui."""

        # Use canonical function name to identify selected function
        self.impact_calculator.set_function(self.impact_function_id)

        # Get the hazard and exposure layers selected in the combos
        # and other related parameters needed for clipping.
        # pylint: disable=W0633,W0612
        (extra_exposure_keywords,
         buffered_geo_extent,
         cell_size,
         exposure_layer,
         geo_extent,
         hazard_layer) = self.clip_parameters

        if self.impact_calculator.requires_clipping():
            # The impact function uses SAFE layers,
            # clip them
            hazard_layer, exposure_layer = self.optimal_clip()
            self.aggregator.set_layers(hazard_layer, exposure_layer)
            # Extent is calculated in the aggregator:
            self.impact_calculator.set_extent(None)

            # See if the inputs need further refinement for aggregations
            try:
                # This line is a fix for #997
                self.aggregator.validate_keywords()
                self.aggregator.deintersect()
            except (InvalidLayerError,
                    UnsupportedProviderError,
                    KeywordDbError):
                raise
            # Get clipped layers
            hazard_layer = self.aggregator.hazard_layer
            exposure_layer = self.aggregator.exposure_layer
        else:
            # It is a 'new-style' impact function,
            # clipping doesn't needed, but we need to set up extent
            self.aggregator.set_layers(hazard_layer, exposure_layer)
            self.impact_calculator.set_extent(buffered_geo_extent)

        # Identify input layers
        self.impact_calculator.set_hazard_layer(hazard_layer)
        self.impact_calculator.set_exposure_layer(exposure_layer)

    def run_aggregator(self):
        """Run all post processing steps.

        Called on self.runner SIGNAL('done()') starts aggregation steps.
        """
        LOGGER.debug('Do aggregation')
        if self.runner.impact_layer() is None:
            # Done was emitted, but no impact layer was calculated
            result = self.runner.result()
            message = str(self.tr(
                'No impact layer was calculated. Error message: %s\n'
            ) % (str(result)))
            exception = self.runner.last_exception()
            if isinstance(exception, ZeroImpactException):
                report = m.Message()
                report.add(LOGO_ELEMENT)
                report.add(m.Heading(self.tr(
                    'Analysis Results'), **INFO_STYLE))
                report.add(m.Text(exception.message))
                report.add(m.Heading(self.tr('Notes'), **SUGGESTION_STYLE))
                exposure_layer_title = self.get_layer_title(
                    self.exposure_layer, self.exposure_keyword)
                hazard_layer_title = self.get_layer_title(
                    self.hazard_layer, self.hazard_keyword)
                report.add(m.Text(self.tr(
                    'It appears that no %s are affected by %s. You may want '
                    'to consider:') % (
                        exposure_layer_title, hazard_layer_title)))
                check_list = m.BulletedList()
                check_list.add(self.tr(
                    'Check that you are not zoomed in too much and thus '
                    'excluding %s from your analysis area.') % (
                        exposure_layer_title))
                check_list.add(self.tr(
                    'Check that the exposure is not no-data or zero for the '
                    'entire area of your analysis.'))
                check_list.add(self.tr(
                    'Check that your impact function thresholds do not '
                    'exclude all features unintentionally.'))
                report.add(check_list)
                self.send_static_message(report)
                self.send_not_busy_signal()
                return
            if exception is not None:
                content = self.tr(
                    'An exception occurred when calculating the results. %s'
                ) % (self.runner.result())
                message = get_error_message(exception, context=content)
            # noinspection PyTypeChecker
            self.send_error_message(message)
            # self.analysis_done.emit(False)
            return

        try:
            self.aggregator.aggregate(self.runner.impact_layer())
        except InvalidGeometryError, e:
            message = get_error_message(e)
            self.send_error_message(message)
            # self.analysis_done.emit(False)
            return
        except Exception, e:  # pylint: disable=W0703
            # noinspection PyPropertyAccess
            e.args = (str(e.args[0]) + '\nAggregation error occurred',)
            raise

        #TODO (MB) do we really want this check?
        if self.aggregator.error_message is None:
            self.run_post_processor()
        else:
            content = self.aggregator.error_message
            exception = AggregationError(self.tr(
                'Aggregation error occurred.'))
            self.analysis_error(exception, content)

    def run_post_processor(self):
        """Carry out any postprocessing required for this impact layer.
        """
        LOGGER.debug('Do postprocessing')
        self.postprocessor_manager = PostprocessorManager(self.aggregator)
        self.postprocessor_manager.function_parameters = \
            self.impact_function_parameters
        self.postprocessor_manager.run()
        self.send_not_busy_signal()
        self.send_analysis_done_signal()

    def run_analysis(self):
        """It's similar with run function in previous dock.py"""
        try:
            self.setup_impact_calculator()
        except CallGDALError, e:
            self.analysis_error(e, self.tr(
                'An error occurred when calling a GDAL command'))
            return
        except IOError, e:
            self.analysis_error(e, self.tr(
                'An error occurred when writing clip file'))
            return
        except InsufficientOverlapError, e:
            self.analysis_error(e, self.tr(
                'An exception occurred when setting up the impact calculator.')
            )
            return
        except NoFeaturesInExtentError, e:
            self.analysis_error(e, self.tr(
                'An error occurred because there are no features visible in '
                'the current view. Try zooming out or panning until some '
                'features become visible.'))
            return
        except InvalidProjectionError, e:
            self.analysis_error(e, self.tr(
                'An error occurred because you are using a layer containing '
                'count data (e.g. population count) which will not '
                'scale accurately if we re-project it from its native '
                'coordinate reference system to WGS84/GeoGraphic.'))
            return
        except MemoryError, e:
            self.analysis_error(
                e,
                self.tr(
                    'An error occurred because it appears that your '
                    'system does not have sufficient memory. Upgrading '
                    'your computer so that it has more memory may help. '
                    'Alternatively, consider using a smaller geographical '
                    'area for your analysis, or using rasters with a larger '
                    'cell size.'))
            return

        try:
            self.runner = self.impact_calculator.get_runner()
        except (InsufficientParametersError, ReadLayerError), e:
            self.analysis_error(
                e,
                self.tr(
                    'An exception occurred when setting up the model runner.'))
            return

        self.runner.done.connect(self.run_aggregator)

        self.send_busy_signal()

        title = self.tr('Calculating impact')
        detail = self.tr(
            'This may take a little while - we are computing the areas that '
            'will be impacted by the hazard and writing the result to a new '
            'layer.')
        message = m.Message(
            m.Heading(title, **PROGRESS_UPDATE_STYLE),
            m.Paragraph(detail))
        self.send_dynamic_message(message)

        try:
            if self.run_in_thread_flag:
                self.runner.start()  # Run in different thread
            else:
                self.runner.run()  # Run in same thread
            # .. todo :: Disconnect done slot/signal

        except Exception, e:  # pylint: disable=W0703

            # FIXME (Ole): This branch is not covered by the tests
            self.analysis_error(
                e,
                self.tr('An exception occurred when starting the model.'))

    def print_analysis(self):
        """Print the variables in the analysis."""
        print 'The properties of the analysis: '
        # Layers
        print self.hazard_layer
        print self.exposure_layer
        print self.aggregation_layer
        print self.hazard_keyword
        print self.exposure_keyword
        print self.aggregation_keyword

        # Impact Functions
        print self.impact_function_id
        print self.impact_function_parameters

        # Variables
        print self.clip_hard
        print self.show_intermediate_layers
        print self.run_in_thread_flag
        print self.map_canvas
        print self.clip_to_viewport

        print self.force_memory

        print self.clip_parameters
        print self.impact_calculator
        print self.runner
        print self.aggregator
        print self.postprocessor_manager
