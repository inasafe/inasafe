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
    if f in ['experimental']:
        continue

    if os.path.isdir(os.path.join(dirname, f)):
        cmd = 'from impact_functions.%s import *' % f
        #print cmd
        try:
            exec(cmd, locals(), globals())
        except ImportError:
            print 'WARNING: module %s does not exist' % f


from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_plugins  # FIXME: Deprecate
from safe.impact_functions.core import get_admissible_plugins
from safe.impact_functions.core import compatible_layers
from safe.impact_functions.core import get_function_title
