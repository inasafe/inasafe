"""
Basic plugin framework based on::
http://martyalchin.com/2008/jan/10/simple-plugin-framework/
"""

import os
import os.path
import glob

dirname = os.path.dirname(__file__)

# Import all the subdirectories
for f in os.listdir(dirname):
    if os.path.isdir(os.path.join(dirname, f)):
        exec('from impact_functions.%s import *' % f, locals(), globals())


from impact_functions.core import FunctionProvider
from impact_functions.core import get_plugins
from impact_functions.core import compatible_layers
