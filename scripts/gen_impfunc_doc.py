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
from safe.api import get_documentation, get_plugins
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
    for k, v in impfunc_doc.iteritems():
        content_rst = k
        content_rst += '\n' + '=' * len(k) + '\n\n'
        # provide documentation
        if type(v) is dict :
            for mykey, myValue in v.iteritems():
                myPrettykey = pretty_key(mykey)
                content_rst += myPrettykey + '\n'
                content_rst += '-' * len(myPrettykey) + '\n'
                if type(myValue) is list and len(myValue) > 0:
                    for myVal in myValue:
                        content_rst += '* ' + myVal + '\n'
                elif myValue is None or len(myValue) == 0:
                    content_rst += 'No documentation found'
                else:
                    content_rst += myValue
                content_rst += '\n\n'
        create_rst_file(impact_func_doc_path, k.replace(' ', ''), content_rst)


def gen_impact_func_index(list_unique_identifier=[]):
    """Generate impact function index
    """
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
    impfunc_doc = {}
    # Get all impact functions
    plugins_dict = get_plugins()
    for k in plugins_dict.keys():
        impfunc_doc[k] = get_documentation(k)
    list_unique_identifier = [x['unique_identifier']
                                for x in impfunc_doc.itervalues()]
    gen_impact_func_index(list_unique_identifier)

    create_dirs(insafe_dir_path + os.sep + doc_dir + os.sep +
                    impact_func_doc_dir)
    gen_rst_doc(impfunc_doc)
