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
from shutil import rmtree
from safe.api import get_documentation, get_plugins, is_function_enabled
from gen_rst_script import (create_dirs, create_rst_file, insafe_dir_path)

doc_dir = "docs" + os.sep + "source" + os.sep + "user-docs"
impact_func_doc_dir = 'impact_function_docs'


def pretty_key(myKey):
    """Return a pretty key for documentation. Just remove underscore and
    capitalize
    :param myKey:string
    :return: a pretty one
    """
    MyPrettyKey = myKey.replace('_', ' ').title()
    return MyPrettyKey


def gen_rst_doc(impfunc_doc):
    """Generate .rst file
    :param
        impfunc_doc : dictionary that contains documentation
    :return
        None
    """
    impact_func_doc_path = insafe_dir_path + os.sep + doc_dir + os.sep +\
                           impact_func_doc_dir
    for myFuncName, myDoc in impfunc_doc.iteritems():
        content_rst = myFuncName
        content_rst += '\n' + '=' * len(myFuncName) + '\n\n'
        # provide documentation
        content_rst += 'Overview'
        content_rst += '\n' + '-' * len('Overview') + '\n\n'
        if type(myDoc) is dict :
            for mykey, myValue in myDoc.iteritems():
                if mykey == 'detailed_description':
                    continue
                myPrettykey = pretty_key(mykey)
                content_rst += '**' + myPrettykey + '**' + ': '
                if type(myValue) is list and len(myValue) > 0:
                    content_rst += '\n\n'
                    for myVal in myValue:
                        content_rst += '* ' + myVal + '\n'
                elif myValue is None or len(myValue) == 0:
                    content_rst += 'No documentation found'
                else:
                    content_rst += myValue
                content_rst += '\n\n'
            content_rst += 'Details'
            content_rst += '\n' + '-' * len('Details') + '\n\n'
            if 'detailed_description' in myDoc.iterkeys():
                content_rst += myDoc['detailed_description']
            else:
                content_rst += 'No documentation found'
        else:
            content_rst += 'No documentation found'

        create_rst_file(impact_func_doc_path, myFuncName.replace(' ', ''),
                        content_rst)


def gen_impact_func_index(list_unique_identifier=None):
    """Generate impact function index
    """
    if list_unique_identifier is None:
        list_unique_identifier = []
    content_rst = ''
    title_page = 'Impact Functions Documentation'
    content_rst += '=' * len(title_page) + '\n'
    content_rst += title_page + '\n'
    content_rst += '=' * len(title_page) + '\n\n'

    content_rst += ('This document explains the purpose of impact functions '
                    'and lists the different available impact function and '
                    'the requirements each has to be used effectively.\n\n')

    content_rst += '.. toctree::\n'
    content_rst += '   :maxdepth: 2\n\n'

    # list impact function
    for ui in list_unique_identifier:
        content_rst += '   ' + impact_func_doc_dir + os.sep + \
                       ui.replace(' ', '') + '\n'

    create_rst_file(insafe_dir_path + os.sep + doc_dir, 'impact_functions_doc',
                        content_rst)


if __name__ == "__main__":
    # remove old files, in case you disabled or remove impact function
    impact_func_doc_dir_path = (insafe_dir_path + os.sep + doc_dir + os.sep +
            impact_func_doc_dir)
    if os.path.exists(impact_func_doc_dir_path):
        rmtree(impact_func_doc_dir_path)

    impfunc_doc = {}
    # Get all impact functions
    plugins_dict = get_plugins()
    for myKey, myFunc in plugins_dict.iteritems():
        if not is_function_enabled(myFunc):
            continue
        impfunc_doc[myKey] = get_documentation(myKey)
    list_unique_identifier = [x['unique_identifier']
                                for x in impfunc_doc.itervalues()]
    gen_impact_func_index(list_unique_identifier)

    create_dirs(impact_func_doc_dir_path)
    gen_rst_doc(impfunc_doc)
