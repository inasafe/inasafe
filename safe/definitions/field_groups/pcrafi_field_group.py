
from safe.definitions.fields import (
    pcrafi_damage_state_1_count_field,
    pcrafi_damage_state_2_count_field,
    pcrafi_damage_state_3_count_field,
    pcrafi_damage_state_4_count_field,
    pcrafi_damage_state_5_count_field,
)
from safe.utilities.i18n import tr

pcrafi_damage_state_count_group = {
    'key': 'pcrafi_damage_state_count_group',
    'name': tr('PCRAFI damage state count group'),
    'header_name': tr('Damage state'),
    'description': tr(
        'TODO'),
    'fields': [
        pcrafi_damage_state_1_count_field,
        pcrafi_damage_state_2_count_field,
        pcrafi_damage_state_3_count_field,
        pcrafi_damage_state_4_count_field,
        pcrafi_damage_state_5_count_field,
    ],
    # Exclusive = False: able to put same layer's field to some fields
    # Exclusive = True: only able to put a layer's field to a field
    'exclusive': False, # TODO : OD : don't know what this is
    'notes': []
}