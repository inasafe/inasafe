# coding=utf-8

import unittest
import logging
import os
from safe.common.custom_logging import setup_logger

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestCustomLogging(unittest.TestCase):

    def test_logger(self):
        """Test logging system."""
        LOGGER = logging.getLogger('InaSAFE')
        setup_logger('InaSAFE')

        handlers = [
            class_name.__class__.__name__ for class_name in LOGGER.handlers]

        self.assertTrue('FileHandler' in handlers)
        self.assertTrue('QgsLogHandler' in handlers)

        if 'MUTE_LOGS' not in os.environ:
            self.assertTrue('StreamHandler' in handlers)

        if 'INASAFE_SENTRY' in os.environ:
            self.assertTrue('SentryHandler' in handlers)


if __name__ == '__main__':
    unittest.main()
