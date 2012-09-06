"""Wrapper around data_audit.

This wrapper is specific to InaSAFE.

This wrapper will run data_audit.py

Specify what extensions, directories and files should be ignored by
the data_audit process.

These will generally be specific to each software project.
"""

from data_audit import IP_verified as IP_engine

# Ignore source code files
extensions_to_ignore = ['.py','.c', '.h', '.cpp', '.f',
                        '.bat', '.m','.sh','.awk', '.pck']

# Ignore shp file auxiliary files
extensions_to_ignore += ['.prj', '.sbn', '.sbx', '.cpg']

# Ignore InaSAFE .keywords files
extensions_to_ignore += ['.keywords']

# Ignore QGIS projects and styles
extensions_to_ignore += ['.qml', '.qpj', '.qgs', '.sld']

# Ignore pdf, doc and csv documents
extensions_to_ignore += ['.pdf', '.doc', '.csv']

# Ignore generated stuff
extensions_to_ignore += ['.pyc', '.o', '.so', '~']
extensions_to_ignore += ['.aux', '.log', '.idx', 'ilg', '.ind',
                         '.bbl', '.blg', '.syn', '.toc', '.xml']

# Ignore license files themselves
extensions_to_ignore += ['.lic', '.permission']

# Ignore certain other files,
files_to_ignore = ['README.txt', 'LICENSE.txt', 'Makefile',
                   '.temp', 'SConstruct', 'SConscript', 'log.ini']

# Ignore directories
directories_to_ignore = ['.svn', '.git', '.metadata']
#directories_to_ignore += ['old_pyvolution_documentation']



def IP_verified(directory, verbose=False):

    result = IP_engine(directory,
                       extensions_to_ignore,
                       directories_to_ignore,
                       files_to_ignore,
                       verbose=verbose)
    return result

