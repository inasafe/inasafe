"""**Generating rst file for documentation**

"""

__author__ = 'Ismail Sunni <ismailsunni@yahoo.co.id>'
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '16/08/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import string

# Constant
insafe_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
'..'))
_docs_dir = "docs" + os.sep + "source" + os.sep + "api-docs"
_safe_qgis_dir = "safe_qgis"
_safe_qgis_path = insafe_dir_path + os.sep + _safe_qgis_dir
_safe_qgis_tests_dir = "safe_qgis_tests"
_safe_qgis_tests_path = insafe_dir_path + os.sep + _safe_qgis_tests_dir

# Default Value
def_max_depth = 2

# Text
index_header = "InaSAFE's API documentation\n"
index_header += "===========================\n\n"
index_header += "This is the API documentation for the InaSAFE project.\n"
index_header += "You can find out more about the InaSAFE project by visiting\n"
index_header += "`riskinabox.org<http://www.inasafe.org/>`_.\n\n"


def create_index(title, max_depth, subtitles):
    """Function for creating text in index.rst for its content.
        title : Title for the content
        max_depth : maxdepth
        subtitles : list of subtitles that is available.
    """

    return_text = title + '\n'
    dash = '-' * len(title) + '\n'

    return_text += dash + '\n'
    return_text += '.. toctree::' + '\n'
    return_text += '   :maxdepth: ' + str(max_depth) + '\n\n'

    for subtitle in subtitles:
        return_text += '   ' + subtitle + '\n\n'
    return return_text


def create_package_index(package_name, max_depth, modules, inner_packages=[]):
    """Function for creating text for index for a package.
        package_name : name of the package
        max_depth : maxdepth
        modules : list of module in the package.
    """

    return_text = 'Package::' + package_name
    dash = '=' * len(return_text)
    return_text += '\n' + dash + '\n\n'
    return_text += '.. toctree::' + '\n'
    return_text += '   :maxdepth: ' + str(max_depth) + '\n\n'
    upper_package = package_name.split('.')[-1]
    for module in modules:
        return_text += '   ' + upper_package + os.sep + module[:-3] + '\n'
    for inner_package in inner_packages:
        return_text += '   ' + upper_package + os.sep + inner_package + '\n'

    return return_text


def create_text_module(module_name):
    """Function for creating text in each .rst file for each module.
        module_name : name of the module.
    """

    return_text = 'Module:  ' + module_name[:-3]
    dash = '=' * len(return_text)
    return_text += '\n' + dash + '\n\n'
    return_text += '.. automodule:: ' + module_name[:-3] + '\n'
    return_text += '      :members:\n\n'
    return_text += 'This module forms part of the `InaSAFE '
    return_text += '<http://inasafe.org>`_ tool.'

    return return_text


def python_file_siever(files, excluded_files=['__init__.py']):
    """Return list of python file from files, except it is an excluded file.
    """

    python_files = []
    for fl in files:
        if fl.endswith('.py') and not fl in excluded_files:
            python_files.append(fl)

    return python_files


def create_dirs(path):
    """Shorter function for creating directory(s).
    """

    if not os.path.exists(path):
        os.makedirs(path)


def create_rst_file(path_file, file_name, content):
    """Shorter procedure for creating rst file
    """

    create_dirs(os.path.split(path_file + os.sep + file_name)[0])
    try:
        fl = open(path_file + os.sep + file_name + '.rst', 'w+')
        fl.write(content)
        fl.close()

    except Exception, e:
        print 'Creating ' + path_file + os.sep + file_name + '.rst failed: ', e


def generate_rst(dir_path, doc_path=insafe_dir_path + os.sep + _docs_dir):
    """Function for generating .rst file for all .py file in dir_path folder.
        dir_path : path of the folder
    """

    dir_path_head = os.path.split(dir_path)[0]
    len_dir_path = len(dir_path_head) + 1

    for path, dirs, files in os.walk(dir_path):
        # Checking __init__.py file
        if '__init__.py' not in files:
            continue
        # Creating directory for the package
        create_dirs(doc_path + os.sep + path[len_dir_path:])

        # Create index_file for the directory
        python_files = python_file_siever(files)
        package = string.replace(path[len_dir_path:], os.sep, '.')
        index_file_text = create_package_index(package, def_max_depth,
        python_files, dirs)
        create_rst_file(doc_path, path[len_dir_path:], index_file_text)

        # Creating .rst file for each .py file
        for py_file in python_files:
            py_module_text = create_text_module(
            string.replace(path[len_dir_path:] + '.' + py_file, os.sep, '.'))
            create_rst_file(doc_path + os.sep + path[len_dir_path:],
            py_file[:-3], py_module_text)


def main():
    # For special case
    _safe_qgis_content = os.listdir(_safe_qgis_path)
    python_module_files = []
    python_test_files = []

    python_files = python_file_siever(_safe_qgis_content)

    for content in python_files:
        if content.startswith('test'):
            python_test_files.append(content)
        else:
            python_module_files.append(content)

    # Create docs directory
    docs_dir_path = insafe_dir_path + os.sep + _docs_dir
    create_dirs(docs_dir_path)

    #creating index.rst file
    module_text = create_index('Packages safe_qgis', def_max_depth,
    ['safe_qgis'])
    test_module_text = create_index('Unit Tests', def_max_depth,
    ['safe_qgis_tests'])
    safe_package_text = create_index('Packages safe', def_max_depth,
    ['safe'])
    create_rst_file(docs_dir_path, 'index', index_header + module_text +
    test_module_text + safe_package_text)

    # Creating safe_qgis.rst file
    safe_qgis_text = create_package_index('safe_qgis', 2, python_module_files)
    create_rst_file(docs_dir_path, 'safe_qgis', safe_qgis_text)

    # Creating safe_qgis_tests.rst file
    safe_qgis_test_text = create_package_index('safe_qgis_tests', 2,
    python_test_files)
    create_rst_file(docs_dir_path, 'safe_qgis_tests', safe_qgis_test_text)

    # Creating each module folder and the contents
    docs_safe_qgis_path = docs_dir_path + os.sep + 'safe_qgis'
    create_dirs(docs_safe_qgis_path)

    for module in python_module_files:
        module_text = create_text_module('safe_qgis.' + module)
        create_rst_file(docs_safe_qgis_path, module[:-3], module_text)

    docs_safe_qgis_tests_path = docs_dir_path + os.sep + 'safe_qgis_tests'
    create_dirs(docs_safe_qgis_tests_path)

    for module in python_test_files:
        module_text = create_text_module('safe_qgis.' + module)
        create_rst_file(docs_safe_qgis_tests_path, module[:-3], module_text)

    # For general packages and modules in safe package
    generate_rst(insafe_dir_path + os.sep + 'safe')


if __name__ == "__main__":
    main()
