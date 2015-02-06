# -*- coding: utf-8 -*-
"""**Postprocessors package.**

.. tip::
   import like this from safe.postprocessors import get_postprocessors

"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

from postprocessor_factory import get_postprocessors
from postprocessor_factory import get_postprocessor_human_name
