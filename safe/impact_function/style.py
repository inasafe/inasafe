# coding=utf-8

"""Styles."""

from collections import OrderedDict
from qgis.core import (
    QgsSymbolV2,
    QgsRendererCategoryV2,
    QgsSingleSymbolRendererV2,
    QgsCategorizedSymbolRendererV2,
    QgsSymbolLayerV2Registry,
    QgsConditionalStyle,
)

from safe.definitions.colors import grey, line_width_exposure
from safe.definitions.fields import hazard_class_field, hazard_count_field
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

    attribute_table_styles = []

    for hazard_class, (color, label) in classification.iteritems():
        if hazard_class == null_hazard_value and not display_null:
            # We don't want to display the null value (not exposed).
            # We skip it.
            continue

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


def generate_classified_legend(
        analysis, hazard_classification, thresholds, unit, enable_rounding):
    """Generate an ordered python structure with the classified symbology.

    :param analysis: The analysis layer.
    :type analysis: QgsVectorLayer

    :param hazard_classification: The hazard classification to use.
    :type hazard_classification: safe.definitions.hazard_classifications

    :param thresholds: Thresholds used on the hazard. It can be null if the
        does not have any thresholds.
    :type thresholds: dict

    :param unit: The unit to use.
    :type unit: safe.definitions.units

    :param enable_rounding: Boolean if we should round numbers.
    :type enable_rounding: bool

    :return: The ordered dictionary to use to build the classified style.
    :rtype: OrderedDict
    """
    # We need to read the analysis layer to get the number of features.
    analysis_row = analysis.getFeatures().next()

    # Todo, implement thresholds in the label.

    template = u'{name} ({value} {unit})'

    classes = OrderedDict()

    not_exposed_field = hazard_count_field['field_name'] % null_hazard_value
    try:
        value = analysis_row[not_exposed_field]
    except KeyError:
        # The field might not exist if there is not feature not exposed.
        value = 0
    # Rounded disabled until we know when we should round values.
    # value = round_affected_number(value, enable_rounding, True)
    label = template.format(
        name=null_hazard_legend, value=value, unit=unit['abbreviation'])
    classes[null_hazard_value] = (grey, label)

    for hazard_class in reversed(hazard_classification['classes']):
        field_name = hazard_count_field['field_name'] % hazard_class['key']
        try:
            value = analysis_row[field_name]
        except KeyError:
            # The field might not exist if no feature impacted in this hazard
            # zone.
            value = 0
        # Rounded disabled until we know when we should round values.
        # value = round_affected_number(value, enable_rounding, True)
        label = template.format(
            name=hazard_class['name'], value=value, unit=unit['abbreviation'])
        classes[hazard_class['key']] = (hazard_class['color'], label)

    return classes


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
