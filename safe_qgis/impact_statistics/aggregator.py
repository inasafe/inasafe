# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Aggregator.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from safe.storage.utilities import safe_to_qgis_layer
from safe_qgis.utilities.defaults import breakdown_defaults

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '19/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import sys
import logging
import time

import numpy
from PyQt4 import QtGui, QtCore
from qgis.core import (
    QgsMapLayer,
    QgsGeometry,
    QgsMapLayerRegistry,
    QgsFeature,
    QgsFeatureRequest,
    QgsRectangle,
    QgsPoint,
    QgsField,
    QgsFields,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QGis,
    QgsSingleSymbolRendererV2,
    QgsFillSymbolV2,
    QgsCoordinateReferenceSystem)
from qgis.analysis import QgsZonalStatistics

from safe_qgis.impact_statistics.zonal_stats import calculate_zonal_stats
from safe_qgis.exceptions import InsufficientParametersError
from collections import OrderedDict
from third_party.pydispatch import dispatcher
from safe_qgis.utilities.clipper import clip_layer
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.utilities import (
    is_polygon_layer,
    layer_attribute_names,
    create_memory_layer)
from safe_qgis.utilities.styling import set_vector_graduated_style
from safe_qgis.safe_interface import (
    temp_dir,
    safe_read_layer,
    ReadLayerError,
    points_in_and_outside_polygon,
    calculate_polygon_centroid,
    unique_filename,
    messaging as m,
    feature_attributes_as_dict,
    get_utm_epsg)
from safe_qgis.safe_interface import (
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    PointsInputError)
from safe_qgis.exceptions import (
    KeywordNotFoundError,
    NoKeywordsFoundError,
    InvalidParameterError,
    KeywordDbError,
    InvalidAggregatorError,
    UnsupportedProviderError,
    InvalidLayerError)
from safe_qgis.safe_interface import styles

PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
INFO_STYLE = styles.INFO_STYLE
WARNING_STYLE = styles.WARNING_STYLE

LOGGER = logging.getLogger('InaSAFE')
#from pydev import pydevd


# If inasafe is running as qgis plugin,
# it can import processing (from QGIS / sextante),
# pylint: disable=F0401
import processing
# pylint: enable=F0401


class Aggregator(QtCore.QObject):
    """The aggregator class facilitates aggregation of impact function results.
    """

    def __init__(self, extent, aggregation_layer):
        """Director for aggregation based operations.

        :param aggregation_layer: Layer representing clipped aggregation
            areas. This will be converted to a memory layer inside this class.
            see self.layer
        :type aggregation_layer: QgsVectorLayer, QgsMapLayer
        """

        QtCore.QObject.__init__(self)

        self.hazard_layer = None    # Used in deintersect() method
        self.exposure_layer = None  # Used in deintersect() method
        self.safe_layer = None      # Aggregation layer in SAFE format

        self.prefix = 'aggr_'
        self.attributes = {}
        self.attribute_title = None
        self._sum_field_name = None
        self.set_sum_field_name()

        #use qgis or inasafe zonal stats
        flag = bool(QtCore.QSettings().value(
            'inasafe/use_native_zonal_stats', False, type=bool))
        self.use_native_zonal_stats = flag

        self.extent = extent
        self._keyword_io = KeywordIO()
        self._defaults = breakdown_defaults()
        self.error_message = None
        self.target_field = None

        # self.impact_layer_attributes is a list of list of dict
        # [
        #    [{...},{...},{...}],
        #    [{...},{...},{...}]
        # ]
        # It contains lists of objects that are covered by
        # aggregation polygons (one list for one polygon)
        self.impact_layer_attributes = []

        self.processing = processing

        # If this flag is not True, no aggregation or postprocessing will run
        # this is set as True by validateKeywords()
        self.is_valid = False
        self.show_intermediate_layers = False

        # This is used to hold an *in memory copy* of the aggregation layer
        # or None if the clip extents should be used.
        self.layer = None
        if aggregation_layer is None:
            self.aoi_mode = True
            # Will be completed in _prepareLayer just before deintersect call
            self.layer = self._create_polygon_layer()
        else:
            self.aoi_mode = False
            self.layer = aggregation_layer

        self.statistics_type = None
        self.statistics_classes = None
        self.preprocessed_feature_count = None

        # If keywords don't assigned with self.layer,
        # set up dummy keywords
        try:
            _ = self.read_keywords(self.layer)
        except NoKeywordsFoundError:
            # No kw file was found for layer - create an empty one.
            keywords = {}
            self.write_keywords(
                self.layer, keywords)

    def read_keywords(self, layer, keyword=None):
        """It is a wrapper around self._keyword_io.read_keywords

        :param layer: Layer you want to get the keywords for.
        :type layer: QgsMapLayer

        :param keyword: Optional specific keyword you want the value for.
        :type keyword: str
        :returns:   KeywordIO.read_keywords object
        :rtype:     KeywordIO.read_keywords

        :raises:  All exceptions are propagated.
        """
        try:
            return self._keyword_io.read_keywords(layer, keyword=keyword)
        except:
            raise

    def update_keywords(self, layer, keywords):
        """It is a wrapper around self._keyword_io.update_keywords

        :param layer: Layer you want to get the keywords for.
        :type layer: QgsMapLayer

        :param keywords: Dict of keywords to apply to the existing keywords.
        :type keywords: dict

        :raises:  All exceptions are propagated.
        """
        try:
            self._keyword_io.update_keywords(layer, keywords=keywords)
        except:
            raise

    def get_statistics(self, layer):
        """It is a wrapper around self._keyword_io.read_keywords

        :param layer: Layer you want to get the keywords for.
        :type layer: QgsMapLayer
        :returns:   KeywordIO.get_statistics object
        :rtype:     KeywordIO.get_statistics

        :raises:  All exceptions are propagated.
        """
        try:
            return self._keyword_io.get_statistics(layer)
        except:
            raise

    def copy_keywords(self, layer, out_filename):
        """It is a wrapper around self._keyword_io.copy_keywords

        :param layer: Layer you want to get the keywords for.
        :type layer: QgsMapLayer

        :param out_filename: Output filename that the keywords should be
            written to.
        :type out_filename: str
        :raises:  All exceptions are propagated.
        """
        try:
            self._keyword_io.copy_keywords(layer, out_filename)
        except:
            raise

    def write_keywords(self, layer, keywords):
        """It is a wrapper around self._keyword_io.write_keywords

        :param layer: Layer you want to get the keywords for.
        :type layer: QgsMapLayer

        :param keywords: Dict of keywords to write.
        :type keywords: dict
        :raises:  All exceptions are propagated.
        """
        try:
            self._keyword_io.write_keywords(layer, keywords)
        except:
            raise

    def get_default_keyword(self, keyword):
        """It is a wrapper around self._defaults.
        Returns default attribute keyword.

        :param keyword: A string containing the keyword to be returned
              for the layer.
        :type keyword: str

        :returns: The value for the given key if it is present.
        :rtype: str

        :raises:  All exceptions are propagated.
        """
        try:
            return self._defaults[keyword]
        except:
            raise

    def validate_keywords(self):
        """Check if the postprocessing layer has all needed attribute keywords.

        This is only applicable in the case where were are not using the AOI
        (in other words self.aoi_mode is False). When self.aoi_mode is True
        then we always use just the defaults and don't allow the user to
        create custom aggregation field mappings.

        This method is called on instance creation and should always be
        called if you change any state of the aggregator class.

        On completion of this method the self.is_valid flag is set. If this
        flag is not True, then no aggregation or postprocessing work will be
        carried out (these methods will raise an InvalidAggregatorError).
        """

        # Otherwise get the attributes for the aggregation layer.
        # noinspection PyBroadException
        try:
            keywords = self.read_keywords(self.layer)
        #discussed with Tim,in this case its ok to be generic
        except Exception:  # pylint: disable=W0703
            keywords = {}

        if self.aoi_mode:
            keywords[self.get_default_keyword('FEMALE_RATIO_ATTR_KEY')] = \
                self.tr('Use default')
            keywords[self.get_default_keyword('YOUTH_RATIO_ATTR_KEY')] = \
                self.tr('Use default')
            keywords[self.get_default_keyword('ADULT_RATIO_ATTR_KEY')] = \
                self.tr('Use default')
            keywords[self.get_default_keyword('ELDERLY_RATIO_ATTR_KEY')] = \
                self.tr('Use default')
            self.update_keywords(self.layer, keywords)
            self.is_valid = True
            return
        else:
            message = m.Message(
                m.Heading(
                    self.tr('Select attribute'), **PROGRESS_UPDATE_STYLE),
                m.Paragraph(self.tr(
                    'Please select which attribute you want to use as ID for '
                    'the aggregated results')))
            #noinspection PyTypeChecker
            self._send_message(message)

            #keywords are already complete
            category = keywords['category']
            aggregation_attribute = self.get_default_keyword('AGGR_ATTR_KEY')
            female_ratio = self.get_default_keyword('FEMALE_RATIO_ATTR_KEY')
            female_ratio_key = self.get_default_keyword('FEMALE_RATIO_KEY')
            youth_ratio = self.get_default_keyword('YOUTH_RATIO_ATTR_KEY')
            youth_ratio_key = self.get_default_keyword('YOUTH_RATIO_KEY')
            adult_ratio = self.get_default_keyword('ADULT_RATIO_ATTR_KEY')
            adult_ratio_key = self.get_default_keyword('ADULT_RATIO_KEY')
            elderly_ratio = self.get_default_keyword('ELDERLY_RATIO_ATTR_KEY')
            elderly_ratio_key = self.get_default_keyword('ELDERLY_RATIO_KEY')

            if (aggregation_attribute in keywords
                and ('category' in keywords and
                             category == 'postprocessing')
                and (female_ratio in keywords and
                         (female_ratio != self.tr('Use default') or
                          female_ratio_key in keywords))
                and (youth_ratio in keywords and
                         (youth_ratio != self.tr('Use default') or
                          youth_ratio_key in keywords))
                and (adult_ratio in keywords and
                         (adult_ratio != self.tr('Use default') or
                          adult_ratio_key in keywords))
                and (elderly_ratio in keywords and
                         (elderly_ratio != self.tr('Use default') or
                          elderly_ratio_key in keywords))):
                self.is_valid = True
            #some keywords are needed
            else:
                #set the default values by writing to the keywords
                keywords['category'] = 'postprocessing'

                #noinspection PyTypeChecker
                my_attributes, _ = layer_attribute_names(
                    self.layer,
                    [QtCore.QVariant.Int, QtCore.QVariant.String])
                if self.get_default_keyword('AGGR_ATTR_KEY') not in keywords:
                    keywords[self.get_default_keyword('AGGR_ATTR_KEY')] = \
                        my_attributes[0]

                if self.get_default_keyword('FEMALE_RATIO_ATTR_KEY') not in \
                        keywords:
                    keywords[self.get_default_keyword(
                        'FEMALE_RATIO_ATTR_KEY')] = self.tr('Use default')

                if self.get_default_keyword('FEMALE_RATIO_KEY') not in \
                        keywords:
                    keywords[self.get_default_keyword('FEMALE_RATIO_KEY')] = \
                        self.get_default_keyword('FEMALE_RATIO')

                if self.get_default_keyword('YOUTH_RATIO_ATTR_KEY') not in \
                        keywords:
                    keywords[self.get_default_keyword(
                        'YOUTH_RATIO_ATTR_KEY')] = self.tr('Use default')

                if self.get_default_keyword('YOUTH_RATIO_KEY') not in \
                        keywords:
                    keywords[self.get_default_keyword('YOUTH_RATIO_KEY')] = \
                        self.get_default_keyword('YOUTH_RATIO')

                if self.get_default_keyword('ADULT_RATIO_ATTR_KEY') not in \
                        keywords:
                    keywords[self.get_default_keyword(
                        'ADULT_RATIO_ATTR_KEY')] = self.tr('Use default')

                if self.get_default_keyword('ADULT_RATIO_KEY') not in \
                        keywords:
                    keywords[self.get_default_keyword('ADULT_RATIO_KEY')] = \
                        self.get_default_keyword('ADULT_RATIO')

                if self.get_default_keyword('ELDERLY_RATIO_ATTR_KEY') not in \
                        keywords:
                    keywords[self.get_default_keyword(
                        'ELDERLY_RATIO_ATTR_KEY')] = self.tr('Use default')

                if self.get_default_keyword('ELDERLY_RATIO_KEY') not in \
                        keywords:
                    keywords[self.get_default_keyword('ELDERLY_RATIO_KEY')] = \
                        self.get_default_keyword('ELDERLY_RATIO')

                self.update_keywords(self.layer, keywords)
                self.is_valid = False

    def set_layers(self, hazard_layer, exposure_layer):
        """Set up aggregator layers

        :param hazard_layer: A hazard layer.
        :type hazard_layer: QgsMapLayer

        :param exposure_layer: An exposure layer.
        :type exposure_layer: QgsMapLayer

        """
        self.hazard_layer = hazard_layer
        self.exposure_layer = exposure_layer
        try:
            self._prepare_layer()
        except (InvalidLayerError, UnsupportedProviderError, KeywordDbError):
            raise

        self.safe_layer = safe_read_layer(str(self.layer.source()))

    def deintersect(self):
        """Ensure there are no intersecting features with self.layer.

        This should only happen after initial checks have been made.

        .. note:: Buildings are not split up by this method.

        :raises: InsufficientParametersError if hazard_layer or exposure_layer
                 is not set.
        """

        if not self.is_valid:
            raise InvalidAggregatorError

        if self.hazard_layer is None:
            message = self.tr('Error: hazard layer is not provided.')
            raise InsufficientParametersError(message)

        if self.exposure_layer is None:
            message = self.tr('Error: exposure layer is not provided.')
            raise InsufficientParametersError(message)

        if not self.aoi_mode:
            if is_polygon_layer(self.hazard_layer):
                self.hazard_layer = self._prepare_polygon_layer(
                    self.hazard_layer)

            if is_polygon_layer(self.exposure_layer):
                # Find out the subcategory for this layer
                subcategory = self.read_keywords(
                    self.exposure_layer, 'subcategory')
                # We don't want to chop up buildings!
                if subcategory != 'structure':
                    self.exposure_layer = self._prepare_polygon_layer(
                        self.exposure_layer)

    def aggregate(self, safe_impact_layer):
        """Do any requested aggregation post processing.

        Performs Aggregation postprocessing step by

            * creating a copy of the data set clipped by the impact layer
              bounding box
            * stripping all attributes beside the aggregation attribute
            * delegating to the appropriate aggregator for raster and vectors

        :param safe_impact_layer: The layer that will be aggregated.
        :type safe_impact_layer: read_layer

        :raises: ReadLayerError
        """

        if not self.is_valid:
            raise InvalidAggregatorError

        message = m.Message(
            m.Heading(self.tr('Aggregating results'), **PROGRESS_UPDATE_STYLE),
            m.Paragraph(self.tr(
                'This may take a little while - we are aggregating the impact'
                ' by %s' % self.layer.name())))
        #noinspection PyTypeChecker
        self._send_message(message)

        qgis_impact_layer = safe_to_qgis_layer(safe_impact_layer)
        if not qgis_impact_layer.isValid():
            message = self.tr('Error when reading %s') % (
                qgis_impact_layer)
            # noinspection PyExceptionInherit
            raise ReadLayerError(message)

        aggregation_layer_name = self.layer.name()
        if self.aoi_mode:
            aggregation_layer_name = aggregation_layer_name.lower()
        layer_name = str(self.tr('%s aggregated to %s') % (
            qgis_impact_layer.name(), aggregation_layer_name))

        #delete unwanted fields
        provider = self.layer.dataProvider()
        fields = provider.fields()

        #mark important attributes as needed
        self._set_persistant_attributes()
        unneeded_attributes = []

        for i in xrange(fields.count()):
            if (fields[i].name() not in
                    self.attributes.values()):
                unneeded_attributes.append(i)
        LOGGER.debug('Removing this attributes: ' + str(unneeded_attributes))
        # noinspection PyBroadException
        try:
            provider.deleteAttributes(unneeded_attributes)
        # TODO (Ole): Disable pylint check for the moment
        # Need to work out what exceptions we will catch here, though.
        except:  # pylint: disable=W0702
            message = self.tr('Could not remove the unneeded fields')
            LOGGER.debug(message)

        self.layer.updateFields()
        del unneeded_attributes, provider, fields
        self.update_keywords(
            self.layer, {'title': layer_name})

        self.statistics_type, self.statistics_classes = (
            self.get_statistics(qgis_impact_layer))

        #call the correct aggregator
        if qgis_impact_layer.type() == QgsMapLayer.VectorLayer:
            self._aggregrate_vector_impact(
                qgis_impact_layer, safe_impact_layer)
        elif qgis_impact_layer.type() == QgsMapLayer.RasterLayer:
            self._aggregate_raster_impact(qgis_impact_layer)
        else:
            message = self.tr(
                '%s is %s but it should be either vector or raster') % (
                    qgis_impact_layer.name(), qgis_impact_layer.type())
            # noinspection PyExceptionInherit
            raise ReadLayerError(message)

        # show a styled aggregation layer
        if self.show_intermediate_layers:
            if self.statistics_type == 'sum':
                #style layer if we are summing
                provider = self.layer.dataProvider()
                attribute = self.sum_field_name()
                attribute_index = provider.fieldNameIndex(attribute)
                request = QgsFeatureRequest()
                request.setFlags(QgsFeatureRequest.NoGeometry)
                request.setSubsetOfAttributes([attribute_index])
                highest_value = 0

                for feature in provider.getFeatures(request):
                    value = feature[attribute_index]
                    # print "val", value
                    if value is not None and value > highest_value:
                        highest_value = value

                classes = []
                colors = ['#fecc5c', '#fd8d3c', '#f31a1c']
                step = int(highest_value / len(colors))
                counter = 0
                for color in colors:
                    minimum = counter
                    counter += step
                    maximum = counter

                    classes.append(
                        {'min': minimum,
                         'max': maximum,
                         'colour': color,
                         'transparency': 30,
                         'label': '%s - %s' % (minimum, maximum)})
                    counter += 1

                style = {
                    'target_field': attribute,
                    'style_classes': classes}
                set_vector_graduated_style(self.layer, style)
            else:
                #make style of layer pretty much invisible
                properties = {
                    'style': 'no',
                    'color_border': '0,0,0,127',
                    'width_border': '0.0'
                }
                # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                symbol = QgsFillSymbolV2.createSimple(properties)
                renderer = QgsSingleSymbolRendererV2(symbol)
                self.layer.setRendererV2(renderer)
                self.layer.saveDefaultStyle()

    def _aggregrate_vector_impact(self, impact_layer, safe_impact_layer):
        """Performs Aggregation postprocessing step on vector impact layers.

        :param impact_layer: A vector impact layer.
        :type impact_layer: QgsVectorLayer

        :param safe_impact_layer: The impact layer in SAFE format
        :type safe_impact_layer: read_layer
        """

        # Reset impact_layer_attributes
        # (if aggregation is running twice, we need empty list
        #   for store the data)
        self.impact_layer_attributes = []

        if not self._setup_target_field(impact_layer):
            # An unexpected error occurs, skip postprocessing
            return

        # Add fields for store aggregation atributes
        aggregation_provider = self.layer.dataProvider()
        if self.statistics_type == 'class_count':
            #add the class count fields to the layer
            fields = []
            for statistics_class in self.statistics_classes:
                field_name = self._aggregation_field_name(statistics_class)
                field = QgsField(field_name, QtCore.QVariant.String)
                fields.append(field)
            aggregation_provider.addAttributes(fields)
            self.layer.updateFields()
        elif self.statistics_type == 'sum':
            #add the total field to the layer
            aggregation_field = self.sum_field_name()
            aggregation_provider.addAttributes([QgsField(
                aggregation_field, QtCore.QVariant.Int)])
            self.layer.updateFields()

        if safe_impact_layer.is_point_data:
            LOGGER.debug('Doing point in polygon aggregation')
            self._aggregate_point_impact(safe_impact_layer)
        elif safe_impact_layer.is_polygon_data:
            LOGGER.debug('Doing polygon in polygon aggregation')
            self._aggregate_polygon_impact(safe_impact_layer)
        elif safe_impact_layer.is_line_data:
            LOGGER.debug('Doing line in polygon aggregation')
            self._aggregate_line_impact(safe_impact_layer)
        else:
            message = m.Paragraph(
                self.tr(
                    'Aggregation on vector impact layers other than points'
                    ' or polygons or lines yet not implemented yet.'
                    ' Called on %s') % (impact_layer.name()))
            LOGGER.debug('Skipping postprocessing due to: %s' % message)
            self.error_message = message
            self.layer.commitChanges()

    def _aggregate_raster_impact(self, impact_layer):
        """Aggregate on a raster impact layer by using zonal statistics.

        :param impact_layer: A raster impact layer.
        :type impact_layer: QgsRasterLayer
        """
        if self.use_native_zonal_stats:
            zonal_statistics = QgsZonalStatistics(
                self.layer,
                impact_layer.dataProvider().dataSourceUri(),
                self.prefix)
            progress_dialog = QtGui.QProgressDialog(
                self.tr('Calculating zonal statistics'),
                self.tr('Abort...'),
                0,
                0)
            start_time = time.clock()
            zonal_statistics.calculateStatistics(progress_dialog)
            if progress_dialog.wasCanceled():
                QtGui.QMessageBox.error(
                    self, self.tr('ZonalStats: Error'),
                    self.tr('You aborted aggregation, '
                            'so there are no data for analysis. Exiting...'))
            cpp_duration = time.clock() - start_time
            LOGGER.debug('Native zonal stats duration: %ss' % cpp_duration)
        else:
            # new way
            # zonal_statistics = {
            # 0L: {'count': 50539,
            #      'sum': 12015061.876953125,
            #      'mean': 237.73841739949594},
            # 1L: {
            #   'count': 19492,
            #   'sum': 2945658.1220703125,
            #   'mean': 151.12138939412642},
            # 2L: {
            #   'count': 57372,
            #   'sum': 1643522.3984985352, 'mean': 28.6467684323108},
            # 3L: {
            #   'count': 0.00013265823369700314,
            #   'sum': 0.24983273179242008,
            #   'mean': 1883.2810058593748},
            # 4L: {
            #   'count': 1.8158245316933218e-05,
            #   'sum': 0.034197078505115275,
            #   'mean': 1883.281005859375},
            # 5L: {
            #   'count': 73941,
            #   'sum': 10945062.435424805,
            #   'mean': 148.024268476553},
            # 6L: {
            #   'count': 54998,
            #   'sum': 11330910.488220215,
            #   'mean': 206.02404611477172}}
            start_time = time.clock()
            zonal_statistics = calculate_zonal_stats(impact_layer, self.layer)
            python_duration = time.clock() - start_time
            LOGGER.debug('Python zonal stats duration: %ss' % python_duration)

            provider = self.layer.dataProvider()

            # add fields for stats to aggregation layer
            # { 1: {'sum': 10, 'count': 20, 'min': 1, 'max': 4, 'mean': 2},
            #             QgsField(self._minFieldName(),
            #                      QtCore.QVariant.Double),
            #             QgsField(self._maxFieldName(),
            #                      QtCore.QVariant.Double)]
            fields = [QgsField(self._count_field_name(),
                               QtCore.QVariant.Double),
                      QgsField(self.sum_field_name(),
                               QtCore.QVariant.Double),
                      QgsField(self._mean_field_name(),
                               QtCore.QVariant.Double)
                      ]
            provider.addAttributes(fields)
            self.layer.updateFields()

            sum_index = provider.fieldNameIndex(self.sum_field_name())
            count_index = provider.fieldNameIndex(self._count_field_name())
            mean_index = provider.fieldNameIndex(self._mean_field_name())
            # minIndex = provider.fieldNameIndex(self._minFieldName())
            # maxIndex = provider.fieldNameIndex(self._maxFieldName())

            for myFeature in provider.getFeatures():
                feature_id = myFeature.id()
                if feature_id not in zonal_statistics:
                    # Blindly ignoring - @mbernasocchi can you review? TS
                    # (YA: see #877)
                    attributes = {
                        sum_index: 0,
                        count_index: 0,
                        mean_index: 0
                    }
                else:
                    statistics = zonal_statistics[feature_id]
                    attributes = {
                        sum_index: statistics['sum'],
                        count_index: statistics['count'],
                        mean_index: statistics['mean']
                    }
                provider.changeAttributeValues({feature_id: attributes})

    def _aggregate_polygon_impact(self, safe_impact_layer):
        """Aggregation of polygons in polygons

        :param safe_impact_layer: The impact layer in SAFE format
        :type safe_impact_layer: read_layer
        """
        # Using centroids to do polygon in polygon aggregation
        # this is always ok because
        # deintersect() took care of splitting
        # polygons that spawn across multiple postprocessing
        # polygons. After deintersect()
        # each impact polygon will never be contained by more than
        # one aggregation polygon

        # Calculate points for each polygon
        impact_geometries = safe_impact_layer.get_geometry()
        aggregation_points = self._get_centroids(impact_geometries)
        self._aggregate_point_impact(safe_impact_layer, aggregation_points)

    def _aggregate_point_impact(self, safe_impact_layer,
                                aggregation_points=None):
        """Aggregation of points in polygons

        :param safe_impact_layer: The impact layer in SAFE format
        :type safe_impact_layer: read_layer

        :param aggregation_points: Points that are used for aggregation
                                   if aggregation_points==None,
                                   all points from  safe_impact_layer are used
        :type aggregation_points: self._get_centroids
        """

        aggreg_remaining_values = safe_impact_layer.get_data()
        aggregation_units = self.safe_layer.get_geometry()
        aggregation_provider = self.layer.dataProvider()

        field_map = {}
        temp_aggregation_field_map = aggregation_provider.fieldNameMap()
        for k, v in temp_aggregation_field_map.iteritems():
            field_map[str(k)] = v

        if aggregation_points is None:
            # Take all points
            impact_geometries = safe_impact_layer.get_geometry()
            aggregation_points = impact_geometries

        #iterate over the aggregation units
        attributes = None
        for polygon_index, polygon in enumerate(aggregation_units):
            if hasattr(polygon, 'outer_ring'):
                outer_ring = polygon.outer_ring
                inner_rings = polygon.inner_rings
            else:
                # Assume it is an array
                outer_ring = polygon
                inner_rings = None

            try:
                # noinspection PyArgumentEqualDefault
                inside, outside = points_in_and_outside_polygon(
                    aggregation_points,
                    outer_ring,
                    holes=inner_rings,
                    closed=True,
                    check_input=True)
            except PointsInputError:  # too few points provided
                inside = []
                outside = []
            #self.impact_layer_attributes is a list of list of dict
            #[
            #   [{...},{...},{...}],
            #   [{...},{...},{...}]
            #]
            self.impact_layer_attributes.append([])
            if self.statistics_type == 'class_count':
                results = OrderedDict()
                for statistics_class in self.statistics_classes:
                    results[statistics_class] = 0

                for i in inside:
                    key = aggreg_remaining_values[i][self.target_field]
                    if isinstance(key, QtCore.QPyNullVariant):
                        message = m.Paragraph(
                            self.tr(
                                'The target_field contains Null values.'
                                ' The impact function should define this.')
                        )
                        LOGGER.debug(
                            'Skipping postprocessing due to: %s' % message)
                        self.error_message = message
                        return

                    try:
                        results[key] += 1
                    except KeyError:
                        error = (
                            'StatisticsClasses %s does not include '
                            'the %s class which was found in the '
                            'data. This is a problem in the impact '
                            'function statistics_classes definition' %
                            (self.statistics_classes,
                            key))
                        raise KeyError(error)

                    self.impact_layer_attributes[polygon_index].append(
                        aggreg_remaining_values[i])
                attributes = {}
                for k, v in results.iteritems():
                    key = self._aggregation_field_name(k)
                    field_index = field_map[key]
                    attributes[field_index] = v

            elif self.statistics_type == 'sum':
                #by default sum attributes
                aggregation_field = self.sum_field_name()
                field_index = field_map[aggregation_field]
                total = 0
                for i in inside:
                    try:
                        total += aggreg_remaining_values[i][
                            self.target_field]
                    except TypeError:
                        pass

                    #add all attributes to the impact_layer_attributes
                    self.impact_layer_attributes[polygon_index].append(
                        aggreg_remaining_values[i])
                attributes = {field_index: total}

            # Add features inside this polygon
            feature_ide = polygon_index
            aggregation_provider.changeAttributeValues(
                {feature_ide: attributes})

            # make outside points the input to the next iteration
            # this could maybe be done more quickly using directly
            # numpy arrays like this:
            # aggregation_points = aggregation_points[outside]
            # aggreg_remaining_values =
            # [aggreg_remaining_values[i] for i in outside]
            temp_points = []
            temp_values = []
            for i in outside:
                temp_points.append(aggregation_points[i])
                temp_values.append(aggreg_remaining_values[i])
            aggregation_points = temp_points
            aggreg_remaining_values = temp_values
            # LOGGER.debug('Before: ' + str(len(aggreg_remaining_values)))
            # LOGGER.debug('After: ' + str(len(aggreg_remaining_values)))
            # LOGGER.debug('Inside: ' + str(len(inside)))
            # LOGGER.debug('Outside: ' + str(len(outside)))

        self.layer.commitChanges()

    def _aggregate_line_impact(self, safe_impact_layer):
        """Aggregation of lines in polygons

        :param safe_impact_layer: The impact layer in SAFE format
        :type safe_impact_layer: read_layer
        """
        if self.statistics_type == 'class_count':
            msg = "Summary length calculation is only one " \
                  "implemented method for line aggregation."
            raise NotImplementedError(msg)
        elif self.statistics_type == 'sum':

            output_directory = temp_dir(sub_dir='pre-process')
            agg_provider = self.layer.dataProvider()

            # Split lines from impact layer by aggregation polygons,
            # Add column with polygon names to the line attributes
            impact_layer = safe_to_qgis_layer(safe_impact_layer)

            splits_filename = unique_filename(
                suffix='.shp', dir=output_directory)
            res = self.processing.runalg('qgis:intersection',
                impact_layer, self.layer, splits_filename)
            impact_layer_splits = QgsVectorLayer(
                res['OUTPUT'], 'split aggregation', 'ogr')

            # Add length column to impact layer

            # We need calculate length in meters, not degrees:
            # We can use processing 'qgis:exportaddgeometrycolumns' with
            # CALC_METHODS=2 (Ellipsoidal) directly, but that
            # requires  QgsProject instance (see ftools source).
            # To simplify test writing, use reprojection before.

            tmp_filename = unique_filename(
                suffix='.shp', dir=output_directory)
            epsg = "EPSG:" + str(get_utm_epsg(self.extent[0], self.extent[1]))
            res = processing.runalg(
                'qgis:reprojectlayer',
                impact_layer_splits,
                epsg,
                tmp_filename)
            projected_layer = QgsVectorLayer(
                res['OUTPUT'],
                'projected aggregation',
                'ogr')
            tmp_filename = unique_filename(
                suffix='.shp', dir=output_directory)
            res = self.processing.runalg('qgis:exportaddgeometrycolumns',
                projected_layer,
                # 2, # Ellipsoidal
                0,  # Layer CRS
                tmp_filename)
            impact_layer_splits = QgsVectorLayer(
                res['OUTPUT'],
                'length aggregation',
                'ogr'
            )
            # This column name is used by the processing algorithm:
            LENGTH_COLUMN = 'length'

            sum_field_index = \
                agg_provider.fieldNameIndex(self.sum_field_name())

            # agg_attribute is a field name of aggregating polygons
            agg_attribute = self.read_keywords(
                    self.layer, self.get_default_keyword('AGGR_ATTR_KEY'))
            agg_attribute_index = agg_provider.fieldNameIndex(agg_attribute)

            request = QgsFeatureRequest().\
                setSubsetOfAttributes([agg_attribute_index])
            agg_attribute_dict = {}
            for feature_id, feat in enumerate(self.layer.getFeatures(request)):
                name = feat.attributes()[0]
                if name in agg_attribute_dict:  # The name isn't unique
                    name += str(feature_id)  # Add a number to make unique key
                agg_attribute_dict[name] = feature_id
            # Total impacted length in the aggregation polygons:
            total = {
                feature_id: 0 for feature_id, __ in enumerate(
                self.layer.getFeatures(request))
            }

            # Create slots for dicts
            self.impact_layer_attributes = []
            for i in range(len(agg_attribute_dict)):
                self.impact_layer_attributes.append([])
                _ = i
            # Create list of line objects that are covered by
            # aggregation polygons (a list of dicts for a polygon)
            impact_field_map = {}   # {'FieldName': FieldIndex}
            temp_aggr_field_map = \
                impact_layer_splits.dataProvider().fieldNameMap()
            for k, v in temp_aggr_field_map.iteritems():
                impact_field_map[str(k)] = v

            request = QgsFeatureRequest().\
                setFlags(QgsFeatureRequest.NoGeometry)
            agg_attribute_index = impact_layer_splits.dataProvider().\
                fieldNameIndex(agg_attribute)
            for feat in impact_layer_splits.getFeatures(request):
                line_attributes = feat.attributes()
                polygon_name = line_attributes[agg_attribute_index]
                line_attribute_dict = \
                    feature_attributes_as_dict(
                        impact_field_map, line_attributes)
                line_attribute_dict[self.sum_field_name()] = \
                    line_attribute_dict[LENGTH_COLUMN]

                if isinstance(
                        line_attribute_dict[self.target_field],
                        QtCore.QPyNullVariant):
                    message = m.Paragraph(
                        self.tr(
                            'The target_field contains Null values.'
                            ' The impact function should define this.')
                    )
                    LOGGER.debug(
                        'Skipping postprocessing due to: %s' % message)
                    self.error_message = message
                    return

                # Postprocessor will sum all impacted length,
                # (remember, if line_attribute_dict[self.target_field]==0,
                # then the line is not impacted), so to keep the impacted
                # length and non-impacted zeros, the multiplication is used
                line_attribute_dict[self.target_field] = \
                    line_attribute_dict[LENGTH_COLUMN] * \
                    line_attribute_dict[self.target_field]
                polygon_index = agg_attribute_dict[polygon_name]
                self.impact_layer_attributes[polygon_index].\
                    append(line_attribute_dict)

                ###################################################
                # total in aggregation polygon
                total[polygon_index] +=  \
                    line_attribute_dict[self.target_field]

            for polygon_index in total.keys():
                agg_provider.changeAttributeValues(
                    {polygon_index: {sum_field_index: total[polygon_index]}})

            self.layer.commitChanges()

    def _prepare_layer(self):
        """Prepare the aggregation layer to match analysis extents.

        :raises: InvalidLayerError, UnsupportedProviderError, KeywordDbError
        """
        message = m.Message(
            m.Heading(
                self.tr('Preparing aggregation layer'),
                **PROGRESS_UPDATE_STYLE),
            m.Paragraph(self.tr(
                'We are clipping the aggregation layer to match the '
                'intersection of the hazard and exposure layer extents.')))
        #noinspection PyTypeChecker
        self._send_message(message)

        # This is used to hold an *in memory copy* of the aggregation layer
        # or a in memory layer with the clip extents as a feature.
        if self.aoi_mode:
            try:
                self.layer = self._extents_to_layer()
            except (InvalidLayerError,
                    UnsupportedProviderError,
                    KeywordDbError):
                raise
        # Area Of Interest (AOI) mode flag is False
        else:
            aggregation_attribute = self.read_keywords(
                self.layer, self.get_default_keyword('AGGR_ATTR_KEY'))

            #noinspection PyArgumentEqualDefault
            clipped_layer = clip_layer(
                layer=self.layer,
                extent=self.extent,
                explode_flag=True,
                explode_attribute=aggregation_attribute)

            name = '%s %s' % (self.layer.name(), self.tr('aggregation'))
            self.layer = clipped_layer
            self.layer.setLayerName(name)
            if self.show_intermediate_layers:
                self.update_keywords(self.layer, {'title': name})
                #noinspection PyArgumentList
                QgsMapLayerRegistry.instance().addMapLayers([self.layer])

    def _count_field_name(self):
        """Field name for the count column."""
        return (self.prefix + 'count')[:10]

    def _mean_field_name(self):
        """Field name for the mean column."""
        return (self.prefix + 'mean')[:10]

    def _min_field_name(self):
        """Field name for the min column."""
        return (self.prefix + 'min')[:10]

    def _max_field_name(self):
        """Field name for the max column."""
        return (self.prefix + 'max')[:10]

    def set_sum_field_name(self, value=None):
        """Set field name for the sum column.

        :param value: A name of sum field
        :type value: string

        :returns: None
        """
        if value is None:
            self._sum_field_name = (self.prefix + 'sum')[:10]
        else:
            self._sum_field_name = value

    def sum_field_name(self):
        """Return field name for the sum column."""
        if self._sum_field_name is None:
            msg = (
                'Field name for summary aggregation information'
                ' is not set.')
            raise InvalidParameterError(msg)
        return self._sum_field_name

    def _aggregation_field_name(self, statistic_class):
        """Return name of aggregation field

        :param statistic_class: A class of aggregation statistic.
        :return:        A string of field name
        """

        name = '%s_%s' % (statistic_class, self.target_field)
        #FIXME (MB) remove next line when we get rid of
        #shape files as internal format
        name = name[:10]
        return name

    def _get_centroids(self, polygons):
        """
        Get centroids of the polygon collection

        :returns: List of centroids of the polygons
        :rtype: List
        """
        centroids = []
        for polygon in polygons:
            if hasattr(polygon, 'outer_ring'):
                outer_ring = polygon.outer_ring
            else:
                # Assume it is an array
                outer_ring = polygon
            c = calculate_polygon_centroid(outer_ring)
            centroids.append(c)
        return centroids

    # noinspection PyDictCreation
    def _set_persistant_attributes(self):
        """Mark any attributes that should remain in the self.layer table."""
        self.attributes = {}
        self.attributes[self.get_default_keyword(
            'AGGR_ATTR_KEY')] = (
                self.read_keywords(
                    self.layer,
                    self.get_default_keyword('AGGR_ATTR_KEY')))

        female_ratio_key = self.get_default_keyword('FEMALE_RATIO_ATTR_KEY')
        female_ratio_attribute = self.read_keywords(
            self.layer,
            female_ratio_key)
        if ((female_ratio_attribute != self.tr('Don\'t use')) and
                (female_ratio_attribute != self.tr('Use default'))):
            self.attributes[female_ratio_key] = \
                female_ratio_attribute

        youth_ratio_key = self.get_default_keyword('YOUTH_RATIO_ATTR_KEY')
        youth_ratio_attribute = self.read_keywords(
            self.layer,
            youth_ratio_key)
        if ((youth_ratio_attribute != self.tr('Don\'t use')) and
                (youth_ratio_attribute != self.tr('Use default'))):
            self.attributes[youth_ratio_key] = \
                youth_ratio_attribute

        adult_ratio_key = self.get_default_keyword('ADULT_RATIO_ATTR_KEY')
        adult_ratio_attribute = self.read_keywords(
            self.layer,
            adult_ratio_key)
        if ((adult_ratio_attribute != self.tr('Don\'t use')) and
                (adult_ratio_attribute != self.tr('Use default'))):
            self.attributes[adult_ratio_key] = \
                adult_ratio_attribute

        elderly_ratio_key = self.get_default_keyword('ELDERLY_RATIO_ATTR_KEY')
        elderly_ratio_attribute = self.read_keywords(
            self.layer,
            elderly_ratio_key)
        if ((elderly_ratio_key != self.tr('Don\'t use')) and
                (elderly_ratio_attribute != self.tr('Use default'))):
            self.attributes[elderly_ratio_key] = \
                elderly_ratio_attribute

    def _prepare_polygon_layer(self, layer):
        """Create a new layer with no intersecting features to self.layer.

        A helper function to align the polygons to the post processing layer
        polygons. If one input polygon is in two or more post processing Layer
        polygons then it is divided so that each part is within only one of the
        post processing layer polygons. this allows to aggregate in
        postprocessing using centroid in polygon.

        The function assumes EPSG:4326 but no checks are enforced.

        :param layer: Layer to be processed.
        :type layer: QgsMapLayer, QgsVectorLayer

        :returns: A processed layer.
        :rtype: QgsMapLayer
        """
#        import time
#        startTime = time.clock()

        message = m.Message(
            m.Heading(
                self.tr('Pre-clipping input data...'),
                **PROGRESS_UPDATE_STYLE),
            m.Paragraph(self.tr(
                'Modifying %s to avoid intersections with the aggregation '
                'layer'
            ) % (layer.name())))
        #noinspection PyTypeChecker
        self._send_message(message)

        layer_filename = str(layer.source())
        postprocessing_polygons = self.safe_layer.get_geometry()
        polygons_layer = safe_read_layer(layer_filename)
        remaining_polygons = numpy.array(
            polygons_layer.get_geometry(), dtype=list)
#        myRemainingAttributes = numpy.array(polygons_layer.get_data())
        remaining_indexes = numpy.array(range(len(remaining_polygons)))

        #used for unit tests only
        self.preprocessed_feature_count = 0

        # TODO (MB) the intersecting array is used only for debugging and
        # could be safely removed
        intersecting_polygons = []
        inside_polygons = []

        # TODO (MB) maybe do raw geos without qgis
        #select all post processing polygons with no attributes
        aggregation_provider = self.layer.dataProvider()
        aggregation_request = QgsFeatureRequest()
        aggregation_request.setSubsetOfAttributes([])

        # copy polygons to a memory layer
        qgis_memory_layer = create_memory_layer(layer)

        polygons_provider = qgis_memory_layer.dataProvider()
        polygons_request = QgsFeatureRequest()
        qgis_feature = QgsFeature()
        inside_feature = QgsFeature()
        fields = polygons_provider.fields()
        temporary_dir = temp_dir(sub_dir='pre-process')
        out_filename = unique_filename(suffix='.shp', dir=temporary_dir)

        self.copy_keywords(layer, out_filename)
        shape_writer = QgsVectorFileWriter(
            out_filename,
            'UTF-8',
            fields,
            polygons_provider.geometryType(),
            polygons_provider.crs())
        if shape_writer.hasError():
            raise InvalidParameterError(shape_writer.errorMessage())
        # end TODO

        for (polygon_index, postprocessing_polygon) in enumerate(
                postprocessing_polygons):
            LOGGER.debug('Post Processing Polygon %s' % polygon_index)
            polygon_count = len(remaining_polygons)
            aggregation_request.setFilterFid(polygon_index)
            aggregation_polygon = aggregation_provider.getFeatures(
                aggregation_request).next()
            geometry = QgsGeometry(aggregation_polygon.geometry())

            # polygon bounding box values
            array = numpy.array(postprocessing_polygon)
            minx = miny = sys.maxint
            maxx = maxy = -minx
            postprocessing_minimum_x = min(minx, min(array[:, 0]))
            postprocessing_maximum_x = max(maxx, max(array[:, 0]))
            postprocessing_minimum_y = min(miny, min(array[:, 1]))
            postprocessing_maximum_y = max(maxy, max(array[:, 1]))

            # create an array full of False to store if a BB vertex is inside
            # or outside the polygon
            inside_vertices = numpy.zeros(polygon_count * 4, dtype=numpy.bool)

            # Create Nx2 vector of vertices of bounding boxes
            bounding_vertices = []
            # Compute bounding box for each geometry type
            for remaining_polygon in remaining_polygons:
                minx = miny = sys.maxint
                maxx = maxy = -minx
                # Do outer ring only as the BB is outside anyway
                array = numpy.array(remaining_polygon)
                minx = min(minx, numpy.min(array[:, 0]))
                maxx = max(maxx, numpy.max(array[:, 0]))
                miny = min(miny, numpy.min(array[:, 1]))
                maxy = max(maxy, numpy.max(array[:, 1]))
                bounding_vertices.extend([
                    (minx, miny),
                    (minx, maxy),
                    (maxx, maxy),
                    (maxx, miny)])

            # see if BB vertices are in polygon
            bounding_vertices = numpy.array(bounding_vertices)
            inside, _ = points_in_and_outside_polygon(
                bounding_vertices, postprocessing_polygon)
            # make True if the vertex was in polygon
            inside_vertices[inside] = True

            # next_iteration_polygons has the 0:count indexes
            # outside_polygons has the mapped to original indexes
            # and is overwritten at every iteration because we care only of
            # the outside polygons remaining after the last iteration
            next_iteration_polygons = []
            outside_polygons = []

            for i in range(polygon_count):
                k = i * 4
                mapped_index = remaining_indexes[i]
                # memory layers counting starts at 1 instead of 0 as in our
                # indexes
                feature_id = mapped_index + 1
                do_intersection = False
                # sum the isInside bool for each of the bounding box vertices
                # of each polygon. for example True + True + False + True is 3
                polygon_location = numpy.sum(inside_vertices[k:k + 4])

                if polygon_location == 4:
                    # all vertices are inside -> polygon is inside
                    # ignore this polygon from further analysis
                    inside_polygons.append(mapped_index)
                    polygons_request.setFilterFid(feature_id)
                    qgis_feature = polygons_provider.getFeatures(
                        polygons_request).next()
                    shape_writer.addFeature(qgis_feature)
                    self.preprocessed_feature_count += 1
#                    LOGGER.debug('Polygon %s is fully inside' %mapped_index)
#                    tmpWriter.addFeature(qgis_feature)

                elif polygon_location == 0:
                    # all vertices are outside
                    # check if the polygon BB is completely outside of the
                    # polygon BB.
                    polygon_min_x = numpy.min(bounding_vertices[k:k + 4, 0])
                    polygon_max_x = numpy.max(bounding_vertices[k:k + 4, 0])
                    polygon_min_y = numpy.min(bounding_vertices[k:k + 4, 1])
                    polygon_max_y = numpy.max(bounding_vertices[k:k + 4, 1])

                    # check if remaining_polygon is all E,W,N,S of polygon
                    if ((polygon_min_x > postprocessing_maximum_x) or
                            (polygon_max_x < postprocessing_minimum_x) or
                            (polygon_min_y > postprocessing_maximum_y) or
                            (polygon_max_y < postprocessing_minimum_y)):
                        # polygon is surely outside
                        outside_polygons.append(mapped_index)
                        # we need this polygon in the next iteration
                        next_iteration_polygons.append(i)
                    else:
                        # polygon might be outside or intersecting. consider
                        # it intersecting so it goes into further analysis
                        do_intersection = True
                else:
                    # some vertices are outside some inside -> polygon is
                    # intersecting
                    do_intersection = True

                # intersect using qgis
                if do_intersection:
#                    LOGGER.debug('Intersecting polygon %s' % mapped_index)
                    intersecting_polygons.append(mapped_index)

                    polygons_request.setFilterFid(feature_id)
                    try:
                        qgis_feature = polygons_provider.getFeatures(
                            polygons_request).next()
                    except StopIteration:
                        LOGGER.debug(
                            'Could not fetch feature: %s' % feature_id)
                        LOGGER.debug([str(error) for error in
                                      polygons_provider.errors()])

                    qgis_polygon_geometry = QgsGeometry(
                        qgis_feature.geometry())
                    attribute_map = qgis_feature.attributes()
#                    for (k, attr) in attribute_map.iteritems():
#                        LOGGER.debug( "%d: %s" % (k, attr.toString()))

                    # make intersection of the qgis_feature and the
                    # post processing polygon
                    # write the inside part to a shp file and the outside part
                    # back to the original QGIS layer
                    try:
                        intersection = geometry.intersection(
                            qgis_polygon_geometry)
#                        if intersection is not None:
                        intersection_geometry = QgsGeometry(intersection)

                        #from ftools
                        unknown_geometry_type = 0
                        geometry_type = intersection_geometry.wkbType()
                        if geometry_type == unknown_geometry_type:
                            int_com = geometry.combine(
                                qgis_polygon_geometry)
                            int_sym = geometry.symDifference(
                                qgis_polygon_geometry)
                            intersection_geometry = QgsGeometry(
                                int_com.difference(int_sym))
                        #LOGGER.debug('wkbType type of intersection: %s' %
                        #   intersection_geometry.wkbType())
                        polygon_types = [QGis.WKBPolygon, QGis.WKBMultiPolygon]
                        if intersection_geometry.wkbType() in polygon_types:
                            inside_feature.setGeometry(intersection_geometry)
                            inside_feature.setAttributes(attribute_map)
                            shape_writer.addFeature(inside_feature)
                            self.preprocessed_feature_count += 1
                        else:
                            #LOGGER.debug(
                            #    'Intersection not a polygon so the two '
                            #    'polygons either touch only or do not '
                            #    'intersect. Not adding this to the inside '
                            #    'list')
                            pass
                        # Part of the polygon that is outside the post
                        # processing polygon
                        outside = qgis_polygon_geometry.difference(
                            intersection_geometry)
#                        if outside is not None:
                        outside_geometry = QgsGeometry(outside)

                        if outside_geometry.wkbType() in polygon_types:
                            # modify the original geometry to the part
                            # outside of the post processing polygon
                            polygons_provider.changeGeometryValues(
                                {feature_id: outside_geometry})
                            # we need this polygon in the next iteration
                            outside_polygons.append(mapped_index)
                            next_iteration_polygons.append(i)

                    except TypeError:
                        LOGGER.debug('ERROR with FID %s', mapped_index)

            #LOGGER.debug('Inside %s' % inside_polygons)
            #LOGGER.debug('Outside %s' % outside_polygons)
            #LOGGER.debug('Intersection %s' % intersecting_polygons)
            if len(next_iteration_polygons) > 0:
                # some polygons are still completely outside of the
                # post processing polygon so go on and reiterate using only
                # these
                next_iteration_index = numpy.array(next_iteration_polygons)

                remaining_polygons = remaining_polygons[
                    next_iteration_index]
                #myRemainingAttributes = myRemainingAttributes[
                #                        next_iteration_index]
                remaining_indexes = remaining_indexes[next_iteration_index]
                LOGGER.debug('Remaining: %s' % len(remaining_polygons))
            else:
                print 'no more polygons to be checked'
                break
            #del tmpWriter

        # here the full polygon set is represented by:
        # inside_polygons + intersecting_polygons + next_iteration_polygons
        # the a polygon intersecting multiple post processing polygons appears
        # multiple times in the array
        # noinspection PyUnboundLocalVariable
        LOGGER.debug('Results:\nInside: %s\nIntersect: %s\nOutside: %s' % (
            inside_polygons, intersecting_polygons, outside_polygons))

        # add in-and outside polygons
        for i in outside_polygons:
            feature_id = i + 1
            polygons_request.setFilterFid(feature_id)
            qgis_feature = polygons_provider.getFeatures(
                polygons_request).next()
            shape_writer.addFeature(qgis_feature)
            self.preprocessed_feature_count += 1

        del shape_writer
#        LOGGER.debug('Created: %s' % self.preprocessed_feature_count)

        name = '%s %s' % (layer.name(), self.tr('preprocessed'))
        output_layer = QgsVectorLayer(out_filename, name, 'ogr')
        if not output_layer.isValid():
            #TODO (MB) use a better exception
            raise Exception('Invalid qgis Layer')

        if self.show_intermediate_layers:
            self.update_keywords(output_layer, {'title': name})
            #noinspection PyArgumentList
            QgsMapLayerRegistry.instance().addMapLayers([output_layer])

        return output_layer

    def _create_polygon_layer(self, crs=None, fields=None):
        """Creates an empty shape file layer.

        :param crs: CRS to use for created layer.
        :type crs: QgsCoordinateReferenceSystem

        :param fields:
        :type fields: QgsFields
        """

        if crs is None:
            crs = QgsCoordinateReferenceSystem()
            crs.createFromSrid(4326)

        if fields is None:
            fields = QgsFields()

        output_directory = temp_dir(sub_dir='pre-process')
        output_filename = unique_filename(
            suffix='.shp', dir=output_directory)
        shape_writer = QgsVectorFileWriter(
            output_filename, 'UTF-8', fields, QGis.WKBPolygon, crs)
        # flush the writer to write to file
        del shape_writer
        name = self.tr('Entire area')
        layer = QgsVectorLayer(output_filename, name, 'ogr')
        LOGGER.debug('created' + layer.name())
        return layer

    def _extents_to_layer(self):
        """Create simple layer with a polygon sized to extents of self.layer.

        Memory layer for aggregation by using canvas extents as feature.

        We do this because the user elected to use no aggregation layer so we
        make a 'dummy' one which covers the whole study area extent.

        This layer is needed when postprocessing because we always want a
        vector layer to store aggregation information in.

        :returns: A memory layer representing the extents of the clip.
        :rtype: QgsVectorLayer

        :raises: InvalidLayerError, UnsupportedProviderError, KeywordDbError
        """

        if not self.layer.isValid():
            message = self.tr(
                'An exception occurred when creating the entire area layer.')
            raise (InvalidLayerError(message))

        provider = self.layer.dataProvider()

        attribute_name = self.tr('Area')
        provider.addAttributes(
            [QgsField(attribute_name, QtCore.QVariant.String)])
        self.layer.updateFields()

        # add a feature the size of the impact layer bounding box
        feature = QgsFeature()
        fields = provider.fields()
        feature.setFields(fields)
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        feature.setGeometry(QgsGeometry.fromRect(
            QgsRectangle(
                QgsPoint(self.extent[0], self.extent[1]),
                QgsPoint(self.extent[2], self.extent[3]))))
        feature[attribute_name] = self.tr('Entire area')
        provider.addFeatures([feature])
        self.layer.updateExtents()
        try:
            self.update_keywords(
                self.layer,
                {self.get_default_keyword('AGGR_ATTR_KEY'): attribute_name})
        except InvalidParameterError:
            self.write_keywords(
                self.layer,
                {self.get_default_keyword('AGGR_ATTR_KEY'): attribute_name})
        except (UnsupportedProviderError, KeywordDbError), e:
            raise e
        return self.layer

    def _send_message(self, message, dynamic=True):
        """Send a message using the messaging system.


        :param message: A message to display to the user.
        :type message: Message

        :param dynamic: Whether the message should be appended to the message
            queue or replace it.
        :type dynamic: bool

        .. seealso::  https://github.com/AIFDR/inasafe/issues/577

        """

        message_type = STATIC_MESSAGE_SIGNAL
        if dynamic:
            message_type = DYNAMIC_MESSAGE_SIGNAL

        dispatcher.send(
            signal=message_type,
            sender=self,
            message=message)

    def _setup_target_field(self, impact_layer):
        """Set up self.target_field

        :param impact_layer: Layer to be processed.
        :type layer: QgsMapLayer, QgsVectorLayer

        :returns: True if the layer contains the target field,
                  False if any errors occur.
        :rtype: bool

        """
        try:
            self.target_field = self.read_keywords(
                impact_layer, 'target_field')
        except KeywordNotFoundError:
            message = m.Paragraph(
                self.tr(
                    'No "target_field" keyword found in the impact layer %s '
                    'keywords. The impact function should define this.') % (
                        impact_layer.name()))
            LOGGER.debug('Skipping postprocessing due to: %s' % message)
            self.error_message = message
            return False
        target_field_index = impact_layer.fieldNameIndex(
            self.target_field)
        #if a feature has no field called
        if target_field_index == -1:
            message = m.Paragraph(
                self.tr('No attribute "%s" was found in the attribute table '
                        'for layer "%s". The impact function must define this'
                        ' attribute for postprocessing to work.') % (
                            self.target_field, impact_layer.name()))
            LOGGER.debug('Skipping postprocessing due to: %s' % message)
            self.error_message = message
            return False
        return True
