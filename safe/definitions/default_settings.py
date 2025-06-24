# coding=utf-8
"""Definitions relating to default setting of fresh InaSAFE."""
from os.path import join

from qgis.core import QgsApplication

from safe.defaults import supporters_logo_path, default_north_arrow_path
from safe.definitions.currencies import idr
from safe.definitions.messages import disclaimer

inasafe_default_settings = {
    'visibleLayersOnlyFlag': False,
    'set_layer_from_title_flag': True,
    'setZoomToImpactFlag': True,
    'set_show_only_impact_on_report': False,
    'print_atlas_report': False,
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
    'ISO19115_LICENSE': 'Free use with accreditation',

    # Welcome message
    'always_show_welcome_message': True,
    'previous_version': '0.0.0',  # It will be set in plugin, no need to worry

    'currency': idr['key'],

    'keywordCachePath': join(
        QgsApplication.qgisSettingsDirPath(), 'inasafe', 'metadata.db'),

    # Make sure first to not have cyclic import
    'organisation_logo_path': supporters_logo_path(),
    'north_arrow_path': default_north_arrow_path(),
    # 'defaultUserDirectory': '',
    # 'reportTemplatePath': '',
    'reportDisclaimer': disclaimer()
}
