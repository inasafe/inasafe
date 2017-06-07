# coding=utf-8
from qgis.core import qgsfunction
from safe.utilities.rounding import fatalities_range

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@qgsfunction(
    args='auto', group='InaSAFE', usesGeometry=False, referencedColumns=[])
def fatality_rounding(number, feature, parent):
    """Round population fatalities according to InaSAFE standards."""
    _ = (feature, parent)  # NOQA
    return fatalities_range(number)
