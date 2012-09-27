"""Module to create damage curves from point data and additional logging
utils relevant to impact_functions.
"""

import numpy
from safe.common.interpolation1d import interpolate1d


class Damage_curve:
    """Class for implementation of damage curves based on point data
    """

    def __init__(self, data):

        try:
            data = numpy.array(data)
        except:
            msg = 'Could not convert data %s to damage curve' % str(data)
            raise RuntimeError(msg)

        msg = 'Damage curve data must be a 2d array or a list of lists'
        if len(data.shape) != 2:
            raise RuntimeError(msg)

        msg = 'Damage curve data must have two columns'
        if data.shape[1] != 2:
            raise RuntimeError(msg)

        self.x = data[:, 0]
        self.y = data[:, 1]

    def __call__(self, zeta):
        return interpolate1d(self.x, self.y, [zeta], mode='linear')[0]


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
    """ A helper function that return a pretty string according to the args
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
    '''Remove double spaces from a string. Return the string without any
        dobule spaces
    '''
    while myStr.find('  ') != -1:
        myStr = myStr.replace('  ', ' ')

    return myStr
