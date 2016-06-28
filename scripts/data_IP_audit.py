# coding=utf-8
from extras.data_audit_wrapper import IP_verified
from safe.test.utilities import standard_data_path, DATADIR

if __name__ == '__main__':
    # Verify external data provided with InaSAFE
    IP_verified(DATADIR)

    # Verify bundled test data
    IP_verified(standard_data_path())
