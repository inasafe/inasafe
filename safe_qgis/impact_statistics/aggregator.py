# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Aggregator.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

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
from third_party.odict import OrderedDict
from third_party.pydispatch import dispatcher
from safe_qgis.utilities.clipper import clip_layer
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.utilities import (
    is_polygon_layer,
    layer_attribute_names,
    create_memory_layer,
    breakdown_defaults,
    extent_to_geo_array,
    safe_to_qgis_layer)
from safe_qgis.utilities.styling import set_vector_graduated_style
from safe_qgis.safe_interface import (
    temp_dir,
    safe_read_layer,
    ReadLayerError,
    points_in_and_outside_polygon,
    calculate_polygon_centroid,
    unique_filename,
    messaging as m)
from safe_qgis.safe_interface import (
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    PointsInputError)
from safe_qgis.exceptions import (
    KeywordNotFoundError,
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


class Aggregator(QtCore.QObject):
    """The aggregator class facilitates aggregation of impact function results.
    """

    def __init__(self, iface, aggregation_layer):
        """Director for aggregation based operations.

        :param aggregation_layer: Layer representing clipped aggregation
            areas. This will be converted to a memory layer inside this class.
            see self.layer
        :type aggregation_layer: QgsVectorLayer
        """

        QtCore.QObject.__init__(self)

        self.hazardLayer = None
        self.exposureLayer = None
        self.safeLayer = None

        self.prefix = 'aggr_'
        self.attributes = {}
        self.attributeTitle = None

        #use qgis or inasafe zonal stats
        myFlag = bool(QtCore.QSettings().value('inasafe/useNativeZonalStats',
                                               False))
        self.useNativeZonalStats = myFlag

        self.iface = iface
        self.keywordIO = KeywordIO()
        self.defaults = breakdown_defaults()
        self.errorMessage = None
        self.targetField = None
        self.impactLayerAttributes = []
        self.aoiMode = True

        # If this flag is not True, no aggregation or postprocessing will run
        # this is set as True by validateKeywords()
        self.isValid = False
        self.showIntermediateLayers = False

        # This is used to hold an *in memory copy* of the aggregation layer
        # or None if the clip extents should be used.
        if aggregation_layer is None:
            self.aoiMode = True
            # Will be completed in _prepareLayer just before deintersect call
            self.layer = self._create_polygon_layer()
        else:
            self.aoiMode = False
            self.layer = aggregation_layer

    def validate_keywords(self):
        """Check if the postprocessing layer has all needed attribute keywords.

        This is only applicable in the case where were are not using the AOI
        (in other words self.aoiMode is False). When self.aoiMode is True
        then we always use just the defaults and dont allow the user to
        create custom aggregation field mappings.

        This method is called on instance creation and should always be
        called if you change any state of the aggregator class.

        On completion of this method the self.isValid flag is set. If this
        flag is not True, then no aggregation or postprocessing work will be
        carried out (these methods will raise an InvalidAggregatorError).
        """

        # Otherwise get the attributes for the aggregation layer.
        # noinspection PyBroadException
        try:
            myKeywords = self.keywordIO.read_keywords(self.layer)
        #discussed with Tim,in this case its ok to be generic
        except Exception:  # pylint: disable=W0703
            myKeywords = {}

        if self.aoiMode:
            myKeywords[self.defaults['FEM_RATIO_ATTR_KEY']] = self.tr(
                'Use default')
            self.keywordIO.update_keywords(self.layer, myKeywords)
            self.isValid = True
            return
        else:
            myMessage = m.Message(
                m.Heading(
                    self.tr('Select attribute'), **PROGRESS_UPDATE_STYLE),
                m.Paragraph(self.tr(
                    'Please select which attribute you want to use as ID for '
                    'the aggregated results')))
            self._send_message(myMessage)

            #myKeywords are already complete
            category = myKeywords['category']
            aggregationAttribute = self.defaults['AGGR_ATTR_KEY']
            femaleRatio = self.defaults['FEM_RATIO_ATTR_KEY']
            femaleRatioKey = self.defaults['FEM_RATIO_KEY']
            if ('category' in myKeywords and
                category == 'postprocessing' and
                aggregationAttribute in myKeywords and
                femaleRatio in myKeywords and
                (femaleRatio != self.tr('Use default') or
                 femaleRatioKey in myKeywords)):
                self.isValid = True
            #some keywords are needed
            else:
                #set the default values by writing to the myKeywords
                myKeywords['category'] = 'postprocessing'

                myAttributes, _ = layer_attribute_names(
                    self.layer,
                    [QtCore.QVariant.Int, QtCore.QVariant.String])
                if self.defaults['AGGR_ATTR_KEY'] not in myKeywords:
                    myKeywords[self.defaults['AGGR_ATTR_KEY']] = \
                        myAttributes[0]

                if self.defaults['FEM_RATIO_ATTR_KEY'] not in myKeywords:
                    myKeywords[self.defaults['FEM_RATIO_ATTR_KEY']] = self.tr(
                        'Use default')

                if self.defaults['FEM_RATIO_KEY'] not in myKeywords:
                    myKeywords[self.defaults['FEM_RATIO_KEY']] = \
                        self.defaults['FEM_RATIO']

                self.keywordIO.update_keywords(self.layer, myKeywords)
                self.isValid = False

    def deintersect(self, hazard_layer, exposure_layer):
        """Ensure there are no intersecting features with self.layer.

        This should only happen after initial checks have been made.

        Buildings are not split up by this method.

        :param hazard_layer: A hazard layer.
        :type hazard_layer: QgsMapLayer

        :param exposure_layer: An exposure layer.
        :type exposure_layer: QgsMapLayer

        """

        if not self.isValid:
            raise InvalidAggregatorError

        # These should have already been clipped to analysis extents
        self.hazardLayer = hazard_layer
        self.exposureLayer = exposure_layer
        try:
            self._prepare_layer()
        except (InvalidLayerError, UnsupportedProviderError, KeywordDbError):
            raise

        if not self.aoiMode:
            # This is a safe version of the aggregation layer
            self.safeLayer = safe_read_layer(str(self.layer.source()))

            if is_polygon_layer(self.hazardLayer):
                self.hazardLayer = self._prepare_polygon_layer(
                    self.hazardLayer)

            if is_polygon_layer(self.exposureLayer):
                # Find out the subcategory for this layer
                mySubcategory = self.keywordIO.read_keywords(
                    self.exposureLayer, 'subcategory')
                # We dont want to chop up buildings!
                if mySubcategory != 'structure':
                    self.exposureLayer = self._prepare_polygon_layer(
                        self.exposureLayer)

    def aggregate(self, safe_impact_layer):
        """Do any requested aggregation post processing.

        Performs Aggregation postprocessing step by

            * creating a copy of the dataset clipped by the impact layer
              bounding box
            * stripping all attributes beside the aggregation attribute
            * delegating to the appropriate aggregator for raster and vectors

        :param safe_impact_layer: The layer that will be aggregated.
        :type safe_impact_layer: read_layer

        :raises: ReadLayerError
        """

        if not self.isValid:
            raise InvalidAggregatorError

        myMessage = m.Message(
            m.Heading(self.tr('Aggregating results'), **PROGRESS_UPDATE_STYLE),
            m.Paragraph(self.tr(
                'This may take a little while - we are aggregating the impact'
                ' by %s') % (self.layer.name())))
        self._send_message(myMessage)

        myQGISImpactLayer = safe_to_qgis_layer(safe_impact_layer)
        if not myQGISImpactLayer.isValid():
            myMessage = self.tr('Error when reading %s') % (
                myQGISImpactLayer)
            # noinspection PyExceptionInherit
            raise ReadLayerError(myMessage)

        myAggrName = self.layer.name()
        if self.aoiMode:
            myAggrName = myAggrName.lower()
        myLayerName = str(self.tr('%s aggregated to %s') % (
            myQGISImpactLayer.name(), myAggrName))

        #delete unwanted fields
        myProvider = self.layer.dataProvider()
        myFields = myProvider.fields()

        #mark important attributes as needed
        self._set_persistant_attributes()
        myUnneededAttributes = []

        for i in xrange(myFields.count()):
            if (myFields[i].name() not in
                    self.attributes.values()):
                myUnneededAttributes.append(i)
        LOGGER.debug('Removing this attributes: ' + str(myUnneededAttributes))
        # noinspection PyBroadException
        try:
            myProvider.deleteAttributes(myUnneededAttributes)
        # FIXME (Ole): Disable pylint check for the moment
        # Need to work out what exceptions we will catch here, though.
        except:  # pylint: disable=W0702
            myMessage = self.tr('Could not remove the unneeded fields')
            LOGGER.debug(myMessage)

        self.layer.updateFields()
        del myUnneededAttributes, myProvider, myFields
        self.keywordIO.update_keywords(
            self.layer, {'title': myLayerName})

        self.statisticsType, self.statisticsClasses = (
            self.keywordIO.get_statistics(myQGISImpactLayer))

        #call the correct aggregator
        if myQGISImpactLayer.type() == QgsMapLayer.VectorLayer:
            self._aggregateVectorImpact(myQGISImpactLayer, safe_impact_layer)
        elif myQGISImpactLayer.type() == QgsMapLayer.RasterLayer:
            self._aggregate_raster_impact(myQGISImpactLayer)
        else:
            myMessage = self.tr(
                '%s is %s but it should be either vector or raster') % (
                    myQGISImpactLayer.name(), myQGISImpactLayer.type())
            # noinspection PyExceptionInherit
            raise ReadLayerError(myMessage)

        # show a styled aggregation layer
        if self.showIntermediateLayers:
            if self.statisticsType == 'sum':
                #style layer if we are summing
                myProvider = self.layer.dataProvider()
                myAttr = self._sum_field_name()
                myAttrIndex = myProvider.fieldNameIndex(myAttr)
                myRequest = QgsFeatureRequest()
                myRequest.setFlags(QgsFeatureRequest.NoGeometry)
                myRequest.setSubsetOfAttributes([myAttrIndex])
                myHighestVal = 0

                for myFeature in myProvider.getFeatures(myRequest):
                    myVal = myFeature[myAttrIndex]
                    print "val", myVal
                    if myVal is not None and myVal > myHighestVal:
                        myHighestVal = myVal

                myClasses = []
                myColors = ['#fecc5c', '#fd8d3c', '#f31a1c']
                myStep = int(myHighestVal / len(myColors))
                myCounter = 0
                for myColor in myColors:
                    myMin = myCounter
                    myCounter += myStep
                    myMax = myCounter

                    myClasses.append(
                        {'min': myMin,
                         'max': myMax,
                         'colour': myColor,
                         'transparency': 30,
                         'label': '%s - %s' % (myMin, myMax)})
                    myCounter += 1

                myStyle = {'target_field': myAttr,
                           'style_classes': myClasses}
                set_vector_graduated_style(self.layer, myStyle)
            else:
                #make style of layer pretty much invisible
                myProps = {'style': 'no',
                           'color_border': '0,0,0,127',
                           'width_border': '0.0'
                           }
                # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                mySymbol = QgsFillSymbolV2.createSimple(myProps)
                myRenderer = QgsSingleSymbolRendererV2(mySymbol)
                self.layer.setRendererV2(myRenderer)
                self.layer.saveDefaultStyle()

    def _aggregateVectorImpact(self, impact_layer, safe_impact_layer):
        """Performs Aggregation postprocessing step on vector impact layers.

        :param impact_layer: A raster impact layer.
        :type impact_layer: QgsRasterLayer

        TODO: Marco document this please!

        :param safe_impact_layer:
        :type safe_impact_layer: read_layer

        TODO: Break this function up into smaller functions!

        """
        #TODO (MB) implement line aggregation

        myAggrFieldMap = {}
        myAggrFieldIndex = None

        try:
            self.targetField = self.keywordIO.read_keywords(
                impact_layer, 'target_field')
        except KeywordNotFoundError:
            myMessage = m.Paragraph(
                self.tr(
                    'No "target_field" keyword found in the impact layer %s '
                    'keywords. The impact function should define this.') % (
                        impact_layer.name()))
            LOGGER.debug('Skipping postprocessing due to: %s' % myMessage)
            self.errorMessage = myMessage
            return
        myTargetFieldIndex = impact_layer.fieldNameIndex(
            self.targetField)
        #if a feature has no field called
        if myTargetFieldIndex == -1:
            myMessage = m.Paragraph(
                self.tr('No attribute "%s" was found in the attribute table '
                        'for layer "%s". The impact function must define this'
                        ' attribute for postprocessing to work.') % (
                            self.targetField, impact_layer.name()))
            LOGGER.debug('Skipping postprocessing due to: %s' % myMessage)
            self.errorMessage = myMessage
            return

        # start data retrieval
        myTotal = 0

        myAggregationProvider = self.layer.dataProvider()

        if self.statisticsType == 'class_count':
            #add the class count fields to the layer
            myFields = [QgsField('%s_%s' % (f, self.targetField),
                                 QtCore.QVariant.String) for f in
                        self.statisticsClasses]
            myAggregationProvider.addAttributes(myFields)
            self.layer.updateFields()

            myTmpAggrFieldMap = myAggregationProvider.fieldNameMap()
            for k, v in myTmpAggrFieldMap.iteritems():
                myAggrFieldMap[str(k)] = v

        elif self.statisticsType == 'sum':
            #add the total field to the layer
            myAggrField = self._sum_field_name()
            myAggregationProvider.addAttributes([QgsField(
                myAggrField, QtCore.QVariant.Int)])
            self.layer.updateFields()

            myAggrFieldIndex = self.layer.fieldNameIndex(
                myAggrField)

        myImpactGeoms = safe_impact_layer.get_geometry()
        myImpactValues = safe_impact_layer.get_data()

        if not self.aoiMode:
            myAggregtionUnits = self.safeLayer.get_geometry()

            if (safe_impact_layer.is_point_data or
                    safe_impact_layer.is_polygon_data):
                LOGGER.debug('Doing point in polygon aggregation')

                myRemainingValues = myImpactValues

                if safe_impact_layer.is_polygon_data:
                    # Using centroids to do polygon in polygon aggregation
                    # this is always ok because
                    # deintersect() took care of splitting
                    # polygons that spawn across multiple postprocessing
                    # polygons. After deintersect()
                    # each impact polygon will never be contained by more than
                    # one aggregation polygon

                    # Calculate points for each polygon
                    myCentroids = []
                    for myPolygon in myImpactGeoms:
                        if hasattr(myPolygon, 'outer_ring'):
                            outer_ring = myPolygon.outer_ring
                        else:
                            # Assume it is an array
                            outer_ring = myPolygon
                        c = calculate_polygon_centroid(outer_ring)
                        myCentroids.append(c)
                    myRemainingPoints = myCentroids

                else:
                    #this are already points data
                    myRemainingPoints = myImpactGeoms

                #iterate over the aggregation units
                for myPolygonIndex, myPolygon in enumerate(myAggregtionUnits):
                    if hasattr(myPolygon, 'outer_ring'):
                        outer_ring = myPolygon.outer_ring
                        inner_rings = myPolygon.inner_rings
                    else:
                        # Assume it is an array
                        outer_ring = myPolygon
                        inner_rings = None

                    try:
                        # noinspection PyArgumentEqualDefault
                        inside, outside = points_in_and_outside_polygon(
                            myRemainingPoints,
                            outer_ring,
                            holes=inner_rings,
                            closed=True,
                            check_input=True)
                    except PointsInputError:  # too few points provided
                        inside = []
                        outside = []
                    #self.impactLayerAttributes is a list of list of dict
                    #[
                    #   [{...},{...},{...}],
                    #   [{...},{...},{...}]
                    #]
                    self.impactLayerAttributes.append([])
                    if self.statisticsType == 'class_count':
                        myResults = OrderedDict()
                        for myClass in self.statisticsClasses:
                            myResults[myClass] = 0

                        for i in inside:
                            myKey = myRemainingValues[i][self.targetField]
                            try:
                                myResults[myKey] += 1
                            except KeyError:
                                myError = (
                                    'StatisticsClasses %s does not include '
                                    'the %s class which was found in the '
                                    'data. This is a problem in the %s '
                                    'statistics_classes definition' %
                                    (self.statisticsClasses,
                                    myKey,
                                    self.getFunctionID()))
                                raise KeyError(myError)

                            self.impactLayerAttributes[myPolygonIndex].append(
                                myRemainingValues[i])
                        myAttrs = {}
                        for k, v in myResults.iteritems():
                            myKey = '%s_%s' % (k, self.targetField)
                            #FIXME (MB) remove next line when we get rid of
                            #shape files as internal format
                            myKey = myKey[:10]
                            myAggrFieldIndex = myAggrFieldMap[myKey]
                            myAttrs[myAggrFieldIndex] = v

                    elif self.statisticsType == 'sum':
                        #by default summ attributes
                        myTotal = 0
                        for i in inside:
                            try:
                                myTotal += myRemainingValues[i][
                                    self.targetField]
                            except TypeError:
                                pass

                            #add all attributes to the impactLayerAttributes
                            self.impactLayerAttributes[myPolygonIndex].append(
                                myRemainingValues[i])
                        myAttrs = {myAggrFieldIndex: myTotal}

                    # Add features inside this polygon
                    myFID = myPolygonIndex
                    myAggregationProvider.changeAttributeValues(
                        {myFID: myAttrs})

                    # make outside points the input to the next iteration
                    # this could maybe be done more quickly using directly
                    # numpy arrays like this:
                    # myRemainingPoints = myRemainingPoints[outside]
                    # myRemainingValues =
                    # [myRemainingValues[i] for i in outside]
                    myTmpPoints = []
                    myTmpValues = []
                    for i in outside:
                        myTmpPoints.append(myRemainingPoints[i])
                        myTmpValues.append(myRemainingValues[i])
                    myRemainingPoints = myTmpPoints
                    myRemainingValues = myTmpValues

                    # LOGGER.debug('Before: ' + str(len(myRemainingValues)))
                    # LOGGER.debug('After: ' + str(len(myRemainingValues)))
                    # LOGGER.debug('Inside: ' + str(len(inside)))
                    # LOGGER.debug('Outside: ' + str(len(outside)))

            elif safe_impact_layer.is_line_data:
                LOGGER.debug('Doing line in polygon aggregation')

            else:
                myMessage = m.Paragraph(
                    self.tr(
                        'Aggregation on vector impact layers other than points'
                        ' or polygons not implemented yet not implemented yet.'
                        ' Called on %s') % (impact_layer.name()))
                LOGGER.debug('Skipping postprocessing due to: %s' % myMessage)
                self.errorMessage = myMessage
                self.layer.commitChanges()
                return
        else:
            if self.statisticsType == 'class_count':
                #loop over all features in impact layer
                myResults = OrderedDict()
                for myClass in self.statisticsClasses:
                    myResults[myClass] = 0

                self.impactLayerAttributes.append([])
                for myImpactValueList in myImpactValues:
                    myKey = myImpactValueList[self.targetField]
                    try:
                        myResults[myKey] += 1
                    except KeyError:
                        myError = (
                            'StatisticsClasses %s does not include the %s '
                            'class which was found in the data. This is a '
                            'problem in the %s statistics_classes definition' %
                            (self.statisticsClasses,
                             myKey,
                             self.getFunctionID()))
                        raise KeyError(myError)

                    self.impactLayerAttributes[0].append(myImpactValueList)

                myAttrs = {}
                for k, v in myResults.iteritems():
                    myKey = '%s_%s' % (k, self.targetField)
                    #FIXME (MB) remove next line when we get rid of
                    #shape files as internal format
                    myKey = myKey[:10]
                    myAggrFieldIndex = myAggrFieldMap[myKey]
                    myAttrs[myAggrFieldIndex] = v

            elif self.statisticsType == 'sum':
                #loop over all features in impact layer
                self.impactLayerAttributes.append([])
                for myImpactValueList in myImpactValues:
                    if myImpactValueList[self.targetField] == 'None':
                        myImpactValueList[self.targetField] = None
                    try:
                        myTotal += myImpactValueList[self.targetField]
                    except TypeError:
                        pass
                    self.impactLayerAttributes[0].append(myImpactValueList)
                myAttrs = {myAggrFieldIndex: myTotal}

            #apply to all area feature
            myFID = 0
            myAggregationProvider.changeAttributeValues({myFID: myAttrs})

        self.layer.commitChanges()
        return

    def _aggregate_raster_impact(self, impact_layer):
        """Aggregate on a raster impact layer by using zonal statistics.

        :param impact_layer: A raster impact layer.
        :type impact_layer: QgsRasterLayer
        """
        if self.useNativeZonalStats:
            myZonalStatistics = QgsZonalStatistics(
                self.layer,
                impact_layer.dataProvider().dataSourceUri(),
                self.prefix)
            myProgressDialog = QtGui.QProgressDialog(
                self.tr('Calculating zonal statistics'),
                self.tr('Abort...'),
                0,
                0)
            startTime = time.clock()
            myZonalStatistics.calculateStatistics(myProgressDialog)
            if myProgressDialog.wasCanceled():
                QtGui.QMessageBox.error(
                    self, self.tr('ZonalStats: Error'),
                    self.tr('You aborted aggregation, '
                            'so there are no data for analysis. Exiting...'))
            cppDuration = time.clock() - startTime
            LOGGER.debug('Native zonal stats duration: %ss' % cppDuration)
        else:
            # new way
            # myZonalStatistics = {
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
            startTime = time.clock()
            myZonalStatistics = calculate_zonal_stats(impact_layer, self.layer)
            pyDuration = time.clock() - startTime
            LOGGER.debug('Python zonal stats duration: %ss' % pyDuration)

            myProvider = self.layer.dataProvider()

            # add fields for stats to aggregation layer
            # { 1: {'sum': 10, 'count': 20, 'min': 1, 'max': 4, 'mean': 2},
            #             QgsField(self._minFieldName(),
            #                      QtCore.QVariant.Double),
            #             QgsField(self._maxFieldName(),
            #                      QtCore.QVariant.Double)]
            myFields = [QgsField(self._count_field_name(),
                                 QtCore.QVariant.Double),
                        QgsField(self._sum_field_name(),
                                 QtCore.QVariant.Double),
                        QgsField(self._mean_field_name(),
                                 QtCore.QVariant.Double)
                        ]
            myProvider.addAttributes(myFields)
            self.layer.updateFields()

            sumIndex = myProvider.fieldNameIndex(self._sum_field_name())
            countIndex = myProvider.fieldNameIndex(self._count_field_name())
            meanIndex = myProvider.fieldNameIndex(self._mean_field_name())
            # minIndex = myProvider.fieldNameIndex(self._minFieldName())
            # maxIndex = myProvider.fieldNameIndex(self._maxFieldName())

            for myFeature in myProvider.getFeatures():
                myFid = myFeature.id()
                if myFid not in myZonalStatistics:
                    # Blindly ignoring - @mbernasocchi can you review? TS
                    continue
                myStats = myZonalStatistics[myFid]
                #          minIndex: myStats['min'],
                #          maxIndex: myStats['max']}
                attrs = {sumIndex: myStats['sum'],
                         countIndex: myStats['count'],
                         meanIndex: myStats['mean']
                         }
                myProvider.changeAttributeValues({myFid: attrs})

    def _prepare_layer(self):
        """Prepare the aggregation layer to match analysis extents.

        :raises: InvalidLayerError, UnsupportedProviderError, KeywordDbError
        """
        myMessage = m.Message(
            m.Heading(
                self.tr('Preparing aggregation layer'),
                **PROGRESS_UPDATE_STYLE),
            m.Paragraph(self.tr(
                'We are clipping the aggregation layer to match the '
                'intersection of the hazard and exposure layer extents.')))
        self._send_message(myMessage)

        # This is used to hold an *in memory copy* of the aggregation layer
        # or a in memory layer with the clip extents as a feature.
        if self.aoiMode:
            try:
                self.layer = self._extents_to_layer()
            except (InvalidLayerError,
                    UnsupportedProviderError,
                    KeywordDbError):
                raise
        # Area Of Interest (AOI) mode flag is False
        else:
            # we use only the exposure extent, because both exposure and hazard
            # have the same extent at this point.
            myGeoExtent = extent_to_geo_array(
                self.exposureLayer.extent(),
                self.exposureLayer.crs())

            myAggrAttribute = self.keywordIO.read_keywords(
                self.layer, self.defaults['AGGR_ATTR_KEY'])

            myClippedLayer = clip_layer(
                layer=self.layer,
                extent=myGeoExtent,
                explode_flag=True,
                explode_attribute=myAggrAttribute)

            myName = '%s %s' % (self.layer.name(), self.tr('aggregation'))
            self.layer = myClippedLayer
            self.layer.setLayerName(myName)
            if self.showIntermediateLayers:
                self.keywordIO.update_keywords(self.layer, {'title': myName})
                QgsMapLayerRegistry.instance().addMapLayer(self.layer)

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

    def _sum_field_name(self):
        """Field name for the sum column."""
        return (self.prefix + 'sum')[:10]

    # noinspection PyDictCreation
    def _set_persistant_attributes(self):
        """Mark any attributes that should remain in the self.layer table."""
        self.attributes = {}
        self.attributes[self.defaults[
            'AGGR_ATTR_KEY']] = (
                self.keywordIO.read_keywords(
                    self.layer,
                    self.defaults['AGGR_ATTR_KEY']))

        myFemaleRatioKey = self.defaults['FEM_RATIO_ATTR_KEY']
        myFemRatioAttr = self.keywordIO.read_keywords(
            self.layer,
            myFemaleRatioKey)
        if ((myFemRatioAttr != self.tr('Don\'t use')) and
                (myFemRatioAttr != self.tr('Use default'))):
            self.attributes[myFemaleRatioKey] = \
                myFemRatioAttr

    def _prepare_polygon_layer(self, layer):
        """Create a new layer with no intersecting features to self.layer.

        A helper function to align the polygons to the postprocLayer
        polygons. If one input polygon is in two or more postprocLayer polygons
        then it is divided so that each part is within only one of the
        postprocLayer polygons. this allows to aggregate in postprocessing
        using centroid in polygon.

        The function assumes EPSG:4326 but no checks are enforced

        :param layer: Layer to be processed.
        :type layer: QgsMapLayer, QgsVectorLayer

        :returns: A processed layer.
        :rtype: QgsMapLayer
        """
#        import time
#        startTime = time.clock()

        myMessage = m.Message(
            m.Heading(
                self.tr('Preclipping input data...'), **PROGRESS_UPDATE_STYLE),
            m.Paragraph(self.tr(
                'Modifying %s to avoid intersections with the aggregation '
                'layer'
            ) % (layer.name())))
        self._send_message(myMessage)

        theLayerFilename = str(layer.source())
        myPostprocPolygons = self.safeLayer.get_geometry()
        myPolygonsLayer = safe_read_layer(theLayerFilename)
        myRemainingPolygons = numpy.array(myPolygonsLayer.get_geometry(),
                                          dtype=list)
#        myRemainingAttributes = numpy.array(myPolygonsLayer.get_data())
        myRemainingIndexes = numpy.array(range(len(myRemainingPolygons)))

        #used for unit tests only
        self.preprocessedFeatureCount = 0

        # FIXME (MB) the intersecting array is used only for debugging and
        # could be safely removed
        myIntersectingPolygons = []
        myInsidePolygons = []

        # FIXME (MB) maybe do raw geos without qgis
        #select all postproc polygons with no attributes
        aggregationProvider = self.layer.dataProvider()
        aggregationRequest = QgsFeatureRequest()
        aggregationRequest.setSubsetOfAttributes([])

        # copy polygons to a memory layer
        myQgisMemoryLayer = create_memory_layer(layer)

        polygonsProvider = myQgisMemoryLayer.dataProvider()
        polygonsRequest = QgsFeatureRequest()
        myQgisFeat = QgsFeature()
        myInsideFeat = QgsFeature()
        fields = polygonsProvider.fields()
        myTempdir = temp_dir(sub_dir='preprocess')
        myOutFilename = unique_filename(
            suffix='.shp', dir=myTempdir)

        self.keywordIO.copy_keywords(layer, myOutFilename)
        mySHPWriter = QgsVectorFileWriter(myOutFilename,
                                          'UTF-8',
                                          fields,
                                          polygonsProvider.geometryType(),
                                          polygonsProvider.crs())
        if mySHPWriter.hasError():
            raise InvalidParameterError(mySHPWriter.errorMessage())
        # end FIXME

        for (myPostprocPolygonIndex,
             myPostprocPolygon) in enumerate(myPostprocPolygons):
            LOGGER.debug('PostprocPolygon %s' % myPostprocPolygonIndex)
            myPolygonsCount = len(myRemainingPolygons)
            aggregationRequest.setFilterFid(myPostprocPolygonIndex)
            myQgisPostprocPoly = aggregationProvider.getFeatures(
                aggregationRequest).next()
            myQgisPostprocGeom = QgsGeometry(myQgisPostprocPoly.geometry())

            # myPostprocPolygon bounding box values
            A = numpy.array(myPostprocPolygon)
            minx = miny = sys.maxint
            maxx = maxy = -minx
            myPostprocPolygonMinx = min(minx, min(A[:, 0]))
            myPostprocPolygonMaxx = max(maxx, max(A[:, 0]))
            myPostprocPolygonMiny = min(miny, min(A[:, 1]))
            myPostprocPolygonMaxy = max(maxy, max(A[:, 1]))

            # create an array full of False to store if a BB vertex is inside
            # or outside the myPostprocPolygon
            myAreVerticesInside = numpy.zeros(myPolygonsCount * 4,
                                              dtype=numpy.bool)

            # Create Nx2 vector of vertices of bounding boxes
            myBBVertices = []
            # Compute bounding box for each geometry type
            for myPoly in myRemainingPolygons:
                minx = miny = sys.maxint
                maxx = maxy = -minx
                # Do outer ring only as the BB is outside anyway
                A = numpy.array(myPoly)
                minx = min(minx, numpy.min(A[:, 0]))
                maxx = max(maxx, numpy.max(A[:, 0]))
                miny = min(miny, numpy.min(A[:, 1]))
                maxy = max(maxy, numpy.max(A[:, 1]))
                myBBVertices.extend([(minx, miny),
                                    (minx, maxy),
                                    (maxx, maxy),
                                    (maxx, miny)])

            # see if BB vertices are in myPostprocPolygon
            myBBVertices = numpy.array(myBBVertices)
            inside, _ = points_in_and_outside_polygon(myBBVertices,
                                                      myPostprocPolygon)
            # make True if the vertex was in myPostprocPolygon
            myAreVerticesInside[inside] = True

            # myNextIterPolygons has the 0:count indexes
            # myOutsidePolygons has the mapped to original indexes
            # and is overwritten at every iteration because we care only of
            # the outside polygons remaining after the last iteration
            myNextIterPolygons = []
            myOutsidePolygons = []

            for i in range(myPolygonsCount):
                k = i * 4
                myMappedIndex = myRemainingIndexes[i]
                # memory layers counting starts at 1 instead of 0 as in our
                # indexes
                myFeatId = myMappedIndex + 1
                doIntersection = False
                # sum the isInside bool for each of the bounding box vertices
                # of each polygon. for example True + True + False + True is 3
                myPolygonLocation = numpy.sum(myAreVerticesInside[k:k + 4])

                if myPolygonLocation == 4:
                    # all vertices are inside -> polygon is inside
                    # ignore this polygon from further analysis
                    myInsidePolygons.append(myMappedIndex)
                    polygonsRequest.setFilterFid(myFeatId)
                    myQgisFeat = polygonsProvider.getFeatures(
                        polygonsRequest).next()
                    mySHPWriter.addFeature(myQgisFeat)
                    self.preprocessedFeatureCount += 1
#                    LOGGER.debug('Polygon %s is fully inside' %myMappedIndex)
#                    tmpWriter.addFeature(myQgisFeat)

                elif myPolygonLocation == 0:
                    # all vertices are outside
                    # check if the polygon BB is completely outside of the
                    # myPostprocPolygon BB.
                    myPolyMinx = numpy.min(myBBVertices[k:k + 4, 0])
                    myPolyMaxx = numpy.max(myBBVertices[k:k + 4, 0])
                    myPolyMiny = numpy.min(myBBVertices[k:k + 4, 1])
                    myPolyMaxy = numpy.max(myBBVertices[k:k + 4, 1])

                    # check if myPoly is all E,W,N,S of myPostprocPolygon
                    if ((myPolyMinx > myPostprocPolygonMaxx) or
                            (myPolyMaxx < myPostprocPolygonMinx) or
                            (myPolyMiny > myPostprocPolygonMaxy) or
                            (myPolyMaxy < myPostprocPolygonMiny)):
                        # polygon is surely outside
                        myOutsidePolygons.append(myMappedIndex)
                        # we need this polygon in the next iteration
                        myNextIterPolygons.append(i)
                    else:
                        # polygon might be outside or intersecting. consider
                        # it intersecting so it goes into further analysis
                        doIntersection = True
                else:
                    # some vertices are outside some inside -> polygon is
                    # intersecting
                    doIntersection = True

                # intersect using qgis
                if doIntersection:
#                    LOGGER.debug('Intersecting polygon %s' % myMappedIndex)
                    myIntersectingPolygons.append(myMappedIndex)

                    polygonsRequest.setFilterFid(myFeatId)
                    try:
                        myQgisFeat = polygonsProvider.getFeatures(
                            polygonsRequest).next()
                    except StopIteration:
                        LOGGER.debug('Couldn\'t fetch feature: %s' % myFeatId)
                        LOGGER.debug([str(error) for error in
                                      polygonsProvider.errors()])

                    myQgisPolyGeom = QgsGeometry(myQgisFeat.geometry())
                    myAtMap = myQgisFeat.attributes()
#                    for (k, attr) in myAtMap.iteritems():
#                        LOGGER.debug( "%d: %s" % (k, attr.toString()))

                    # make intersection of the myQgisFeat and the postprocPoly
                    # write the inside part to a shp file and the outside part
                    # back to the original QGIS layer
                    try:
                        myIntersec = myQgisPostprocGeom.intersection(
                            myQgisPolyGeom)
#                        if myIntersec is not None:
                        myIntersecGeom = QgsGeometry(myIntersec)

                        #from ftools
                        myUnknownGeomType = 0
                        if myIntersecGeom.wkbType() == myUnknownGeomType:
                            int_com = myQgisPostprocGeom.combine(
                                myQgisPolyGeom)
                            int_sym = myQgisPostprocGeom.symDifference(
                                myQgisPolyGeom)
                            myIntersecGeom = QgsGeometry(
                                int_com.difference(int_sym))
#                        LOGGER.debug('wkbType type of intersection: %s' %
# myIntersecGeom.wkbType())
                        polygonTypesList = [QGis.WKBPolygon,
                                            QGis.WKBMultiPolygon]
                        if myIntersecGeom.wkbType() in polygonTypesList:
                            myInsideFeat.setGeometry(myIntersecGeom)
                            myInsideFeat.setAttributes(myAtMap)
                            mySHPWriter.addFeature(myInsideFeat)
                            self.preprocessedFeatureCount += 1
                        else:
                            pass
#                            LOGGER.debug('Intersection not a polygon so '
#                                         'the two polygons either touch '
#                                         'only or do not intersect. Not '
#                                         'adding this to the inside list')
                        # Part of the polygon that is outside the postprocpoly
                        myOutside = myQgisPolyGeom.difference(myIntersecGeom)
#                        if myOutside is not None:
                        myOutsideGeom = QgsGeometry(myOutside)

                        if myOutsideGeom.wkbType() in polygonTypesList:
                            # modifiy the original geometry to the part
                            # outside of the postproc polygon
                            polygonsProvider.changeGeometryValues(
                                {myFeatId: myOutsideGeom})
                            # we need this polygon in the next iteration
                            myOutsidePolygons.append(myMappedIndex)
                            myNextIterPolygons.append(i)

                    except TypeError:
                        LOGGER.debug('ERROR with FID %s', myMappedIndex)

#            LOGGER.debug('Inside %s' % myInsidePolygons)
#            LOGGER.debug('Outside %s' % myOutsidePolygons)
#            LOGGER.debug('Intersec %s' % myIntersectingPolygons)
            if len(myNextIterPolygons) > 0:
                # some polygons are still completely outside of the
                # postprocPoly so go on and reiterate using only these
                nextIterPolygonsIndex = numpy.array(myNextIterPolygons)

                myRemainingPolygons = myRemainingPolygons[
                    nextIterPolygonsIndex]
#                myRemainingAttributes = myRemainingAttributes[
#                                        nextIterPolygonsIndex]
                myRemainingIndexes = myRemainingIndexes[nextIterPolygonsIndex]
                LOGGER.debug('Remaining: %s' % len(myRemainingPolygons))
            else:
                print 'no more polygons to be checked'
                break
#            del tmpWriter

        # here the full polygon set is represented by:
        # myInsidePolygons + myIntersectingPolygons + myNextIterPolygons
        # the a polygon intersecting multiple postproc polygons appears
        # multiple times in the array
        # noinspection PyUnboundLocalVariable
        LOGGER.debug('Results:\nInside: %s\nIntersect: %s\nOutside: %s' % (
            myInsidePolygons, myIntersectingPolygons, myOutsidePolygons))

        # add in- and outside polygons
        for i in myOutsidePolygons:
            myFeatId = i + 1
            polygonsRequest.setFilterFid(myFeatId)
            myQgisFeat = polygonsProvider.getFeatures(polygonsRequest).next()
            mySHPWriter.addFeature(myQgisFeat)
            self.preprocessedFeatureCount += 1

        del mySHPWriter
#        LOGGER.debug('Created: %s' % self.preprocessedFeatureCount)

        myName = '%s %s' % (layer.name(), self.tr('preprocessed'))
        myOutLayer = QgsVectorLayer(myOutFilename, myName, 'ogr')
        if not myOutLayer.isValid():
            #TODO (MB) use a better exception
            raise Exception('Invalid qgis Layer')

        if self.showIntermediateLayers:
            self.keywordIO.update_keywords(myOutLayer, {'title': myName})
            QgsMapLayerRegistry.instance().addMapLayer(myOutLayer)

        return myOutLayer

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

        myTempdir = temp_dir(sub_dir='preprocess')
        myOutFilename = unique_filename(suffix='.shp',
                                        dir=myTempdir)
        mySHPWriter = QgsVectorFileWriter(myOutFilename,
                                          'UTF-8',
                                          fields,
                                          QGis.WKBPolygon,
                                          crs)
        # flush the writer to write to file
        del mySHPWriter
        myName = self.tr('Entire area')
        myLayer = QgsVectorLayer(myOutFilename, myName, 'ogr')
        LOGGER.debug('created' + myLayer.name())
        return myLayer

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

        # Note: this code duplicates from Dock.viewportGeoArray - make DRY. TS

        myRect = self.iface.mapCanvas().extent()
        myCrs = QgsCoordinateReferenceSystem()
        myCrs.createFromSrid(4326)
        myGeoExtent = extent_to_geo_array(myRect, myCrs)

        if not self.layer.isValid():
            myMessage = self.tr(
                'An exception occurred when creating the entire area layer.')
            raise (InvalidLayerError(myMessage))

        myProvider = self.layer.dataProvider()

        myAttrName = self.tr('Area')
        myProvider.addAttributes(
            [QgsField(myAttrName, QtCore.QVariant.String)])
        self.layer.updateFields()

        # add a feature the size of the impact layer bounding box
        myFeature = QgsFeature()
        myFields = myProvider.fields()
        myFeature.setFields(myFields)
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        myFeature.setGeometry(QgsGeometry.fromRect(
            QgsRectangle(
                QgsPoint(myGeoExtent[0], myGeoExtent[1]),
                QgsPoint(myGeoExtent[2], myGeoExtent[3]))))
        myFeature[myAttrName] = self.tr('Entire area')
        myProvider.addFeatures([myFeature])

        try:
            self.keywordIO.update_keywords(
                self.layer,
                {self.defaults['AGGR_ATTR_KEY']: myAttrName})
        except InvalidParameterError:
            self.keywordIO.write_keywords(
                self.layer,
                {self.defaults['AGGR_ATTR_KEY']: myAttrName})
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

        myType = STATIC_MESSAGE_SIGNAL
        if dynamic:
            myType = DYNAMIC_MESSAGE_SIGNAL

        dispatcher.send(
            signal=myType,
            sender=self,
            message=message)
