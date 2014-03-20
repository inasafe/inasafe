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

__author__ = 'imajimatika@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '14/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import json
from exceptions import NotImplementedError
from safe.impact_functions.utilities import add_to_list

class ImpactFunctionMetadata():
    """Abstract metadata class for an impact function.

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
    categories are allowed, so there is no explicit method for that (we could
    change that later.
    """

    def __init__(self):
        """Constructor"""
        pass

    @staticmethod
    def is_subset(my_element, my_bigger_element):
        """Check the membership of my_element from my_bigger_element based on
        their type.
        Only valid for string and list
        """
        if type(my_element) is list:
            if type(my_bigger_element) is list:
                return set(my_element) <= set(my_bigger_element)
        else:
            if type(my_bigger_element) is list:
                return my_element in my_bigger_element
            else:
                return my_element == my_bigger_element
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
        """Return metadata as a dictionary

        This is a static method. You can use it to get the metadata
        in dictionary format for an impact function. Each concrete
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
        result = list()
        if category is None:
            return cls.allowed_subcategories('exposure') + cls\
                .allowed_subcategories('hazard')
        metadata_dict = cls.get_metadata()
        categories = metadata_dict['categories']
        result = add_to_list(result, categories[category]['subcategory'])
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
        data_type (s) would be ambiguous (i.e. whether they can be used as
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
        if subcategory in cls.allowed_subcategories(
                'exposure'):
            # implementation logic that returns the allowed data_types for
            # exposure layer with subcategory as passed in to this method

            layer_constraints = categories['exposure']['layer_constraints']
            for layer_constraint in layer_constraints:
                result = add_to_list(result, layer_constraint['data_type'])
        elif subcategory in cls.allowed_subcategories(
                'hazard'):
            # implementation logic that returns the allowed data_types for
            # hazard layer with subcategory as passed in to this method
            layer_constraints = categories['hazard']['layer_constraints']
            for layer_constraint in layer_constraints:
                result = add_to_list(result, layer_constraint['data_type'])
        else:
            raise Exception('Invalid subcategory.')

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
        if not data_type in cls.allowed_data_types(subcategory):
            return result
        metadata_dict = cls.get_metadata()
        categories = metadata_dict['categories']
        if subcategory in cls.allowed_subcategories(
                'exposure'):
            # implementation logic that returns the allowed data_types for
            # exposure layer with subcategory as passed in to this method

            result = add_to_list(result, categories['exposure']['units'])
        elif subcategory in cls.allowed_subcategories(
                'hazard'):
            # implementation logic that returns the allowed data_types for
            # hazard layer with subcategory as passed in to this method
            result = add_to_list(result, categories['hazard']['units'])
        else:
            raise Exception('Invalid subcategory.')

        return result

    @classmethod
    def is_disabled(cls):
        """Return True if the metadata disabled value is True. Usually is
        used for checking whether a impact function is disabled or not. If
        there is not disabled keyword in the metadata, return False. If there
        is not Metadata inner class in the function, return True

        :returns: True or False based on the metadata_dict
        :rtype: bool
        """
        try:
            metadata_dict = cls.get_metadata()
            return metadata_dict.get('disabled', False)
        except AttributeError:
            return True
        except NotImplementedError, e:
            print e, cls