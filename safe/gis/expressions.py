# coding=utf-8
from qgis.core import (
    qgsfunction,
    QgsMapLayerRegistry,
    QgsExpressionContextUtils,
)
from safe.definitions.provenance import provenance_layer_analysis_impacted_id
from safe.utilities.rounding import denomination

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[])
def inasafe_impact_analysis_layer(field, feature, parent):
    """Retrieve a value from a field in the impact analysis layer.

    For instance:  inasafe_impact_analysis_layer('total_not_exposed') -> 3
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    registry = QgsMapLayerRegistry.instance()

    key = provenance_layer_analysis_impacted_id['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    layer = registry.mapLayer(project_context_scope.variable(key))

    if not layer:
        return None

    index = layer.fieldNameIndex(field)
    if index < 0:
        return None

    feature = layer.getFeatures().next()
    return feature[index]


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[])
def inasafe_place_value_name(number, feature, parent):
    """Given a number, it will return the place value name.

    For instance:
    *  inasafe_place_value_name(10) -> Ten \n
    *  inasafe_place_value_name(1700) -> Thousand

    It needs to be used with inasafe_place_value_coefficient.
    """
    _ = feature, parent  # NOQA
    value, unit = denomination(number)
    if value > 1:
        return unit['plural_name']
    else:
        return unit['name']


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[])
def inasafe_place_value_coefficient(number, feature, parent):
    """Given a number, it will return the coefficient of the place value name.

    For instance:
    *  inasafe_place_value_coefficient(10) -> 1
    *  inasafe_place_value_coefficient(1700) -> 1.7

    It needs to be used with inasafe_number_denomination_unit.
    """
    _ = feature, parent  # NOQA
    value, unit = denomination(number)
    return value
