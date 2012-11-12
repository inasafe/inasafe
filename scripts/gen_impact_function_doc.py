"""**Generating impact function documentation**

"""

__author__ = 'Ismail Sunni <ismailsunni@yahoo.co.id>'
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '17/09/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
from gen_rst_script import (create_dirs, create_rst_file, python_file_siever,
                            create_index)

# Constants
insafe_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
'..'))
docs_dir = (insafe_dir_path + os.sep + 'docs' + os.sep + 'source' + os.sep +
                        'user-docs')
impact_function_dir = 'impact_functions'
impact_functions_path = (insafe_dir_path + os.sep + 'safe' + os.sep +
                        impact_function_dir)


index_header = '\n================\n'
index_header += 'Impact Functions\n'
index_header += '================\n\n'
index_header += 'This document explains the purpose of impact functions and '
index_header += 'lists the different available impact function and '
index_header += 'the requirements each has to be used effectively.\n\n'
excluded_files = ['__init__.py']


def get_doc(file_path):
    '''Get documentation for an impact function
    '''
    retval = {}
    param = []
    f = open(file_path)
    codelines = f.readlines()
    f.close()

    # parsing
    i = 0
    for cl in codelines:
        if cl[-1] == '\n':
            cl = cl[:-1]
        if len(cl) > 0:
            cl = remove_double_spaces(cl)
            cl = remove_first_last_space(cl)
        if cl.startswith(':author '):
            retval['author'] = cl[8:]
        elif cl.startswith(':rating '):
            retval['rating'] = cl[8:]
        elif cl.startswith("title = _('"):
            retval['title'] = cl[11:-2]
        elif cl.startswith('target_field = '):
            retval['title'] = cl[16:-1]
        elif cl.startswith(':param requires '):
            param.append(i)
        i += 1
    retval['param'] = param
    return retval


def generate_rst(dir_path, doc_path=docs_dir + os.sep + 'functions'):
    '''Generate .rst file contains documentation for all impact functions
    '''
    dir_path_head = os.path.split(dir_path)[0]
    len_dir_path = len(dir_path_head) + 1

    for path, _, files in os.walk(dir_path):
        # Checking __init__.py file
        if '__init__.py' not in files:
            continue
        # Creating directory for the package
        create_dirs(doc_path + os.sep + path[len_dir_path:])


def remove_double_spaces(myStr):
    '''Remove double spaces from a string. Return the string without any
        dobule spaces
    '''
    while myStr.find('  ') != -1:
        myStr = myStr.replace('  ', ' ')

    return myStr


def remove_first_last_space(myStr):
    '''Return a string that has been removed its first and last
    space (if exist)
    '''
    if myStr[0] == ' ':
        myStr = myStr[1:]
    if myStr[-1] == ' ':
        myStr = myStr[:-1]

    return myStr


def main():
    create_dirs(docs_dir)
    # get all impact functions directories
    imp_func_dirs = [name for name in
                     os.listdir(impact_functions_path)
                     if (os.path.isdir(impact_functions_path + os.sep + name)
                     and ((os.listdir(impact_functions_path + os.sep +
                                     name)).count('__init__.py')) > 0)]

    # create index subtitle
    imp_func_subtitle = ['functions' + os.sep + imp_func_dir
                         for imp_func_dir in imp_func_dirs]
    index_text = create_index('impact_functions', 2, imp_func_subtitle)
    print '\n'.join(imp_func_subtitle)

    # create impact_function.rst file
    create_rst_file(docs_dir, 'impact_functions', index_header + index_text)

    for myIFD in imp_func_dirs:
        myAbsIFD = impact_functions_path + os.sep + myIFD
        generate_rst(myAbsIFD, docs_dir + os.sep + 'functions')

    impact_functions_contents = os.listdir(impact_functions_path)

    python_files = python_file_siever(impact_functions_contents,
                                      excluded_files)
    print python_files

    #create_rst_file(docs_dir, 'impact_functions', index_header)

if __name__ == "__main__":
    print remove_double_spaces('        askaska;lks;as jkasldjkaskl sajkd   ')
    ifName = 'volcano_population_evacuation_polygon_hazard.py'
    print get_doc(impact_functions_path + os.sep + 'volcanic'
                                + os.sep + ifName)
    #main()
