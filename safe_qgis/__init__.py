import os
import sys

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

import safe
from safe.common.utilities import setup_logger
setup_logger()
