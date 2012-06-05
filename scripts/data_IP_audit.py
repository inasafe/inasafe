import os
import sys

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from extras.data_audit_wrapper import IP_verified
from storage.utilities_test import DATADIR

if __name__ == '__main__':
    IP_verified(DATADIR)
