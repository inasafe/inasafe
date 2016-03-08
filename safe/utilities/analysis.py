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

from qgis.core import QgsMapLayer, QgsRectangle

from safe.storage.safe_layer import SafeLayer
from safe.common.exceptions import (
    InsufficientOverlapError,
    CallGDALError,
    NoFeaturesInExtentError,
    InvalidProjectionError,
    InvalidAggregationKeywords,
    InsufficientMemoryWarning)
from safe import messaging as m
from safe.utilities.memory_checker import check_memory_usage
from safe.utilities.i18n import tr
from safe.messaging import styles
from safe.common.signals import (
    analysis_error)


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
        self._impact_function = None

    @property
    def impact_function(self):
        if not self._impact_function:
            # RMN: need to put sane exception to easily identify errors
            raise ValueError('Impact function property cannot be empty')
        return self._impact_function

    @impact_function.setter
    def impact_function(self, impact_function):
        self._impact_function = impact_function

    @property
    def aggregator(self):
        return self.impact_function.aggregator

    @property
    def clip_hard(self):
        return self.impact_function.clip_hard

    @clip_hard.setter
    def clip_hard(self, clip_hard):
        self.impact_function.clip_hard = clip_hard

    @property
    def show_intermediate_layers(self):
        return self.impact_function.show_intermediate_layers

    @show_intermediate_layers.setter
    def show_intermediate_layers(self, flag):
        self.impact_function.show_intermediate_layers = flag

    @property
    def force_memory(self):
        return self.impact_function.force_memory

    @force_memory.setter
    def force_memory(self, force_memory):
        self.impact_function.force_memory = force_memory

    @property
    def viewport_extent(self):
        return self.impact_function.viewport_extent

    @viewport_extent.setter
    def viewport_extent(self, viewport_extent):
        # We transfer the viewport extent to the IF.
        self.impact_function.viewport_extent = viewport_extent

    @property
    def user_extent(self):
        return self.impact_function.requested_extent

    @user_extent.setter
    def user_extent(self, user_extent):
        # We transfer the extent to the IF as a list.
        if isinstance(user_extent, QgsRectangle):
            extent = [
                user_extent.xMinimum(),
                user_extent.yMinimum(),
                user_extent.xMaximum(),
                user_extent.yMaximum()]
            self.impact_function.requested_extent = extent
        elif user_extent is None:
            pass
        else:
            # This is a temporary hack, analysis.py will disappear soon.
            raise Exception('The extent should be a QgsRectangle.')

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
        return self.impact_function.impact

    @impact_layer.setter
    def impact_layer(self, layer):
        """Set impact layer.

        :param layer: The impact layer that would be assigned.
        :type layer: SAFE Layer, QgsMapLayer, QgsWrapper
        """
        # There is not setter for impact layer as we are outside of the IF.
        self.impact_function._impact = layer

    def run_analysis(self):
        """It's similar with run function in previous dock.py"""
        self.impact_function.run_analysis()

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

        self.impact_function.setup_aggregator()

        # go check if our postprocessing layer has any keywords set and if not
        # prompt for them. if a prompt is shown run method is called by the
        # accepted signal of the keywords dialog
        self.aggregator.validate_keywords()
        if self.aggregator.is_valid:
            pass
        else:
            raise InvalidAggregationKeywords

        try:
            self.impact_function.setup_impact_function()
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
