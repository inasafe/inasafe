# coding=utf-8
"""Definitions relating to default setting of fresh InaSAFE."""
from os.path import expanduser, abspath, join
# from safe.utilities.resources import resources_path

inasafe_default_settings = {
    'visibleLayersOnlyFlag': True,
    'set_layer_from_title_flag': True,
    'setZoomToImpactFlag': True,
    'set_show_only_impact_on_report': False,
    'setHideExposureFlag': False,
    'useSelectedFeaturesOnly': True,
    'useSentry': False,
    'template_warning_verbose': True,
    'showOrganisationLogoInDockFlag': False,
    'developer_mode': False,
    'generate_report': True,
    'memory_profile': False,

    'ISO19115_ORGANIZATION': 'InaSAFE.org',
    'ISO19115_URL': 'http://inasafe.org',
    'ISO19115_EMAIL': 'info@inasafe.org',
    'ISO19115_TITLE': 'InaSAFE analysis result',
    'ISO19115_LICENSE': 'Free use with accreditation',

    'keywordCachePath': abspath(join(
        expanduser('~'), '.inasafe', 'keywords.db')),

    # Make sure first to not have cyclic import
    # 'organisation_logo_path': resources_path(
    #     'img', 'logos', 'supporters.png'),
    # 'north_arrow_path': resources_path(
    #     'img', 'north_arrows', 'simple_north_arrow.png'),
    # 'defaultUserDirectory': '',
    # 'reportTemplatePath': '',
    # 'reportDisclaimer': ''
}
