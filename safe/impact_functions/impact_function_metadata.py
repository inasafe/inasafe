# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Message Modele.**

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
    def add_to_list(my_list, my_element):
        """Helper function to add new my_element to my_list based on its type
        . Add as new element if it's not a list, otherwise extend to the list
        if it's a list.
        """
        if type(my_element) is list:
            my_list.extend(my_element)
        else:
            my_list.append(my_element)

        return my_list

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
        metadata_dict = cls.get_metadata()
        requirements = metadata_dict['requirements']
        result = []
        for requirement in requirements:
            if category is not None:
                if requirement['category'] == category:
                    result.append(requirement['subcategory'])
            else:
                result.append(requirement['subcategory'])
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
        if subcategory is None:
            return result
        metadata_dict = cls.get_metadata()
        requirements = metadata_dict['requirements']
        for requirement in requirements:
            if requirement['subcategory'] == subcategory:
                if 'data_type' in requirement.keys():
                    result = cls.add_to_list(result, requirement['data_type'])
                else:
                    my_layer_types = requirement['layer_types']
                    if type(my_layer_types) is list:
                        for my_layer_type in my_layer_types:
                            result = cls.add_to_list(result,
                                                     my_layer_type['data_type'])
                    else:
                        result = cls.add_to_list(result,
                                                 my_layer_types['data_type'])

        return list(set(result))
        # if subcategory in ImpactFunctionMetadata.allowed_subcategories(
        #         'exposure'):
        #
        #     pass
        #     # implementation logic that returns the allowed data_types for
        #     # exposure layer with subcategory as passed in to this method
        #
        # elif subcategory in ImpactFunctionMetadata.allowed_subcategories(
        #         'hazard'):
        #     pass
        #     # implementation logic that returns the allowed data_types for
        #     # hazard layer with subcategory as passed in to this method
        #
        # else:
        #     raise Exception('Invalid subcategory.')

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
        requirements = metadata_dict['requirements']
        for requirement in requirements:
            if cls.is_subset(subcategory, requirement['subcategory']):
                if 'units' in requirement.keys():
                    result = cls.add_to_list(result, requirement['units'])
                elif 'data_types' in requirement.keys():
                    raise (NotImplementedError(
                        'units not found, data_types found'))
                elif 'layer_types' in requirements.keys():
                    raise (NotImplementedError(
                        'units and data_types not found, layer_types found'))
                else:
                    raise (NotImplementedError('Error something else...'))
            else:
                continue
        return list(set(result))