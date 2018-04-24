# coding=utf-8
"""Utilities module for helping definitions retrieval."""

from collections import OrderedDict
from copy import deepcopy
from os import listdir
from os.path import join, exists, splitext, split

from qgis.PyQt.QtXml import QDomDocument, QDomNode
from qgis.core import QgsApplication

from safe import definitions
from safe.definitions import fields
from safe.definitions import (
    layer_purposes,
    hazard_all,
    exposure_all,
    hazard_category_all,
    aggregation_fields,
    impact_fields,
    aggregation_name_field,
    hazard_value_field,
    exposure_type_field,
    exposure_fields,
    hazard_fields,
    layer_purpose_hazard,
    layer_purpose_exposure,
    layer_purpose_aggregation,
    layer_purpose_exposure_summary,
    exposure_population,
    not_exposed_class,
)
from safe.definitions.reports.report_descriptions import (
    landscape_map_report_description, portrait_map_report_description)
from safe.report.report_metadata import QgisComposerComponentsMetadata
from safe.utilities.settings import setting

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def purposes_for_layer(layer_geometry_key):
    """Get purposes of a layer geometry id.

    :param layer_geometry_key: The geometry id
    :type layer_geometry_key: str

    :returns: List of suitable layer purpose.
    :rtype: list
    """
    return_value = []
    for layer_purpose in layer_purposes:
        layer_geometry_keys = [
            i['key'] for i in layer_purpose['allowed_geometries']]
        if layer_geometry_key in layer_geometry_keys:
            return_value.append(layer_purpose['key'])

    return sorted(return_value)


def hazards_for_layer(layer_geometry_key):
    """Get hazard categories form layer_geometry_key.

    :param layer_geometry_key: The geometry id
    :type layer_geometry_key: str

    :returns: List of hazard
    :rtype: list
    """
    result = []
    for hazard in hazard_all:
        if layer_geometry_key in hazard.get('allowed_geometries'):
            result.append(hazard)

    return sorted(result, key=lambda k: k['key'])


def exposures_for_layer(layer_geometry_key):
    """Get hazard categories form layer_geometry_key

    :param layer_geometry_key: The geometry key
    :type layer_geometry_key: str

    :returns: List of hazard
    :rtype: list
    """
    result = []
    for exposure in exposure_all:
        if layer_geometry_key in exposure.get('allowed_geometries'):
            result.append(exposure)

    return sorted(result, key=lambda k: k['key'])


def hazard_categories_for_layer():
    """Get hazard categories

    :returns: List of hazard_categories
    :rtype: list
    """
    return sorted(hazard_category_all, key=lambda k: k['key'])


def get_layer_modes(subcategory):
    """Return all sorted layer modes from exposure or hazard.

    :param subcategory: Hazard or Exposure key.
    :type subcategory: str

    :returns: List of layer modes definition.
    :rtype: list
    """
    layer_modes = definition(subcategory)['layer_modes']
    return sorted(layer_modes, key=lambda k: k['key'])


def hazard_units(hazard):
    """Helper to get unit of a hazard.

    :param hazard: Hazard type.
    :type hazard: str

    :returns: List of hazard units.
    :rtype: list
    """
    units = definition(hazard)['continuous_hazard_units']
    return sorted(units, key=lambda k: k['key'])


def exposure_units(exposure):
    """Helper to get unit of an exposure.

    :param exposure: Exposure type.
    :type exposure: str

    :returns: List of exposure units.
    :rtype: list
    """
    units = definition(exposure)['units']
    return sorted(units, key=lambda k: k['key'])


def get_classifications(subcategory_key):
    """Get hazard or exposure classifications.

    :param subcategory_key: The hazard or exposure key
    :type subcategory_key: str

    :returns: List of hazard or exposure classifications
    :rtype: list
    """
    classifications = definition(subcategory_key)['classifications']
    return sorted(classifications, key=lambda k: k['key'])


def get_fields(
        layer_purpose, layer_subcategory=None, replace_null=None,
        in_group=True):
    """Get all field based on the layer purpose.

    :param layer_purpose: The layer purpose.
    :type layer_purpose: str

    :param layer_subcategory: Exposure or hazard value.
    :type layer_subcategory: str

    :param replace_null: If None all fields are returned, if True only if
        it's True, if False only if it's False.
    :type replace_null: None or bool

    :param in_group: Flag to include field in field_groups or not.
    :type in_group: bool

    :returns: List of fields.
    :rtype: list
    """
    fields_for_purpose = []
    if layer_purpose == layer_purpose_exposure['key']:
        if layer_subcategory:
            subcategory = definition(layer_subcategory)
            fields_for_purpose += subcategory['compulsory_fields']
            fields_for_purpose += subcategory['fields']
            fields_for_purpose += subcategory['extra_fields']
        else:
            fields_for_purpose = deepcopy(exposure_fields)
    elif layer_purpose == layer_purpose_hazard['key']:
        if layer_subcategory:
            subcategory = definition(layer_subcategory)
            fields_for_purpose += subcategory['compulsory_fields']
            fields_for_purpose += subcategory['fields']
            fields_for_purpose += subcategory['extra_fields']
        else:
            fields_for_purpose = deepcopy(hazard_fields)
    elif layer_purpose == layer_purpose_aggregation['key']:
        fields_for_purpose = deepcopy(aggregation_fields)
    elif layer_purpose == layer_purpose_exposure_summary['key']:
        fields_for_purpose = deepcopy(impact_fields)

    if in_group:
        field_groups = get_field_groups(layer_purpose, layer_subcategory)
        fields_for_purpose += fields_in_field_groups(field_groups)

    if isinstance(replace_null, bool):
        fields_for_purpose = [
            f for f in fields_for_purpose
            if f.get('replace_null') == replace_null]
        return fields_for_purpose
    else:
        return fields_for_purpose


def get_compulsory_fields(layer_purpose, layer_subcategory=None):
    """Get compulsory field based on layer_purpose and layer_subcategory

    :param layer_purpose: The layer purpose.
    :type layer_purpose: str

    :param layer_subcategory: Exposure or hazard value.
    :type layer_subcategory: str

    :returns: Compulsory field
    :rtype: dict
    """
    if not layer_subcategory:
        if layer_purpose == 'hazard':
            return hazard_value_field
        elif layer_purpose == 'exposure':
            return exposure_type_field
        elif layer_purpose == 'aggregation':
            return aggregation_name_field
        else:
            return None
    else:
        return definition(layer_subcategory).get('compulsory_fields')[0]


def get_non_compulsory_fields(layer_purpose, layer_subcategory=None):
    """Get non compulsory field based on layer_purpose and layer_subcategory.

    Used for get field in InaSAFE Fields step in wizard.

    :param layer_purpose: The layer purpose.
    :type layer_purpose: str

    :param layer_subcategory: Exposure or hazard value.
    :type layer_subcategory: str

    :returns: Compulsory fields
    :rtype: list
    """
    all_fields = get_fields(
        layer_purpose, layer_subcategory, replace_null=False)
    compulsory_field = get_compulsory_fields(
        layer_purpose, layer_subcategory)
    if compulsory_field in all_fields:
        all_fields.remove(compulsory_field)
    return all_fields


def definition(keyword, key=None):
    """Given a keyword and a key (optional), try to get a definition
    dict for it.

    .. versionadded:: 3.2

    Definition dicts are defined in keywords.py. We try to return
    one if present, otherwise we return none. Using this method you
    can present rich metadata to the user e.g.

    keyword = 'layer_purpose'
    kio = safe.utilities.keyword_io.Keyword_IO()
    definition = kio.definition(keyword)
    print definition

    :param keyword: A keyword key.
    :type keyword: str

    :param key: A specific key for a deeper search
    :type key: str

    :returns: A dictionary containing the matched key definition
        from definitions, otherwise None if no match was found.
    :rtype: dict, None
    """

    for item in dir(definitions):
        if not item.startswith("__"):
            var = getattr(definitions, item)
            if isinstance(var, dict):
                if var.get('key') == keyword or var.get(key) == keyword:
                    return var
    return None


def get_name(key):
    """Given a keyword, try to get the name of it.

    .. versionadded:: 4.2

    Definition dicts are defined in keywords.py. We try to return
    the name if present, otherwise we return none.

    keyword = 'layer_purpose'
    kio = safe.utilities.keyword_io.Keyword_IO()
    name = kio.get_name(keyword)
    print name

    :param key: A keyword key.
    :type key: str

    :returns: The name of the keyword
    :rtype: str
    """
    definition_dict = definition(key)
    if definition_dict:
        return definition_dict.get('name', key)
    # Else, return the keyword
    return key


def get_class_name(class_key, classification_key):
    """Helper to get class name from a class_key of a classification.

    :param class_key: The key of the class.
    :type class_key: str

    :type classification_key: The key of a classification.
    :param classification_key: str

    :returns: The name of the class.
    :rtype: str
    """
    classification = definition(classification_key)
    for the_class in classification['classes']:
        if the_class.get('key') == class_key:
            return the_class.get('name', class_key)
    return class_key


def get_allowed_geometries(layer_purpose_key):
    """Helper function to get all possible geometry

    :param layer_purpose_key: A layer purpose key.
    :type layer_purpose_key: str

    :returns: List of all allowed geometries.
    :rtype: list
    """
    preferred_order = [
        'point',
        'line',
        'polygon',
        'raster'
    ]
    allowed_geometries = set()
    all_layer_type = []
    if layer_purpose_key == layer_purpose_hazard['key']:
        all_layer_type = hazard_all
    elif layer_purpose_key == layer_purpose_exposure['key']:
        all_layer_type = exposure_all

    for layer in all_layer_type:
        for allowed_geometry in layer['allowed_geometries']:
            allowed_geometries.add(allowed_geometry)

    allowed_geometries = list(allowed_geometries)
    allowed_geometries_definition = []
    for allowed_geometry in allowed_geometries:
        allowed_geometries_definition.append(definition(allowed_geometry))

    # Adapted from http://stackoverflow.com/a/15650556/1198772
    order_dict = {color: index for index, color in enumerate(preferred_order)}
    allowed_geometries_definition.sort(key=lambda x: order_dict[x["key"]])

    return allowed_geometries_definition


def all_default_fields():
    """Helper to retrieve all fields which has default value.

    :returns: List of default fields.
    :rtype: list
    """
    default_fields = []
    for item in dir(fields):
        if not item.startswith("__"):
            var = getattr(definitions, item)
            if isinstance(var, dict):
                if var.get('replace_null', False):
                    default_fields.append(var)
    return default_fields


def postprocessor_output_field(postprocessor_definition):
    """Extract postprocessor output field definition.

    :param postprocessor_definition: Postprocessor definition
    :type postprocessor_definition: dict

    :return: Field definition of postprocessor output
    :rtype: dict
    """
    return list(postprocessor_definition['output'].items())[0][1]['value']


def default_classification_thresholds(classification, unit=None):
    """Helper to get default thresholds from classification and unit.

    :param classification: Classification definition.
    :type classification: dict

    :param unit: Unit key definition.
    :type unit: basestring

    :returns: Dictionary with key = the class key and value = list of
        default numeric minimum and maximum value.
    :rtype: dict
    """
    thresholds = {}
    for hazard_class in classification['classes']:
        if isinstance(hazard_class['numeric_default_min'], dict):
            min_value = hazard_class['numeric_default_min'][unit]
        else:
            min_value = hazard_class['numeric_default_min']
        if isinstance(hazard_class['numeric_default_max'], dict):
            max_value = hazard_class['numeric_default_max'][unit]
        else:
            max_value = hazard_class['numeric_default_max']
        thresholds[hazard_class['key']] = [min_value, max_value]

    return thresholds


def default_classification_value_maps(classification):
    """Helper to get default value maps from classification.

    :param classification: Classification definition.
    :type classification: dict

    :returns: Dictionary with key = the class key and value = default strings.
    :rtype: dict
    """
    value_maps = {}
    for hazard_class in classification['classes']:
        value_maps[hazard_class['key']] = hazard_class.get(
            'string_defaults', [])

    return value_maps


def fields_in_field_groups(field_groups):
    """Obtain list of fields from a list of field groups

    :param field_groups: List of field group.
    :type field_groups: list

    :returns: List of fields.
    :rtype: list
    """
    field_list = []
    for field_group in field_groups:
        field_list += field_group['fields']
    return field_list


def get_field_groups(layer_purpose, layer_subcategory=None):
    """Obtain list of field groups from layer purpose and subcategory.

    :param layer_purpose: The layer purpose.
    :type layer_purpose: str

    :param layer_subcategory: Exposure or hazard value.
    :type layer_subcategory: str

    :returns: List of layer groups.
    :rtype: list
    """
    layer_purpose_dict = definition(layer_purpose)
    if not layer_purpose_dict:
        return []
    field_groups = deepcopy(layer_purpose_dict.get('field_groups', []))
    if layer_purpose in [
            layer_purpose_exposure['key'], layer_purpose_hazard['key']]:
        if layer_subcategory:
            subcategory = definition(layer_subcategory)
            if 'field_groups' in subcategory:
                field_groups += deepcopy(subcategory['field_groups'])
    return field_groups


def override_component_template(component, template_path):
    """Override a default component with a new component with given template.

    :param component: Component as dictionary.
    :type component: dict

    :param template_path: Custom template path that will be used.
    :type template_path: str

    :returns: New report component.
    :rtype: dict
    """
    copy_component = deepcopy(component)
    template_directory, template_filename = split(template_path)
    file_name, file_format = splitext(template_filename)
    if file_format[1:] != (
            QgisComposerComponentsMetadata.OutputFormat.QPT) or (
                not exists(template_path)):
        return copy_component

    # we do the import here to avoid circular import when starting
    # up the plugin
    from safe.definitions.reports.components import (
        map_report_component_boilerplate)
    custom_template_component = deepcopy(
        map_report_component_boilerplate)

    # we need to update several items in this component
    pdf_output_file = '{file_name}.pdf'.format(file_name=file_name)
    qpt_output_file = '{file_name}.qpt'.format(file_name=file_name)

    custom_template_component['key'] = file_name
    custom_template_component['template'] = template_path
    custom_template_component['output_path']['template'] = qpt_output_file
    custom_template_component['output_path']['map'] = pdf_output_file

    # we need to update the orientation of the custom template
    with open(custom_template_component['template']) as (
            template_file):
        template_content = template_file.read()
    document = QDomDocument()
    document.setContent(template_content)
    root_element = document.namedItem('Composer')
    composition_element = root_element.namedItem('Composition')
    all_orientations = [
        landscape_map_report_description,
        portrait_map_report_description
    ]
    orientation = None
    if isinstance(root_element, QDomNode):
        paper_width = composition_element.attributes().namedItem(
            'paperWidth').nodeValue()
        paper_height = composition_element.attributes().namedItem(
            'paperHeight').nodeValue()
        for _orientation in all_orientations:
            if _orientation['width'] == int(paper_width) and (
                    _orientation['height'] == int(paper_height)):
                orientation = _orientation['orientation']
                break

    # By default, the component is landscape oriented, So if we found that
    # the custom template is portrait, we need to delete the information about
    # orientation in the component because in the report metadata, if there is
    # no specification about the orientation, then they will set it
    # to portrait.
    if orientation == portrait_map_report_description['orientation']:
        custom_template_component['orientation'] = orientation
        del custom_template_component['page_width']
        del custom_template_component['page_height']

    copy_component['components'] = [custom_template_component]

    return copy_component


def update_template_component(
        component, custom_template_dir=None, hazard=None, exposure=None):
    """Get a component based on custom qpt if exists

    :param component: Component as dictionary.
    :type component: dict

    :param custom_template_dir: The directory where the custom template stored.
    :type custom_template_dir: basestring

    :param hazard: The hazard definition.
    :type hazard: dict

    :param exposure: The exposure definition.
    :type exposure: dict

    :returns: Map report component.
    :rtype: dict
    """
    copy_component = deepcopy(component)

    # get the default template component from the original map report component
    default_component_keys = []
    for component in copy_component['components']:
        default_component_keys.append(component['key'])

    if not custom_template_dir:
        # noinspection PyArgumentList
        custom_template_dir = join(
            QgsApplication.qgisSettingsDirPath(), 'inasafe')

    for component in copy_component['components']:
        if not component.get('template'):
            continue

        template_format = splitext(component['template'])[-1][1:]
        if template_format != QgisComposerComponentsMetadata.OutputFormat.QPT:
            continue

        qpt_file_name = component['template'].split('/')[-1]
        custom_qpt_path = join(custom_template_dir, qpt_file_name)
        if exists(custom_qpt_path):
            component['template'] = custom_qpt_path

    # we want to check if there is hazard-exposure specific template available
    # in user's custom template directory
    if exists(custom_template_dir) and hazard and exposure:
        for filename in listdir(custom_template_dir):

            file_name, file_format = splitext(filename)
            if file_format[1:] != (
                    QgisComposerComponentsMetadata.OutputFormat.QPT):
                continue
            if hazard['key'] in file_name and exposure['key'] in file_name:
                # we do the import here to avoid circular import when starting
                # up the plugin
                from safe.definitions.reports.components import (
                    map_report_component_boilerplate)
                hazard_exposure_component = deepcopy(
                    map_report_component_boilerplate)

                # we need to update several items in this component
                pdf_output_file = '{file_name}.pdf'.format(file_name=file_name)
                qpt_output_file = '{file_name}.qpt'.format(file_name=file_name)

                hazard_exposure_component['key'] = file_name
                hazard_exposure_component['template'] = join(
                    custom_template_dir, filename)
                hazard_exposure_component['output_path']['template'] = (
                    qpt_output_file)
                hazard_exposure_component['output_path']['map'] = (
                    pdf_output_file)

                # add this hazard-exposure component to the returned component
                copy_component['components'].append(hazard_exposure_component)

                # remove the original template component because we want to
                # override it using this new hazard-exposure template component
                new_component = [
                    component for component in copy_component['components']
                    if component['key'] not in default_component_keys
                ]
                copy_component['components'] = new_component

    return copy_component


def set_provenance(provenance_collection, provenance_dict, value):
    """Helper to set provenance_dict to provenance_collection.

    :param provenance_collection: The target of dictionary of provenance to
        be updated.
    :type provenance_collection: dict

    :param provenance_dict: The provenance dictionary to be the key.
    :type provenance_dict: dict

    :param value: The value that will be set.
    :type value: object
    """
    provenance_collection[provenance_dict['provenance_key']] = value


def get_provenance(provenance_collection, provenance_dict):
    """Helper to get provenance_dict value from provenance_collection.

    :param provenance_collection: The target of dictionary of provenance to
        be updated.
    :type provenance_collection: dict

    :param provenance_dict: The provenance dictionary to be the key.
    :type provenance_dict: dict

    :returns: The value of the provenance.
    :rtype value: object
    """
    return provenance_collection.get(provenance_dict['provenance_key'])


# TODO(IS): Add parameter to filter the exposure
def generate_default_profile():
    """Helper to create data format from default definitions.
    Example:

        Flood:
            - Flood classification A
                - Flood class 1: affected, displacement_rate
                - Flood class 2: affected, displacement_rate
            - Flood classification B
                - Flood class 1: affected, displacement_rate
                - Flood class 2: affected, displacement_rate
        Earthquake:
            - EQ classification A
                - EQ class 1: affected, displacement_rate
                - EQ class 2: affected, displacement_rate
            - EQ classification B
                - EQ class 1: affected, displacement_rate
                - EQ class 2: affected, displacement_rate

    :returns: A dictionary like the format above.
    :rtype: dict
    """
    data_format = {}
    for hazard in hazard_all:
        if exposure_population in hazard['disabled_exposures']:
            continue
        data_format[hazard['key']] = {}
        for classification in hazard['classifications']:
            data_format[hazard['key']][classification['key']] = OrderedDict()
            for the_class in classification['classes']:
                entry = {
                    'affected': the_class['affected'],
                    'displacement_rate': the_class['displacement_rate'],
                }
                data_format[hazard['key']][classification['key']][the_class[
                    'key']] = entry

    return data_format


def get_displacement_rate(
        hazard, classification, hazard_class, qsettings=None):
    """Get displacement rate for hazard in classification in hazard class.

    :param hazard: The hazard key.
    :type hazard: basestring

    :param classification: The classification key.
    :type classification: basestring

    :param hazard_class: The hazard class key.
    :type hazard_class: basestring

    :param qsettings: A custom QSettings to use. If it's not defined, it will
        use the default one.
    :type qsettings: qgis.PyQt.QtCore.QSettings

    :returns: The value of displacement rate. If it's not affected, return 0.
    :rtype: int
    """
    is_affected_value = is_affected(
        hazard, classification, hazard_class, qsettings)
    if is_affected_value == not_exposed_class['key']:
        return 0  # Just to make it clear
    elif not is_affected_value:
        return 0
    preference_data = setting(
        'population_preference',
        default=generate_default_profile(),
        qsettings=qsettings)

    # Use default from the default profile
    default_profile = generate_default_profile()
    default_displacement_rate_value = default_profile.get(hazard, {}).get(
        classification, {}).get(hazard_class, {}).get('displacement_rate', 0)

    # noinspection PyUnresolvedReferences
    return preference_data.get(hazard, {}).get(classification, {}).get(
        hazard_class, {}).get(
        'displacement_rate', default_displacement_rate_value)


def is_affected(hazard, classification, hazard_class, qsettings=None):
    """Get affected flag for hazard in classification in hazard class.

    :param hazard: The hazard key.
    :type hazard: basestring

    :param classification: The classification key.
    :type classification: basestring

    :param hazard_class: The hazard class key.
    :type hazard_class: basestring

    :param qsettings: A custom QSettings to use. If it's not defined, it will
        use the default one.
    :type qsettings: qgis.PyQt.QtCore.QSettings

    :returns: True if it's affected, else False. Default to False.
    :rtype: bool
    """
    preference_data = setting(
        'population_preference',
        default=generate_default_profile(),
        qsettings=qsettings)

    # Use default from the default profile
    default_profile = generate_default_profile()
    default_affected_value = default_profile.get(hazard, {}).get(
        classification, {}).get(hazard_class, {}).get(
        'affected', not_exposed_class['key'])
    # noinspection PyUnresolvedReferences
    return preference_data.get(hazard, {}).get(classification, {}).get(
        hazard_class, {}).get('affected', default_affected_value)
