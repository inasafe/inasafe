# File name : gen_rst_script.py
# Python script for generating .rst file to be used in sphinx documentation
# Author : @ismailsunni
# Date : 16 August 2012

import os

# Constant
insafe_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_docs_dir = "_docs"
_safe_qgis_dir = "safe_qgis"
_safe_qgis_path = insafe_dir_path + "/" + _safe_qgis_dir

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
    dash = '-'*len(title) + '\n'

    return_text += dash + '\n'
    return_text += '.. toctree::' + '\n'
    return_text += '   :maxdepth: ' + str(max_depth) + '\n\n'
    
    for subtitle in subtitles:
        return_text += '   ' + subtitle + '\n\n'
        
    return return_text

def create_text_module(module_name):
    """Function for creating text in each .rst file for each module.
        module_name : name of the module.
    """
    
    return_text = 'Module:  ' + module_name
    dash = '='*len(return_text)
    return_text += '\n' + dash + '\n\n'
    return_text += 'This page contains the documentation for the InaSAFE '
    return_text += '**' + module_name + '**' + '\n'
    return_text += 'module.\n\n'
    return_text += '.. automodule:: ' + module_name + '\n'
    return_text += '      :members:'
    
    return return_text
    
def create_package_index(package_name, max_depth, modules):
    """Function for creating text for index for a package.
        package_name : name of the package
        max_depth : maxdepth
        modules : list of module in the package.
    """
    
    return_text = 'Package::' + package_name
    dash = '='*len(return_text)
    return_text += '\n' + dash + '\n\n'
    return_text += '.. toctree::' + '\n'
    return_text += '   :maxdepth: ' + str(max_depth) + '\n\n'
    
    for module in modules:
        return_text += '   ' + package_name + '/' + module[:-3] + '\n'
        
    return return_text
    
def main():
    # print _safe_qgis_path
    # print os.path.exists(_safe_qgis_path)
    _safe_qgis_content = os.listdir(_safe_qgis_path)

    python_module_files = []
    python_test_files = []

    for content in _safe_qgis_content:
        if content.endswith('.py') and not content.startswith('__init__.py'):
            if content.startswith('test'):
                python_test_files.append(content)
            else:
                python_module_files.append(content)

    #For testing only
    #print python_test_files
    #print python_module_files

    # Create docs directory
    docs_dir_path = insafe_dir_path + '/' + _docs_dir
    print docs_dir_path
    if not os.path.exists(docs_dir_path):
        os.makedirs(docs_dir_path)

    #creating index.rst file
    try:
        index_file = open(docs_dir_path + '/index.rst', 'w+')
        index_file.write(index_header)
        
        module_text = create_index('Packages', def_max_depth, ['safe_qgis'])
        test_module_text = create_index('Unit Tests', def_max_depth, ['safe_qgis_tests'])

        
        index_file.write(module_text)
        index_file.write(test_module_text)

    except Exception, e:
        print 'creating index.rst failed: ', e
        
    finally:
        index_file.close()

    # Creating safe_qgis.rst file
    try:
        safe_qgis_text = create_package_index('safe_qgis', 2, python_module_files)
        safe_qgis_file = open(docs_dir_path + '/safe_qgis.rst', 'w+')
        safe_qgis_file.write(safe_qgis_text)
        
    except Exception, e:
        print 'Creating safe_qgis.rst failed: ', e
        
    finally:
        safe_qgis_file.close()

    # TO DO

    # creating safe_qgis_tests.rst file
    

if __name__ == "__main__":
    main()
