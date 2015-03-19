# coding=utf-8
"""Module to create damage curves from point data and additional logging
utils relevant to impact_functions.
"""

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
