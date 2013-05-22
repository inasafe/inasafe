"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Aggregator.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'tim@linfiniti.com'
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
    getDefaults)
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
    KeywordDbError)

from third_party.odict import OrderedDict


LOGGER = logging.getLogger('InaSAFE')
#from pydev import pydevd


class Aggregator(QtCore.QObject):
    """The aggregator class facilitates aggregation of impact function results.
    """
    def __init__(self, iface):
        """Director for aggregation based operations.
        Args:
           iface: iface - A QGIS iface instance.

        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """

        super(Aggregator, self).__init__()
        # Aggregation / post processing related items
        self.postProcessingOutput = {}
        self.prefix = 'aggr_'
        self.zonalMode = False
        # This is used to hold an in memory copy of the aggregation layer
        self.layer = None
        self.defaults = None
        self.attributes = {}
        self.attributeTitle = None
        self.runtimeKeywordsDialog = None
        self.iface = iface
        self.keywordIO = KeywordIO()
        # These should have already been clipped to analysis extents
        self.hazardLayer = None
        self.exposureLayer = None

    # noinspection PyDictCreation
    def runStarting(self):
        """Prepare for the fact that an analysis run is starting."""
        # Attributes that will not be deleted from the postprocessing layer
        # attribute table

        self.attributes = {}
        self.attributes[self.defaults[
            'AGGR_ATTR_KEY']] = (
                self.keywordIO.readKeywords(
                    self.layer,
                    self.defaults['AGGR_ATTR_KEY']))

        myFemaleRatioKey = self.defaults['FEM_RATIO_ATTR_KEY']
        myFemRatioAttr = self.keywordIO.readKeywords(
            self.layer,
            myFemaleRatioKey)
        if ((myFemRatioAttr != self.tr('Don\'t use')) and
                (myFemRatioAttr != self.tr('Use default'))):
            self.attributes[myFemaleRatioKey] = \
                myFemRatioAttr

    def countFieldName(self):
        return self.prefix + 'count'

    def meanFieldName(self):
        return self.prefix + 'mean'

    def sumFieldName(self):
        return self.prefix + 'sum'

    def prepareInputLayer(self,
                          theClippedHazardFilename,
                          theClippedExposureFilename):
        """Need a doc string here TS"""
        myHazardLayer = self.hazardLayer
        myExposureLayer = self.exposureLayer

        #get safe version of postproc layers
        self.mySafePostprocLayer = safe_read_layer(
            str(self.layer.source()))

        myTitle = self.tr('Preclipping input data...')
        myMessage = self.tr(
            'We are clipping the input layers to avoid intersections with the '
            'aggregation layer')
        myProgress = 44
        self.showBusy(myTitle, myMessage, myProgress)
#        import cProfile
        if isPolygonLayer(myHazardLayer):
            # http://stackoverflow.com/questions/1031657/
            # profiling-self-and-arguments-in-python
            # cProfile.runctx('self.preparePolygonLayer(
            #    theClippedHazardFilename, myHazardLayer)', globals(),
            # locals())
            # raise
            theClippedHazardFilename = self.preparePolygonLayer(
                theClippedHazardFilename, myHazardLayer)

        if isPolygonLayer(myExposureLayer):
            mySubcategory = self.keywordIO.readKeywords(myExposureLayer,
                                                        'subcategory')
            if mySubcategory != 'structure':
                theClippedExposureFilename = self.preparePolygonLayer(
                    theClippedExposureFilename, myExposureLayer)

        return theClippedHazardFilename, theClippedExposureFilename

    def preparePolygonLayer(self, theLayerFilename, theQgisLayer):
        """ A helper function to align the polygons to the postprocLayer
        polygons. If one input polygon is in two or more postprocLayer polygons
        then it is divided so that each part is within only one of the
        postprocLayer polygons. this allows to aggregate in postrocessing using
        centroid in polygon.

        The function assumes EPSG:4326 but no checks are enforced

        Args:
            theLayerFilename str of the file to be processed
        Returns:
            str of the processed file

        Raises:
            Any exceptions raised by the InaSAFE library will be propagated.
        """
#        import time
#        startTime = time.clock()
        myPostprocPolygons = self.mySafePostprocLayer.get_geometry()
        myPolygonsLayer = safe_read_layer(theLayerFilename)
        myRemainingPolygons = numpy.array(myPolygonsLayer.get_geometry())
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
        postprocProvider = self.layer.dataProvider()
        postprocProvider.select([])

        # copy polygons to a memory layer
        myQgisMemoryLayer = copyInMemory(theQgisLayer)

        polygonsProvider = myQgisMemoryLayer.dataProvider()
        allPolygonAttrs = polygonsProvider.attributeIndexes()
        polygonsProvider.select(allPolygonAttrs)
        myQgisPostprocPoly = QgsFeature()
        myQgisFeat = QgsFeature()
        myInsideFeat = QgsFeature()
        fields = polygonsProvider.fields()
        myTempdir = temp_dir(sub_dir='preprocess')
        myOutFilename = unique_filename(suffix='.shp',
                                        dir=myTempdir)

        self.keywordIO.copyKeywords(theQgisLayer, myOutFilename)
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
            postprocProvider.featureAtId(myPostprocPolygonIndex,
                                         myQgisPostprocPoly, True, [])
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
            # make True if the vertice was in myPostprocPolygon
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
                # summ the isInside bool for each of the boundingbox vertices
                # of each poygon. for example True + True + False + True is 3
                myPolygonLocation = numpy.sum(myAreVerticesInside[k:k + 4])

                if myPolygonLocation == 4:
                    # all vertices are inside -> polygon is inside
                    #ignore this polygon from further analysis
                    myInsidePolygons.append(myMappedIndex)
                    polygonsProvider.featureAtId(myFeatId,
                                                 myQgisFeat,
                                                 True,
                                                 allPolygonAttrs)
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
                        #polygon is surely outside
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

                #intersect using qgis
                if doIntersection:
#                    LOGGER.debug('Intersecting polygon %s' % myMappedIndex)
                    myIntersectingPolygons.append(myMappedIndex)

                    ok = polygonsProvider.featureAtId(myFeatId,
                                                      myQgisFeat,
                                                      True,
                                                      allPolygonAttrs)
                    if not ok:
                        LOGGER.debug('Couldn\'t fetch feature: %s' % myFeatId)
                        LOGGER.debug([str(error) for error in
                                      polygonsProvider.errors()])

                    myQgisPolyGeom = QgsGeometry(myQgisFeat.geometry())
                    myAtMap = myQgisFeat.attributeMap()
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
                            myInsideFeat.setAttributeMap(myAtMap)
                            mySHPWriter.addFeature(myInsideFeat)
                            self.preprocessedFeatureCount += 1
                        else:
                            pass
#                            LOGGER.debug('Intersection not a polygon so '
#                                         'the two polygons either touch '
#                                         'only or do not intersect. Not '
#                                         'adding this to the inside list')
                        #Part of the polygon that is outside the postprocpoly
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
                #some polygons are still completely outside of the postprocPoly
                #so go on and reiterate using only these
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

        #add in- and outside polygons

        for i in myOutsidePolygons:
            myFeatId = i + 1
            polygonsProvider.featureAtId(myFeatId, myQgisFeat, True,
                                         allPolygonAttrs)
            mySHPWriter.addFeature(myQgisFeat)
            self.preprocessedFeatureCount += 1

        del mySHPWriter
#        LOGGER.debug('Created: %s' % self.preprocessedFeatureCount)
        if self.showPostProcLayers:
            self.iface.addVectorLayer(myOutFilename,
                                      theQgisLayer.title(),
                                      'ogr')
        return myOutFilename

    def postProcess(self, runner):
        """Run all post processing steps.

        Called on self.runner SIGNAL('done()') starts all postprocessing steps

        Args:
            None

        Returns:
            None
        """

        if self.runner.impactLayer() is None:
            # Done was emitted, but no impact layer was calculated
            myResult = runner.result()
            myMessage = str(self.tr('No impact layer was calculated. '
                                    'Error message: %1\n').arg(str(myResult)))
            myException = runner.lastException()
            if myException is not None:
                myContext = self.tr('An exception occurred when calculating '
                                    'the results. %1').\
                    arg(runner.result())
                myMessage = getExceptionWithStacktrace(
                    myException, theHtml=True, theContext=myContext)
            raise Exception(myMessage)

        try:
            self.aggregate()
            if self.aggregationErrorSkipPostprocessing is None:
                self.run()
            QtGui.qApp.restoreOverrideCursor()
        except Exception, e:  # pylint: disable=W0703
            raise e
        self.completed()

    def initialise(self):
        """Initializes and clears self.getOutput.

        .. note:: Needs to run at the end of postProcess.

        Args: None
        Returns: None
        """
        #check and generate keywords for the aggregation layer
        self.defaults = getDefaults()
        self.postProcessingOutput = {}
        self.aggregationErrorSkipPostprocessing = None
        self.targetField = None
        self.impactLayerAttributes = []
        try:
            if ((self.layer is not None) and
                    (self.lastUsedFunction != self.getFunctionID())):
                # Remove category keyword so we force the keyword editor to
                # popup. See the beginning of checkAttributes to
                # see how the popup decision is made
                self.keywordIO.deleteKeyword(
                    self.layer, 'category')
        except AttributeError:
            #first run, self.lastUsedFunction does not exist yet
            pass

        self.zonalMode = True
        if self.layer is None:
            # generate on the fly a memory layer to be used in postprocessing
            # this is needed because we always want a vector layer to store
            # information
            self.zonalMode = False
            myGeoCrs = QgsCoordinateReferenceSystem()
            myGeoCrs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
            crs = myGeoCrs.authid().toLower()
            myUUID = str(uuid.uuid4())
            myUri = 'Polygon?crs=%s&index=yes&uuid=%s' % (crs, myUUID)
            myName = 'tmpPostprocessingLayer'
            myLayer = QgsVectorLayer(myUri, myName, 'memory')
            LOGGER.debug('created' + myLayer.name())

            if not myLayer.isValid():
                myMessage = self.tr('An exception occurred when creating the '
                                    'Entire area layer.')
                raise(Exception(myMessage))

            myProvider = myLayer.dataProvider()
            myLayer.startEditing()
            myAttrName = self.tr('Area')
            myProvider.addAttributes([QgsField(myAttrName,
                                               QtCore.QVariant.String)])
            myLayer.commitChanges()

            self.layer = myLayer
            try:
                self.keywordIO.appendKeywords(
                    self.layer,
                    {self.defaults['AGGR_ATTR_KEY']: myAttrName})
            except KeywordDbError, e:
                raise e

    def getOutput(self, theSingleTableFlag=False):
        """Returns the results of the post processing as a table.

        Args:
            theSingleTableFlag - bool indicating if result should be rendered
                as a single table. Default False.

        Returns: str - a string containing the html in the requested format.
        """

#        LOGGER.debug(self.postProcessingOutput)
        if self.aggregationErrorSkipPostprocessing is not None:
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
                    ' %1').arg(self.aggregationErrorSkipPostprocessing)
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

    def aggregate(self, theAggregationLayerName):
        """Do any requested aggregation post processing.

        Performs Aggregation postprocessing step by
         * creating a copy of the dataset clipped by the impactlayer bounding
          box
         * stripping all attributes beside the aggregation attribute
         * delegating to the appropriate aggregator for raster and vectors

        Args:
            theAggregationLayerName - content of the combo for aggregation in
             dock. e.g. 'Entire Area', or 'kapubaten jakarta'

        Returns: None

        Raises:
            ReadLayerError
        """
        myImpactLayer = self.runner.impactLayer()

        myTitle = self.tr('Aggregating results...')
        myMessage = self.tr('This may take a little while - we are '
                            ' aggregating the hazards by %1').\
            arg(theAggregationLayerName)
        myProgress = 88
        self.showBusy(myTitle, myMessage, myProgress)

        myQGISImpactLayer = self.readImpactLayer(myImpactLayer)
        if not myQGISImpactLayer.isValid():
            myMessage = self.tr('Error when reading %1').arg(myQGISImpactLayer)
            raise ReadLayerError(myMessage)
        myLayerName = str(self.tr('%1 aggregated to %2').arg(
            myQGISImpactLayer.name()).arg(self.layer.name()))

        #delete unwanted fields
        myProvider = self.layer.dataProvider()
        myFields = myProvider.fields()
        myUnneededAttributes = []
        for i in myFields:
            if (myFields[i].name() not in
                    self.attributes.values()):
                myUnneededAttributes.append(i)
        LOGGER.debug('Removing this attributes: ' + str(myUnneededAttributes))
        # noinspection PyBroadException
        try:
            self.layer.startEditing()
            myProvider.deleteAttributes(myUnneededAttributes)
            self.layer.commitChanges()
        # FIXME (Ole): Disable pylint check for the moment
        # Need to work out what exceptions we will catch here, though.
        except:  # pylint: disable=W0702
            myMessage = self.tr('Could not remove the unneeded fields')
            LOGGER.debug(myMessage)

        del myUnneededAttributes, myProvider, myFields
        self.keywordIO.appendKeywords(
            self.layer, {'title': myLayerName})

        #find needed statistics type
        try:
            self.statisticsType = self.keywordIO.readKeywords(
                myQGISImpactLayer, 'statistics_type')
            self.statisticsClasses = self.keywordIO.readKeywords(
                myQGISImpactLayer, 'statistics_classes')

        except KeywordNotFoundError:
            #default to summing
            self.statisticsType = 'sum'

        #call the correct aggregator
        if myQGISImpactLayer.type() == QgsMapLayer.VectorLayer:
            self.aggregateVectorImpact(myQGISImpactLayer)
        elif myQGISImpactLayer.type() == QgsMapLayer.RasterLayer:
            self.aggregateRasterImpact(myQGISImpactLayer)
        else:
            myMessage = self.tr('%1 is %2 but it should be either vector or '
                                'raster').\
                arg(myQGISImpactLayer.name()).arg(myQGISImpactLayer.type())
            raise ReadLayerError(myMessage)

        if self.showPostProcLayers and self.zonalMode:
            if self.statisticsType == 'sum':
                #style layer if we are summing
                myProvider = self.layer.dataProvider()
                myAttr = self.sumFieldName()
                myAttrIndex = myProvider.fieldNameIndex(myAttr)
                myProvider.select([myAttrIndex], QgsRectangle(), False)
                myFeature = QgsFeature()
                myHighestVal = 0

                while myProvider.nextFeature(myFeature):
                    myAttrMap = myFeature.attributeMap()
                    myVal, ok = myAttrMap[myAttrIndex].toInt()
                    if ok and myVal > myHighestVal:
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
                setVectorStyle(self.layer, myStyle)
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

    def aggregateVectorImpact(self, myQGISImpactLayer):
        """Performs Aggregation postprocessing step on vector impact layers.

        Args:
            myQGISImpactLayer a valid QgsRasterLayer

        Returns:
            None
        """
        #TODO implement polygon to polygon aggregation (dissolve,
        # line in polygon, point in polygon)

        # Note: The next line raises a pylint error but I am not disabling the
        # pylint warning because I think we need some redesign here. TS
        global myAttrs
        myAggrFieldMap = {}
        myAggrFieldIndex = None

        try:
            self.targetField = self.keywordIO.readKeywords(myQGISImpactLayer,
                                                           'target_field')
        except KeywordNotFoundError:
            myMessage = self.tr('No "target_field" keyword found in the impact'
                                ' layer %1 keywords. The impact function'
                                ' should define this.').\
                arg(myQGISImpactLayer.name())
            LOGGER.debug('Skipping postprocessing due to: %s' % myMessage)
            self.aggregationErrorSkipPostprocessing = myMessage
            return
        myImpactProvider = myQGISImpactLayer.dataProvider()
        myTargetFieldIndex = myQGISImpactLayer.fieldNameIndex(self.targetField)
        #if a feature has no field called
        if myTargetFieldIndex == -1:
            myMessage = self.tr('No attribute "%1" was found in the attribute '
                                'table for layer "%2". The impact function '
                                'must define this attribute for '
                                'postprocessing to work.').arg(
                                    self.targetField, myQGISImpactLayer.name())
            LOGGER.debug('Skipping postprocessing due to: %s' % myMessage)
            self.aggregationErrorSkipPostprocessing = myMessage
            return

        # start data retreival: fetch no geometry and
        # 1 attr for each feature
        myImpactProvider.select([myTargetFieldIndex], QgsRectangle(), False)
        myTotal = 0

        myPostprocessorProvider = self.layer.dataProvider()
        self.layer.startEditing()

        if self.statisticsType == 'class_count':
            #add the class count fields to the layer
            myFields = [QgsField('%s_%s' % (f, self.targetField),
                                 QtCore.QVariant.String) for f in
                        self.statisticsClasses]
            myPostprocessorProvider.addAttributes(myFields)
            self.layer.commitChanges()

            myTmpAggrFieldMap = myPostprocessorProvider.fieldNameMap()
            for k, v in myTmpAggrFieldMap.iteritems():
                myAggrFieldMap[str(k)] = v

        elif self.statisticsType == 'sum':
            #add the total field to the layer
            myAggrField = self.sumFieldName()
            myPostprocessorProvider.addAttributes([QgsField(
                myAggrField, QtCore.QVariant.Int)])
            self.layer.commitChanges()
            myAggrFieldIndex = self.layer.fieldNameIndex(
                myAggrField)

        self.layer.startEditing()

        mySafeImpactLayer = self.runner.impactLayer()
        myImpactGeoms = mySafeImpactLayer.get_geometry()
        myImpactValues = mySafeImpactLayer.get_data()

        if self.zonalMode:
            myPostprocPolygons = self.mySafePostprocLayer.get_geometry()

            if (mySafeImpactLayer.is_point_data or
                    mySafeImpactLayer.is_polygon_data):
                LOGGER.debug('Doing point in polygon aggregation')

                myRemainingValues = myImpactValues

                if mySafeImpactLayer.is_polygon_data:
                    # Using centroids to do polygon in polygon aggregation
                    # this is always ok because
                    # prepareInputLayer() took care of splitting
                    # polygons that spawn across multiple postprocessing
                    # polygons. After prepareInputLayer()
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
                    myRemainingPoints = myImpactGeoms

                for myPolygonIndex, myPolygon in enumerate(myPostprocPolygons):
                    if hasattr(myPolygon, 'outer_ring'):
                        outer_ring = myPolygon.outer_ring
                        inner_rings = myPolygon.inner_rings
                    else:
                        # Assume it is an array
                        outer_ring = myPolygon
                        inner_rings = None

                    inside, outside = points_in_and_outside_polygon(
                        myRemainingPoints,
                        outer_ring,
                        holes=inner_rings,
                        closed=True,
                        check_input=True)

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
                                myError = ('StatisticsClasses %s does not '
                                           'include the %s class which was '
                                           'found in the data. This is a '
                                           'problem in the %s '
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
                            myAttrs[myAggrFieldIndex] = QtCore.QVariant(v)

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
                        myAttrs = {myAggrFieldIndex: QtCore.QVariant(myTotal)}

                    # Add features inside this polygon
                    myFID = myPolygonIndex
                    myPostprocessorProvider.changeAttributeValues(
                        {myFID: myAttrs})

                    # make outside points the input to the next iteration
                    # this could maybe be done quicklier using directly numpy
                    # arrays like this:
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

#                    LOGGER.debug('Before: ' + str(len(myRemainingValues)))
#                    LOGGER.debug('After: ' + str(len(myRemainingValues)))
#                    LOGGER.debug('Inside: ' + str(len(inside)))
#                    LOGGER.debug('Outside: ' + str(len(outside)))

            elif mySafeImpactLayer.is_line_data:
                LOGGER.debug('Doing line in polygon aggregation')

            else:
                myMessage = self.tr('Aggregation on vector impact layers other'
                                    'than points or polygons not implemented '
                                    'yet not implemented yet. '
                                    'Called on %1').\
                    arg(myQGISImpactLayer.name())
                LOGGER.debug('Skipping postprocessing due to: %s' % myMessage)
                self.aggregationErrorSkipPostprocessing = myMessage
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
                        myError = ('StatisticsClasses %s does not '
                                   'include the %s class which was '
                                   'found in the data. This is a '
                                   'problem in the %s '
                                   'statistics_classes definition' %
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
                    myAttrs[myAggrFieldIndex] = QtCore.QVariant(v)

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
                myAttrs = {myAggrFieldIndex: QtCore.QVariant(myTotal)}

            #apply to all area feature
            myFID = 0
            myPostprocessorProvider.changeAttributeValues({myFID: myAttrs})

        self.layer.commitChanges()
        return

    def aggregateRasterImpact(self, theQGISImpactLayer):
        """
        Performs Aggregation postprocessing step on raster impact layers by
        calling QgsZonalStatistics
        Args:
            QgsMapLayer: theQGISImpactLayer a valid QgsVectorLayer

        Returns: None
        """
        myZonalStatistics = QgsZonalStatistics(
            self.layer,
            theQGISImpactLayer.dataProvider().dataSourceUri(),
            self.prefix)
        myProgressDialog = QtGui.QProgressDialog(
            self.tr('Calculating zonal statistics'),
            self.tr('Abort...'),
            0,
            0)
        myZonalStatistics.calculateStatistics(myProgressDialog)
        if myProgressDialog.wasCanceled():
            QtGui.QMessageBox.error(
                self, self.tr('ZonalStats: Error'),
                self.tr('You aborted aggregation, '
                        'so there are no data for analysis. Exiting...'))

        return

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
            self.sumFieldName())

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

    def checkAttributes(self):
        """Checks if the postprocessing layer has all attribute keyword.

        If not it calls _promptPostprocAttributes to prompt for inputs

        Args:
            None

        Returns:
            None

        Raises:
            Propagates any error
        """

        # noinspection PyBroadException
        try:
            myKeywords = self.keywordIO.readKeywords(self.layer)
        #discussed with tim,in this case its ok to be generic
        except Exception:  # pylint: disable=W0703
            myKeywords = {}

        #myKeywords are already complete
        if ('category' in myKeywords and
            myKeywords['category'] == 'postprocessing' and
            self.defaults['AGGR_ATTR_KEY'] in myKeywords and
            self.defaults['FEM_RATIO_ATTR_KEY'] in myKeywords and
            (self.defaults['FEM_RATIO_ATTR_KEY'] != self.tr('Use default') or
             self.defaults['FEM_RATIO_KEY'] in myKeywords)):
            return True
        #some keywords are needed
        else:
            #set the default values by writing to the myKeywords
            myKeywords['category'] = 'postprocessing'

            myAttributes, _ = getLayerAttributeNames(
                self.layer,
                [QtCore.QVariant.Int, QtCore.QVariant.String])
            if self.defaults['AGGR_ATTR_KEY'] not in myKeywords:
                myKeywords[self.defaults['AGGR_ATTR_KEY']] = myAttributes[0]

            if self.defaults['FEM_RATIO_ATTR_KEY'] not in myKeywords:
                myKeywords[self.defaults['FEM_RATIO_ATTR_KEY']] = self.tr(
                    'Use default')

            if self.defaults['FEM_RATIO_KEY'] not in myKeywords:
                myKeywords[self.defaults['FEM_RATIO_KEY']] = \
                    self.defaults['FEM_RATIO']

#            delete = self.keywordIO.deleteKeyword(self.layer,
#               'subcategory')
#            LOGGER.debug('Deleted: ' + str(delete))
            self.keywordIO.appendKeywords(self.layer, myKeywords)
            if self.zonalMode:
                #prompt user for a choice
                myTitle = self.tr(
                    'Waiting for attribute selection...')
                myMessage = self.tr('Please select which attribute you want to'
                                    ' use as ID for the aggregated results')
                myProgress = 1
                self.showBusy(myTitle, myMessage, myProgress)

                self.disableBusyCursor()
                self.runtimeKeywordsDialog.setLayer(self.layer)
                #disable gui elements that should not be applicable for this
                self.runtimeKeywordsDialog.radExposure.setEnabled(False)
                self.runtimeKeywordsDialog.radHazard.setEnabled(False)
                self.runtimeKeywordsDialog.pbnAdvanced.setEnabled(False)
                self.runtimeKeywordsDialog.setModal(True)
                self.runtimeKeywordsDialog.show()

                return False
            else:
                return True

    def clip(self, theGeoExtent):

        #If doing entire area, create a fake feature that covers the whole
        #theGeoExtent
        if not self.zonalMode:
            self.layer.startEditing()
            myProvider = self.layer.dataProvider()
            # add a feature the size of the impact layer bounding box
            myFeature = QgsFeature()
            # noinspection PyCallByClass,PyTypeChecker
            myFeature.setGeometry(QgsGeometry.fromRect(
                QgsRectangle(
                    QgsPoint(theGeoExtent[0], theGeoExtent[1]),
                    QgsPoint(theGeoExtent[2], theGeoExtent[3]))))
            myFeature.setAttributeMap({0: QtCore.QVariant(
                self.tr('Entire area'))})
            myProvider.addFeatures([myFeature])
            self.layer.commitChanges()

        myPath = clipLayer(
            theLayer=self.layer,
            theExtent=theGeoExtent,
            theExplodeFlag=False,
            theHardClipFlag=False)

        return myPath
