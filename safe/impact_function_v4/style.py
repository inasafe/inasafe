# coding=utf-8

"""
Styles.
"""

from qgis.core import (
    QgsSymbolV2,
    QgsRendererCategoryV2,
    QgsSingleSymbolRendererV2,
    QgsCategorizedSymbolRendererV2,
    QgsSymbolLayerV2Registry,
)

from safe.definitionsv4.colors import no_hazard
from safe.definitionsv4.fields import hazard_class_field


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def hazard_class_style(layer, classification):
    """Style for hazard class according to the standards.

    :param layer: The layer to style.
    :type layer: QgsVectorLayer

    :param classification: The hazard classification to use.
    :type classification: dict safe.definitionsv4.hazard_classifications
    """
    categories = []
    for hazard_class, (color, label) in classification.iteritems():
        symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        symbol.setColor(color)
        category = QgsRendererCategoryV2(hazard_class, symbol, label)
        categories.append(category)

    symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
    symbol.setColor(no_hazard)
    category = QgsRendererCategoryV2('', symbol, 'No hazard')
    categories.append(category)

    renderer = QgsCategorizedSymbolRendererV2(
        hazard_class_field['field_name'], categories)
    layer.setRendererV2(renderer)


def simple_polygon_without_brush(layer):
    """Simple style to apply a border line only to a polygon layer.

    :param layer: The layer to style.
    :type layer: QgsVectorLayer
    """
    registry = QgsSymbolLayerV2Registry.instance()
    line_metadata = registry.symbolLayerMetadata("SimpleLine")
    symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())

    # Line layer
    line_layer = line_metadata.createSymbolLayer(
        {
            'width': '0.26',
            'color': '0,0,0',
            'offset': '0',
            'penstyle': 'solid',
            'use_custom_dash': '0',
            'joinstyle': 'bevel',
            'capstyle': 'square'
        })

    # Replace the default layer with our custom line
    symbol.deleteSymbolLayer(0)
    symbol.appendSymbolLayer(line_layer)

    renderer = QgsSingleSymbolRendererV2(symbol)
    layer.setRendererV2(renderer)
