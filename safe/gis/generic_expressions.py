# coding=utf-8

"""QGIS Expressions which are available in the QGIS GUI interface."""

import datetime

from qgis.core import (
    qgsfunction,
    QgsMapLayerRegistry,
    QgsExpressionContextUtils
)

from safe.definitions.extra_keywords import all_extra_keywords_description
from safe.definitions.provenance import provenance_layer_analysis_impacted_id
from safe.definitions.utilities import definition
from safe.gis.tools import load_layer
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.rounding import denomination, round_affected_number
from safe.utilities.utilities import generate_expression_help

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

##
# For QGIS < 2.18.13 and QGIS < 2.14.19, docstrings are used in the QGIS GUI
# in the Expression dialog and also in the InaSAFE Help dialog.
#
# For QGIS >= 2.18.13, QGIS >= 2.14.19 and QGIS 3, the translated variable will
# be used in QGIS.
# help_text is used for QGIS 2.18 and 2.14
# helpText is used for QGIS 3 : https://github.com/qgis/QGIS/pull/5059
##

description = tr('Retrieve a value from a field in the impact analysis layer.')
examples = {
    'inasafe_impact_analysis_field_value(\'total_not_exposed\')': 3
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def inasafe_impact_analysis_field_value(field, feature, parent):
    """Retrieve a value from a field in the impact analysis layer.

    e.g. inasafe_impact_analysis_field_value('total_not_exposed') -> 3
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


description = tr(
    'Given a number, it will return the place value name. It needs to be used '
    'with inasafe_place_value_coefficient.')
examples = {
    'inasafe_place_value_name(10)': tr('Ten'),
    'inasafe_place_value_name(1700)': tr('Thousand')
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
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
        use_rounding=True,
        use_population_rounding=True
    )
    value, unit = denomination(rounded_number, 1000)
    if not unit:
        return None
    else:
        return unit['name']


description = tr(
    'Given a number, it will return the coefficient of the place value name. '
    'It needs to be used with inasafe_number_denomination_unit.')
examples = {
    'inasafe_place_value_coefficient(10)': 1,
    'inasafe_place_value_coefficient(1700)': 1.7
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
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
            use_rounding=True,
            use_population_rounding=True
        )
        min_number = 1000
        value, unit = denomination(rounded_number, min_number)
        if number < min_number:
            rounded_number = int(round(value, 1))
        else:
            rounded_number = round(value, 1)
        return str(rounded_number)
    else:
        return None


description = tr(
    'Given a number and total, it will return the percentage of the number to '
    'the total.')
examples = {
    'inasafe_place_value_percentage(inasafe_impact_analysis_field_value('
    '\'female_displaced\'), '
    'inasafe_impact_analysis_field_value(\'displaced\'))': tr(
        'will calculate the percentage of female displaced count to total '
        'displaced count.'),
    'inasafe_place_value_percentage(50,100)': '50.0%'
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def inasafe_place_value_percentage(number, total, feature, parent):
    """Given a number and total, it will return the percentage of the number
    to the total.

    For instance:
    *   inasafe_place_value_percentage(inasafe_impact_analysis_field_value(
        'female_displaced'), inasafe_impact_analysis_field_value('displaced'))
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


description = tr(
    'Given an InaSAFE analysis time, it will convert it to a date with '
    'year-month-date format.')
examples = {
    'beautify_date( @start_datetime )': tr(
        'will convert datetime provided by qgis_variable.')
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def beautify_date(inasafe_time, feature, parent):
    """Given an InaSAFE analysis time, it will convert it to a date with
    year-month-date format.

    For instance:
    *   beautify_date( @start_datetime ) -> will convert datetime provided by
        qgis_variable.
    """
    _ = feature, parent  # NOQA
    try:
        datetime_object = datetime.datetime.strptime(
            inasafe_time, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        try:
            datetime_object = datetime.datetime.strptime(
                inasafe_time, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return datetime
    date = datetime_object.strftime('%Y-%m-%d')
    return date


description = tr(
    'Given an InaSAFE analysis time, it will convert it to a time with '
    'hour:minute format.')
examples = {
    'beautify_date( @start_datetime )': tr(
        'will convert datetime provided by qgis_variable.')
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def beautify_time(inasafe_time, feature, parent):
    """Given an InaSAFE analysis time, it will convert it to a time with
    hour:minute format.

    For instance:
    *   beautify_date( @start_datetime ) -> will convert datetime provided by
        qgis_variable.
    """
    _ = feature, parent  # NOQA
    try:
        datetime_object = datetime.datetime.strptime(
            inasafe_time, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        try:
            datetime_object = datetime.datetime.strptime(
                inasafe_time, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return datetime
    time = datetime_object.strftime('%H:%M')
    return time


description = tr(
    "Given a keyword, it will return the value of the keyword "
    "from the hazard layer's extra keywords.")
examples = {
    "hazard_extra_keyword( 'depth' )": tr(
        "will return the value of 'depth' in "
        "current hazard layer's extra keywords")
}
extra_information = {
    'title': tr("Available keywords:"),
    'detail': all_extra_keywords_description
}
help_message = generate_expression_help(
    description, examples, extra_information=extra_information)


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def hazard_extra_keyword(keyword, feature, parent):
    """Given a keyword, it will return the value of the keyword
    from the hazard layer's extra keywords.

    For instance:
    *   hazard_extra_keyword( 'depth' ) -> will return the value of 'depth'
        in current hazard layer's extra keywords.
    """
    _ = feature, parent  # NOQA
    hazard_layer_path = QgsExpressionContextUtils.projectScope().variable(
        'hazard_layer')
    hazard_layer = load_layer(hazard_layer_path)[0]
    keywords = KeywordIO.read_keywords(hazard_layer)
    extra_keywords = keywords.get('extra_keywords')
    if extra_keywords:
        value = extra_keywords.get(keyword)
        if value:
            value_definition = definition(value)
            if value_definition:
                return value_definition['name']
            return value
        else:
            return tr('Keyword %s is not found' % keyword)
    return tr('No extra keywords found')
