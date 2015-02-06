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
        if hasattr(func, 'title'):
            result += 'Title: %s\n' % func.title
        else:
            result += 'Title: %s\n' % func.__class__

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
    if type(keywords) == type(dict()):
        for item, value in keywords.iteritems():
            result += 'Key: %s Value: %s\n' % (item, value)
    if type(keywords) == type(list()):
        for list_item in keywords:
            result += '---\n'
            for item, value in list_item.iteritems():
                result += 'Key: %s Value: %s\n' % (item, value)
    return result


def pretty_string(myArg):
    """A helper function that return a pretty string according to the args

    Args:

      * myArs = string or list

    Returns:

      * if myArgs is string return myArgs

        if myArgs is list return each element as string separated by ','
    """
    if type(myArg) == type(str()):
        return myArg
    elif type(myArg) == type(list()):
        return ', '.join(myArg)
    else:
        return str(myArg)


def remove_double_spaces(myStr):
    """Remove double spaces from a string. Return the string without any
        double spaces
    """
    while myStr.find('  ') != -1:
        myStr = myStr.replace('  ', ' ')

    return myStr


def add_to_list(my_list, my_element):
    """Helper function to add new my_element to my_list based on its type
    . Add as new element if it's not a list, otherwise extend to the list
    if it's a list.
    It's also guarantee that all elements are unique

    :param my_list: A list
    :type my_list: list

    :param my_element: A new element
    :type my_element: str, list

    :returns: A list with unique element
    :rtype: list

    """
    if type(my_element) is list:
        for element in my_element:
            my_list = add_to_list(my_list, element)
    else:
        if my_element not in my_list:
            my_list.append(my_element)

    return my_list


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

    return os.path.abspath(sys.modules[python_class.__module__].__file__)


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
    if_py_files = [get_python_file(c) for c in impact_function.plugins]
    if_pyc_files = [get_python_file(c) + 'c' for c in impact_function.plugins]

    impact_function_name = impact_function.__name__
    impact_function_py = get_python_file(impact_function)
    impact_function_pyc = impact_function_py + 'c'

    if impact_function_name in if_class_names:
        if (impact_function_py in if_py_files or
                impact_function_pyc in if_pyc_files):
            return False
        else:
            # Same name, different location
            return True
    else:
        return False
