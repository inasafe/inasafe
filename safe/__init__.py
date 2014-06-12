# coding=utf-8
from safe.common.version import get_version

__version__ = (1, 0, 0, 'final', 0)

__full_version__ = get_version(__version__)

from safe.common.custom_logging import setup_logger
setup_logger('InaSAFE')
