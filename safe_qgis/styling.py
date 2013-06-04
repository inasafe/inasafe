"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **IS Utilitles implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '29/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import sys
import logging
import math
import numpy

from PyQt4 import QtCore, QtGui

from qgis.core import (
    QGis,
    QgsRasterLayer,
    QgsGraduatedSymbolRendererV2,
    QgsSymbolV2,
    QgsRendererRangeV2,
    QgsRendererCategoryV2,
    QgsSymbolLayerV2Registry,
    QgsColorRampShader,
    QgsRasterTransparency,
    QgsCategorizedSymbolRendererV2)

from safe_qgis.exceptions import StyleError

from safe_qgis.utilities import qgisVersion

LOGGER = logging.getLogger('InaSAFE')


def setVectorGraduatedStyle(theQgisVectorLayer, theStyle):
    """Set graduated QGIS vector style based on InaSAFE style dictionary.

    For **opaque** a value of **0** can be used. For **fully transparent**, a
    value of **100** can be used. The calling function should take care to
    scale the transparency level to between 0 and 100.

    Args:
        * theQgisVectorLayer: QgsMapLayer
        * theStyle: dict - Dictionary of the form as in the example below

    Returns:
        None - Sets and saves style for theQgisVectorLayer

    Raises:
        None

    Example:

        {'target_field': 'DMGLEVEL',
        'style_classes':
        [{'transparency': 1, 'max': 1.5, 'colour': '#fecc5c',
          'min': 0.5, 'label': '[0.5 - 1.5] Low damage', 'size' : 1},
        {'transparency': 55, 'max': 2.5, 'colour': '#fd8d3c',
         'min': 1.5, 'label': '[1.5 - 2.5] Medium damage', 'size' : 1},
        {'transparency': 80, 'max': 3.5, 'colour': '#f31a1c',
         'min': 2.5, 'label': '[2.5 - 3.5] High damage', 'size' : 1}]}

        .. note:: The transparency and size keys are optional. Size applies
           to points only.

    """
    myTargetField = theStyle['target_field']
    myClasses = theStyle['style_classes']
    myGeometryType = theQgisVectorLayer.geometryType()

    myRangeList = []
    for myClass in myClasses:
        # Transparency 100: transparent
        # Transparency 0: opaque
        mySize = 2  # mm
        if 'size' in myClass:
            mySize = myClass['size']
        myTransparencyPercent = 0
        if 'transparency' in myClass:
            myTransparencyPercent = myClass['transparency']

        if 'min' not in myClass:
            raise StyleError('Style info should provide a "min" entry')
        if 'max' not in myClass:
            raise StyleError('Style info should provide a "max" entry')

        try:
            myMin = float(myClass['min'])
        except TypeError:
            raise StyleError(
                'Class break lower bound should be a number.'
                'I got %s' % myClass['min'])

        try:
            myMax = float(myClass['max'])
        except TypeError:
            raise StyleError('Class break upper bound should be a number.'
                             'I got %s' % myClass['max'])

        myColour = myClass['colour']
        myLabel = myClass['label']
        myColour = QtGui.QColor(myColour)
        # noinspection PyArgumentList
        mySymbol = QgsSymbolV2.defaultSymbol(myGeometryType)
        myColourString = "%s, %s, %s" % (
                         myColour.red(),
                         myColour.green(),
                         myColour.blue())
        # Work around for the fact that QgsSimpleMarkerSymbolLayerV2
        # python bindings are missing from the QGIS api.
        # .. see:: http://hub.qgis.org/issues/4848
        # We need to create a custom symbol layer as
        # the border colour of a symbol can not be set otherwise
        # noinspection PyArgumentList
        myRegistry = QgsSymbolLayerV2Registry.instance()
        if myGeometryType == QGis.Point:
            myMetadata = myRegistry.symbolLayerMetadata('SimpleMarker')
            # note that you can get a list of available layer properties
            # that you can set by doing e.g.
            # QgsSimpleMarkerSymbolLayerV2.properties()
            mySymbolLayer = myMetadata.createSymbolLayer({'color_border':
                                                          myColourString})
            mySymbolLayer.setSize(mySize)
            mySymbol.changeSymbolLayer(0, mySymbolLayer)
        elif myGeometryType == QGis.Polygon:
            myMetadata = myRegistry.symbolLayerMetadata('SimpleFill')
            mySymbolLayer = myMetadata.createSymbolLayer({'color_border':
                                                          myColourString})
            mySymbol.changeSymbolLayer(0, mySymbolLayer)
        else:
            # for lines we do nothing special as the property setting
            # below should give us what we require.
            pass

        mySymbol.setColor(myColour)
        # .. todo:: Check that vectors use alpha as % otherwise scale TS
        # Convert transparency % to opacity
        # alpha = 0: transparent
        # alpha = 1: opaque
        alpha = 1 - myTransparencyPercent / 100.0
        mySymbol.setAlpha(alpha)
        myRange = QgsRendererRangeV2(myMin,
                                     myMax,
                                     mySymbol,
                                     myLabel)
        myRangeList.append(myRange)

    myRenderer = QgsGraduatedSymbolRendererV2('', myRangeList)
    myRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
    myRenderer.setClassAttribute(myTargetField)
    theQgisVectorLayer.setRendererV2(myRenderer)
    theQgisVectorLayer.saveDefaultStyle()


def setVectorCategorizedStyle(theQgisVectorLayer, theStyle):
    """Set categorized QGIS vector style based on InaSAFE style dictionary.

    For **opaque** a value of **0** can be used. For **fully transparent**, a
    value of **100** can be used. The calling function should take care to
    scale the transparency level to between 0 and 100.

    Args:
        * theQgisVectorLayer: QgsMapLayer
        * theStyle: dict - Dictionary of the form as in the example below

    Returns:
        None - Sets and saves style for theQgisVectorLayer

    Raises:
        None

    Example:

        {'target_field': 'DMGLEVEL',
        'style_classes':
        [{'transparency': 1, 'value': 1, 'colour': '#fecc5c',
          'label': 'Low damage', 'size' : 1},
        {'transparency': 55, 'value': 2, 'colour': '#fd8d3c',
         'label': 'Medium damage', 'size' : 1},
        {'transparency': 80, 'value': 3, 'colour': '#f31a1c',
         'label': 'High damage', 'size' : 1}]}

        .. note:: The transparency and size keys are optional. Size applies
           to points only.

        .. todo:: We should change 'value' in style classes to something more
            meaningful e.g. descriminant value

    """
    myTargetField = theStyle['target_field']
    myClasses = theStyle['style_classes']
    myGeometryType = theQgisVectorLayer.geometryType()

    myCategoryList = []
    for myClass in myClasses:
        # Transparency 100: transparent
        # Transparency 0: opaque
        mySize = 2  # mm
        if 'size' in myClass:
            mySize = myClass['size']
        myTransparencyPercent = 0
        if 'transparency' in myClass:
            myTransparencyPercent = myClass['transparency']

        if 'value' not in myClass:
            raise StyleError('Style info should provide a "value" entry')

        try:
            myValue = float(myClass['value'])
        except TypeError:
            raise StyleError(
                'Value should be a number. I got %s' % myClass['value'])

        myColour = myClass['colour']
        myLabel = myClass['label']
        myColour = QtGui.QColor(myColour)
        # noinspection PyArgumentList
        mySymbol = QgsSymbolV2.defaultSymbol(myGeometryType)
        myColourString = "%s, %s, %s" % (
            myColour.red(),
            myColour.green(),
            myColour.blue())
        # Work around for the fact that QgsSimpleMarkerSymbolLayerV2
        # python bindings are missing from the QGIS api.
        # .. see:: http://hub.qgis.org/issues/4848
        # We need to create a custom symbol layer as
        # the border colour of a symbol can not be set otherwise
        # noinspection PyArgumentList
        myRegistry = QgsSymbolLayerV2Registry.instance()
        if myGeometryType == QGis.Point:
            myMetadata = myRegistry.symbolLayerMetadata('SimpleMarker')
            # note that you can get a list of available layer properties
            # that you can set by doing e.g.
            # QgsSimpleMarkerSymbolLayerV2.properties()
            mySymbolLayer = myMetadata.createSymbolLayer({
                'color_border': myColourString})
            mySymbolLayer.setSize(mySize)
            mySymbol.changeSymbolLayer(0, mySymbolLayer)
        elif myGeometryType == QGis.Polygon:
            myMetadata = myRegistry.symbolLayerMetadata('SimpleFill')
            mySymbolLayer = myMetadata.createSymbolLayer({
                'color_border': myColourString})
            mySymbol.changeSymbolLayer(0, mySymbolLayer)
        else:
            # for lines we do nothing special as the property setting
            # below should give us what we require.
            pass

        mySymbol.setColor(myColour)
        # .. todo:: Check that vectors use alpha as % otherwise scale TS
        # Convert transparency % to opacity
        # alpha = 0: transparent
        # alpha = 1: opaque
        alpha = 1 - myTransparencyPercent / 100.0
        mySymbol.setAlpha(alpha)
        myCategory = QgsRendererCategoryV2(myValue, mySymbol, myLabel)
        myCategoryList.append(myCategory)

    myRenderer = QgsCategorizedSymbolRendererV2('', myCategoryList)
    myRenderer.setClassAttribute(myTargetField)
    theQgisVectorLayer.setRendererV2(myRenderer)
    theQgisVectorLayer.saveDefaultStyle()


def setRasterStyle(theQgsRasterLayer, theStyle):
    """Set QGIS raster style based on InaSAFE style dictionary.

    This function will set both the colour map and the transparency
    for the passed in layer.

    Args:
        * theQgsRasterLayer: QgsRasterLayer
        * style: dict - Dictionary of the form as in the example below.

    Example:
        style_classes = [dict(colour='#38A800', quantity=2, transparency=0),
                         dict(colour='#38A800', quantity=5, transparency=50),
                         dict(colour='#79C900', quantity=10, transparency=50),
                         dict(colour='#CEED00', quantity=20, transparency=50),
                         dict(colour='#FFCC00', quantity=50, transparency=34),
                         dict(colour='#FF6600', quantity=100, transparency=77),
                         dict(colour='#FF0000', quantity=200, transparency=24),
                         dict(colour='#7A0000', quantity=300, transparency=22)]

    Returns:
        list: RangeList
        list: TransparencyList
    """
    myNewStyles = _addMinMaxToStyle(theStyle['style_classes'])
    # test if QGIS 1.8.0 or older
    # see issue #259
    if qgisVersion() <= 10800:
        LOGGER.debug('Rendering raster using <= 1.8 styling')
        return _setLegacyRasterStyle(theQgsRasterLayer, myNewStyles)
    else:
        LOGGER.debug('Rendering raster using 2+ styling')
        return _setNewRasterStyle(theQgsRasterLayer, myNewStyles)


def _addMinMaxToStyle(theStyle):
    """Add a min and max to each style class in a style dictionary.

    When InaSAFE provides style classes they are specific values, not ranges.
    However QGIS wants to work in ranges, so this helper will address that by
    updating the dictionary to include a min max value for each class.

    It is assumed that we will start for 0 as the min for the first class
    and the quantity of each class shall constitute the max. For all other
    classes , min shall constitute the smalles increment to a float that can
    meaningfully be made by python (as determined by numpy.nextafter()).

    Args:
        style: list - A list of dictionaries of the form as in the example
            below.

    Returns:
        dict: A new dictionary list with min max attributes added to each
            entry.

    Example input:

        style_classes = [dict(colour='#38A800', quantity=2, transparency=0),
                         dict(colour='#38A800', quantity=5, transparency=50),
                         dict(colour='#79C900', quantity=10, transparency=50),
                         dict(colour='#CEED00', quantity=20, transparency=50),
                         dict(colour='#FFCC00', quantity=50, transparency=34),
                         dict(colour='#FF6600', quantity=100, transparency=77),
                         dict(colour='#FF0000', quantity=200, transparency=24),
                         dict(colour='#7A0000', quantity=300, transparency=22)]

    Example output:

        style_classes = [dict(colour='#38A800', quantity=2, transparency=0,
                              min=0, max=2),
                         dict(colour='#38A800', quantity=5, transparency=50,
                              min=2.0000000000002, max=5),
                         ),
                         dict(colour='#79C900', quantity=10, transparency=50,
                              min=5.0000000000002, max=10),),
                         dict(colour='#CEED00', quantity=20, transparency=50,
                              min=5.0000000000002, max=20),),
                         dict(colour='#FFCC00', quantity=50, transparency=34,
                              min=20.0000000000002, max=50),),
                         dict(colour='#FF6600', quantity=100, transparency=77,
                              min=50.0000000000002, max=100),),
                         dict(colour='#FF0000', quantity=200, transparency=24,
                              min=100.0000000000002, max=200),),
                         dict(colour='#7A0000', quantity=300, transparency=22,
                              min=200.0000000000002, max=300),)]
    """
    myNewStyles = []
    myLastMax = 0.0
    for myClass in theStyle:
        myQuantity = float(myClass['quantity'])
        myClass['min'] = myLastMax
        myClass['max'] = myQuantity
        if myQuantity == myLastMax and myQuantity != 0:
            # skip it as it does not represent a class increment
            continue
        myLastMax = numpy.nextafter(myQuantity, sys.float_info.max)
        myNewStyles.append(myClass)
    return myNewStyles


def _setLegacyRasterStyle(theQgsRasterLayer, theStyle):
    """Set QGIS raster style based on InaSAFE style dictionary for QGIS < 2.0.

    This function will set both the colour map and the transparency
    for the passed in layer.

    Args:
        * theQgsRasterLayer: QgsRasterLayer.
        * style: List - of the form as in the example below.

    Returns:
        * list: RangeList
        * list: TransparencyList

    Example:

        style_classes = [dict(colour='#38A800', quantity=2, transparency=0),
                         dict(colour='#38A800', quantity=5, transparency=50),
                         dict(colour='#79C900', quantity=10, transparency=50),
                         dict(colour='#CEED00', quantity=20, transparency=50),
                         dict(colour='#FFCC00', quantity=50, transparency=34),
                         dict(colour='#FF6600', quantity=100, transparency=77),
                         dict(colour='#FF0000', quantity=200, transparency=24),
                         dict(colour='#7A0000', quantity=300, transparency=22)]

    .. note:: There is currently a limitation in QGIS in that
       pixel transparency values can not be specified in ranges and
       consequently the opacity is of limited value and seems to
       only work effectively with integer values.

    """
    theQgsRasterLayer.setDrawingStyle(QgsRasterLayer.PalettedColor)
    LOGGER.debug(theStyle)
    myRangeList = []
    myTransparencyList = []
    # Always make 0 pixels transparent see issue #542
    # noinspection PyCallingNonCallable
    myPixel = QgsRasterTransparency.TransparentSingleValuePixel()
    myPixel.pixelValue = 0.0
    myPixel.percentTransparent = 100
    myTransparencyList.append(myPixel)
    myLastValue = 0
    for myClass in theStyle:
        LOGGER.debug('Evaluating class:\n%s\n' % myClass)
        myMax = myClass['quantity']
        myColour = QtGui.QColor(myClass['colour'])
        myLabel = QtCore.QString()
        if 'label' in myClass:
            myLabel = QtCore.QString(myClass['label'])
        # noinspection PyCallingNonCallable
        myShader = QgsColorRampShader.ColorRampItem(myMax, myColour, myLabel)
        myRangeList.append(myShader)

        if math.isnan(myMax):
            LOGGER.debug('Skipping class.')
            continue

        # Create opacity entries for this range
        myTransparencyPercent = 0
        if 'transparency' in myClass:
            myTransparencyPercent = int(myClass['transparency'])
        if myTransparencyPercent > 0:
            # Always assign the transparency to the class' specified quantity
            # noinspection PyCallingNonCallable
            myPixel = QgsRasterTransparency.TransparentSingleValuePixel()
            myPixel.pixelValue = myMax
            myPixel.percentTransparent = myTransparencyPercent
            myTransparencyList.append(myPixel)

            # Check if range extrema are integers so we know if we can
            # use them to calculate a value range
            if (myLastValue == int(myLastValue)) and (myMax == int(myMax)):
                # Ensure that they are integers
                # (e.g 2.0 must become 2, see issue #126)
                myLastValue = int(myLastValue)
                myMax = int(myMax)

                # Set transparencies
                myRange = range(myLastValue, myMax)
                for myValue in myRange:
                    # noinspection PyCallingNonCallable
                    myPixel = \
                        QgsRasterTransparency.TransparentSingleValuePixel()
                    myPixel.pixelValue = myValue
                    myPixel.percentTransparent = myTransparencyPercent
                    myTransparencyList.append(myPixel)

    # Apply the shading algorithm and design their ramp
    theQgsRasterLayer.setColorShadingAlgorithm(
        QgsRasterLayer.ColorRampShader)
    myFunction = theQgsRasterLayer.rasterShader().rasterShaderFunction()
    # Discrete will shade any cell between maxima of this break
    # and minima of previous break to the colour of this break
    myFunction.setColorRampType(QgsColorRampShader.DISCRETE)
    myFunction.setColorRampItemList(myRangeList)

    # Now set the raster transparency
    theQgsRasterLayer.rasterTransparency()\
        .setTransparentSingleValuePixelList(myTransparencyList)

    theQgsRasterLayer.saveDefaultStyle()
    return myRangeList, myTransparencyList


def _setNewRasterStyle(theQgsRasterLayer, theClasses):
    """Set QGIS raster style based on InaSAFE style dictionary for QGIS >= 2.0.

    This function will set both the colour map and the transparency
    for the passed in layer.

    Args:
        * theQgsRasterLayer: QgsRasterLayer
        * theClasses: List of the form as in the example below.

    Returns:
        * list: RangeList
        * list: TransparencyList

    Example:
        style_classes = [dict(colour='#38A800', quantity=2, transparency=0),
                         dict(colour='#38A800', quantity=5, transparency=50),
                         dict(colour='#79C900', quantity=10, transparency=50),
                         dict(colour='#CEED00', quantity=20, transparency=50),
                         dict(colour='#FFCC00', quantity=50, transparency=34),
                         dict(colour='#FF6600', quantity=100, transparency=77),
                         dict(colour='#FF0000', quantity=200, transparency=24),
                         dict(colour='#7A0000', quantity=300, transparency=22)]

    """
    # Note imports here to prevent importing on unsupported QGIS versions
    # pylint: disable=E0611
    # pylint: disable=W0621
    # pylint: disable=W0404
    # noinspection PyUnresolvedReferences
    from qgis.core import (QgsRasterShader,
                           QgsColorRampShader,
                           QgsSingleBandPseudoColorRenderer,
                           QgsRasterTransparency)
    # pylint: enable=E0611
    # pylint: enable=W0621
    # pylint: enable=W0404

    myRampItemList = []
    myTransparencyList = []
    LOGGER.debug(theClasses)
    for myClass in theClasses:

        LOGGER.debug('Evaluating class:\n%s\n' % myClass)

        if 'quantity' not in myClass:
            LOGGER.exception('Class has no quantity attribute')
            continue

        myMax = myClass['max']
        if math.isnan(myMax):
            LOGGER.debug('Skipping class - max is nan.')
            continue

        myMin = myClass['min']
        if math.isnan(myMin):
            LOGGER.debug('Skipping class - min is nan.')
            continue

        myColour = QtGui.QColor(myClass['colour'])
        myLabel = QtCore.QString()
        if 'label' in myClass:
            myLabel = QtCore.QString(myClass['label'])
        # noinspection PyCallingNonCallable
        myRampItem = QgsColorRampShader.ColorRampItem(myMax, myColour, myLabel)
        myRampItemList.append(myRampItem)

        # Create opacity entries for this range
        myTransparencyPercent = 0
        if 'transparency' in myClass:
            myTransparencyPercent = int(myClass['transparency'])
        if myTransparencyPercent > 0:
            # Check if range extrema are integers so we know if we can
            # use them to calculate a value range
            # noinspection PyCallingNonCallable
            myPixel = QgsRasterTransparency.TransparentSingleValuePixel()
            myPixel.min = myMin
            # We want it just a leeetle bit smaller than max
            # so that ranges are discrete
            myPixel.max = myMax
            myPixel.percentTransparent = myTransparencyPercent
            myTransparencyList.append(myPixel)

    myBand = 1  # gdal counts bands from base 1
    LOGGER.debug('Setting colour ramp list')
    myRasterShader = QgsRasterShader()
    myColorRampShader = QgsColorRampShader()
    myColorRampShader.setColorRampType(QgsColorRampShader.INTERPOLATED)
    myColorRampShader.setColorRampItemList(myRampItemList)
    LOGGER.debug('Setting shader function')
    myRasterShader.setRasterShaderFunction(myColorRampShader)
    LOGGER.debug('Setting up renderer')
    myRenderer = QgsSingleBandPseudoColorRenderer(
        theQgsRasterLayer.dataProvider(),
        myBand,
        myRasterShader)
    LOGGER.debug('Assigning renderer to raster layer')
    theQgsRasterLayer.setRenderer(myRenderer)

    LOGGER.debug('Setting raster transparency list')

    myRenderer = theQgsRasterLayer.renderer()
    myTransparency = QgsRasterTransparency()
    myTransparency.setTransparentSingleValuePixelList(myTransparencyList)
    myRenderer.setRasterTransparency(myTransparency)
    # For interest you can also view the list like this:
    #pix = t.transparentSingleValuePixelList()
    #for px in pix:
    #    print 'Min: %s Max %s Percent %s' % (
    #       px.min, px.max, px.percentTransparent)

    LOGGER.debug('Saving style as default')
    theQgsRasterLayer.saveDefaultStyle()
    LOGGER.debug('Setting raster style done!')
    return myRampItemList, myTransparencyList
