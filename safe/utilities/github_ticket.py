# coding=utf-8

"""Prepare a github ticket with a exception and with some context."""

from osgeo import gdal

from safe.common.version import inasafe_version
from safe.impact_function.impact_function import ImpactFunction
from safe.impact_function.multi_exposure_wrapper import (
    MultiExposureImpactFunction)
from safe.utilities.gis import qgis_version
from safe.utilities.utilities import (
    get_error_message,
    readable_os_version,
)


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

"""
Any change to this file about the template, please read the readme.md in the 
.github folder. Update the GitHub template if needed to avoid duplicate
efforts.
"""


def markdown(exception_raised, impact_function=None):
    """Prepare markdown."""
    try:
        message = get_error_message(exception_raised).to_text()
        markdown_template = '''
### Problem
An exception has been raised in InaSAFE
```
{exception_text}
```

### Environment
* InaSAFE : {inasafe_version}
* QGIS : {qgis_version}
* GDAL : {gdal_version}
* OS : {os_name}
'''
        markdown_template = markdown_template.format(
            exception_text=message,
            inasafe_version=inasafe_version,
            qgis_version=qgis_version(),
            gdal_version=gdal.__version__,
            os_name=readable_os_version(),
        )

        is_single = isinstance(impact_function, ImpactFunction)
        is_multi = isinstance(impact_function, MultiExposureImpactFunction)

        if is_single or is_multi:
            markdown_template += '''
### Impact function environment
* Hazard : {hazard}

'''
            print markdown_template
            markdown_template.format(
                hazard=impact_function.hazard.publicSource())
            markdown_template += '''
* Aggregation : {aggregation}
'''
            print markdown_template

            if impact_function.aggregation is not None:
                markdown_template.format(
                    aggregation=impact_function.aggregation.publicSource())
            else:
                markdown_template.format(
                    aggregation='No Provided by IF')
    except AttributeError:
        return None

    return markdown_template
