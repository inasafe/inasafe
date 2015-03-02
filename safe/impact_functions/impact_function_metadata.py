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
from safe.common.utilities import add_to_list


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

        my_json = json.dumps(ImpactFunctionMetadata.get_metadata())
        return my_json

    @staticmethod
    def get_metadata():
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
            metadata_dict = cls.get_metadata()
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
        metadata_dict = cls.get_metadata()
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
        metadata_dict = cls.get_metadata()
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

        Usually is used for checking whether a impact function is disabled
        or not. If there is not disabled keyword in the metadata, return
        False. If there is not Metadata inner class in the function, return
        True

        :returns: Return True if the metadata disabled value is True.
        :rtype: bool
        """
        try:
            metadata_dict = cls.get_metadata()
            return metadata_dict.get('disabled', False)
        except AttributeError:
            return True

    @classmethod
    def is_valid(cls):
        """Check whether the metadata is valid or not.

        Valid metadata means, it has:
        id, name, impact, author, date_implemented, and overview.
        Also categories which has hazard and exposure.
        Each hazard and exposure has definition, subcategories, units,
        and layer_constraints.
        Subcategories, units, and layer_constraints must be in list.

        :returns: True or False based on the validity of IF Metadata
        :rtype: bool
        """
        metadata_dict = cls.get_metadata()
        expected_keys = [
            'id',
            'name',
            'impact',
            'title',
            'author',
            'date_implemented',
            'overview',
            'detailed_description',
            'hazard_input',
            'exposure_input',
            'output',
            'actions',
            'limitations',  # list of string
            'citations',  # list of string
            'categories'  # dict
        ]

        for key in expected_keys:
            if key not in metadata_dict.keys():
                return False, 'key %s not in metadata' % key

            if key in expected_keys[-3:-1]:
                if type(metadata_dict[key]) is not list:
                    message = ('Value of key %s is not list but %s' %
                               (key, type(metadata_dict[key])))
                    return False, message
            elif key == expected_keys[-1]:
                if type(metadata_dict[key]) is not dict:
                    message = ('Value of key %s is not dict but %s' %
                               (key, type(metadata_dict[key])))
                    return False, message
            else:
                if type(metadata_dict[key]) not in [str, unicode]:
                    message = ('Value of key %s is not str but %s' %
                               (key, type(metadata_dict[key])))
                    return False, message

        expected_keys = [
            'hazard',
            'exposure'
        ]
        categories = metadata_dict['categories']
        for key in expected_keys:
            if key not in categories.keys():
                return False, 'key %s not in categories' % key

        expected_keys = [
            'definition',
            'subcategories',
            'units',
            'layer_constraints'
        ]
        hazard = categories['hazard']
        for key in expected_keys:
            if key not in hazard.keys():
                return False, 'key %s not in hazard' % key
        for key in expected_keys[1:]:
            if type(hazard[key]) is not list:
                return (
                    False,
                    'key %s in hazard not a list, but %s ' % (
                        key, type(hazard[key])))
        exposure = categories['exposure']
        for key in expected_keys:
            if key not in exposure.keys():
                return False, 'key %s not in exposure' % key
        for key in expected_keys[1:]:
            if type(exposure[key]) is not list:
                return (
                    False,
                    'key %s in exposure not a list, but %s ' % (
                        key, type(exposure[key])))
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
            metadata_dict = cls.get_metadata()
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
    def categories_for_layer(cls, layer_type, data_type):
        """Determine the valid categories for a layer.

        This method is used to determine if a given layer can be used as a
        hazard, exposure or aggregation layer.

        In the returned the values are categories (if any) applicable for that
        layer_type and data_type.

        :param layer_type: The type for this layer. Valid values would be,
            'raster' or 'vector'.
        :type layer_type: str

        :param data_type: The data_type for this layer. Valid possibilities
            would be 'numeric' (for raster), point, line, polygon (for
            vectors).
        :type data_type: str

        :returns: A list as per the example above where each value represents
            a valid category.
        :rtype: list
        """
        layer_constraints = {
            'layer_type': layer_type,
            'data_type': data_type
        }
        result = []

        exposure_layer_constraints = cls.allowed_layer_constraints('exposure')
        exposure_layer_constraints = [
            cls.simplify_layer_constraint(e) for e in
            exposure_layer_constraints]

        hazard_layer_constraints = cls.allowed_layer_constraints('hazard')
        hazard_layer_constraints = [
            cls.simplify_layer_constraint(e) for e in
            hazard_layer_constraints]

        if layer_constraints in exposure_layer_constraints:
            result = add_to_list(result, 'exposure')
        if layer_constraints in hazard_layer_constraints:
            result = add_to_list(result, 'hazard')
        return result

    @classmethod
    def subcategories_for_layer(cls, category, layer_type, data_type):
        """Return a list of valid subcategories for a layer.

        This method is used to determine which subcategories a given layer
        can be for.

        In the returned the values are categories (if any) applicable for that
        layer_type and data_type.

        :param layer_type: The type for this layer. Valid values would be,
            'raster' or 'vector'.
        :type layer_type: str

        :param data_type: The data_type for this layer. Valid possibilities
            would be 'numeric' (for raster), point, line, polygon
            (for vectors).
        :type data_type: str

        :param category: The category for this layer. Valid possibilities
            would be 'hazard', 'exposure' and 'aggregation'.
        :type category: str


        :returns: A list as per the example above where each value represents
            a valid subcategory.
        :rtype: list
        """
        layer_constraints = {
            'layer_type': layer_type,
            'data_type': data_type
        }

        category_layer_constraints = cls.allowed_layer_constraints(category)
        category_layer_constraints = [
            cls.simplify_layer_constraint(e) for e in
            category_layer_constraints
        ]

        if layer_constraints not in category_layer_constraints:
            return []
        else:
            return cls.allowed_subcategories(category)

    @classmethod
    def get_hazards(cls):
        """Return hazards of the impact function.

        .. versionadded:: 2.2

        :return: List of valid hazards of the impact function.
        :rtype: list
        """
        hazards = cls.get_metadata()['categories']['hazard']['subcategories']
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
        exposures = cls.get_metadata()['categories']['exposure'][
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
        return cls.get_metadata()['categories']['hazard']['layer_constraints']

    @classmethod
    def get_exposure_layer_constraint(cls):
        """Helper function to get the constraints for exposure layer.

        :return: List of layer constraint of exposure layer.
        :rtype: list
        """
        return cls.get_metadata()[
            'categories']['exposure']['layer_constraints']
