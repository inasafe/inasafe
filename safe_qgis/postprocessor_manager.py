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

import numpy
import sys
import logging
import uuid

from PyQt4 import QtGui, QtCore

from qgis.core import (
    QgsMapLayer,
    QgsGeometry,
    QgsMapLayerRegistry,
    QgsFeature,
    QgsRectangle,
    QgsField,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QGis,
    QgsSingleSymbolRendererV2,
    QgsFillSymbolV2,
    QgsCoordinateReferenceSystem)
from qgis.analysis import QgsZonalStatistics
from safe_qgis.clipper import clipLayer
from safe_qgis.keyword_io import KeywordIO
from safe_qgis.utilities import (
    getExceptionWithStacktrace,
    isPolygonLayer,
    getLayerAttributeNames,
    setVectorCategorizedStyle,
    copyInMemory,
    getDefaults,
    extentToGeoArray,
    safeToQGISLayer)
from safe_qgis.safe_interface import (
    safeTr,
    temp_dir,
    safe_read_layer,
    ReadLayerError,
    points_in_and_outside_polygon,
    calculate_polygon_centroid,
    unique_filename,
    get_postprocessors,
    get_postprocessor_human_name)
from safe_qgis.exceptions import (
    KeywordNotFoundError,
    InvalidParameterError,
    KeywordDbError,
    InvalidAggregatorError)

from third_party.odict import OrderedDict


LOGGER = logging.getLogger('InaSAFE')
#from pydev import pydevd


class PostprocessorManager(QtCore.QObject):
    """A manager for post processing of impact function results.
    """

    def __init__(
            self,
            iface,
            theAggregationLayer):
        """Director for aggregation based operations.
        Args:
          theAggregationLayer: QgsMapLayer representing clipped
              aggregation. This will be converted to a memory layer inside
              this class. see self.layer
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """

        super(Aggregator, self).__init__()

        # This is used to hold an *in memory copy* of the aggregation layer
        # or None if the clip extents should be used.
        if theAggregationLayer is None:
            self.aoiMode = True
            # Will be set in _prepareLayer just before deintersect call
            self.layer = None
        else:
            self.aoiMode = False
            self.layer = theAggregationLayer

        self.hazardLayer = None
        self.exposureLayer = None
        self.safeLayer = None

        # Aggregation / post processing related items
        self.postProcessingOutput = {}
        self.prefix = 'aggr_'
        self.defaults = None
        self.attributes = {}
        self.attributeTitle = None

        self.iface = iface
        # An impact_calculator instance
        self.runner = None
        self.keywordIO = KeywordIO()
        self.defaults = getDefaults()
        self.postProcessingOutput = {}
        self.errorMessage = None
        self.targetField = None
        self.impactLayerAttributes = []

        # If this flag is not True, no aggregation or postprocessing will run
        self.isValid = False
        self.validateKeywords()

    def _sumFieldName(self):
        return self.prefix + 'sum'

    def getOutput(self, theSingleTableFlag=False):
        """Returns the results of the post processing as a table.

        Args:
            theSingleTableFlag - bool indicating if result should be rendered
                as a single table. Default False.

        Returns: str - a string containing the html in the requested format.
        """

#        LOGGER.debug(self.postProcessingOutput)
        if self.errorMessage is not None:
            myHTML = (
                '<table class="table table-striped condensed">'
                '    <tr>'
                '       <td>'
                '         <strong>'
                + self.tr('Postprocessing report skipped') +
                '         </strong>'
                '       </td>'
                '    </tr>'
                '    <tr>'
                '       <td>' +
                self.tr(
                    'Due to a problem while processing the results,'
                    ' the detailed postprocessing report is unavailable:'
                    ' %1').arg(self.errorMessage)
                +
                '       </td>'
                '    </tr>'
                '</table>')
            return myHTML

        if theSingleTableFlag:
            #FIXME, return a parsed HTML
            return str(self.postProcessingOutput)
        else:
            return self.generateTables()

    def generateTables(self):
        """Parses the postprocessing output as one table per postprocessor.

        Args:
            None

        Returns:
            str - a string containing the html
        """

        myHTML = ''
        for proc, resList in self.postProcessingOutput.iteritems():
            #sorting using the first indicator of a postprocessor
            try:
                myFirstKey = resList[0][1].keyAt(0)
            # [1]['Total']['value']
            # resList is for example:
            # [
            #    (PyQt4.QtCore.QString(u'Entire area'), OrderedDict([
            #        (u'Total', {'value': 977536, 'metadata': {}}),
            #        (u'Female population', {'value': 508319, 'metadata': {}}),
            #        (u'Weekly hygiene packs', {'value': 403453, 'metadata': {
            #         'description': 'Females hygiene packs for weekly use'}})
            #    ]))
            #]
                myEndOfList = -1
                # return -1 if the postprocessor returns NO_DATA to put at
                # the end of the list
                # d[1] is the orderedDict
                # d[1][myFirstKey] is the 1st indicator in the orderedDict
                resList = sorted(
                    resList,
                    key=lambda d: (
                        myEndOfList if (d[1][myFirstKey]['value'] ==
                                        self.defaults['NO_DATA'])
                        else d[1][myFirstKey]['value']),
                    reverse=True)
            except KeyError:
                LOGGER.debug('Skipping sorting as the postprocessor did not '
                             'have a "Total" field')
            myHTML += ('<table class="table table-striped condensed">'
                       '  <tbody>'
                       '    <tr>'
                       '       <td colspan="100%">'
                       '         <strong>'
                       +
                       self.tr('Detailed %1 report').arg(
                           safeTr(get_postprocessor_human_name(proc)).lower())
                       +
                       '         </strong>'
                       '       </td>'
                       '    </tr>'
                       '    <tr>'
                       '      <th width="25%">'
                       + str(self.attributeTitle).capitalize() +
                       '      </th>')
            # add th according to the ammount of calculation done by each
            # postprocessor
            for calculationName in resList[0][1]:
                myHTML += ('      <th>'
                           + self.tr(calculationName) +
                           '      </th>')
                #close header row
            myHTML += '    </tr>'
            for zoneName, calc in resList:
                myHTML += '    <tr><td>' + zoneName + '</td> '
                for calculationName, calculationData in calc.iteritems():
                    myHTML += ('      <td>'
                               + str(calculationData['value']) +
                               '      </td>')
                    #close header row
                myHTML += '    </tr>'

            #close table
            myHTML += '</tbody></table>'

        return myHTML

    def run(self):
        """Run any post processors requested by the impact function.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        try:
            myRequestedPostProcessors = self.functionParams['postprocessors']
            myPostProcessors = get_postprocessors(myRequestedPostProcessors)
        except (TypeError, KeyError):
            # TypeError is for when functionParams is none
            # KeyError is for when ['postprocessors'] is unavailable
            myPostProcessors = {}
        LOGGER.debug('Running this postprocessors: ' + str(myPostProcessors))

        myFeatureNameAttribute = self.attributes[
            self.defaults['AGGR_ATTR_KEY']]
        if myFeatureNameAttribute is None:
            self.attributeTitle = self.tr('Aggregation unit')
        else:
            self.attributeTitle = myFeatureNameAttribute

        myNameFieldIndex = self.layer.fieldNameIndex(
            myFeatureNameAttribute)
        mySumFieldIndex = self.layer.fieldNameIndex(
            self._sumFieldName())

        myFemaleRatioIsVariable = False
        myFemRatioFieldIndex = None
        myFemaleRatio = None

        if 'Gender' in myPostProcessors:
            #look if we need to look for a variable female ratio in a layer
            try:
                myFemRatioField = self.attributes[
                    self.defaults['FEM_RATIO_ATTR_KEY']]
                myFemRatioFieldIndex = self.layer.fieldNameIndex(
                    myFemRatioField)
                myFemaleRatioIsVariable = True

            except KeyError:
                myFemaleRatio = self.keywordIO.readKeywords(
                    self.layer,
                    self.defaults['FEM_RATIO_KEY'])

        #iterate zone features
        myProvider = self.layer.dataProvider()
        myAttributes = myProvider.attributeIndexes()
        # start data retreival: fetch no geometry and all attributes for each
        # feature
        myProvider.select(myAttributes, QgsRectangle(), False)
        myFeature = QgsFeature()
        myPolygonIndex = 0
        while myProvider.nextFeature(myFeature):
            #get all attributes of a feature
            myAttributeMap = myFeature.attributeMap()

            #if a feature has no field called
            if myNameFieldIndex == -1:
                myZoneName = str(myFeature.id())
            else:
                myZoneName = myAttributeMap[myNameFieldIndex].toString()

            #create dictionary of attributes to pass to postprocessor
            myGeneralParams = {'target_field': self.targetField}

            if self.statisticsType == 'class_count':
                myGeneralParams['impact_classes'] = self.statisticsClasses
            elif self.statisticsType == 'sum':
                myImpactTotal, _ = myAttributeMap[mySumFieldIndex].toDouble()
                myGeneralParams['impact_total'] = myImpactTotal

            try:
                myGeneralParams['impact_attrs'] = (
                    self.impactLayerAttributes[myPolygonIndex])
            except IndexError:
                #rasters and attributeless vectors have no attributes
                myGeneralParams['impact_attrs'] = None

            for myKey, myValue in myPostProcessors.iteritems():
                myParameters = myGeneralParams
                try:
                    #look if params are available for this postprocessor
                    myParameters.update(
                        self.functionParams['postprocessors'][myKey]['params'])
                except KeyError:
                    pass

                if myKey == 'Gender':
                    if myFemaleRatioIsVariable:
                        myFemaleRatio, mySuccessFlag = myAttributeMap[
                            myFemRatioFieldIndex].toDouble()
                        if not mySuccessFlag:
                            myFemaleRatio = self.defaults['FEM_RATIO']
                        LOGGER.debug(mySuccessFlag)
                    myParameters['female_ratio'] = myFemaleRatio

                myValue.setup(myParameters)
                myValue.process()
                myResults = myValue.results()
                myValue.clear()
#                LOGGER.debug(myResults)
                try:
                    self.postProcessingOutput[myKey].append(
                        (myZoneName, myResults))
                except KeyError:
                    self.postProcessingOutput[myKey] = []
                    self.postProcessingOutput[myKey].append(
                        (myZoneName, myResults))
            #increment the index
            myPolygonIndex += 1

