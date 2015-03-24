from safe.common.utilities import format_int

from safe.utilities.i18n import tr


class BuildingExposureReportMixin(object):

    @property
    def action_checklist(self, affected_buildings):
        """Breakdown by building type.

        :param affected_buildings: The affected buildings
        :type affected_buildings: OrderedDict

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
        """
        schools_closed = self.schools_closed(affected_buildings)
        hospitals_closed = self.hospitals_closed(affected_buildings)
        return [
            {
                'content': tr('Action Checklist:'),
                'header': True
            },
            {
                'content': tr('Are the critical facilities still open?')
            },
            {
                'content': tr(
                    'Which structures have warning capacity '
                    '(eg. sirens, speakers, etc.)?')},
            {
                'content': tr('Which buildings will be evacuation centres?')
            },
            {
                'content': tr('Where will we locate the operations centre?')
            },
            {
                'content': tr(
                    'Where will we locate warehouse and/or distribution '
                    'centres?')
            },
            {
                'content': tr(
                    'Where will the students from the %s closed schools go to '
                    'study?'),
                'arguments': (format_int(schools_closed),),
                'condition': schools_closed > 0
            },
            {
                'content': tr(
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
        buildings_breakdown_report = []
        category_names = affected_buildings.keys()
        table_headers = [tr('Building type')]
        table_headers += [tr(x) for x in category_names]
        table_headers += [tr('Total')]
        buildings_breakdown_report.append(
            {
                'content': table_headers,
                'header': True
            })
        # Let's sort alphabetically first
        building_types = [building_type for building_type in buildings]
        building_types.sort()
        for building_type in building_types:
            building_type = building_type.replace('_', ' ')
            affected_by_usage = []
            for category in category_names:
                if building_type in affected_buildings[category]:
                    affected_by_usage.append(
                        format_int(
                            affected_buildings[category][building_type]))
                else:
                    affected_by_usage.append(format_int(0))
            building_detail = (
                # building type
                [building_type.capitalize()] +
                # categories
                affected_by_usage +
                # total
                [format_int(buildings[building_type])])
            buildings_breakdown_report.append(
                {
                    'content': building_detail
                })

        return buildings_breakdown_report

    #This could be a property if we make affected_buildings a class property
    def schools_closed(self, affected_buildings):
        """Get the number of schools

        :param affected_buildings: The affected buildings
        :type affected_buildings: OrderedDict

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
        """
        return self._count_usage('school', affected_buildings)

    #This could also be a property if we make affected_buildings a class property
    def hospitals_closed(self, affected_buildings):
        """Get the number of schools

        :param affected_buildings: The affected buildings
        :type affected_buildings: OrderedDict

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
        """
        return self._count_usage('hospital', affected_buildings)

    def _count_usage(self, usage, affected_buildings):
        count = 0
        for cagegory, category_breakdown in affected_buildings:
            for current_usage in category_breakdown:
                if current_usage.lower() == usage.lower():
                    count += affected_buildings[current_usage]
        return count

