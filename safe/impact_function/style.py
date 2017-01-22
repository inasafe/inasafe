# coding=utf-8

"""Styles."""

from qgis.core import (
    QgsSymbolV2,
    QgsRendererCategoryV2,
    QgsSingleSymbolRendererV2,
    QgsCategorizedSymbolRendererV2,
    QgsSymbolLayerV2Registry,
    QgsConditionalStyle,
)

from safe.definitions.colors import grey, line_width_exposure
from safe.definitions.fields import hazard_class_field
from safe.definitions.hazard_classifications import (
    null_hazard_value, null_hazard_legend)
from safe.definitions.utilities import definition
from safe.utilities.gis import is_line_layer


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def hazard_class_style(layer, classification, display_null=False):
    """Set colors to the layer according to the hazard.

    :param layer: The layer to style.
    :type layer: QgsVectorLayer

    :param display_null: If we should display the null hazard zone. Default to
        False.
    :type display_null: bool

    :param classification: The hazard classification to use.
    :type classification: dict safe.definitions.hazard_classifications
    """
    categories = []

    if display_null:
        symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        symbol.setColor(grey)
        if is_line_layer(layer):
            symbol.setWidth(line_width_exposure)
        category = QgsRendererCategoryV2(
            null_hazard_value, symbol, null_hazard_legend)
        categories.append(category)

    attribute_table_styles = []

    for hazard_class, (color, label) in classification.iteritems():
        symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        symbol.setColor(color)
        if is_line_layer(layer):
            symbol.setWidth(line_width_exposure)
        category = QgsRendererCategoryV2(hazard_class, symbol, label)
        categories.append(category)

        style = QgsConditionalStyle()
        style.setName(hazard_class)
        style.setBackgroundColor(color.lighter())
        style.setRule("hazard_class='%s'" % hazard_class)
        attribute_table_styles.append(style)

    # Disabled until we improve it a little bit. ET 20/01/17.
    # layer.conditionalStyles().setRowStyles(attribute_table_styles)
    renderer = QgsCategorizedSymbolRendererV2(
        hazard_class_field['field_name'], categories)
    layer.setRendererV2(renderer)


def layer_title(layer):
    """Set the layer title according to the standards.

    :param layer: The layer to style.
    :type layer: QgsVectorLayer
    """
    exposure_type = layer.keywords['exposure_keywords']['exposure']
    exposure_definitions = definition(exposure_type)
    title = exposure_definitions['layer_legend_title']
    layer.setTitle(title)
    layer.keywords['title'] = title


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
