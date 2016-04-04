# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Impact Function Registry.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@kartoza.com, akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '01/03/15'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from safe.common.utilities import is_subset, convert_to_list, project_list


class Registry(object):
    """A simple registry for keeping track of all impact functions.

    We will use a singleton pattern to ensure that there is only
    one canonical registry. The registry can be used by impact functions
    to register themselves and their GUID's.

    To get the impact functions, please do not use directly from this Registry,
    but rather user ImpactFunctionManager.
    """

    _instance = None
    _impact_functions = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Registry, cls).__new__(cls, *args, **kwargs)
            cls._impact_functions = []
        return cls._instance

    @property
    def impact_functions(self):
        """Return all registered impact functions."""
        return self._impact_functions

    @classmethod
    def register(cls, impact_function):
        """Register an impact function to the Registry.

        Impact Function that will be registered has to have a unique id that
        is not registered yet.

        :param impact_function: The impact function to register.
        :type impact_function: ImpactFunction.
        """
        is_disabled = impact_function.metadata().is_disabled()
        # pylint: disable=unused-variable
        is_valid, reason = impact_function.metadata().is_valid()
        # pylint: enable=unused-variable
        impact_function_id = impact_function.metadata().as_dict()['id']
        if not is_disabled and is_valid and impact_function not in \
                cls._impact_functions:
            id_unique = cls.filter_by_metadata('id', impact_function_id) == []
            if id_unique:
                cls._impact_functions.append(impact_function)
            else:
                raise Exception('Impact Function with ID %s is already '
                                'registered' % impact_function_id)

    @classmethod
    def clear(cls):
        """Remove all registered impact functions in the registry."""
        cls._impact_functions = []

    @classmethod
    def list(cls):
        """List of all registered impact functions by their name."""
        return [
            impact_function.metadata().as_dict()['name'] for impact_function in
            cls._impact_functions]

    @classmethod
    def get_instance(cls, name):
        """Return an instance of impact function given its class name.

        :param name: the name of IF class
        :type name: str

        :return: impact function instance
        :rtype: safe.impact_functions.base.ImpactFunction.instance()
        """
        return cls.get_class(name).instance()

    @classmethod
    def get_class(cls, name):
        """Return the class of an impact function given its class name.

        :param name: The class name of the IF.
        :type name: str

        :return: impact function class
        :rtype: safe.impact_functions.base.ImpactFunction
        """
        for impact_function in cls._impact_functions:
            if impact_function.__name__ == name:
                return impact_function
        raise Exception('Impact function with the class name %s not found' %
                        name)

    @classmethod
    def filter_by_metadata(cls, metadata_key, metadata_value):
        """Return IF classes given its metadata key and value.

        :param metadata_key: The key of the metadata e.g 'id', 'name'
        :type metadata_key: str

        :param metadata_value: The value of the metadata, e.g for the key
            'id' the value is 'FloodNativePolygonExperimentalFunction'
        :type metadata_value: str, dict

        :return: impact function classes
        :rtype: list
        """
        impact_functions = []
        for impact_function in cls._impact_functions:
            if_metadata = impact_function.metadata().as_dict()
            if metadata_key in if_metadata:
                if if_metadata[metadata_key] == metadata_value:
                    impact_functions.append(impact_function)

        return impact_functions

    @classmethod
    def filter(cls, hazard_metadata=None, exposure_metadata=None):
        """Filter impact function given the hazard and exposure metadata.

        :param hazard_metadata: Dictionary represent hazard keywords
        :type hazard_metadata: dict

        :param exposure_metadata: Dictionary represent exposure keywords
        :type exposure_metadata: dict

        :returns: List of impact functions.
        :rtype: list

        """
        if hazard_metadata is None and exposure_metadata is None:
            return cls._impact_functions

        impact_functions = cls._impact_functions
        impact_functions = cls.filter_by_hazard(
            impact_functions, hazard_metadata)
        impact_functions = cls.filter_by_exposure(
            impact_functions, exposure_metadata)

        return impact_functions

    @staticmethod
    def filter_by_hazard(impact_functions, hazard_keywords):
        """Filter impact function by hazard_keywords.

        :param impact_functions: List of impact functions.
        :type impact_functions: list

        :param hazard_keywords: Dictionary represent hazard keywords.
        :type hazard_keywords: dict

        :returns: List of impact functions.
        :rtype: list
        """
        filtered_impact_functions = []
        for impact_function in impact_functions:
            if_hazard_requirements = impact_function.metadata().as_dict()[
                'layer_requirements']['hazard']

            layer_mode = if_hazard_requirements['layer_mode']
            layer_geometries = if_hazard_requirements['layer_geometries']
            hazard_categories = if_hazard_requirements['hazard_categories']
            hazard_types = if_hazard_requirements['hazard_types']
            continuous_hazard_units = if_hazard_requirements[
                'continuous_hazard_units']
            vector_hazard_classifications = if_hazard_requirements[
                'vector_hazard_classifications']
            raster_hazard_classifications = if_hazard_requirements[
                'raster_hazard_classifications']

            if (layer_mode and not is_subset(
                    hazard_keywords.get('layer_mode'), layer_mode)):
                continue
            if (layer_geometries and not is_subset(
                    hazard_keywords.get('layer_geometry'), layer_geometries)):
                continue
            if (hazard_categories and not is_subset(
                    hazard_keywords.get('hazard_category'),
                    hazard_categories)):
                continue
            if (hazard_types and not is_subset(
                    hazard_keywords.get('hazard'), hazard_types)):
                continue
            if (continuous_hazard_units and not is_subset(
                    hazard_keywords.get('continuous_hazard_unit'),
                    continuous_hazard_units)):
                continue
            if (vector_hazard_classifications and not is_subset(
                    hazard_keywords.get('vector_hazard_classification'),
                    vector_hazard_classifications)):
                continue
            if (raster_hazard_classifications and not is_subset(
                    hazard_keywords.get('raster_hazard_classification'),
                    raster_hazard_classifications)):
                continue
            filtered_impact_functions.append(impact_function)

        return filtered_impact_functions

    @staticmethod
    def filter_by_exposure(impact_functions, exposure_keywords):
        """Filter impact function by exposure_keywords.

        :param impact_functions: List of impact functions
        :type impact_functions: list

        :param exposure_keywords: Dictionary represent exposure keywords
        :type exposure_keywords: dict

        :returns: List of impact functions.
        :rtype: list

        """
        filtered_impact_functions = []
        for impact_function in impact_functions:
            if_exposure_keywords = impact_function.metadata().as_dict()[
                'layer_requirements']['exposure']

            layer_mode = if_exposure_keywords['layer_mode']
            layer_geometries = if_exposure_keywords['layer_geometries']
            exposure_types = if_exposure_keywords['exposure_types']
            exposure_units = if_exposure_keywords['exposure_units']

            if (layer_mode and not is_subset(
                    exposure_keywords.get('layer_mode'), layer_mode)):
                continue
            if (layer_geometries and not is_subset(
                    exposure_keywords.get(
                        'layer_geometry'), layer_geometries)):
                continue
            if (exposure_types and not is_subset(
                    exposure_keywords.get('exposure'),
                    exposure_types)):
                continue
            if (exposure_units and not is_subset(
                    exposure_keywords.get('exposure_unit'), exposure_units)):
                continue

            filtered_impact_functions.append(impact_function)

        return filtered_impact_functions

    @classmethod
    def filter_by_keyword_string(
            cls, hazard_keywords=None, exposure_keywords=None):
        """Get available impact functions from hazard and exposure keywords.

        Disabled impact function will not be loaded.

        :param hazard_keywords: The keywords of the hazard.
        :type hazard_keywords: dict

        :param exposure_keywords: The keywords of the exposure.
        :type exposure_keywords: dict
        """
        if hazard_keywords is None and exposure_keywords is None:
            return cls._impact_functions

        impact_functions = []
        layer_purposes = []
        keywords = {}
        if hazard_keywords is not None:
            layer_purposes.append('hazard')
            keywords['hazard'] = hazard_keywords
        if exposure_keywords is not None:
            layer_purposes.append('exposure')
            keywords['exposure'] = exposure_keywords

        for impact_function in cls._impact_functions:
            requirement_met = True
            for layer_purpose in layer_purposes:
                layer_requirement = impact_function.metadata().as_dict()[
                    'layer_requirements'][layer_purpose]

                # general requirements
                layer_mode = layer_requirement['layer_mode']
                layer_mode = project_list(convert_to_list(layer_mode), 'key')

                layer_geometries = layer_requirement['layer_geometries']
                layer_geometries = project_list(
                    convert_to_list(layer_geometries), 'key')

                # hazard layer specific requirements
                if layer_purpose == 'hazard':
                    hazard_categories = layer_requirement['hazard_categories']
                    hazard_categories = project_list(
                        convert_to_list(hazard_categories), 'key')

                    hazard_types = layer_requirement['hazard_types']
                    hazard_types = project_list(
                        convert_to_list(hazard_types), 'key')

                    continuous_hazard_units = layer_requirement.get(
                        'continuous_hazard_units')
                    continuous_hazard_units = project_list(
                        convert_to_list(continuous_hazard_units), 'key')

                    vector_hazard_classifications = layer_requirement.get(
                        'vector_hazard_classifications')
                    vector_hazard_classifications = project_list(
                        convert_to_list(vector_hazard_classifications), 'key')

                    raster_hazard_classifications = layer_requirement.get(
                        'raster_hazard_classifications')
                    raster_hazard_classifications = project_list(
                        convert_to_list(raster_hazard_classifications), 'key')

                # exposure layer specific requirements
                if layer_purpose == 'exposure':
                    exposure_types = layer_requirement['exposure_types']
                    exposure_types = project_list(
                        convert_to_list(exposure_types), 'key')

                    exposure_units = layer_requirement['exposure_units']
                    exposure_units = project_list(
                        convert_to_list(exposure_units), 'key')

                keyword = keywords[layer_purpose]
                if layer_mode and keyword.get('layer_mode') not in layer_mode:
                    requirement_met = False
                    continue

                if (layer_geometries and keyword.get('layer_geometry') not in
                        layer_geometries):
                    requirement_met = False
                    continue

                # hazard layer specific requirements
                if layer_purpose == 'hazard':
                    if (hazard_types and keyword.get('hazard') not in
                            hazard_types):
                        requirement_met = False
                        continue

                    if (hazard_categories and keyword.get('hazard_category')
                            not in hazard_categories):
                        requirement_met = False
                        continue

                    if (continuous_hazard_units and keyword.get(
                            'continuous_hazard_unit')
                            not in continuous_hazard_units):
                        requirement_met = False
                        continue

                    if (vector_hazard_classifications and keyword.get(
                            'vector_hazard_classification')
                            not in vector_hazard_classifications):
                        requirement_met = False
                        continue

                    if (raster_hazard_classifications and keyword.get(
                            'raster_hazard_classification')
                            not in raster_hazard_classifications):
                        requirement_met = False
                        continue

                # exposure layer specific requirements
                if layer_purpose == 'exposure':
                    if (exposure_types and keyword.get('exposure') not in
                            exposure_types):
                        requirement_met = False
                        continue

                    if (exposure_units and keyword.get('exposure_unit') not in
                            exposure_units):
                        requirement_met = False
                        continue

            if requirement_met and impact_function not in impact_functions:
                impact_functions.append(impact_function)

        return impact_functions
