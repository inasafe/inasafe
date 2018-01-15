# coding=utf-8
"""InaSAFE Defaults."""

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA pylint: disable=unused-import

from parameters.text_parameter import TextParameter
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def default_provenance():
    """The provenance for the default values.

    :return: default provenance.
    :rtype: str
    """
    field = TextParameter()
    field.name = tr('Provenance')
    field.description = tr('The provenance of minimum needs')
    field.value = 'The minimum needs are based on BNPB Perka 7/2008.'
    return field


def black_inasafe_logo_path():
    """Get the path to the Black InaSAFE SVG logo.

    .. versionadded:: 3.2
    """
    path = resources_path('img', 'logos', 'inasafe-logo-url.svg')
    return path


def white_inasafe_logo_path():
    """Get the path to the White InaSAFE SVG logo.

    .. versionadded:: 3.2
    """
    path = resources_path('img', 'logos', 'inasafe-logo-url-white.svg')
    return path


def supporters_logo_path():
    """Get the supporters logo path.

    .. versionchanged:: Changed in 3.2 from default_organisation_path to
        supporters_logo_path.

    :return: Default organisation logo path.
    :rtype: str
    """
    path = resources_path('img', 'logos', 'supporters.png')
    return path


def default_north_arrow_path():
    """Get a default north arrow image path.

    :return: Default north arrow path.
    :rtype: str
    """
    path = resources_path('img', 'north_arrows', 'simple_north_arrow.png')
    return path
