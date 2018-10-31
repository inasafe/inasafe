#!/usr/bin/env python
"""Generating rst file for api documentation."""

import os
from shutil import rmtree
import sys

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# Text
INDEX_HEADER = 'API documentation\n'
INDEX_HEADER += '=================\n'
INDEX_HEADER += 'This is the API documentation for the InaSAFE project.\n'
INDEX_HEADER += 'You can find out more about the InaSAFE project by visiting\n'
INDEX_HEADER += '`inasafe.org <http://www.inasafe.org/>`_.\n\n'
# known packages/directories/modules that don't have python files in it.
EXCLUDED_PACKAGES = [
    'i18n', 'test', 'converter_data', 'ui', 'resources', 'fixtures']


def create_top_level_index_entry(title, max_depth, subtitles):
    """Function for creating a text entry in index.rst for its content.

    :param title : Title for the content.
    :type title: str

    :param max_depth : Value for max_depth in the top level index content.
    :type max_depth: int

    :param subtitles : list of subtitles that is available.
    :type subtitles: list

    :return: A text for the content of top level index.
    :rtype: str
    """

    return_text = title + '\n'
    dash = '-' * len(title) + '\n'

    return_text += dash + '\n'
    return_text += '.. toctree::' + '\n'
    return_text += '   :maxdepth: ' + str(max_depth) + '\n\n'

    for subtitle in subtitles:
        return_text += '   ' + subtitle + '\n\n'
    return return_text


def create_package_level_rst_index_file(
        package_name, max_depth, modules, inner_packages=None):
    """Function for creating text for index for a package.

    :param package_name: name of the package
    :type package_name: str

    :param max_depth: Value for max_depth in the index file.
    :type max_depth: int

    :param modules: list of module in the package.
    :type modules: list

    :return: A text for the content of the index file.
    :rtype: str
    """
    if inner_packages is None:
        inner_packages = []
    return_text = 'Package::' + package_name
    dash = '=' * len(return_text)
    return_text += '\n' + dash + '\n\n'
    return_text += '.. toctree::' + '\n'
    return_text += '   :maxdepth: ' + str(max_depth) + '\n\n'
    upper_package = package_name.split('.')[-1]
    for module in modules:
        if module in EXCLUDED_PACKAGES:
            continue
        return_text += '   ' + upper_package + os.sep + module[:-3] + '\n'
    for inner_package in inner_packages:
        if inner_package in EXCLUDED_PACKAGES:
            continue
        return_text += '   ' + upper_package + os.sep + inner_package + '\n'

    return return_text


def create_module_rst_file(module_name):
    """Function for creating content in each .rst file for a module.

    :param module_name: name of the module.
    :type module_name: str

    :returns: A content for auto module.
    :rtype: str
    """

    return_text = 'Module:  ' + module_name
    dash = '=' * len(return_text)
    return_text += '\n' + dash + '\n\n'
    return_text += '.. automodule:: ' + module_name + '\n'
    return_text += '   :members:\n\n'

    return return_text


def create_dirs(path):
    """Shorter function for creating directory."""
    if not os.path.exists(path):
        os.makedirs(path)


def write_rst_file(file_directory, file_name, content):
    """Shorter procedure for creating rst file.

    :param file_directory: Directory of the filename.
    :type file_directory: str

    :param file_name: Name of the file.
    :type file_name: str

    :param content: The content of the file.
    :type content: str
    """
    create_dirs(os.path.split(os.path.join(file_directory, file_name))[0])
    try:
        fl = open(os.path.join(file_directory, file_name + '.rst'), 'w+')
        fl.write(content)
        fl.close()

    except Exception as e:
        print(('Creating %s failed' % os.path.join(
            file_directory, file_name + '.rst'), e))


def get_python_files_from_list(files, excluded_files=None):
    """Return list of python file from files, without excluded files.

    :param files: List of files.
    :type files: list

    :param excluded_files: List of excluded file names.
    :type excluded_files: list, None

    :returns: List of python file without the excluded file, not started with
        test.
    :rtype: list
    """
    if excluded_files is None:
        excluded_files = ['__init__.py']
    python_files = []
    for fl in files:
        if (fl.endswith('.py')
                and fl not in excluded_files
                and not fl.startswith('test')):
            python_files.append(fl)

    return python_files


def create_top_level_index(api_docs_path, packages, max_depth=2):
    """Create the top level index page (writing to file)

    :param api_docs_path: Path to the api-docs of inasafe documentation.
    :type api_docs_path: str

    :param packages: List of packages which want to be extracted their api/
    :type packages: list

    :param max_depth: The maximum depth of tree in the api docs.
    :type max_depth: int
    """
    page_text = INDEX_HEADER
    for package in packages:
        # Write top level index file entries for safe
        text = create_top_level_index_entry(
            title='Package %s' % package,
            max_depth=max_depth,
            subtitles=[package])

        page_text += '%s\n' % text
    write_rst_file(api_docs_path, 'index', page_text)


def get_inasafe_code_path(custom_inasafe_path=None):
    """Determine the path to inasafe location.

    :param custom_inasafe_path: Custom inasafe project location.
    :type custom_inasafe_path: str

    :returns: Path to inasafe source code.
    :rtype: str
    """

    inasafe_code_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..'))

    if custom_inasafe_path is not None:
        inasafe_code_path = custom_inasafe_path
    return inasafe_code_path


def clean_api_docs_dirs():
    """Empty previous api-docs directory.

    :returns: Path to api-docs directory.
    :rtype: str
    """
    inasafe_docs_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', 'docs', 'api-docs'))
    if os.path.exists(inasafe_docs_path):
        rmtree(inasafe_docs_path)
    create_dirs(inasafe_docs_path)
    return inasafe_docs_path


def create_api_docs(code_path, api_docs_path, max_depth=2):
    """Function for generating .rst file for all .py file in dir_path folder.

    :param code_path: Path of the source code.
    :type code_path: str

    :param api_docs_path: Path of the api documentation directory.
    :type api_docs_path: str

    :param max_depth: Maximum depth for the index.
    :type max_depth: int
    """
    base_path = os.path.split(code_path)[0]
    for package, subpackages, candidate_files in os.walk(code_path):
        # Checking __init__.py file
        if '__init__.py' not in candidate_files:
            continue
        # Creating directory for the package
        package_relative_path = package.replace(base_path + os.sep, '')
        index_package_path = os.path.join(
            api_docs_path, package_relative_path)
        # calculate dir one up from package to store the index in
        index_base_path, package_base_name = os.path.split(index_package_path)

        if package_base_name in EXCLUDED_PACKAGES:
            continue

        full_package_name = package_relative_path.replace(os.sep, '.')
        new_rst_dir = os.path.join(api_docs_path, package_relative_path)
        create_dirs(new_rst_dir)

        # Create index_file for the directory
        modules = get_python_files_from_list(candidate_files)
        index_file_text = create_package_level_rst_index_file(
            package_name=full_package_name,
            max_depth=max_depth,
            modules=modules,
            inner_packages=subpackages)

        write_rst_file(
            file_directory=index_base_path,
            file_name=package_base_name,
            content=index_file_text)

        # Creating .rst file for each .py file
        for module in modules:
            module = module[:-3]  # strip .py off the end
            py_module_text = create_module_rst_file(
                '%s.%s' % (full_package_name, module))
            write_rst_file(
                file_directory=new_rst_dir,
                file_name=module,
                content=py_module_text)


def usage():
    """Helper function for telling how to use the script."""
    print('Usage:')
    print(('python %s [optional path to inasafe directory]' % sys.argv[0]))


def main():
    if len(sys.argv) > 2:
        usage()
        sys.exit()
    elif len(sys.argv) == 2:
        print(('Building rst files from %s' % sys.argv[1]))
        inasafe_code_path = os.path.abspath(sys.argv[1])
    else:
        inasafe_code_path = None

    print('Please make sure there is no unused source '
          'code file in inasafe-dev')

    inasafe_code_path = get_inasafe_code_path(inasafe_code_path)
    print('Cleaning api docs...')
    api_docs_path = clean_api_docs_dirs()
    max_depth = 2
    packages = ['safe', 'realtime']

    # creating top level index for api-docs
    print('Creating top level index page...')
    create_top_level_index(api_docs_path, packages, max_depth)

    for package in packages:
        print('Creating api docs for package %s...' % package)
        package_code_path = os.path.join(inasafe_code_path, package)
        create_api_docs(
            code_path=package_code_path,
            api_docs_path=api_docs_path,
            max_depth=max_depth)

    print('Done.')


if __name__ == '__main__':
    main()
