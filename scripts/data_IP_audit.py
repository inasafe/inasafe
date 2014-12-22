# coding=utf-8
from extras.data_audit_wrapper import IP_verified
from safe.common.testing import DATADIR
from safe.test.utilities import test_data_path

if __name__ == '__main__':
    # Verify external data provided with InaSAFE
    IP_verified(DATADIR)

    # Verify bundled test data
    IP_verified(test_data_path())
