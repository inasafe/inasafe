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
from safe.common.utilities import add_to_list, get_list_key
from safe.new_definitions import (
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

        :param layer_constraint: Dictionary that represent layer_constraint
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
        if type(element) is list:
            if type(container) is list:
                return set(element) <= set(container)
        else:
            if type(container) is list:
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
            categories = metadata_dict['categories']
            result = add_to_list(result, categories[category]['subcategories'])
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
    def allowed_units(cls, subcategory, data_type):
        """Get the list of allowed units for a subcategory and data_type.

        .. note:: One data_type could be  used by more than one subcategory,
            so we need to explicitly pass the subcategory to this function.

        Example usage::

            foo = IF()
            meta = IF.metadata
            ubar = meta.allowed_data_types('structure')
            ubar
            > ['polygon']


        :param subcategory: Required subcategory which will be used to subset
            the allowed data_types.
        :type subcategory: str

        :param data_type: Required data_type which will be used to subset the
            allowed units.
        :type data_type: str

        :returns: A list of one or more strings is returned.
        :rtype: list
        """
        # pass  # must implement here
        result = []
        if data_type not in cls.allowed_data_types(subcategory):
            return result
        metadata_dict = cls.as_dict()
        categories = metadata_dict['categories']
        if subcategory in [x['id'] for x in cls.allowed_subcategories(
                'exposure')]:
            # implementation logic that returns the allowed data_types for
            # exposure layer with subcategory as passed in to this method

            result = add_to_list(result, categories['exposure']['units'])
        elif subcategory in [x['id'] for x in cls.allowed_subcategories(
                'hazard')]:
            # implementation logic that returns the allowed data_types for
            # hazard layer with subcategory as passed in to this method
            result = add_to_list(result, categories['hazard']['units'])
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
            'raster_hazard_classifications': list
        }

        hazard = layer_requirements['hazard']
        for key, value in expected_hazard_metadata.iteritems():
            if key not in hazard.keys():
                return False, 'key %s is not in hazard' % key
            if type(hazard[key]) is not value:
                message = 'key %s in hazard is not a %s, but %s ' % (
                    key, value, type(hazard[key]))
                return False, message

        expected_exposure_metadata = {
            'layer_mode': dict,
            'layer_geometries': list,
            'exposure_types': list,
            'exposure_units': list
        }

        exposure = layer_requirements['exposure']
        for key, value in expected_exposure_metadata.iteritems():
            if key not in exposure.keys():
                return False, 'key %s is not in exposure' % key
            if type(exposure[key]) is not value:
                message = 'key %s in exposure not a %s, but %s ' % (
                    key, value, type(exposure[key]))
                return False, message
        return True, ''

    @classmethod
    def allowed_layer_constraints(cls, category=None):
        """Determine allowed layer constraints.

        It is optionally filtered by category.

        Example usage::

            foo = IF()
            meta = IF.metadata
            ubar = meta.allowed_layer_constraints('exposure')
            ubar
            >  [
                {
                    'layer_type': 'vector',
                    'data_type': 'polygon'
                },
                {
                    'layer_type': 'raster',
                    'data_type': 'numeric'
                }
            ]

        :param category: Optional category which will be used to subset the
            allowed layer_constraints. If omitted, all supported
            layer_constraints will be returned (for both hazard and exposure).
            Default is None.
        :type category: str

        :returns: A list of one or more dictionary is returned.
        :rtype: list
        """
        result = []
        if category is None:
            result = add_to_list(result,
                                 cls.allowed_layer_constraints('hazard'))
            result = add_to_list(
                result, cls.allowed_layer_constraints('exposure'))
            return result

        else:
            metadata_dict = cls.as_dict()
            categories = metadata_dict['categories']
            return categories[category]['layer_constraints']

    @classmethod
    def units_for_layer(cls, subcategory, layer_type, data_type):
        """Get the valid units for a layer.

        Example usage::

            foo  = units_for_layer('flood', 'vector', 'polygon')
            print foo

        Would output this::

            {'Wet/Dry': ['wet','dry']}

        While passing a raster layer::

            foo  = units_for_layer('flood', 'raster', None)
            print foo

        Might return this::

            {
                'metres': None,
                'feet': None,
                'wet/dry': ['wet', 'dry'],
            }

        In the returned dictionary the keys are unit types and the values
        are the categories (if any) applicable for that unit type.

        :param subcategory: The subcategory for this layer.
        :type subcategory: str

        :param layer_type: The type for this layer. Valid values would be,
            'raster' or 'vector'.
        :type layer_type: str

        :param data_type: The data_type for this layer. Valid possibilities
            would be 'numeric' (for raster), point, line, polygon
            (for vectors).
        :type data_type: str

        :returns: A dictionary as per the example above where each key
            represents a unit and each value that is not None represents a
            list of categories.
        :rtype: dict
        """
        layer_constraints = {
            'layer_type': layer_type,
            'data_type': data_type
        }
        if subcategory in [x['id'] for x in
                           cls.allowed_subcategories('hazard')]:
            category = 'hazard'
        elif subcategory in [x['id'] for x in
                             cls.allowed_subcategories('exposure')]:
            category = 'exposure'
        else:
            return []

        category_layer_constraints = cls.allowed_layer_constraints(category)
        category_layer_constraints = [
            cls.simplify_layer_constraint(e) for e in
            category_layer_constraints
        ]

        if layer_constraints in category_layer_constraints:
            return cls.allowed_units(subcategory, data_type)
        else:
            return []

    @classmethod
    def get_hazards(cls):
        """Return hazards of the impact function.

        .. versionadded:: 2.2

        :return: List of valid hazards of the impact function.
        :rtype: list
        """
        hazards = cls.as_dict()['categories']['hazard']['subcategories']
        if type(hazards) is not list:
            hazards = [hazards]
        return hazards

    @classmethod
    def get_exposures(cls):
        """Return exposures of the impact function.

        .. versionadded:: 2.2

        :return: List of valid exposures of the impact function.
        :rtype: list
        """
        exposures = cls.as_dict()['categories']['exposure'][
            'subcategories']
        if type(exposures) is not list:
            exposures = [exposures]
        return exposures

    @classmethod
    def has_hazard(cls, hazard):
        """Check whether an impact function has hazard or not

        .. versionadded:: 2.2

        :param hazard: Dictionary that represent the hazard.
        :type hazard: dict

        :returns: True if it has hazard, else false
        :rtype: bool
        """
        hazards = cls.get_hazards()
        return hazard in hazards

    @classmethod
    def has_hazard_id(cls, hazard_id):
        """Check whether an impact function has hazard_id or not

        .. versionadded:: 2.2

        :param hazard_id: String that represent the hazard id.
        :type hazard_id: str

        :returns: True if it has hazard_id, else false
        :rtype: bool
        """
        hazards = cls.get_hazards()
        hazard_ids = [hazard['id'] for hazard in hazards]
        return hazard_id in hazard_ids

    @classmethod
    def has_exposure(cls, exposure):
        """Check whether an impact function has exposure or not

        .. versionadded:: 2.2

        :param exposure: Dictionary that represent the exposure.
        :type exposure: dict

        :returns: True if it has exposure, else false
        :rtype: bool
        """
        exposures = cls.get_exposures()
        return exposure in exposures

    @classmethod
    def has_exposure_id(cls, exposure_id):
        """Check whether an impact function has exposure_id or not

        .. versionadded:: 2.2

        :param exposure_id: String that represent the hazard id.
        :type exposure_id: str

        :returns: True if it has exposure_id, else false
        :rtype: bool
        """
        exposures = cls.get_exposures()
        exposure_ids = [exposure['id'] for exposure in exposures]
        return exposure_id in exposure_ids

    @classmethod
    def get_hazard_layer_constraint(cls):
        """Helper function to get the constraints for hazard layer.

        :return: List of layer constraint of hazard layer.
        :rtype: list
        """
        return cls.as_dict()['categories']['hazard']['layer_constraints']

    @classmethod
    def get_exposure_layer_constraint(cls):
        """Helper function to get the constraints for exposure layer.

        :return: List of layer constraint of exposure layer.
        :rtype: list
        """
        return cls.as_dict()[
            'categories']['exposure']['layer_constraints']

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
    # @classmethod
    # def get_layer_requirements_by_key(cls, key):
    #     """Obtain all layer_requirements for a key.
    #     :param key:
    #     :return:
    #     """

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
    def hazard_categories_for_layer(cls, layer_geometry_key):
        """Get hazard categories form layer_geometry_key

        :param layer_geometry_key: The geometry id
        :type layer_geometry_key: str

        :returns: List of hazard_categories
        :rtype: list
        """
        hazard_layer_req = cls.get_hazard_requirements()
        hazard_geometries = hazard_layer_req['layer_geometries']
        hazard_geometry_keys = get_list_key(hazard_geometries)
        if layer_geometry_key in hazard_geometry_keys:
            return hazard_layer_req['hazard_categories']
        else:
            return {}

    @classmethod
    def hazard_for_layer(cls, layer_geometry_key, hazard_category_key):
        """Get hazard categories form layer_geometry_key

        :param layer_geometry_key: The geometry id
        :type layer_geometry_key: str

        :param hazard_category_key: The hazard category
        :type hazard_category_key: str

        :returns: List of hazard
        :rtype: list
        """
        hazard_categories = cls.hazard_categories_for_layer(layer_geometry_key)
        hazard_category_keys = get_list_key(hazard_categories)
        if hazard_category_key in hazard_category_keys:
            hazard_layer_req = cls.get_hazard_requirements()
            return hazard_layer_req['hazard_types']
        else:
            return []

    @classmethod
    def exposure_for_layer(cls, layer_geometry_key):
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