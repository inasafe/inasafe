# -*- coding: utf-8 -*-
"""**Postprocessors package.**

"""

__author__ = 'Dmitry Kolesov <kolesov.dm@google.com>'
__revision__ = '$Format:%H$'
__date__ = '08/01/2014'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


from safe.postprocessors.building_type_postprocessor import BuildingTypePostprocessor

from safe.common.utilities import ugettext as tr


class RoadTypePostprocessor(BuildingTypePostprocessor):
    """
    Postprocessor that calculates road types related statistics.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        """
        Constructor for postprocessor class,
        It takes care of defining self.impact_total
        """
        BuildingTypePostprocessor.__init__(self)
        self.fields_values = {
            'Construction': ['construction'],
            'Crossing': ['crossing'],
            'Cycleway': ['cycleway'],
            'Footway': ['footway', 'path', 'pedestrian'],
            'Highway': ['highway'],
            'Industri': ['industri'],
            'Living street': ['living_street'],
            'Motorway': ['motorway', 'motorway_link'],
            'Primary': ['primary', 'primary_link'],
            'Raceway': ['raceway'],
            'Residential': ['residential'],
            'Secondary': ['secondary', 'secondary_link'],
            'Service': ['service'],
            'Tertiary': ['tertiary', 'tertiary_link'],
            'Track': ['track'],
            'unclassified': ['unclassified', 'yes', 'road'],
         }

    def description(self):
        """Describe briefly what the post processor does.

        Args:
            None

        Returns:
            Str the translated description

        Raises:
            Errors are propagated
        """
        return tr('Calculates road types related statistics.')