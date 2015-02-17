#!/usr/bin/env python
"""**Generating impact function documentation**

"""

__author__ = 'Ismail Sunni <ismailsunni@yahoo.co.id>'
__version__ = '1.0.0'
__revision__ = '$Format:%H$'
__date__ = '17/09/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
user_home = os.environ["HOME"]

import sys
sys.path.append('%s/dev/python/inasafe-dev' % user_home)

from shutil import rmtree
from safe.api import (
    get_metadata,
    get_plugins,
    is_function_enabled,
    get_doc_string)
from scripts.create_api_docs import (
    create_dirs, write_rst_file)
# from third_party.odict import OrderedDict
from collections import OrderedDict

doc_dir = os.path.join('docs', 'source', 'user-docs')
impact_func_doc_dir = 'impact-function-docs'


def get_inasafe_documentation_path(custom_inasafe_doc_path=None):
    """Determine the path to inasafe-doc location.

    :param custom_inasafe_doc_path: Custom inasafe documentation.
    :type custom_inasafe_doc_path: str

    :returns: Path to inasafe doc.
    :rtype: str
    """
    if custom_inasafe_doc_path is None:
        custom_inasafe_doc_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'inasafe-doc'))

    return custom_inasafe_doc_path


def get_pretty_key(ugly_key):
    """Pretty ugly_key for documentation - removes underscore and title-lise.

    :param ugly_key: Key to format.
    :type ugly_key: str

    :returns: A nicely formatted string.
    :rtype: str
    """
    pretty_key = ugly_key.replace('_', ' ').title()
    return pretty_key


def generate_documentation(functions_metadata, docstrings):
    """Generates an .rst file for each impact function.

    The .rst file will contain the docstring and the standard
    functions_metadata fields for each impact function.

    :param functions_metadata: Key value pairs containing function
        documentation.
    :type functions_metadata: dict

    :param docstrings: Key Value Pair where the key is an impact function
        name and the value is the docstring for that impact function.
    :type docstrings: dict
    """
    impact_function_doc_path = os.path.join(
        get_inasafe_documentation_path(), doc_dir, impact_func_doc_dir)

    for name, docstring in functions_metadata.items():
        rst_content = name
        rst_content += '\n' + '=' * len(name) + '\n\n'
        # provide documentation
        rst_content += 'Overview'
        rst_content += '\n' + '-' * len('Overview') + '\n\n'

        if type(docstring) is dict or type(docstring) is OrderedDict:
            for dictionary_key, value in docstring.items():
                if dictionary_key == 'detailed_description':
                    continue
                pretty_key = get_pretty_key(dictionary_key)
                rst_content += ('**%s**: \n' % pretty_key)
                if value is None or len(value) == 0:
                    rst_content += 'No documentation found'
                else:
                    rst_content += value
                rst_content += '\n\n'
            rst_content += 'Details'
            rst_content += '\n' + '-' * len('Details') + '\n\n'
            if (('detailed_description' in docstring.keys()) and (len(
                    docstring['detailed_description']) > 0)):
                rst_content += docstring['detailed_description']
            else:
                rst_content += 'No documentation found'
        else:
            rst_content += 'No documentation found'

        if name in docstrings:
            doc_string = docstrings[name]
            rst_content += '\n\nDoc String'
            rst_content += '\n' + '-' * len('Doc String') + '\n\n'
            rst_content += doc_string

        print 'Creating doc string for %s' % name

        write_rst_file(
            impact_function_doc_path, name.replace(' ', ''), rst_content)


def create_index(list_function_id=None):
    """Generate impact function index.

    :param list_function_id: A collection of function ids that will be listed
        in the index.rst.
    :type list_function_id: list
    """
    if list_function_id is None:
        list_function_id = []
    content_rst = ''
    page_title = 'Impact Functions Documentation'
    content_rst += '=' * len(page_title) + '\n'
    content_rst += page_title + '\n'
    content_rst += '=' * len(page_title) + '\n\n'

    content_rst += (
        'This document explains the purpose of impact functions and lists the '
        'different available impact function and the requirements each has to '
        'be used effectively.\n\n')

    content_rst += '.. toctree::\n'
    content_rst += '   :maxdepth: 2\n\n'

    # list impact function
    for identifier in list_function_id:
        content_rst += ('   %s%s%s\n' % (
            impact_func_doc_dir, os.sep, identifier.replace(' ', '')))

    index_path = os.path.join(get_inasafe_documentation_path(), doc_dir)
    write_rst_file(index_path, 'impact_functions_doc', content_rst)


def usage():
    """Helper function for telling how to use the script."""
    print 'Usage:'
    print 'python %s [optional path to inasafe-doc directory]' % sys.argv[0]


if __name__ == '__main__':
    if len(sys.argv) > 2:
        usage()
        sys.exit()
    elif len(sys.argv) == 2:
        print('Building rst files from %s' % sys.argv[1])
        inasafe_doc_path = os.path.abspath(sys.argv[1])
    else:
        inasafe_doc_path = None

    # remove old files, in case you disabled or remove impact function
    documentation_path = (
        os.path.join(
            get_inasafe_documentation_path(
                inasafe_doc_path), doc_dir, impact_func_doc_dir))

    if os.path.exists(documentation_path):
        rmtree(documentation_path)

    metadata = {}
    doc_strings = {}
    # Get all impact functions
    plugins_dict = get_plugins()
    for key, impact_function in plugins_dict.iteritems():
        if not is_function_enabled(impact_function):
            continue
        metadata[key] = get_metadata(key)
        doc_strings[key] = get_doc_string(impact_function)
    function_ids = [x['unique_identifier'] for x in metadata.values()]
    print 'Generating index page for Impact Functions Documentation'
    create_index(function_ids)

    create_dirs(documentation_path)

    print 'Generating page for Impact Functions'
    generate_documentation(metadata, doc_strings)

    print 'Fin.'
