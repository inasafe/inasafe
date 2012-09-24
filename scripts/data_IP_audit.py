import os
import sys

from extras.data_audit_wrapper import IP_verified
from safe.common.testing import DATADIR, UNITDATA

if __name__ == '__main__':
    # Verify external data provided with InaSAFE
    IP_verified(DATADIR)

    # Verify bundled test data
    IP_verified(UNITDATA)
