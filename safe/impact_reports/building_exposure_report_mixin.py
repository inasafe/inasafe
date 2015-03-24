from safe.common.utilities import format_int


class BuildingExposureReportMixin(object):
    def __init__(self):
        self.affected_buildings = {}

    @property
    def action_checklist(self):
        schools_closed = 0
        hospitals_closed = 0
        for usage in self.affected_buildings:
            if usage.lower() == 'school':
                schools_closed = self.affected_buildings[usage]
            if usage.lower() == 'hospital':
                hospitals_closed = self.affected_buildings[usage]

        return [
            {
                'text': tr('Action Checklist:'),
                'header': True
            },
            {
                'text': tr('Are the critical facilities still open?')
            },
            {
                'text': tr(
                    'Which structures have warning capacity '
                    '(eg. sirens, speakers, etc.)?')},
            {
                'text': tr('Which buildings will be evacuation centres?')
            },
            {
                'text': tr('Where will we locate the operations centre?')
            },
            {
                'text': tr(
                    'Where will we locate warehouse and/or distribution '
                    'centres?')
            },
            {
                'text': tr(
                    'Where will the students from the %s closed schools go to '
                    'study?'),
                'arguments': (format_int(schools_closed),),
                'condition': schools_closed > 0
            },
            {
                'text': tr(
                    'Where will the patients from the %s closed hospitals go '
                    'for treatment and how will we transport them?'),
                'arguments': (format_int(hospitals_closed),),
                'condition': hospitals_closed > 0
            }
        ]

    def buildings_breakdown(self, affected_buildings, buildings):
        """Breakdown by building type.

        :param affected_buildings: The affected buildings
        :type affected_buildings: OrderedDict

        :param buildings: The buildings totals
        :type buildings: dict

        :returns: The buildings breakdown report.
        :rtype: list

        ..Notes:
        Expect affected buildings to be given as following:
            affected_buildings = OrderedDict([
                (category, {building_type: amount}),
            e.g.
                (inundated, {residential: 1000, school: 0 ...}),
                (wet, {residential: 12, school: 2 ...}),
                (dry, {residential: 50, school: 50})
            ])
            buildings = {residential: 1062, school: 52 ...}
        """
        category_names = affected_buildings.keys()
        table_headers = [tr('Building type')]
        table_headers += [tr(x) for x in category_names]
        table_headers += [tr('Total')]
        building_list = []
        # Let's sort alphabetically first
        building_types = [building_type for building_type in buildings
        building_types.sort()
        for building_type in building_types:
            building_type = usage.replace('_', ' ')
            affected_by_usage = []
            for category in category_names:
                if usage in affected_buildings[category]:
                    affected_by_usage.append(
                        format_int(affected_buildings[category][usage]))
                else:
                    affected_by_usage.append(format_int(0))
            building_list.appen(
                # building type                 categories            total
                [building_type.capitalize()] + affected_by_usage + [format_int(buildings[usage])])

