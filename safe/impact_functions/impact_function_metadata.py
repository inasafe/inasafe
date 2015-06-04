# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Function Metadata**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.
"""

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '14/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import json

from safe.common.utilities import add_to_list, get_list_key, is_key_exist
from safe.definitions import (
    layer_purpose_exposure,
    layer_purpose_hazard)


class ImpactFunctionMetadata(object):
    """Abstract metadata class for an impact function.

    .. versionadded:: 2.1

    There will be a concrete implementation of this interface which is specific
    to a single IF class. So anything returned (e.g. data_types) will only be
    relevant to the category/subcategories of the concrete implementation's IF.

        Example usage::

          foo = IF()
          meta = IF.metadata

          bar = meta.allowed_subcategories('exposure')
          bar
          > [structure]

    .. note:: We already know that for an IF only hazard and exposure
       categories are allowed, so there is no explicit method for that
       (we could change that later).
    """

    def __init__(self):
        """Constructor."""
        pass

    @staticmethod
    def simplify_layer_constraint(layer_constraint):
        """Simplify layer constraint to layer_type and data_type only.

        :param layer_constraint: Dictionary that represents layer_constraint
        :type layer_constraint: dict

        :returns: Simple version of layer_constraint
        :rtype: dict
        """
        simple_layer_constraint = {
            'layer_type': layer_constraint['layer_type'],
            'data_type': layer_constraint['data_type'],
            }

        return simple_layer_constraint

    @staticmethod
    def is_subset(element, container):
        """Check the membership of element from container.

        It will check based on the type. Only valid for string and list.

        :param element: Element that will be searched for in container.
        :type element: list, str

        :param container: Container that will be checked.
        :type container: list, str

        :returns: boolean of the membership
        :rtype: bool
        """
        if isinstance(element, list):
            if isinstance(container, list):
                return set(element) <= set(container)
        else:
            if isinstance(container, list):
                return element in container
            else:
                return element == container
        return False

    @staticmethod
    def json():
        """JSON representation of the metadata for this impact function.

        This is a static method. You can use it to get the raw json metadata
        for an impact function. Each concrete implementation of the
        metadata base class should implement  this. Nothing else needs to
        be overridden from the base class unless you want to modify the
        default behaviour.

        :returns: A json document representing all the metadata for the
            concrete impact function.
        :rtype: json
        """

        my_json = json.dumps(ImpactFunctionMetadata.as_dict())
        return my_json

    @staticmethod
    def as_dict():
        """Return metadata as a dictionary.

        This is a static method. You can use it to get the metadata in
        dictionary format for an impact function. Each concrete
        implementation of the metadata base class should implement this.
        Nothing else needs to be overridden from the base class unless you
        want to modify the default behaviour.

        :returns: A dictionary representing all the metadata for the
            concrete impact function.
        :rtype: dict
        """

        raise NotImplementedError(
            'You must implement this method in your concrete class.')

    @classmethod
    def allowed_subcategories(cls, category=None):
        """Get the list of allowed subcategories for a given category.

        :param category: Optional category which will be used to subset the
            allowed subcategories. If omitted, all supported subcategories will
            be returned (for both hazard and exposure). Default is None.
        :type category: str

        :returns: A list of strings is returned.
        :rtype: list
        """
        result = []
        if category is None:
            return cls.allowed_subcategories('exposure') + cls\
                .allowed_subcategories('hazard')
        else:
            metadata_dict = cls.as_dict()
            categories = metadata_dict['layer_requirements']
            result = add_to_list(result,
                                 categories[category]['%s_types' % category])
            return result

    @classmethod
    def allowed_data_types(cls, subcategory):
        """Get the list of allowed data types for a subcategory.

        Example usage::

            foo = IF()
            meta = IF.metadata
            ubar = meta.allowed_data_types('structure')
            ubar
            > ['polygon']

        In the above example it does not show ‘numeric’ as the request is
        specific to the structure subcategory for that IF (using the IF
        declaration at the top of this file as the basis for IF())

        Passing a subcategory is required otherwise the context of the
        data_type(s) would be ambiguous (i.e. whether they can be used as
        exposure or hazards).

        :param subcategory: Required subcategory which will be used to subset
            the allowed data_types.
        :type subcategory: str

        :returns: A list of one or more strings is returned.
        :rtype: list
        """
        result = []
        metadata_dict = cls.as_dict()
        categories = metadata_dict['categories']
        if subcategory in [x['id'] for x in cls.allowed_subcategories(
                'exposure')]:
            # implementation logic that returns the allowed data_types for
            # exposure layer with subcategory as passed in to this method

            layer_constraints = categories['exposure']['layer_constraints']
            for layer_constraint in layer_constraints:
                result = add_to_list(result, layer_constraint['data_type'])
        elif subcategory in [x['id'] for x in cls.allowed_subcategories(
                'hazard')]:
            # implementation logic that returns the allowed data_types for
            # hazard layer with subcategory as passed in to this method
            layer_constraints = categories['hazard']['layer_constraints']
            for layer_constraint in layer_constraints:
                result = add_to_list(result, layer_constraint['data_type'])
        else:
            # raise Exception('Invalid subcategory.')
            # TODO (ismailsunni): create custom exception to catch since it
            # will called by all impact function
            pass

        return result

    @classmethod
    def is_disabled(cls):
        """Determine if an impact function is disable.

        Usually is used for checking whether an impact function is disabled
        or not. If there is no disabled keyword in the metadata, return
        False.

        :returns: Return True if the metadata disabled value is True.
        :rtype: bool
        """
        try:
            metadata_dict = cls.as_dict()
            return metadata_dict.get('disabled', False)
        except AttributeError:
            return False

    @classmethod
    def is_valid(cls):
        """Check whether the metadata is valid or not.

        TODO(IS): Add comment explaining how we validate IF Metadata.

        :returns: True or False based on the validity of IF Metadata
        :rtype: bool
        """
        metadata_dict = cls.as_dict()
        expected_metadata = {
            'id': basestring,
            'name': basestring,
            'impact': basestring,
            'title': basestring,
            'author': basestring,
            'date_implemented': basestring,
            'overview': basestring,
            'detailed_description': basestring,
            'hazard_input': basestring,
            'exposure_input': basestring,
            'output': basestring,
            'actions': basestring,
            'limitations': list,  # list of string
            'citations': list,  # list of string
            'layer_requirements': dict
        }

        for key, value in expected_metadata.iteritems():
            if key not in metadata_dict.keys():
                return False, 'key %s not in metadata' % key

            if not isinstance(metadata_dict[key], value):
                message = 'key %s in metadata is not a %s, but %s ' % (
                    key, value, type(metadata_dict[key]))
                return False, message

        expected_layer_requirements_keys = ['hazard', 'exposure']
        layer_requirements = metadata_dict['layer_requirements']
        for key in expected_layer_requirements_keys:
            if key not in layer_requirements.keys():
                return False, 'key %s is not in layer_requirements' % key

        expected_hazard_metadata = {
            'layer_mode': dict,
            'layer_geometries': list,
            'hazard_categories': list,
            'hazard_types': list,
            'continuous_hazard_units': list,
            'vector_hazard_classifications': list,
            'raster_hazard_classifications': list,
            'additional_keywords': list
        }

        hazard = layer_requirements['hazard']
        for key, value in expected_hazard_metadata.iteritems():
            if key not in hazard.keys():
                return False, 'key %s is not in hazard' % key
            if not isinstance(hazard[key], value):
                message = 'key %s in hazard is not a %s, but %s ' % (
                    key, value, type(hazard[key]))
                return False, message

        expected_exposure_metadata = {
            'layer_mode': dict,
            'layer_geometries': list,
            'exposure_types': list,
            'exposure_units': list,
            'additional_keywords': list
        }

        exposure = layer_requirements['exposure']
        for key, value in expected_exposure_metadata.iteritems():
            if key not in exposure.keys():
                return False, 'key %s is not in exposure' % key
            if not isinstance(exposure[key], value):
                message = 'key %s in exposure not a %s, but %s ' % (
                    key, value, type(exposure[key]))
                return False, message
        return True, ''

    @classmethod
    def parameters(cls):
        """Return list of parameters.

        This is a static method. You can use it to get the list of parameters
        for the impact function.

        :returns: A list that contains all parameters.
        :rtype: list

        """
        return cls.as_dict().get('parameters', [])

    @classmethod
    def get_layer_requirements(cls):
        """Return layer requirements.

        This is a static method. You can use it to get the layer requirements
        for the impact function.

        :returns: A dict that contains layer requirements.
        :rtype: dict

        """
        return cls.as_dict().get('layer_requirements', {})

    @classmethod
    def get_name(cls):
        """Return IF name.

        :returns: The IF name.
        :rtype: str

        """
        return cls.as_dict().get('name', '')

    @classmethod
    def get_hazard_requirements(cls):
        """Get hazard layer requirements."""
        return cls.get_layer_requirements()['hazard']

    @classmethod
    def get_exposure_requirements(cls):
        """Get exposure layer requirements."""
        return cls.get_layer_requirements()['exposure']

    @classmethod
    def purposes_for_layer(cls, layer_geometry_key):
        """Get purposes of a layer geometry id.

        :param layer_geometry_key: The geometry id
        :type layer_geometry_key: str

        :returns: List of purposes
        :rtype: list
        """
        result = []

        hazard_layer_req = cls.get_hazard_requirements()
        hazard_geometries = hazard_layer_req['layer_geometries']
        hazard_geometry_keys = get_list_key(hazard_geometries)
        if layer_geometry_key in hazard_geometry_keys:
            result.append(layer_purpose_hazard)

        exposure_layer_req = cls.get_exposure_requirements()
        exposure_geometries = exposure_layer_req['layer_geometries']
        exposure_geometry_keys = get_list_key(exposure_geometries)
        if layer_geometry_key in exposure_geometry_keys:
            result.append(layer_purpose_exposure)

        return result

    @classmethod
    def hazard_categories_for_layer(cls, layer_geometry_key, hazard_key=None):
        """Get hazard categories form layer_geometry_key

        :param layer_geometry_key: The geometry id
        :type layer_geometry_key: str

            :param hazard_key: The hazard key
        :type hazard_key: str


        :returns: List of hazard_categories
        :rtype: list
        """
        hazard_layer_req = cls.get_hazard_requirements()
        hazards = hazard_layer_req['hazard_types']
        hazard_geometries = hazard_layer_req['layer_geometries']

        if not is_key_exist(layer_geometry_key, hazard_geometries):
            return []
        if hazard_key:
            if not is_key_exist(hazard_key, hazards):
                return []

        return hazard_layer_req['hazard_categories']

    @classmethod
    def hazards_for_layer(cls, hazard_geometry_key, hazard_category_key=None):
        """Get hazard categories form layer_geometry_key

        :param hazard_geometry_key: The geometry id
        :type hazard_geometry_key: str

        :param hazard_category_key: The hazard category
        :type hazard_category_key: str

        :returns: List of hazard
        :rtype: list
        """
        hazard_layer_req = cls.get_hazard_requirements()
        hazard_categories = hazard_layer_req['hazard_categories']
        hazard_geometries = hazard_layer_req['layer_geometries']

        if not is_key_exist(hazard_geometry_key, hazard_geometries):
            return []
        if hazard_category_key:
            if not is_key_exist(hazard_category_key, hazard_categories):
                return []

        return hazard_layer_req['hazard_types']

    @classmethod
    def exposures_for_layer(cls, layer_geometry_key):
        """Get hazard categories form layer_geometry_key

        :param layer_geometry_key: The geometry id
        :type layer_geometry_key: str

        :returns: List of exposure
        :rtype: list
        """
        exposure_layer_req = cls.get_exposure_requirements()
        layer_geometries = exposure_layer_req['layer_geometries']
        layer_geometry_keys = get_list_key(layer_geometries)
        if layer_geometry_key in layer_geometry_keys:
            return exposure_layer_req['exposure_types']
        else:
            return []

    @classmethod
    def exposure_units_for_layer(
            cls, exposure_key, layer_geometry_key, layer_mode_key):
        """Get exposure units.

        :param exposure_key: The exposure key
        :type exposure_key: str

        :param layer_geometry_key: The geometry key
        :type layer_geometry_key: str

        :param layer_mode_key: The layer mode key
        :type layer_mode_key: str

        :returns: List of exposure unit
        :rtype: list
        """

        exposure_layer_req = cls.get_exposure_requirements()

        if not exposure_layer_req['exposure_units']:
            return []

        exposures = exposure_layer_req['exposure_types']
        exposure_keys = get_list_key(exposures)
        if exposure_key not in exposure_keys:
            return []

        layer_geometries = exposure_layer_req['layer_geometries']
        layer_geometry_keys = get_list_key(layer_geometries)
        if layer_geometry_key not in layer_geometry_keys:
            return []

        layer_mode = exposure_layer_req['layer_mode']
        if layer_mode_key != layer_mode['key']:
            return []

        return exposure_layer_req['exposure_units']

    @classmethod
    def continuous_hazards_units_for_layer(
            cls, hazard_key, layer_geometry_key, layer_mode_key,
            hazard_category_key):
        """Get continuous hazard units.
        :param hazard_key: The hazard key
        :type hazard_key: str

        :param layer_geometry_key: The layer geometry key
        :type layer_geometry_key: str

        :param layer_mode_key: The layer mode key
        :type layer_mode_key: str

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :returns: List of continuous hazard unit
        :rtype: list
        """

        hazard_layer_req = cls.get_hazard_requirements()

        if not hazard_layer_req['continuous_hazard_units']:
            return []

        hazards = hazard_layer_req['hazard_types']
        hazard_keys = get_list_key(hazards)
        if hazard_key not in hazard_keys:
            return []

        layer_geometries = hazard_layer_req['layer_geometries']
        layer_geometry_keys = get_list_key(layer_geometries)
        if layer_geometry_key not in layer_geometry_keys:
            return []

        layer_mode = hazard_layer_req['layer_mode']
        if layer_mode_key != layer_mode['key']:
            return []

        hazard_categories = hazard_layer_req['hazard_categories']
        hazard_category_keys = get_list_key(hazard_categories)
        if hazard_category_key not in hazard_category_keys:
            return []

        return hazard_layer_req['continuous_hazard_units']

    @classmethod
    def vector_hazards_classifications_for_layer(
            cls, hazard_key, layer_geometry_key, layer_mode_key,
            hazard_category_key):
        """Get vector_hazards_classifications.
        :param hazard_key: The hazard key
        :type hazard_key: str

        :param layer_geometry_key: The layer geometry key
        :type layer_geometry_key: str

        :param layer_mode_key: The layer mode key
        :type layer_mode_key: str

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :returns: List of continuous hazard unit
        :rtype: list
        """

        hazard_layer_req = cls.get_hazard_requirements()

        if not hazard_layer_req['vector_hazard_classifications']:
            return []

        hazards = hazard_layer_req['hazard_types']
        hazard_keys = get_list_key(hazards)
        if hazard_key not in hazard_keys:
            return []

        layer_geometries = hazard_layer_req['layer_geometries']
        layer_geometry_keys = get_list_key(layer_geometries)
        if layer_geometry_key not in layer_geometry_keys:
            return []

        layer_mode = hazard_layer_req['layer_mode']
        if layer_mode_key != layer_mode['key']:
            return []

        hazard_categories = hazard_layer_req['hazard_categories']
        hazard_category_keys = get_list_key(hazard_categories)
        if hazard_category_key not in hazard_category_keys:
            return []

        return hazard_layer_req['vector_hazard_classifications']

    @classmethod
    def raster_hazards_classifications_for_layer(
            cls, hazard_key, layer_geometry_key, layer_mode_key,
            hazard_category_key):
        """Get vector_hazards_classifications.
        :param hazard_key: The hazard key
        :type hazard_key: str

        :param layer_geometry_key: The layer geometry key
        :type layer_geometry_key: str

        :param layer_mode_key: The layer mode key
        :type layer_mode_key: str

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :returns: List of continuous hazard unit
        :rtype: list
        """

        hazard_layer_req = cls.get_hazard_requirements()

        if not hazard_layer_req['raster_hazard_classifications']:
            return []

        hazards = hazard_layer_req['hazard_types']
        hazard_keys = get_list_key(hazards)
        if hazard_key not in hazard_keys:
            return []

        layer_geometries = hazard_layer_req['layer_geometries']
        layer_geometry_keys = get_list_key(layer_geometries)
        if layer_geometry_key not in layer_geometry_keys:
            return []

        layer_mode = hazard_layer_req['layer_mode']
        if layer_mode_key != layer_mode['key']:
            return []

        hazard_categories = hazard_layer_req['hazard_categories']
        hazard_category_keys = get_list_key(hazard_categories)
        if hazard_category_key not in hazard_category_keys:
            return []

        return hazard_layer_req['raster_hazard_classifications']

    @classmethod
    def available_hazards(cls, hazard_category_key):
        """Get available hazards from hazard_category_key

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :returns: List of available hazards
        :rtype: list
        """

        hazard_layer_req = cls.get_hazard_requirements()

        hazard_categories = hazard_layer_req['hazard_categories']
        hazard_category_keys = get_list_key(hazard_categories)
        if hazard_category_key not in hazard_category_keys:
            return []

        return hazard_layer_req['hazard_types']

    @classmethod
    def available_exposures(cls):
        """get_available_exposure

        :returns: List of available exposure
        :rtype: list
        """

        exposure_layer_req = cls.get_exposure_requirements()
        return exposure_layer_req['exposure_types']

    @classmethod
    def is_function_for_constraint(
            cls, hazard_key, exposure_key, hazard_geometry_key=None,
            exposure_geometry_key=None, hazard_mode_key=None,
            exposure_mode_key=None):
        """Check if the constraints match with the function.

        :param hazard_key: The hazard key
        :type hazard_key: str

        :param exposure_key: the exposure key
        :type exposure_key: str

        :param hazard_geometry_key: The hazard geometry key
        :type hazard_geometry_key: str

        :param exposure_geometry_key: The exposure geometry key
        :type exposure_geometry_key: str

        :param hazard_mode_key: The hazard mode key
        :type hazard_mode_key: str

        :param exposure_mode_key: The exposure mode key
        :type exposure_mode_key: str

        :returns: True if match, else False
        :rtype: bool
        """
        hazard_layer_req = cls.get_hazard_requirements()
        exposure_layer_req = cls.get_exposure_requirements()

        hazards = hazard_layer_req['hazard_types']
        exposures = exposure_layer_req['exposure_types']
        hazard_geometries = hazard_layer_req['layer_geometries']
        exposure_geometries = exposure_layer_req['layer_geometries']
        hazard_mode = hazard_layer_req['layer_mode']
        exposure_mode = exposure_layer_req['layer_mode']

        if not is_key_exist(hazard_key, hazards):
            return False
        if not is_key_exist(exposure_key, exposures):
            return False
        if hazard_geometry_key:
            if not is_key_exist(hazard_geometry_key, hazard_geometries):
                return False
        if exposure_geometry_key:
            if not is_key_exist(exposure_geometry_key, exposure_geometries):
                return False
        if hazard_mode_key:
            if hazard_mode_key != hazard_mode['key']:
                return False
        if exposure_mode_key:
            if exposure_mode_key != exposure_mode['key']:
                return False

        return True

    @classmethod
    def available_hazard_constraints(cls, hazard_key, hazard_category_key):
        """Get hazard constraints for hazard_key and hazard_category_key

        :param hazard_key: The hazard key
        :type hazard_key: str

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :returns: List of tuple of layer_mode and layer_geometry
        :rtype: list
        """
        hazard_layer_req = cls.get_hazard_requirements()
        hazards = hazard_layer_req['hazard_types']
        hazard_categories = hazard_layer_req['hazard_categories']

        if not is_key_exist(hazard_key, hazards):
            return []
        if not is_key_exist(hazard_category_key, hazard_categories):
            return []

        layer_mode = hazard_layer_req['layer_mode']
        layer_geometries = hazard_layer_req['layer_geometries']

        result = []
        for layer_geometry in layer_geometries:
            result.append((layer_mode, layer_geometry))

        return result

    @classmethod
    def available_exposure_constraints(cls, exposure_key):
        """Get exposure constraints for exposure_key.

        :param exposure_key: The exposure key
        :type exposure_key: str

        :returns: List of tuple of layer_mode and layer_geometry
        :rtype: list
        """
        exposure_layer_req = cls.get_exposure_requirements()
        exposures = exposure_layer_req['exposure_types']

        if not is_key_exist(exposure_key, exposures):
            return []

        layer_mode = exposure_layer_req['layer_mode']
        layer_geometries = exposure_layer_req['layer_geometries']

        result = []
        for layer_geometry in layer_geometries:
            result.append((layer_mode, layer_geometry))

        return result

    @classmethod
    def valid_layer_keywords(cls):
        """Return a dictionary for valid layer keywords."""
        hazard_layer_req = cls.get_hazard_requirements()
        exposure_layer_req = cls.get_exposure_requirements()

        hazard_keywords = {
            'layer_mode': hazard_layer_req['layer_mode']['key'],
            'layer_geometry': [x['key'] for x in hazard_layer_req[
                'layer_geometries']],
            'hazard_category': [x['key'] for x in hazard_layer_req[
                'hazard_categories']],
            'hazard': [x['key'] for x in hazard_layer_req[
                'hazard_types']],
            'continuous_hazard_unit': [x['key'] for x in hazard_layer_req[
                'continuous_hazard_units']],
            'vector_hazard_classification': [
                x['key'] for x in hazard_layer_req[
                    'vector_hazard_classifications']],
            'raster_hazard_classification': [
                x['key'] for x in hazard_layer_req[
                    'raster_hazard_classifications']],
        }

        exposure_keywords = {
            'layer_mode': exposure_layer_req['layer_mode']['key'],
            'layer_geometry': [x['key'] for x in exposure_layer_req[
                'layer_geometries']],
            'exposure': [x['key'] for x in exposure_layer_req[
                'exposure_types']],
            'exposure_unit': [x['key'] for x in exposure_layer_req[
                'exposure_units']],
        }

        keywords = {
            'hazard_keywords': hazard_keywords,
            'exposure_keywords': exposure_keywords,
        }

        return keywords

    @classmethod
    def available_hazard_layer_mode(
            cls, hazard_key, hazard_geometry_key, hazard_category_key):
        """Return all available layer_mode.

        :param hazard_key: The hazard key
        :type hazard_key: str

        :param hazard_geometry_key: The hazard geometry key
        :type hazard_geometry_key: str

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :returns: A layer mode
        :rtype: dict, None
        """

        hazard_layer_req = cls.get_hazard_requirements()
        hazards = hazard_layer_req['hazard_types']
        hazard_categories = hazard_layer_req['hazard_categories']
        hazard_geometries = hazard_layer_req['layer_geometries']

        if not is_key_exist(hazard_key, hazards):
            return None
        if not is_key_exist(hazard_geometry_key, hazard_geometries):
            return None
        if not is_key_exist(hazard_category_key, hazard_categories):
            return None

        layer_mode = hazard_layer_req['layer_mode']

        return layer_mode

    @classmethod
    def available_exposure_layer_mode(
            cls, exposure_key, exposure_geometry_key):
        """Get exposure layer mode for exposure_key.

        :param exposure_key: The exposure key
        :type exposure_key: str

        :param exposure_geometry_key: The exposure geometry key
        :type exposure_geometry_key: str

        :returns: A layer mode
        :rtype: dict
        """
        exposure_layer_req = cls.get_exposure_requirements()
        exposures = exposure_layer_req['exposure_types']
        exposure_geometries = exposure_layer_req['layer_geometries']

        if not is_key_exist(exposure_key, exposures):
            return None
        if not is_key_exist(exposure_geometry_key, exposure_geometries):
            return None

        layer_mode = exposure_layer_req['layer_mode']

        return layer_mode

    @classmethod
    def hazard_additional_keywords(
            cls, layer_mode_key=None, layer_geometry_key=None,
            hazard_category_key=None, hazard_key=None):
        """Return additional_keywords for hazard.

        :param layer_mode_key: The layer mode key
        :type layer_mode_key: str

        :param layer_geometry_key: The layer geometry key
        :type layer_geometry_key: str

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :param hazard_key: The hazard key
        :type hazard_key: str

        :returns: List of additional keywords
        :rtype: list
        """
        hazard_layer_req = cls.get_hazard_requirements()
        layer_mode = hazard_layer_req['layer_mode']
        layer_geometries = hazard_layer_req['layer_geometries']
        hazard_categories = hazard_layer_req['hazard_categories']
        hazards = hazard_layer_req['hazard_types']

        if layer_mode_key:
            if layer_mode_key != layer_mode['key']:
                return []
        if layer_geometry_key:
            if not is_key_exist(layer_geometry_key, layer_geometries):
                return []
        if hazard_category_key:
            if not is_key_exist(hazard_category_key, hazard_categories):
                return []
        if hazard_key:
            if not is_key_exist(hazard_key, hazards):
                return []

        additional_keywords = hazard_layer_req['additional_keywords']

        return additional_keywords

    @classmethod
    def exposure_additional_keywords(
            cls, layer_mode_key=None, layer_geometry_key=None,
            exposure_key=None):
        """Return additional_keywords for exposure.

        :param layer_mode_key: The layer mode key
        :type layer_mode_key: str

        :param layer_geometry_key: The layer geometry key
        :type layer_geometry_key: str

        :param exposure_key: The hazard key
        :type exposure_key: str

        :returns: List of additional keywords
        :rtype: list
        """
        exposure_layer_req = cls.get_exposure_requirements()
        layer_mode = exposure_layer_req['layer_mode']
        layer_geometries = exposure_layer_req['layer_geometries']
        exposures = exposure_layer_req['exposure_types']

        if layer_mode_key:
            if layer_mode_key != layer_mode['key']:
                return []
        if layer_geometry_key:
            if not is_key_exist(layer_geometry_key, layer_geometries):
                return []
        if exposure_key:
            if not is_key_exist(exposure_key, exposures):
                return []

        additional_keywords = exposure_layer_req['additional_keywords']

        return additional_keywords
