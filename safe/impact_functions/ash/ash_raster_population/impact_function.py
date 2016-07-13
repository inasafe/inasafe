# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Ash Raster on Population
Impact Function

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import numpy

from safe.common.exceptions import ZeroImpactException

from safe.impact_functions.bases.continuous_rh_continuous_re import \
    ContinuousRHContinuousRE
import safe.messaging as m

from safe.impact_functions.core import (
    population_rounding,
    has_no_data
)
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.storage.raster import Raster
from safe.utilities.i18n import tr
from safe.common.utilities import (
    verify,
    humanize_class,
    create_classes,
    create_label)

from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    filter_needs_parameters, get_needs_provenance_value
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin

from safe.impact_functions.ash.ash_raster_population.metadata_definitions \
    import AshRasterHazardPopulationFunctionMetadata


__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'impact_function.py'
__date__ = '7/13/16'
__copyright__ = 'imajimatika@gmail.com'


class AshRasterPopulationFunction(
        ContinuousRHContinuousRE,
        PopulationExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Simple impact function for ash raster on people."""
    _metadata = AshRasterHazardPopulationFunctionMetadata()

    def __init__(self):
        """Constructor."""
        super(AshRasterPopulationFunction, self).__init__()
        PopulationExposureReportMixin.__init__(self)

        self.parameters = add_needs_parameters(self.parameters)
        self.no_data_warning = False

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: safe.messaging.Message
        """
        return []   # TODO: what to put here?

    def run(self):
        """Run the impact function.

        :returns: A vector layer with affected areas marked.
        :type: safe_layer
        """

