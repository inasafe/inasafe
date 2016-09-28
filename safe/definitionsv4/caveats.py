from safe.utilities.i18n import tr

caveat_simulation = tr(
    'The extent and severity of the mapped scenario or hazard zones '
    'may not be consistent with future events.')
caveat_local_conditions = tr(
    'The impacts on roads, people, buildings and other exposure '
    'elements may differ from the analysis results due to local '
    'conditions such as terrain and infrastructure type.')
no_data_warning = [
    tr(
        'The layers contained "no data" values. This missing data '
        'was carried through to the impact layer.'),
    tr(
        '"No data" values in the impact layer were treated as 0 '
        'when counting the affected or total population.')
]
