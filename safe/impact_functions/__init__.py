"""
Basic plugin framework based on::
http://martyalchin.com/2008/jan/10/simple-plugin-framework/
"""
import os

dirname = os.path.dirname(__file__)

# Import all the subdirectories
for f in os.listdir(dirname):
    if os.path.isdir(os.path.join(dirname, f)):
        try:
            __import__('safe.impact_functions.%s' % f)
        except ImportError:
            # Ignore e.g. directories that are not Python modules
            # FIXME (Ole): Should we emit a warning to the log file?
            pass


from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_plugins  # FIXME: Deprecate
from safe.impact_functions.core import get_plugin
from safe.impact_functions.core import get_admissible_plugins
from safe.impact_functions.core import compatible_layers
from safe.impact_functions.core import get_function_title
