# coding=utf-8

"""QGIS Expressions which are available in the QGIS GUI interface."""

from qgis.core import qgsfunction

from safe.common.parameters.resource_parameter import ResourceParameter
from safe.definitions.fields import (
    under_5_displaced_count_field,
    over_60_displaced_count_field)
from safe.definitions.reports.infographic import (
    infographic_header,
    map_overview_header,
    people_section_header,
    age_gender_section_header,
    vulnerability_section_header,
    female_vulnerability_section_header,
    minimum_needs_section_header,
    additional_minimum_needs_section_header,
    population_chart_header,
    age_gender_section_notes,
    minimum_needs_section_notes)
from safe.definitions.units import exposure_unit
from safe.definitions.utilities import definition
from safe.utilities.i18n import tr
from safe.utilities.utilities import generate_expression_help

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

group = tr('InaSAFE - Infographic Elements')

##
# For QGIS < 2.18.13 and QGIS < 2.14.19, docstrings are used in the QGIS GUI
# in the Expression dialog and also in the InaSAFE Help dialog.
#
# For QGIS >= 2.18.13, QGIS >= 2.14.19 and QGIS 3, the translated variable will
# be used in QGIS.
# help_text is used for QGIS 2.18 and 2.14
# helpText is used for QGIS 3 : https://github.com/qgis/QGIS/pull/5059
##

description = tr('Retrieve a header name of the field name from definitions.')
examples = {
    'inasafe_field_header(\'minimum_needs__clean_water\')': tr('Clean water')
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def inasafe_field_header(field, feature, parent):
    """Retrieve a header name of the field name from definitions.

    For instance:
    inasafe_field_header('minimum_needs__clean_water') -> 'Clean water'
    """
    _ = feature, parent  # NOQA
    age_fields = [under_5_displaced_count_field, over_60_displaced_count_field]
    symbol_mapping = {
        'over': '>',
        'under': '<'
    }

    field_definition = definition(field, 'field_name')
    if field_definition:
        if field_definition in age_fields:
            header_format = tr('{symbol} {age} y.o')
            field_name = field_definition.get('field_name')
            if field_name:
                symbol, age = field_name.split('_')[:2]
                if symbol.lower() in list(symbol_mapping.keys()):
                    header_name = header_format.format(
                        symbol=symbol_mapping[symbol.lower()],
                        age=age
                    )
                    return header_name

        header_name = field_definition.get('header_name')
        name = field_definition.get('name')
        if header_name:
            return header_name.capitalize()
        else:
            return name.capitalize()
    return None


description = tr('Retrieve units of the given minimum needs field name.')
examples = {
    'minimum_needs_unit(\'minimum_needs__clean_water\')': tr('l/weekly')
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def minimum_needs_unit(field, feature, parent):
    """Retrieve units of the given minimum needs field name.

    For instance:
    * minimum_needs_unit('minimum_needs__clean_water') -> 'l/weekly'
    """
    _ = feature, parent  # NOQA
    field_definition = definition(field, 'field_name')
    if field_definition:
        unit_abbreviation = None
        frequency = None
        if field_definition.get('need_parameter'):
            need = field_definition['need_parameter']
            if isinstance(need, ResourceParameter):
                unit_abbreviation = need.unit.abbreviation
                frequency = need.frequency
        elif field_definition.get('unit'):
            need_unit = field_definition.get('unit')
            unit_abbreviation = need_unit.get('abbreviation')

        if field_definition.get('frequency') and not frequency:
            frequency = field_definition.get('frequency')

        if not unit_abbreviation:
            unit_abbreviation = exposure_unit['plural_name']

        once_frequency_field_keys = [
            'minimum_needs__toilets_count_field'
        ]
        if not frequency or (
                field_definition['key'] in once_frequency_field_keys):
            return unit_abbreviation.lower()

        unit_format = u'{unit_abbreviation}/{frequency}'
        return unit_format.format(
            unit_abbreviation=unit_abbreviation, frequency=frequency).lower()

    return None


description = tr(
    'Get a formatted infographic header sentence for an impact function.')
examples = {
    'infographic_header_element(\'flood\')': tr('Estimated impact of a flood')
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def infographic_header_element(impact_function_name, feature, parent):
    """Get a formatted infographic header sentence for an impact function.

    For instance:
    * infographic_header_element('flood') -> 'Estimated impact of a flood'
    """
    _ = feature, parent  # NOQA
    string_format = infographic_header['string_format']
    if impact_function_name:
        header = string_format.format(
            impact_function_name=impact_function_name)
        return header.capitalize()
    return None


description = tr('Retrieve map overview header string from definitions.')
examples = {
    'map_overview_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def map_overview_header_element(feature, parent):
    """Retrieve map overview header string from definitions."""
    _ = feature, parent  # NOQA
    header = map_overview_header['string_format']
    return header.capitalize()


description = tr('Retrieve population chart header string from definitions.')
examples = {
    'population_chart_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def population_chart_header_element(feature, parent):
    """Retrieve population chart header string from definitions."""
    _ = feature, parent  # NOQA
    header = population_chart_header['string_format']
    return header.capitalize()


description = tr('Retrieve people section header string from definitions.')
examples = {
    'people_section_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def people_section_header_element(feature, parent):
    """Retrieve people section header string from definitions."""
    _ = feature, parent  # NOQA
    header = people_section_header['string_format']
    return header.capitalize()


description = tr('Retrieve age gender section header string from definitions.')
examples = {
    'age_gender_section_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def age_gender_section_header_element(feature, parent):
    """Retrieve age gender section header string from definitions."""
    _ = feature, parent  # NOQA
    header = age_gender_section_header['string_format']
    return header.capitalize()


description = tr('Retrieve age gender section notes string from definitions.')
examples = {
    'age_gender_section_notes_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def age_gender_section_notes_element(feature, parent):
    """Retrieve age gender section notes string from definitions."""
    _ = feature, parent  # NOQA
    notes = age_gender_section_notes['string_format']
    return notes


description = tr(
    'Retrieve vulnerability section header string from definitions.')
examples = {
    'vulnerability_section_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def vulnerability_section_header_element(feature, parent):
    """Retrieve vulnerability section header string from definitions."""
    _ = feature, parent  # NOQA
    header = vulnerability_section_header['string_format']
    return header.capitalize()


description = tr(
    'Retrieve female vulnerability section header string from definitions.')
examples = {
    'female_vulnerability_section_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def female_vulnerability_section_header_element(feature, parent):
    """Retrieve female vulnerability section header string from definitions."""
    _ = feature, parent  # NOQA
    header = female_vulnerability_section_header['string_format']
    return header.capitalize()


description = tr(
    'Retrieve minimum needs section header string from definitions.')
examples = {
    'minimum_needs_section_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def minimum_needs_section_header_element(feature, parent):
    """Retrieve minimum needs section header string from definitions."""
    _ = feature, parent  # NOQA
    header = minimum_needs_section_header['string_format']
    return header.capitalize()


description = tr(
    'Retrieve additional minimum needs section header string from definition.')
examples = {
    'additional_minimum_needs_section_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def additional_minimum_needs_section_header_element(feature, parent):
    """Retrieve additional minimum needs section header string
    from definitions.
    """
    _ = feature, parent  # NOQA
    header = additional_minimum_needs_section_header['string_format']
    return header.capitalize()


description = tr(
    'Retrieve minimum needs section notes string from definitions.')
examples = {
    'minimum_needs_section_notes_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def minimum_needs_section_notes_element(feature, parent):
    """Retrieve minimum needs section notes string from definitions."""
    _ = feature, parent  # NOQA
    notes = minimum_needs_section_notes['string_format']
    return notes
