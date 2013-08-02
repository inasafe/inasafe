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

from safe.common.utilities import unhumanize_number, format_int

from safe_qgis.utilities.keyword_io import KeywordIO
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

    def _sortNoData(self, data):
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
            myPosition = unhumanize_number(myPosition)

        return myPosition

    def _generateTables(self):
        """Parses the postprocessing output as one table per postprocessor.

        Args:
            None

        Returns:
            str - a string containing the html
        """
        myMessage = m.Message()

        for proc, results_list in self.postProcessingOutput.iteritems():
            # results_list is for example:
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
                    results_list,
                    key=self._sortNoData,
                    reverse=True)

            except KeyError:
                LOGGER.debug('Skipping sorting as the postprocessor did not '
                             'have a "Total" field')

            #init table
            hasNoDataValues = False
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
                    myValue = calculationData['value']
                    if myValue == self.aggregator.defaults['NO_DATA']:
                        hasNoDataValues = True
                        myValue += ' *'
                    myRow.add(myValue)
                myTable.add(myRow)

            #add table to message
            myMessage.add(myTable)
            if hasNoDataValues:
                myMessage.add(m.EmphasizedText(self.tr(
                    '* "%1" values mean that there where some problems while '
                    'calculating them. This did not affect the other '
                    'values.').arg(self.aggregator.defaults['NO_DATA'])))

        return myMessage

    def _consolidate_multipart_stats(self):
        """Sums the values of multipart polygons together to display only one.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        LOGGER.debug('Consolidating multipart postprocessing results')

        # copy needed because of
        # self.postProcessingOutput[proc].pop(corrected_index)
        postProcessingOutput = self.postProcessingOutput

        # iterate postprocessors
        for proc, results_list in postProcessingOutput.iteritems():
            #see self._generateTables to see details about results_list
            checked_polygon_names = {}
            parts_to_delete = []
            polygon_index = 0
            # iterate polygons
            for polygon_name, results in results_list:
                if polygon_name in checked_polygon_names.keys():
                    LOGGER.debug('%s postprocessor found multipart polygon '
                                 'with name %s' % (proc, polygon_name))
                    for result_name, result in results.iteritems():
                        first_part_index = checked_polygon_names[polygon_name]
                        first_part = self.postProcessingOutput[proc][
                            first_part_index]
                        first_part_results = first_part[1]
                        first_part_result = first_part_results[result_name]
                        new_result = (
                            unhumanize_number(first_part_result['value']) +
                            unhumanize_number(result['value']))
                        first_part_result['value'] = format_int(new_result)

                    parts_to_delete.append(polygon_index)

                else:
                    # add polygon to checked list
                    checked_polygon_names[polygon_name] = polygon_index

                polygon_index += 1

            # http://stackoverflow.com/questions/497426/
            # deleting-multiple-elements-from-a-list
            results_list = [res for j, res in enumerate(results_list)
                            if j not in parts_to_delete]
            self.postProcessingOutput[proc] = results_list


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
                    myFemaleRatio = self.keywordIO.read_keywords(
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
        if self.errorMessage is not None:
            myMessage = m.Message(
                m.Heading(self.tr('Postprocessing report skipped')),
                m.Paragraph(self.tr(
                    'Due to a problem while processing the results,'
                    ' the detailed postprocessing report is unavailable:'
                    ' %1').arg(self.errorMessage)))
            return myMessage
        else:
            try:
                if (self.keywordIO.read_keywords(
                        self.aggregator.layer, 'HAD_MULTIPART_POLY')):
                        self._consolidate_multipart_stats()
            except KeywordNotFoundError:
                pass

            return self._generateTables()
