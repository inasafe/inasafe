# coding=utf-8
"""This module is used for tests to force using SIP API V.2.

Separating this module is necessary to not import any modules that could
import PyQT4 first before importing this. Import force_sip_2 before
importing any PyQT4 in any modules on tests e.g:

    import safe.test.sip_api_2
    from PyQT4 import QtCore

"""

import sip
api_names = ["QDate", "QDateTime", "QString", "QTextStream", "QTime",
             "QUrl", "QVariant"]
api_version = 2
for name in api_names:
    sip.setapi(name, api_version)
