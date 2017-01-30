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

from safe.definitions.styles import (
    line_width_exposure,
    template_without_thresholds,
    template_with_minimum_thresholds,
    template_with_maximum_thresholds,
    template_with_range_thresholds,
)
from safe.definitions.fields import hazard_class_field, hazard_count_field
from safe.definitions.hazard_classifications import not_exposed_class
from safe.definitions.utilities import definition
from safe.utilities.gis import is_line_layer
from safe.utilities.rounding import round_affected_number


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
        if hazard_class == not_exposed_class['key'] and not display_null:
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
        analysis,
        exposure,
        hazard,
        debug_mode):
    """Generate an ordered python structure with the classified symbology.

    :param analysis: The analysis layer.
    :type analysis: QgsVectorLayer

    :param exposure: The exposure layer.
    :type exposure: QgsVectorLayer

    :param hazard: The hazard layer.
    :type hazard: QgsVectorLayer

    :param debug_mode: Boolean if run in debug mode.
    :type debug_mode: bool

    :return: The ordered dictionary to use to build the classified style.
    :rtype: OrderedDict
    """
    # We need to read the analysis layer to get the number of features.
    analysis_row = analysis.getFeatures().next()

    # Let's style the hazard class in each layers.
    hazard_classification = hazard.keywords['classification']
    hazard_classification = definition(hazard_classification)

    # Let's check if there is some thresholds:
    thresholds = hazard.keywords.get('thresholds')
    if thresholds:
        hazard_unit = hazard.keywords.get('continuous_hazard_unit')
        hazard_unit = definition(hazard_unit)['abbreviation']
    else:
        hazard_unit = None

    # TODO We need to work on the unit from the exposure.
    exposure = exposure.keywords['exposure']
    exposure_definitions = definition(exposure)
    exposure_unit = exposure_definitions['units'][0]['abbreviation']

    classes = OrderedDict()

    # In debug mode we don't round number.
    enable_rounding = not debug_mode

    for i, hazard_class in enumerate(hazard_classification['classes']):
        # Get the hazard class name.
        field_name = hazard_count_field['field_name'] % hazard_class['key']

        # Get the number of affected feature by this hazard class.
        try:
            value = analysis_row[field_name]
        except KeyError:
            # The field might not exist if no feature impacted in this hazard
            # zone.
            value = 0
        value = round_affected_number(value, enable_rounding, True)

        minimum = None
        maximum = None

        # Check if we need to add thresholds.
        if thresholds:
            if i == 0:
                minimum = thresholds[hazard_class['key']][0]
            elif i == len(hazard_classification['classes']) - 1:
                maximum = thresholds[hazard_class['key']][1]
            else:
                minimum = thresholds[hazard_class['key']][0]
                maximum = thresholds[hazard_class['key']][1]

        label = _format_label(
            hazard_class=hazard_class['name'],
            value=value,
            exposure_unit=exposure_unit,
            minimum=minimum,
            maximum=maximum,
            hazard_unit=hazard_unit)

        classes[hazard_class['key']] = (hazard_class['color'], label)

    if exposure_definitions['display_not_exposed'] or debug_mode:
        classes[not_exposed_class['key']] = _add_not_exposed(
            analysis_row, enable_rounding, exposure_unit)

    return classes


def _add_not_exposed(analysis_row, enable_rounding, exposure_unit):
    """Helper to add the `not exposed` item to the legend.

    :param analysis_row: The analysis row as a list.
    :type analysis_row: list

    :param enable_rounding: If we need to do a rounding.
    :type enable_rounding: bool

    :param exposure_unit: The exposure unit.
    :type exposure_unit: safe.definitions.units

    :return: A tuple with the color and the formatted label.
    :rtype: tuple
    """
    # We add the not exposed class at the end.
    not_exposed_field = (
        hazard_count_field['field_name'] % not_exposed_class['key'])
    try:
        value = analysis_row[not_exposed_field]
    except KeyError:
        # The field might not exist if there is not feature not exposed.
        value = 0
    value = round_affected_number(value, enable_rounding, True)
    label = _format_label(
        hazard_class=not_exposed_class['name'],
        value=value,
        exposure_unit=exposure_unit)

    return not_exposed_class['color'], label


def _format_label(
        hazard_class,
        value,
        exposure_unit,
        hazard_unit=None,
        minimum=None,
        maximum=None):
    """Helper function to format the label in the legend.

    :param hazard_class: The main name of the label.
    :type hazard_class: basestring

    :param value: The number of features affected by this hazard class.
    :type value: float

    :param exposure_unit: The exposure unit.
    :type exposure_unit: basestring

    :param hazard_unit: The hazard unit.
        It can be null if there isn't thresholds.
    :type hazard_unit: basestring

    :param minimum: The minimum value used in the threshold. It can be null.
    :type minimum: float

    :param maximum: The maximum value used in the threshold. It can be null.
    :type maximum: float

    :return: The formatted label.
    :rtype: basestring
    """

    # If the exposure unit is not null, we need to add a space.
    if exposure_unit != '':
        exposure_unit = ' %s' % exposure_unit

    if minimum is None and maximum is None:
        label = template_without_thresholds.format(
            name=hazard_class,
            count=value,
            exposure_unit=exposure_unit)
    elif minimum is not None and maximum is None:
        label = template_with_minimum_thresholds.format(
            name=hazard_class,
            count=value,
            exposure_unit=exposure_unit,
            min=minimum,
            hazard_unit=hazard_unit)
    elif minimum is None and maximum is not None:
        label = template_with_maximum_thresholds.format(
            name=hazard_class,
            count=value,
            exposure_unit=exposure_unit,
            max=maximum,
            hazard_unit=hazard_unit)
    else:
        label = template_with_range_thresholds.format(
            name=hazard_class,
            count=value,
            exposure_unit=exposure_unit,
            min=minimum,
            max=maximum,
            hazard_unit=hazard_unit)

    return label


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
