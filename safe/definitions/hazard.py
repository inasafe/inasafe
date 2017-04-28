# coding=utf-8

"""Definitions relating to hazards."""

from safe.definitions.hazard_classifications import (
    generic_hazard_classes,
    volcano_hazard_classes,
    earthquake_mmi_scale,
    flood_hazard_classes,
    flood_petabencana_hazard_classes,
    tsunami_hazard_classes,
    tsunami_hazard_population_classes,
    tsunami_hazard_classes_ITB,
    tsunami_hazard_population_classes_ITB,
    ash_hazard_classes,
    cyclone_au_bom_hazard_classes,
    cyclone_sshws_hazard_classes)
from safe.definitions.caveats import (
    caveat_simulation, caveat_local_conditions, caveat_analysis_extent,)
from safe.definitions.concepts import concepts
from safe.definitions.units import (
    unit_feet,
    unit_generic,
    unit_kilogram_per_meter_square,
    unit_kilometres,
    unit_metres,
    unit_millimetres,
    unit_centimetres,
    unit_mmi,
    unit_miles_per_hour,
    unit_kilometres_per_hour,
    unit_knots,
    unit_metres_per_second)
from safe.definitions.layer_modes import (
    layer_mode_classified, layer_mode_continuous)
from safe.definitions.fields import (
    hazard_name_field, hazard_fields, hazard_value_field)
from safe.definitions.earthquake import EARTHQUAKE_FUNCTIONS
from safe.definitions.exposure import (
    exposure_place,
    exposure_land_cover,
    exposure_road,
    exposure_population)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

continuous_hazard_unit = {
    'key': 'continuous_hazard_unit',
    'name': tr('Units'),
    'description': tr(
        'Hazard units are used for continuous data. Examples of hazard units '
        'include metres and feet.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'types': [
        unit_feet,
        unit_generic,
        unit_kilogram_per_meter_square,
        unit_kilometres,
        unit_metres,
        unit_millimetres,
        unit_centimetres,
        unit_mmi,
        unit_kilometres_per_hour,
        unit_miles_per_hour,
        unit_knots,
        unit_metres_per_second
    ]
}
continuous_hazard_unit_all = continuous_hazard_unit['types']
hazard_generic = {
    'key': 'hazard_generic',
    'name': tr('Generic'),
    'description': tr(
        'A <b>generic hazard</b> can be used for any type of hazard where the '
        'data have been classified or generalised. For example: earthquake, '
        'flood, volcano, tsunami, landslide, smoke haze or strong wind. '
        'You can use the generic hazard functionality in InaSAFE to carry '
        'out an assessment for hazard data that are not explicitly supported '
        'yet in InaSAFE.'),
    'notes': [  # additional generic notes for generic
        caveat_simulation,
        caveat_local_conditions,
        caveat_analysis_extent,
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'single_event_notes': [  # notes specific to single event data
    ],
    'multi_event_notes': [  # notes specific to multi event data
    ],
    'actions': [  # these are additional generic actions

    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'continuous_hazard_units': [],
    'allowed_geometries': [
        'polygon',
        'raster'
    ],
    'classifications': [generic_hazard_classes],
    'compulsory_fields': [hazard_value_field],
    'fields': hazard_fields,
    'extra_fields': [],
    'field_groups': [],
    'layer_modes': [layer_mode_classified],
    'disabled_exposures': [exposure_place]
}
hazard_earthquake = {
    'key': 'earthquake',
    'name': tr('Earthquake'),
    'description': tr(
        'An <b>earthquake</b> describes the sudden violent shaking of the '
        'ground that occurs as a result of volcanic activity or movement '
        'in the earth\'s crust.'),
    'notes': [  # additional generic notes for earthquake
        caveat_simulation,
        caveat_local_conditions,
        caveat_analysis_extent,
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'single_event_notes': [  # notes specific to single event data
    ],
    'multi_event_notes': [  # notes specific to multi event data
    ],
    'actions': [  # these are additional generic actions
    ],
    'earthquake_fatality_models': EARTHQUAKE_FUNCTIONS,  # Only for EQ
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'continuous_hazard_units': [unit_mmi, unit_generic],
    'allowed_geometries': [
        'polygon',
        'raster'
    ],
    'classifications': [generic_hazard_classes, earthquake_mmi_scale],
    'compulsory_fields': [hazard_value_field],
    'fields': hazard_fields,
    'extra_fields': [],
    'field_groups': [],
    'layer_modes': [layer_mode_classified, layer_mode_continuous],
    'disabled_exposures': [
        exposure_place,
        exposure_land_cover,
    ]
}
hazard_flood = {
    'key': 'flood',
    'name': tr('Flood'),
    'description': tr(
        'A <b>flood</b> describes the inundation of land that is normally dry '
        'by a large amount of water. For example: A <b>flood</b> can occur '
        'after heavy rainfall, when a river overflows its banks or when a '
        'dam breaks. The effect of a <b>flood</b> is for land that is '
        'normally dry to become wet.'),
    'notes': [  # additional generic notes for flood
        caveat_simulation,
        caveat_local_conditions,
        caveat_analysis_extent,
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'single_event_notes': [  # notes specific to single event data
    ],
    'multi_event_notes': [  # notes specific to multi event data
    ],
    'actions': [  # these are additional generic actions

    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'continuous_hazard_units': [unit_feet, unit_metres, unit_generic],
    'allowed_geometries': [
        'polygon',
        'raster'
    ],
    'classifications': [
        flood_hazard_classes,
        flood_petabencana_hazard_classes,
        generic_hazard_classes],
    'compulsory_fields': [hazard_value_field],
    'fields': hazard_fields,
    'extra_fields': [],
    'field_groups': [],
    'layer_modes': [layer_mode_classified, layer_mode_continuous],
    'disabled_exposures': [exposure_place]
}

hazard_cyclone = {
    'key': 'cyclone',
    'name': tr('Cyclone'),
    'description': tr(
        'A <b>Cyclone</b> is a rapidly rotating storm system characterised '
        'by a low-pressure centre, a closed low-level atmospheric '
        'circulation, strong winds, and a spiral arrangement of thunderstorms '
        'that produce heavy rain. It is also referred to as <b>hurricane</b> '
        'or <b>typhoon</b>.'),
    'notes': [  # additional generic notes for cyclone
        caveat_simulation,
        caveat_local_conditions,
        caveat_analysis_extent,
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'single_event_notes': [  # notes specific to single event data
    ],
    'multi_event_notes': [  # notes specific to multi event data
    ],
    'actions': [  # these are additional generic actions

    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'continuous_hazard_units': [
        unit_miles_per_hour,
        unit_kilometres_per_hour,
        unit_knots,
        unit_metres_per_second
    ],
    'allowed_geometries': [
        'polygon',
        'raster'
    ],
    'classifications': [
        cyclone_au_bom_hazard_classes,
        cyclone_sshws_hazard_classes,
        generic_hazard_classes
    ],
    'compulsory_fields': [hazard_value_field],
    'fields': hazard_fields,
    'extra_fields': [],
    'field_groups': [],
    'layer_modes': [layer_mode_classified, layer_mode_continuous],
    'disabled_exposures': [
        exposure_place,
        exposure_land_cover,
        exposure_road,
        exposure_population
    ]
}

hazard_volcanic_ash = {
    'key': 'volcanic_ash',
    'name': tr('Volcanic ash'),
    'description': tr(
        '<b>Volcanic ash</b> describes fragments of pulverized rock, minerals '
        'and volcanic glass, ejected into the atmosphere during volcanic '
        'eruptions.'),
    'notes': [  # additional generic notes for volcanic ash
        caveat_simulation,
        caveat_local_conditions,
        caveat_analysis_extent,
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'single_event_notes': [  # notes specific to single event data
        tr('Volcanic ash is modelled hazard data estimating the thickness of '
           'ash on the ground following a volcanic eruption.')
    ],
    'multi_event_notes': [  # notes specific to multi event data
    ],
    'actions': [  # these are additional volcanic ash actions
        tr('What action can be taken to secure water supplies and protect '
           'crops?')
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'continuous_hazard_units': [unit_centimetres],
    'allowed_geometries': [
        'polygon',
        'raster'
    ],
    'classifications': [ash_hazard_classes, generic_hazard_classes],
    'compulsory_fields': [hazard_value_field],
    'fields': hazard_fields,
    'extra_fields': [],
    'field_groups': [],
    'layer_modes': [layer_mode_classified, layer_mode_continuous],
    'disabled_exposures': []
}
hazard_tsunami = {
    'key': 'tsunami',
    'name': tr('Tsunami'),
    'description': tr(
        'A <b>tsunami</b> describes a large ocean wave or series or '
        'waves usually caused by an underwater earthquake or volcano. '
        'A <b>tsunami</b> at sea may go unnoticed but a <b>tsunami</b> '
        'wave that strikes land may cause massive destruction and '
        'flooding.'),
    'notes': [  # additional generic notes for tsunami
        caveat_simulation,
        caveat_local_conditions,
        caveat_analysis_extent,
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'single_event_notes': [  # notes specific to single event data
        tr('Tsunami hazard scenarios estimate the maximum extent of tsunami '
           'waves on land.')
    ],
    'multi_event_notes': [  # notes specific to multi event data
    ],
    'actions': [  # these are additional tsunami actions

    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'continuous_hazard_units': [unit_feet, unit_metres],
    'allowed_geometries': [
        'polygon',
        'raster'
    ],
    'classifications': [
        tsunami_hazard_classes,
        tsunami_hazard_population_classes,
        tsunami_hazard_classes_ITB,
        tsunami_hazard_population_classes_ITB,
    ],
    'compulsory_fields': [hazard_value_field],
    'fields': hazard_fields,
    'extra_fields': [],
    'field_groups': [],
    'layer_modes': [layer_mode_classified, layer_mode_continuous],
    'disabled_exposures': [exposure_place]
}
hazard_volcano = {
    'key': 'volcano',
    'name': tr('Volcano'),
    'description': tr(
        'A <b>volcano</b> describes a mountain which has a vent through '
        'which rock fragments, ash, lava, steam and gases can be ejected '
        'from below the earth\'s surface. The type of material ejected '
        'depends on the type of <b>volcano</b>.'),
    'notes': [  # additional generic notes for volcano
        caveat_simulation,
        caveat_local_conditions,
        caveat_analysis_extent,
    ],
    'actions': [  # these are additional volcano actions

    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'single_event_notes': [  # notes specific to single event data
    ],
    'multi_event_notes': [  # notes specific to multi event data
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'continuous_hazard_units': [],
    'allowed_geometries': [
        'polygon',
        # 'raster'  # Disable per #3600
    ],
    'classifications': [volcano_hazard_classes, generic_hazard_classes],
    'compulsory_fields': [hazard_value_field],
    'fields': hazard_fields,
    'extra_fields': [hazard_name_field],
    'field_groups': [],
    'layer_modes': [layer_mode_classified],
    'disabled_exposures': [exposure_place]
}
hazard_all = [
    hazard_flood,
    hazard_tsunami,
    hazard_earthquake,
    hazard_volcano,
    hazard_volcanic_ash,
    hazard_cyclone,
    hazard_generic
]
hazards = {
    'key': 'hazards',
    'name': tr('Hazards'),
    'description': concepts['hazard']['description'],
    'types': hazard_all,
    'citations': concepts['hazard']['citations']
}
