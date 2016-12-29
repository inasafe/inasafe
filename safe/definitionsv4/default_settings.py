# coding=utf-8
"""Definitions relating to default setting of fresh InaSAFE."""
from os.path import expanduser, abspath, join

inasafe_default_settings = {
    'visibleLayersOnlyFlag': True,
    'set_layer_from_title_flag': True,
    'setZoomToImpactFlag': True,
    'setHideExposureFlag': False,
    'useSelectedFeaturesOnly': False,
    'useSentry': False,
    'keywordCachePath': abspath(join(
        expanduser('~'), '.inasafe', 'keywords.db')),
    'template_warning_verbose': True,
    'showOrganisationLogoInDockFlag': False,
    'developer_mode': False,
    'ISO19115_ORGANIZATION': 'InaSAFE.org',
    'ISO19115_URL': 'http://inasafe.org',
    'ISO19115_EMAIL': 'info@inasafe.org',
    'ISO19115_TITLE': 'InaSAFE analysis result',
    'ISO19115_LICENSE': 'Free use with accreditation'

    # Some extras possible setting to be put here:
    # organisation_logo_path
    # defaultUserDirectory
    # north_arrow_path
    # reportTemplatePath
    # reportDisclaimer
}
