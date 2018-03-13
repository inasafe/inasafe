# coding=utf-8

"""Definitions relating to the version of InaSAFE."""

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# InaSAFE version (please synchronize with metadata.txt)
inasafe_version = '4.2.5'
# alpha, beta, rc or final
inasafe_release_status = 'final'

# InaSAFE Keyword Version compatibility.
inasafe_keyword_version = '4.2'
keyword_version_compatibilities = {
    # 'InaSAFE keyword version': 'List of supported InaSAFE keyword version'
    '3.3': ['3.2'],
    '3.4': ['3.2', '3.3'],
    '3.5': ['3.4', '3.3'],
    '4.1': ['4.0'],
    '4.2': ['4.1', '4.0'],
}
