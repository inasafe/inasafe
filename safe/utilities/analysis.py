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
# noinspection PyPackageRequirements
import logging

# noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings

from qgis.core import QgsMapLayer

from safe.impact_statistics.postprocessor_manager import (
    PostprocessorManager)
from safe.impact_statistics.aggregator import Aggregator
from safe.common.exceptions import ZeroImpactException
from safe.storage.utilities import safe_to_qgis_layer
from safe.storage.safe_layer import SafeLayer
from safe.common.exceptions import (
    KeywordDbError,
    InsufficientOverlapError,
    InvalidLayerError,
    CallGDALError,
    NoFeaturesInExtentError,
    InvalidProjectionError,
    InvalidGeometryError,
    AggregationError,
    UnsupportedProviderError,
    InvalidAggregationKeywords,
    InsufficientMemoryWarning)
from safe import messaging as m
from safe.utilities.memory_checker import check_memory_usage
from safe.utilities.gis import extent_to_array
from safe.utilities.i18n import tr
from safe.utilities.utilities import get_error_message
from safe.utilities.clipper import clip_layer
from safe.messaging import styles
from safe.common.signals import (
    analysis_error,
    send_static_message,
    send_busy_signal,
    send_not_busy_signal,
    send_error_message,
    send_dynamic_message,
    send_analysis_done_signal)
from safe.engine.core import calculate_impact


__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '10/20/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
INFO_STYLE = styles.INFO_STYLE
WARNING_STYLE = styles.WARNING_STYLE
KEYWORD_STYLE = styles.KEYWORD_STYLE
SUGGESTION_STYLE = styles.SUGGESTION_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE
LOGO_ELEMENT = m.Brand()

LOGGER = logging.getLogger('InaSAFE')


class Analysis(object):
    """Class for running full analysis."""

    def __init__(self):
        """Constructor."""

        # Impact Function
        self.impact_function = None

        # Variables
        self.clip_hard = None
        self.show_intermediate_layers = None
        self.run_in_thread_flag = None

        self.force_memory = False

        self.aggregator = None
        self.postprocessor_manager = None

        self.num_dynamic_signals = 3

    @property
    def map_canvas(self):
        """Property for map canvas.

        :returns: Map canvas of the analysis.
        :rtype: QgsMapCanvas
        """
        return self.impact_function.map_canvas

    @map_canvas.setter
    def map_canvas(self, map_canvas):
        """Setter for the map canvas for the analysis.

        :param map_canvas: The map canvas.
        :type map_canvas: QgsMapCanvas

        """
        # We transfer the map canvas to the IF.
        self.impact_function.map_canvas = map_canvas

    @property
    def user_extent(self):
        return self.impact_function.requested_extent

    @user_extent.setter
    def user_extent(self, user_extent):
        # We transfer the extent to the IF as a list.
        extent = [
            user_extent.xMinimum(),
            user_extent.yMinimum(),
            user_extent.xMaximum(),
            user_extent.yMaximum()]
        self.impact_function.requested_extent = extent

    @property
    def user_extent_crs(self):
        return self.impact_function.requested_extent_crs

    @user_extent_crs.setter
    def user_extent_crs(self, user_extent_crs):
        # We transfer the CRS to the IF.
        self.impact_function.requested_extent_crs = user_extent_crs

    @property
    def hazard(self):
        """Property for hazard layer.

        :returns: Hazard Layer of the analysis.
        :rtype: SafeLayer

        """
        return self.impact_function.hazard

    @hazard.setter
    def hazard(self, hazard_layer):
        """Setter for the hazard layer for the analysis.

        :param hazard_layer: The hazard layer.
        :type hazard_layer: QgsMapLayer,SafeLayer

        """
        if self.impact_function is None:
            raise Exception('Impact Function not found.')

        # We transfer the layer to the IF.
        self.impact_function.hazard = hazard_layer

    @property
    def exposure(self):
        """Property for exposure layer.

        :returns: Exposure Layer of the analysis.
        :rtype: SafeLayer

        """
        return self.impact_function.exposure

    @exposure.setter
    def exposure(self, exposure_layer):
        """Setter for the exposure layer for the analysis.

        :param exposure_layer: The exposure layer.
        :type exposure_layer: QgsMapLayer,SafeLayer

        """
        if self.impact_function is None:
            raise Exception('Impact Function not found.')

        # We transfer the layer to the IF.
        self.impact_function.exposure = exposure_layer

    @property
    def aggregation(self):
        """Property for aggregation layer.

        :returns: Aggregation Layer of the analysis.
        :rtype: SafeLayer

        """
        return self.impact_function.aggregation

    @aggregation.setter
    def aggregation(self, aggregation_layer):
        """Setter for the aggregation layer for the analysis.

        :param aggregation_layer: The aggregation layer.
        :type aggregation_layer: QgsMapLayer,SafeLayer

        """
        if isinstance(aggregation_layer, SafeLayer) or \
                isinstance(aggregation_layer, QgsMapLayer):
            self.impact_function.aggregation = aggregation_layer
        else:
            self.impact_function.aggregation = None

    @property
    def impact_layer(self):
        """Obtain impact layer from the runner."""
        return self.impact_function.impact_layer

    @impact_layer.setter
    def impact_layer(self, layer):
        """Set impact layer.

        :param layer: The impact layer that would be assigned.
        :type layer: SAFE Layer, QgsMapLayer, QgsWrapper
        """
        # There is not setter for impact layer as we are outside of the IF.
        self.impact_function._impact_layer = layer

    def setup_aggregator(self):
        """Create an aggregator for this analysis run."""
        # Refactor from dock.prepare_aggregator
        clip_parameters = self.impact_function.clip_parameters
        try:
            buffered_geo_extent = self.impact_layer.extent
        except AttributeError:
            # if we have no runner, set dummy extent
            buffered_geo_extent = clip_parameters['adjusted_geo_extent']

        if self.aggregation is not None:
            qgis_layer = self.aggregation.qgis_layer()
        else:
            qgis_layer = None

        # setup aggregator to use buffered_geo_extent to deal with #759
        self.aggregator = Aggregator(
            buffered_geo_extent, qgis_layer)

        self.aggregator.show_intermediate_layers = \
            self.show_intermediate_layers

    def setup_analysis(self):
        """Setup analysis so that it will be ready for running."""
        # Refactor from dock.accept()

        # Fixme : temporary call from here until we delete this file.
        self.impact_function.emit_pre_run_message()

        # Find out what the usable extent and cell size are
        try:
            clip_parameters = self.impact_function.clip_parameters
            adjusted_geo_extent = clip_parameters['adjusted_geo_extent']
            cell_size = clip_parameters['cell_size']
        except InsufficientOverlapError as e:
            raise e
        except (RuntimeError, AttributeError) as e:
            LOGGER.exception('Error calculating extents. %s' % str(e.message))
            context = tr(
                'A problem was encountered when trying to determine the '
                'analysis extents.'
            )
            analysis_error(self, e, context)
            raise e

        if not self.force_memory:
            # Ensure there is enough memory
            result = check_memory_usage(adjusted_geo_extent, cell_size)
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

        try:
            self.setup_impact_function()
        except CallGDALError, e:
            analysis_error(self, e, tr(
                'An error occurred when calling a GDAL command'))
            return
        except IOError, e:
            analysis_error(self, e, tr(
                'An error occurred when writing clip file'))
            return
        except InsufficientOverlapError, e:
            analysis_error(self, e, tr(
                'An exception occurred when setting up the '
                'impact calculator.'))
            return
        except NoFeaturesInExtentError, e:
            analysis_error(self, e, tr(
                'An error occurred because there are no features visible in '
                'the current view. Try zooming out or panning until some '
                'features become visible.'))
            return
        except InvalidProjectionError, e:
            analysis_error(self, e, tr(
                'An error occurred because you are using a layer containing '
                'count data (e.g. population count) which will not '
                'scale accurately if we re-project it from its native '
                'coordinate reference system to WGS84/GeoGraphic.'))
            return
        except MemoryError, e:
            analysis_error(
                self,
                e,
                tr(
                    'An error occurred because it appears that your '
                    'system does not have sufficient memory. Upgrading '
                    'your computer so that it has more memory may help. '
                    'Alternatively, consider using a smaller geographical '
                    'area for your analysis, or using rasters with a larger '
                    'cell size.'))
            return

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
            clip_parameters = self.impact_function.clip_parameters
            extra_exposure_keywords = clip_parameters[
                'extra_exposure_keywords']
            adjusted_geo_extent = clip_parameters['adjusted_geo_extent']
            cell_size = clip_parameters['cell_size']
        except:
            raise
        # Find out what clipping behaviour we have - see #2210
        settings = QSettings()
        mode = settings.value(
            'inasafe/analysis_extents_mode',
            'HazardExposureView')
        detail = None
        if mode == 'HazardExposureView':
            detail = tr(
                'Resampling and clipping the hazard layer to match the '
                'intersection of the exposure layer and the current view '
                'extents.')
        elif mode == 'HazardExposure':
            detail = tr(
                'Resampling and clipping the hazard layer to match the '
                'intersection of the exposure layer extents.')
        elif mode == 'HazardExposureBookmark':
            detail = tr(
                'Resampling and clipping the hazard layer to match the '
                'bookmarked extents.')
        elif mode == 'HazardExposureBoundingBox':
            detail = tr(
                'Resampling and clipping the hazard layer to match the '
                'intersection of your preferred analysis area.')
        # Make sure that we have EPSG:4326 versions of the input layers
        # that are clipped and (in the case of two raster inputs) resampled to
        # the best resolution.
        title = tr('Preparing hazard data')

        message = m.Message(
            m.Heading(title, **PROGRESS_UPDATE_STYLE),
            m.Paragraph(detail))
        send_dynamic_message(self, message)
        try:
            clipped_hazard = clip_layer(
                layer=self.hazard.qgis_layer(),
                extent=adjusted_geo_extent,
                cell_size=cell_size,
                hard_clip_flag=self.clip_hard)
        except CallGDALError, e:
            raise e
        except IOError, e:
            raise e

        title = tr('Preparing exposure data')
        # Find out what clipping behaviour we have - see #2210
        settings = QSettings()
        mode = settings.value(
            'inasafe/analysis_extents_mode',
            'HazardExposureView')
        if mode == 'HazardExposureView':
            detail = tr(
                'Resampling and clipping the exposure layer to match '
                'the intersection of the hazard layer and the current view '
                'extents.')
        elif mode == 'HazardExposure':
            detail = tr(
                'Resampling and clipping the exposure layer to match '
                'the intersection of the hazard layer extents.')
        elif mode == 'HazardExposureBookmark':
            detail = tr(
                'Resampling and clipping the exposure layer to match '
                'the bookmarked extents.')
        elif mode == 'HazardExposureBoundingBox':
            detail = tr(
                'Resampling and clipping the exposure layer to match '
                'the intersection of your preferred analysis area.')
        message = m.Message(
            m.Heading(title, **PROGRESS_UPDATE_STYLE),
            m.Paragraph(detail))
        send_dynamic_message(self, message)

        clipped_exposure = clip_layer(
            layer=self.exposure.qgis_layer(),
            extent=adjusted_geo_extent,
            cell_size=cell_size,
            extra_keywords=extra_exposure_keywords,
            hard_clip_flag=self.clip_hard)
        return clipped_hazard, clipped_exposure

    def setup_impact_function(self):
        """Setup impact function."""
        # Get the hazard and exposure layers selected in the combos
        # and other related parameters needed for clipping.

        if self.impact_function.requires_clipping:
            # The impact function uses SAFE layers,
            # clip them
            hazard_layer, exposure_layer = self.optimal_clip()
            self.aggregator.set_layers(hazard_layer, exposure_layer)

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
            self.hazard = self.aggregator.hazard_layer
            self.exposure = self.aggregator.exposure_layer
        else:
            # It is a QGIS impact function,
            # clipping isn't needed, but we need to set up extent
            self.aggregator.set_layers(
                self.hazard.qgis_layer(), self.exposure.qgis_layer())
            clip_parameters = self.impact_function.clip_parameters
            adjusted_geo_extent = clip_parameters['adjusted_geo_extent']
            self.impact_function.requested_extent = adjusted_geo_extent

        # Set input layers
        self.impact_function.hazard = self.hazard
        self.impact_function.exposure = self.exposure

    def run_aggregator(self):
        """Run all post processing steps."""
        LOGGER.debug('Do aggregation')
        if self.impact_layer is None:
            # Done was emitted, but no impact layer was calculated
            message = tr('No impact layer was generated.\n')
            send_not_busy_signal(self)
            send_error_message(self, message)
            send_analysis_done_signal(self)
            return
        try:
            qgis_impact_layer = safe_to_qgis_layer(self.impact_layer)
            self.aggregator.extent = extent_to_array(
                qgis_impact_layer.extent(),
                qgis_impact_layer.crs())
            self.aggregator.aggregate(self.impact_layer)
        except InvalidGeometryError, e:
            message = get_error_message(e)
            send_error_message(self, message)
            # self.analysis_done.emit(False)
            return
        except Exception, e:  # pylint: disable=W0703
            # noinspection PyPropertyAccess
            e.args = (str(e.args[0]) + '\nAggregation error occurred',)
            raise

        # TODO (MB) do we really want this check?
        if self.aggregator.error_message is None:
            self.run_post_processor()
        else:
            content = self.aggregator.error_message
            exception = AggregationError(tr(
                'Aggregation error occurred.'))
            analysis_error(self, exception, content)

    def run_post_processor(self):
        """Carry out any postprocessing required for this impact layer.
        """
        LOGGER.debug('Do postprocessing')
        self.postprocessor_manager = PostprocessorManager(self.aggregator)
        self.postprocessor_manager.function_parameters = \
            self.impact_function.parameters
        self.postprocessor_manager.run()
        send_not_busy_signal(self)
        send_analysis_done_signal(self)

    def run_analysis(self):
        """It's similar with run function in previous dock.py"""
        send_busy_signal(self)

        title = tr('Calculating impact')
        detail = tr(
            'This may take a little while - we are computing the areas that '
            'will be impacted by the hazard and writing the result to a new '
            'layer.')
        message = m.Message(
            m.Heading(title, **PROGRESS_UPDATE_STYLE),
            m.Paragraph(detail))
        send_dynamic_message(self, message)

        try:
            self.impact_layer = calculate_impact(self.impact_function)
            self.run_aggregator()
        except ZeroImpactException, e:
            report = m.Message()
            report.add(LOGO_ELEMENT)
            report.add(m.Heading(tr(
                'Analysis Results'), **INFO_STYLE))
            report.add(m.Text(e.message))
            report.add(m.Heading(tr('Notes'), **SUGGESTION_STYLE))
            exposure_layer_title = self.exposure.name
            hazard_layer_title = self.hazard.name
            report.add(m.Text(tr(
                'It appears that no %s are affected by %s. You may want '
                'to consider:') % (
                    exposure_layer_title, hazard_layer_title)))
            check_list = m.BulletedList()
            check_list.add(tr(
                'Check that you are not zoomed in too much and thus '
                'excluding %s from your analysis area.') % (
                    exposure_layer_title))
            check_list.add(tr(
                'Check that the exposure is not no-data or zero for the '
                'entire area of your analysis.'))
            check_list.add(tr(
                'Check that your impact function thresholds do not '
                'exclude all features unintentionally.'))
            # See #2288 and 2293
            check_list.add(tr(
                'Check that your dataset coordinate reference system is '
                'compatible with InaSAFE\'s current requirements.'))
            report.add(check_list)
            send_static_message(self, report)
            send_analysis_done_signal(self)
            return
        except MemoryError, e:
            message = tr(
                'An error occurred because it appears that your system does '
                'not have sufficient memory. Upgrading your computer so that '
                'it has more memory may help. Alternatively, consider using a '
                'smaller geographical area for your analysis, or using '
                'rasters with a larger cell size.')
            analysis_error(self, e, message)
        except Exception, e:  # pylint: disable=W0703
            # FIXME (Ole): This branch is not covered by the tests
            analysis_error(
                self,
                e,
                tr('An exception occurred when running the impact analysis.'))
