# coding=utf-8
from qgis.core import (
    qgsfunction,
    QgsMapLayerRegistry,
    QgsExpressionContextUtils,
)

import datetime

from safe.definitions.provenance import provenance_layer_analysis_impacted_id
from safe.utilities.rounding import denomination, round_affected_number

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

##
# Docstrings for these expressions are used in the QGIS GUI in the Expression
# dialog and also in the InaSAFE Help dialog.
##


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
    if number is None:
        return None
    rounded_number = round_affected_number(
        number,
        enable_rounding=True,
        use_population_rounding=True
    )
    value, unit = denomination(rounded_number, 1000)
    if not unit:
        return None
    elif value > 1:
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

    if number >= 0:
        rounded_number = round_affected_number(
            number,
            enable_rounding=True,
            use_population_rounding=True
        )
        value, unit = denomination(rounded_number, 1000)
        return str(round(value, 1))
    else:
        return None


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[])
def inasafe_place_value_percentage(number, total, feature, parent):
    """Given a number and total, it will return the percentage of the number
    to the total.

    For instance:
    *   inasafe_place_value_percentage(inasafe_impact_analysis_layer(
        'female_displaced'), inasafe_impact_analysis_layer('displaced'))
        -> will calculate the percentage of female displaced count to total
        displaced count.

    It also can be used by pure number (int, float).
    """
    _ = feature, parent  # NOQA
    if number < 0:
        return None
    percentage_format = '{percentage}%'
    percentage = round((float(number) / float(total)) * 100, 1)
    return percentage_format.format(percentage=percentage)


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[])
def beautify_date(inasafe_time, feature, parent):
    """Given an inasafe analysis time, it will convert it to a date with
    year-month-date format.

    For instance:
    *   beautify_date( @start_datetime ) -> will convert datetime provided by
        qgis_variable.
    """
    _ = feature, parent  # NOQA
    datetime_object = datetime.datetime.strptime(
        inasafe_time, '%Y-%m-%dT%H:%M:%S.%f')
    date = datetime_object.strftime('%Y-%m-%d')
    return date


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[])
def beautify_time(inasafe_time, feature, parent):
    """Given an inasafe analysis time, it will convert it to a time with
    hour:minute format.

    For instance:
    *   beautify_date( @start_datetime ) -> will convert datetime provided by
        qgis_variable.
    """
    _ = feature, parent  # NOQA
    datetime_object = datetime.datetime.strptime(
        inasafe_time, '%Y-%m-%dT%H:%M:%S.%f')
    time = datetime_object.strftime('%H:%M')
    return time
