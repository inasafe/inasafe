# coding=utf-8

"""Definitions relating to infographic template elements."""

from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


"""Map elements"""


map_overview = {
    'id': 'map-overview',
    'path': resources_path('img', 'raster_layer', 'map-overview.tif')
}


"""HTML frame elements"""


people_section_notes = {
    'id': 'people-section-notes',
    'mode': 'text',
    'text': '',
    'component': 'infographic-people-section-notes'
}

population_chart_legend = {
    'id': 'population-chart-legend',
    'mode': 'text',
    'text': '',
    'component': 'population-chart-legend'
}

html_frame_elements = [people_section_notes, population_chart_legend]


"""Header label elements"""


infographic_header = {
    'id': 'infographic-header',
    'string_format': tr('Estimated impact of {impact_function_name}')
}

map_overview_header = {
    'id': 'map-overview-header',
    'string_format': tr('Event location')
}

population_chart_header = {
    'id': 'population-chart-header',
    'string_format': tr('Estimated number of people affected by hazard level')
}

people_section_header = {
    'id': 'people-section-header',
    'string_format': tr('People affected by hazard')
}

age_gender_section_header = {
    'id': 'age-gender-section-header',
    'string_format': tr('People displaced by age and gender')
}

vulnerability_section_header = {
    'id': 'vulnerability-section-header',
    'string_format': tr(
        'Vulnerable people displaced by age, gender, and disability')
}

female_vulnerability_section_header = {
    'id': 'female-vulnerability-section-header',
    'string_format': tr('Displaced females by vulnerability')
}

minimum_needs_section_header = {
    'id': 'minimum-needs-section-header',
    'string_format': tr('Minimum needs for displaced people')
}

additional_minimum_needs_section_header = {
    'id': 'additional-minimum-needs-section-header',
    'string_format': tr('Additional needs for vulnerable females')
}

no_data_replacement = {
    'id': 'no-data-replacement',
    'string_format': tr('-')
}

minimum_needs_unit = {
    'id': 'minimum-needs-unit',
    'string_format': tr('{unit_abbreviation}/{frequency}')
}

age_gender_section_notes = {
    'id': 'age-gender-section-notes',
    'string_format': tr('The total number of displaced people presented is '
                        'the result of the InaSAFE population analysis. '
                        'The total results has been rounded to the nearest '
                        'thousand. The size of the icon does not represent '
                        'the number.If there is a value of 0, then '
                        'corresponding object will not be displayed on '
                        'this page.')
}

minimum_needs_section_notes = {
    'id': 'minimum-needs-section-notes',
    'string_format': tr(
        'Minimum needs based on Peraturan Kepala (Perka) BNPB No. 7/2008. '
        'Additional needs for vulnerable females based on Sphere Standard '
        '(http://www.spherehandbook.org/en/appendix-6/)')
}


"""Image elements"""


inasafe_logo_white = {
    'id': 'inasafe-logo-white',
    'path': resources_path('img', 'logos', 'inasafe-logo-url-white.svg')
}

icon_overview = {
    'id': 'icon-overview',
    'path': resources_path('img', 'icons', 'map-overview.svg')
}

population_chart = {
    'id': 'population-chart',
    'path': ''
}

icon_affected = {
    'id': 'icon-affected',
    'path': resources_path('img', 'definitions', 'people.svg')
}

icon_displaced = {
    'id': 'icon-displaced',
    'path': resources_path('img', 'definitions', 'displaced.svg')
}

icon_infant_displaced = {
    'id': 'icon-infant-displaced',
    'path': resources_path('img', 'definitions', 'infant.svg')
}

icon_child_displaced = {
    'id': 'icon-child-displaced',
    'path': resources_path('img', 'definitions', 'child.svg')
}

icon_adult_displaced = {
    'id': 'icon-adult-displaced',
    'path': resources_path('img', 'definitions', 'adult.svg')
}

icon_elderly_displaced = {
    'id': 'icon-elderly-displaced',
    'path': resources_path('img', 'definitions', 'elderly.svg')
}

icon_male_displaced = {
    'id': 'icon-male-displaced',
    'path': resources_path('img', 'definitions', 'male.svg')
}

icon_female_displaced = {
    'id': 'icon-female-displaced',
    'path': resources_path('img', 'definitions', 'female.svg')
}

icon_under_5_displaced = {
    'id': 'icon-under-5-displaced',
    'path': resources_path('img', 'definitions', 'under_5.svg')
}

icon_over_60_dsplaced = {
    'id': 'icon-over-60-displaced',
    'path': resources_path('img', 'definitions', 'over_60.svg')
}

icon_disabled_displaced = {
    'id': 'icon-disabled-displaced',
    'path': resources_path('img', 'definitions', 'disabled.svg')
}

icon_child_bearing_age_displaced = {
    'id': 'icon-child-bearing-age-displaced',
    'path': resources_path('img', 'definitions', 'child_bearing.svg')
}

icon_pregnant_displaced = {
    'id': 'icon-pregnant-displaced',
    'path': resources_path('img', 'definitions', 'pregnant.svg')
}

icon_lactating_displaced = {
    'id': 'icon-lactating-displaced',
    'path': resources_path('img', 'definitions', 'pregnant_lactating.svg')
}

icon_minimum_needs_rice = {
    'id': 'icon-minimum-needs-rice',
    'path': resources_path('img', 'definitions', 'rice.svg')
}

icon_minimum_needs_drinking_water = {
    'id': 'icon-minimum-needs-drinking-water',
    'path': resources_path('img', 'definitions', 'drinking_water.svg')
}

icon_minimum_needs_clean_water = {
    'id': 'icon-minimum-needs-clean-water',
    'path': resources_path('img', 'definitions', 'clean_water.svg')
}

icon_minimum_needs_family_kit = {
    'id': 'icon-minimum-needs-family-kit',
    'path': resources_path('img', 'definitions', 'family_kits.svg')
}

icon_minimum_needs_toilet = {
    'id': 'icon-minimum-needs-toilet',
    'path': resources_path('img', 'definitions', 'toilets.svg')
}

icon_additional_rice = {
    'id': 'icon-additional-rice',
    'path': resources_path('img', 'definitions', 'rice.svg')
}

icon_hygiene_pack = {
    'id': 'icon-hygiene-pack',
    'path': resources_path('img', 'definitions', 'hygiene_pack.svg')
}

image_item_elements = [
    inasafe_logo_white,
    icon_overview,
    population_chart,
    icon_affected,
    icon_displaced,
    icon_infant_displaced,
    icon_child_displaced,
    icon_adult_displaced,
    icon_elderly_displaced,
    icon_male_displaced,
    icon_female_displaced,
    icon_under_5_displaced,
    icon_over_60_dsplaced,
    icon_disabled_displaced,
    icon_child_bearing_age_displaced,
    icon_pregnant_displaced,
    icon_lactating_displaced,
    icon_minimum_needs_rice,
    icon_minimum_needs_drinking_water,
    icon_minimum_needs_clean_water,
    icon_minimum_needs_family_kit,
    icon_minimum_needs_toilet,
    icon_additional_rice,
    icon_hygiene_pack
]
