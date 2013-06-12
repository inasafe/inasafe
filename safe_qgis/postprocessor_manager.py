"""
InaSAFE Disaster risk assessment tool by AusAid - **Postprocessor Manager**

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

import logging

from PyQt4 import QtCore

from qgis.core import (
    QgsFeature,
    QgsRectangle)

from safe_qgis.keyword_io import KeywordIO
from safe_qgis.safe_interface import (
    safeTr,
    get_postprocessors,
    get_postprocessor_human_name,
    messaging as m)
from safe_qgis.exceptions import KeywordNotFoundError

LOGGER = logging.getLogger('InaSAFE')
#from pydev import pydevd


class PostprocessorManager(QtCore.QObject):
    """A manager for post processing of impact function results.
    """

    def __init__(
            self,
            theAggregator):
        """Director for aggregation based operations.
        Args:
          theAggregationLayer: QgsMapLayer representing clipped
              aggregation. This will be converted to a memory layer inside
              this class. see self.aggregator.layer
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """

        super(PostprocessorManager, self).__init__()

        # Aggregation / post processing related items
        self.postProcessingOutput = {}
        self.keywordIO = KeywordIO()
        self.errorMessage = None

        self.aggregator = theAggregator

    def _sumFieldName(self):
        return self.aggregator.prefix + 'sum'

    def _isNoData(self, data):
        """Check if the value field of the postprocessor is NO_DATA.

        this is used for sorting, it returns -1 if the value is NO_DATA, so
        that no data items can be put at the end of a list

        Args:
            list - data

        Returns:
            returns -1 if the value is NO_DATA else the value
        """
        #black magic to get the value of each postprocessor field
        #get the first postprocessor just to discover the data structure
        myFirsPostprocessor = self.postProcessingOutput.itervalues().next()
        #get the key position of the value field
        myValueKey = myFirsPostprocessor[0][1].keyAt(0)

        #get the value
        # data[1] is the orderedDict
        # data[1][myFirstKey] is the 1st indicator in the orderedDict
        if data[1][myValueKey]['value'] == self.aggregator.defaults['NO_DATA']:
            myPosition = -1
        else:
            myPosition = data[1][myValueKey]['value']
            #FIXME MB this is to dehumanize the strings and have ints
            myPosition = myPosition.replace(',', '')
            myPosition = int(float(myPosition))

        return myPosition

    def _generateTables(self):
        """Parses the postprocessing output as one table per postprocessor.

        Args:
            None

        Returns:
            str - a string containing the html
        """
        myMessage = m.Message()

        for proc, resList in self.postProcessingOutput.iteritems():
            # resList is for example:
            # [
            #    (PyQt4.QtCore.QString(u'Entire area'), OrderedDict([
            #        (u'Total', {'value': 977536, 'metadata': {}}),
            #        (u'Female population', {'value': 508319, 'metadata': {}}),
            #        (u'Weekly hygiene packs', {'value': 403453, 'metadata': {
            #         'description': 'Females hygiene packs for weekly use'}})
            #    ]))
            #]
            try:
                #sorting using the first indicator of a postprocessor
                sortedResList = sorted(
                    resList,
                    key=self._isNoData,
                    reverse=True)

            except KeyError:
                LOGGER.debug('Skipping sorting as the postprocessor did not '
                             'have a "Total" field')

            #init table
            myTable = m.Table(
                style_class='table table-condensed table-striped')
            myTable.caption = self.tr('Detailed %1 report').arg(safeTr(
                get_postprocessor_human_name(proc)).lower())

            myHeaderRow = m.Row()
            myHeaderRow.add(str(self.attributeTitle).capitalize())
            for calculationName in sortedResList[0][1]:
                myHeaderRow.add(self.tr(calculationName))
            myTable.add(myHeaderRow)

            for zoneName, calc in sortedResList:
                myRow = m.Row(zoneName)

                for _, calculationData in calc.iteritems():
                    myRow.add(calculationData['value'])
                myTable.add(myRow)

            #add table to message
            myMessage.add(myTable)

        return myMessage

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

        myFeatureNameAttribute = self.aggregator.attributes[
            self.aggregator.defaults['AGGR_ATTR_KEY']]
        if myFeatureNameAttribute is None:
            self.attributeTitle = self.tr('Aggregation unit')
        else:
            self.attributeTitle = myFeatureNameAttribute

        myNameFieldIndex = self.aggregator.layer.fieldNameIndex(
            self.attributeTitle)
        mySumFieldIndex = self.aggregator.layer.fieldNameIndex(
            self._sumFieldName())

        myFemaleRatioIsVariable = False
        myFemRatioFieldIndex = None
        myFemaleRatio = None

        if 'Gender' in myPostProcessors:
            #look if we need to look for a variable female ratio in a layer
            try:
                myFemRatioField = self.aggregator.attributes[
                    self.aggregator.defaults['FEM_RATIO_ATTR_KEY']]
                myFemRatioFieldIndex = self.aggregator.layer.fieldNameIndex(
                    myFemRatioField)
                myFemaleRatioIsVariable = True

            except KeyError:
                try:
                    myFemaleRatio = self.keywordIO.readKeywords(
                        self.aggregator.layer,
                        self.aggregator.defaults['FEM_RATIO_KEY'])
                except KeywordNotFoundError:
                    myFemaleRatio = self.aggregator.defaults['FEM_RATIO']

        #iterate zone features
        myProvider = self.aggregator.layer.dataProvider()
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
            myGeneralParams = {'target_field': self.aggregator.targetField}

            if self.aggregator.statisticsType == 'class_count':
                myGeneralParams['impact_classes'] = (
                    self.aggregator.statisticsClasses)
            elif self.aggregator.statisticsType == 'sum':
                myImpactTotal, _ = myAttributeMap[mySumFieldIndex].toDouble()
                myGeneralParams['impact_total'] = myImpactTotal

            try:
                myGeneralParams['impact_attrs'] = (
                    self.aggregator.impactLayerAttributes[myPolygonIndex])
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
                            myFemaleRatio = self.aggregator.defaults[
                                'FEM_RATIO']
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

    def getOutput(self):
        """Returns the results of the post processing as a table.

        Args:
            theSingleTableFlag - bool indicating if result should be rendered
                as a single table. Default False.

        Returns: str - a string containing the html in the requested format.
        """

        # LOGGER.debug(self.postProcessingOutput)
        if self.errorMessage is not None:
            myMessage = m.Message(
                m.Heading(self.tr('Postprocessing report skipped')),
                m.Paragraph(self.tr(
                    'Due to a problem while processing the results,'
                    ' the detailed postprocessing report is unavailable:'
                    ' %1').arg(self.errorMessage)))
            return myMessage

        return self._generateTables()
