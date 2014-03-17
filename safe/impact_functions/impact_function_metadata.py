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
    def json():
        """JSON representation of the metadata for this impact function.

        This is a static method. You can use it to get the raw json metadata
        for an impact function. Each concrete implementation of the
        metadata base class should implement  this. Nothing else needs to
        be overridden from the base class unless you want to modify the
        default behaviour.

        :returns: A json document representing all the metadata for the
            concrete impact function.
        :rtype: str
        """
        raise NotImplementedError(
            'You must implement this method in your concrete class.')

    @staticmethod
    def allowed_subcategories(category=None):
        """Get the list of allowed subcategories for a given category.

        :param category: Optional category which will be used to subset the
        allowed subcategories. If omitted, all supported subcategories will
        be returned (for both hazard and exposure). Default is None.
        :type category: str

        :returns: A list of strings is returned.
        :rtype: list
        """
        pass  # implementation goes here

    @staticmethod
    def allowed_subcategories(category=None):
        """Get the list of allowed subcategories for a given category.

        :param category: Optional category which will be used to subset the
            allowed subcategories. If omitted, all supported subcategories will
            be returned (for both hazard and exposure). Default is None.
        :type category: str

        :returns: A list of strings is returned.
        :rtype: list
        """
        pass  # implementation goes here

    @staticmethod
    def allowed_data_types(subcategory):
        """Get the list of allowed data types for a subcategory.

        Example usage::

            foo = IF()
            meta = IF.metadata
            ubar = meta.allowed_data_types('structure')
            ubar
            >>> ['polygon']

        In the above examplem it does not show ‘numeric’ as the request is
        specifc to the structure subcategory for that IF (using the IF
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
        if subcategory in ImpactFunctionMetadata.allowed_subcategories(
                'exposure'):
            pass
            # implementation logic that returns the allowed data_types for
            # exposure layer with subcategory as passed in to this method

        elif subcategory in ImpactFunctionMetadata.allowed_subcategories(
                'hazard'):
            pass
            # implementation logic that returns the allowed data_types for
            # hazard layer with subcategory as passed in to this method

        else:
            raise Exception('Invalid subcategory.')

    @staticmethod
    def allowed_units(subcategory, data_type):
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
        pass  # must implement here
