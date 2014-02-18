# -*- coding: utf-8 -*-
"""**Postprocessors package.**

"""

__author__ = 'Dmitry Kolesov <kolesov.dm@google.com>'
__revision__ = '$Format:%H$'
__date__ = '08/01/2014'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


from safe.postprocessors.building_type_postprocessor import \
    BuildingTypePostprocessor

from safe.common.utilities import (
    ugettext as tr,
    OrderedDict)


# The road postprocessing is the same workflow as Building postprocessing
# So we can redefine field values and call BuildingTypePostprocessor
# That is why I define RoadTypePostprocessor
# as descendant of BuildingTypePostprocessor
class RoadTypePostprocessor(BuildingTypePostprocessor):
    """
    Postprocessor that calculates road types related statistics.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        """
        Constructor for postprocessor class.

        It takes care of defining self.impact_total
        """

        BuildingTypePostprocessor.__init__(self)
        # Note: Do we need these explicityl defined? With new osm-reporter
        # changes you already get a nicely named list in the 'type' field
        self.fields_values = OrderedDict([
            ('Motorway / highway', ['Motorway or highway']),
            ('Motorway link', ['Motorway link']),
            ('Primary road', ['Primary road']),
            ('Primary link', ['Primary link']),
            ('Tertiary', ['Tertiary']),
            ('Tertiary link', ['Tertiary link']),
            ('Secondary', ['Secondary']),
            ('Secondary link', ['Secondary link']),
            ('Road, residential, living street, etc.',
                ['Road, residential, living street, etc.']),
            ('Track', ['Track']),
            ('Cycleway, footpath, etc.', ['Cycleway, footpath, etc.']),
            ('Other', [])
        ])
        self.known_types = []
        self._update_known_types()

    def description(self):
        """Describe briefly what the post processor does.
        """
        return tr('Calculates road types related statistics.')
