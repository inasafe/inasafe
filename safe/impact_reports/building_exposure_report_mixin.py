__author__ = 'christian@kartoza.com'

from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.common.tables import Table, TableRow


class BuildingExposureReportMixin(object):

    def generate_html_report(self, question, affected_buildings, buildings):
        """Breakdown by building type.

        :param question: The impact question.
        :type question: basestring

        :param affected_buildings: The affected buildings
        :type affected_buildings: OrderedDict

        :param buildings: The buildings and totals.
        :type buildings: dict

        :returns: The report in .
        :rtype: list
        """
        return self.parse_to_html(
            self.generate_report(
                question,
                affected_buildings,
                buildings))

    def generate_report(self, question, affected_buildings, buildings):
        """Breakdown by building type.

        :param question: The impact question.
        :type question: basestring

        :param affected_buildings: The affected buildings
        :type affected_buildings: OrderedDict

        :param buildings: The buildings and totals.
        :type buildings: dict

        :returns: The report.
        :rtype: list
        """
        report = [{'content': question}]
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.impact_summary(affected_buildings)
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.buildings_breakdown(affected_buildings, buildings)
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.action_checklist(affected_buildings)
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.notes()
        return report

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

    def impact_summary(self, affected_buildings):
        """The impact summary as per category

        :returns:
        """
        impact_summary_report = [
            {
                'content': [tr('Hazard Category'), tr('Buildings Affected')],
                'header': True
            }]
        for (category, building_breakdown) in affected_buildings.items():
            total_affected = 0
            for number_affected in building_breakdown.values():
                total_affected += number_affected
            impact_summary_report.append(
                {
                    'content': [tr(category), format_int(total_affected)]
                })
        return impact_summary_report

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

    @staticmethod  # While we have a static don't have affected_buildings as a
    def _count_usage(usage, affected_buildings):
        count = 0
        for category, category_breakdown in affected_buildings.items():
            for current_usage in category_breakdown:
                if current_usage.lower() == usage.lower():
                    count += category_breakdown[current_usage]
        return count

    def notes(self):
        """Additional notes to be used.

        :return: The notes to be added to this report

        ..Notes:
        Notes are very much specific to IFs so it is expected that this method
        is overwritten in the IF if needed.
        """
        return []

    def parse_to_html(self, report):
        """Convert a json compatible list of results to a tabulated version.

        :param report: A json compatible reoprt
        :type report: list

        :returns: Returns a tabulated version of the report
        :rtype: basestring
        """
        tabulated_report = []
        for row in report:
            row_template = {
                'content': '',
                'condition': True,
                'arguments': (),
                'header': False
            }
            row_template.update(row)
            if not row_template['condition']:
                continue
            if row_template['arguments']:
                content = row_template['content'] % row_template['arguments']
            else:
                content = row_template['content']
            if row_template['header']:
                table_row = TableRow(content, header=True)
            else:
                table_row = TableRow(content)
            tabulated_report.append(table_row)

        html_tabulated_report = Table(tabulated_report).toNewlineFreeString()
        return html_tabulated_report
