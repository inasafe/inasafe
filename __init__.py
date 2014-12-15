# coding=utf-8

import sys
import os
sys.path.append(os.path.dirname(__file__))


# noinspection PyDocstring,PyPep8Naming
def classFactory(iface):
    """Load Plugin class from file Plugin."""
    from plugin import Plugin
    return Plugin(iface)
