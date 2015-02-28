# coding=utf-8
"""Module to create damage curves from point data and additional logging
utils relevant to impact_functions.
"""

import sys
import os


def admissible_plugins_to_str(plugin_list):
    """A helper to write the admissible plugin list to a string.

    Intended for use with the LOGGER so that admissible plugins can
    be pretty printed to the logs.

    Args: plugin_list str (required). A list of plugins

    Returns: A string representing the plugin list with nice formatting.

    Raises: None
    """
    result = '\n------------ Admissible Plugins ------------------------\n'
    for plugin, func in plugin_list.iteritems():
        result += 'ID: %s\n' % plugin
        result += 'Title: %s\n' % get_function_title(func)

    result += '---\n'
    return result


def keywords_to_str(keywords):
    """Pretty print keywords dict or list of dicts to a string.

    Intended for use with the LOGGER so that keywords can
    be pretty printed to the logs.

    Args: keywords dict or list (required). A list or dict of keywords.

    Returns: A string representing the keyword list with nice formatting.

    Raises: None
    """
    result = '\n----------------- Keywords -------------------\n'
    if isinstance(keywords, dict):
        for item, value in keywords.iteritems():
            result += 'Key: %s Value: %s\n' % (item, value)
    if isinstance(keywords, list):
        for list_item in keywords:
            result += '---\n'
            for item, value in list_item.iteritems():
                result += 'Key: %s Value: %s\n' % (item, value)
    return result


def get_list_id(list_dictionary):
    """Helper function to return list of id from list of dictionary.

     Each dictionary must have id in its key.

    :param list_dictionary: List of dictionary
    :type list_dictionary: list

    :returns: List of id
    :rtype: list
    """
    return [e['id'] for e in list_dictionary]


def get_python_file(python_class):
    """Obtain location where the python class is loaded from.

    :param python_class: A valid python class.
    :type python_class: class

    :returns: A absolute path to python file.
    :rtype: str
    """

    python_file = os.path.abspath(
        sys.modules[python_class.__module__].__file__)
    if python_file[-1] == 'c':
        python_file = python_file[:-1]
    return python_file


def is_duplicate_impact_function(impact_function):
    """Check whether the impact_function has been added or not.

    Duplicate means:
        - Same class name
        - Different file (we can check based on .py or .pyc files)

    :param impact_function: An impact function class
    :type impact_function: FunctionProvider

    :returns: True if duplicate, otherwise False
    :rtype: bool
    """

    if_class_names = [c.__name__ for c in impact_function.plugins]
    # if_py_files = [get_python_file(c) for c in impact_function.plugins]

    impact_function_name = impact_function.__name__
    # impact_function_py = get_python_file(impact_function)

    if impact_function_name in if_class_names:
        # if impact_function_py in if_py_files:
        #     return False
        # else:
        #     # Same name, different location
        #     return True
        return True
    else:
        return False


def function_name(impact_function):
    """Return the name for the impact function.

    It assume that the impact function is valid and has name in its metadata.

    :param impact_function: An impact function.
    :type impact_function: FunctionProvider

    :returns: The name of the impact function.
    :rtype: str
    """
    # noinspection PyUnresolvedReferences
    return impact_function.Metadata.get_metadata()['name']


def get_function_title(func):
    """Get title for impact function

    :param func: Impact function class

    :returns:  It's title if available as an attribute in the class
        description, otherwise what is returned by the function
        pretty_function_name.
    :rtype: str
    """
    try:
        title = func.Metadata.get_metadata()['title']
    except KeyError:
        title = func.__class__.__name__
    return title
