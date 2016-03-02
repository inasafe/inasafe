

# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Building Exposure Report Mixin Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'Samweli Twesa Mwakisambwe "Samweli" <smwltwesa6@gmail.com>'
__date__ = '13/10/15'

from collections import OrderedDict

from safe.utilities.i18n import tr
from safe.impact_reports.report_mixin_base import ReportMixin

import safe.messaging as m
from safe.common.utilities import format_int
from safe.impact_functions.core import (
    evacuated_population_needs
)
from safe.gui.tools.minimum_needs.needs_profile import filter_needs_parameters
from safe.impact_functions.core import (
    population_rounding
)
from safe.messaging import styles


class PolygonPopulationExposureReportMixin(ReportMixin):
    """Population specific report.
    """

    def __init__(self):
        """Area specific report mixin.

        .. versionadded:: 3.2

        ..Notes::


        """
        self._question = ''
        self._areas = {}
        self._affected_areas = {}
        self._areas_population = {}
        self._total_population = 0
        self._unaffected_population = 0
        self._affected_population = {}
        self._other_population_counts = {}
        self._minimum_needs = []

    def generate_report(self):
        """Breakdown by building type.

        :returns: The report.
        :rtype: list
        """
        message = m.Message()
        message.add(m.Paragraph(self.question))
        message.add(self.impact_summary())
        message.add(self.minimum_needs_breakdown())
        message.add(self.action_checklist())
        message.add(self.notes())

        return message

    def action_checklist(self):
        """Polygon Population action.

        :returns: The population breakdown report.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        message.add(m.Heading(tr('Action checklist'), **styles.INFO_STYLE))
        population = population_rounding(
            sum(self.affected_population.values()))
        checklist = m.BulletedList()
        checklist.add(tr('Which group or people is most affected?'))
        checklist.add(
            tr('Who are the vulnerable people in the population and why?'))
        checklist.add(tr('How will warnings be disseminated?'))
        checklist.add(tr('What are people\'s likely movements?'))
        checklist.add(
            tr('What are the security factors for the affected people?'))
        checklist.add(
            tr('What are the security factors for relief responders?'))
        checklist.add(tr('How will we reach evacuated people?'))
        checklist.add(
            tr('What kind of food does the people normally consume?'))
        checklist.add(
            tr('What are the critical non-food items required by the affected '
               'people?'))
        checklist.add(tr(
            'Are there enough water supply, sanitation, hygiene, food, '
            'shelter, medicines and relief items available for %s people?'
            % format_int(population)))

        checklist.add(tr(
            'If yes, where are they located and how will we distribute them?'))
        checklist.add(tr(
            'If no, where can we obtain additional relief items and how will '
            'we distribute them?'))
        checklist.add(tr('What are the related health risks?'))
        checklist.add(
            tr('Who are the key people responsible for coordination?'))
        message.add(checklist)

        return message

    def minimum_needs_breakdown(self):
        """Breakdown by polygon population.

        :returns: The population breakdown report.
        :rtype: list
        """
        message = m.Message(style_class='container')
        message.add(m.Heading(
            tr('Evacuated people minimum needs'),
            **styles.INFO_STYLE))
        table = m.Table(
            style_class='table table-condensed table-striped')
        table.caption = None
        total_needs = self.total_needs
        for frequency, needs in total_needs.items():
            row = m.Row()
            row.add(m.Cell(
                tr('Relief items to be provided %s' % frequency),
                header=True
            ))
            row.add(m.Cell(tr('Total'), header=True, align='right'))
            table.add(row)
            for resource in needs:
                row = m.Row()
                row.add(m.Cell(tr(resource['table name'])))
                row.add(m.Cell(
                    tr(format_int(resource['amount'])),
                    align='right'
                ))
                table.add(row)
        message.add(table)
        return message

    @property
    def total_needs(self):
        """Get the total minimum needs based on the total evacuated.

        :returns: Total minimum needs.
        :rtype: dict
        """
        total_population_evacuated = sum(self.affected_population.values())
        self.minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]

        return evacuated_population_needs(
            total_population_evacuated, self.minimum_needs)

    def impact_summary(self):
        """The impact summary as per category

        :returns: The impact summary.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        table = m.Table(
            style_class='table table-condensed table-striped')
        table.caption = None

        row = m.Row()
        row = self.head_row(row)
        table.add(row)

        second_row = m.Row()
        second_row.add(m.Cell(tr('All')))
        second_row = self.total_row(second_row)
        table.add(second_row)

        break_row = m.Row()
        break_row.add(m.Cell(
            tr('Breakdown by Area'),
            header=True,
            align='right'))
        # intentionally empty right cells
        break_row.add(m.Cell('', header=True))
        break_row.add(m.Cell('', header=True))
        break_row.add(m.Cell('', header=True))
        break_row.add(m.Cell('', header=True))
        break_row.add(m.Cell('', header=True))
        break_row.add(m.Cell('', header=True))
        table.add(break_row)

        table = self.impact_calculation(table)
        last_row = m.Row()
        last_row.add(m.Cell(
            tr('Total')))
        table.add(self.total_row(last_row))

        hazard_table = m.Table(
            style_class='table table-condensed table-striped')
        hazard_table = self.hazard_table(hazard_table)

        message.add(hazard_table)
        message.add(table)

        return message

    def impact_calculation(self, table):
        """ Calculates impact on each area

        :param table: A table with first and second row
        :type table:Table

        :return A table with impact on each area
        :rtype Table
        """
        areas = self.areas
        affected_areas = self.affected_areas
        for area_id, value in areas.iteritems():
            if area_id in affected_areas:
                affected = affected_areas[area_id]
            else:
                affected = 0.0
            single_total_area = value

            if value:
                affected_area_ratio = affected / single_total_area
            else:
                affected_area_ratio = 0.0
            percent_affected = affected_area_ratio * 100
            percent_affected = round(percent_affected, 1)
            number_people_affected = (
                affected_area_ratio * self.areas_population[area_id])

            # rounding to float without decimal, we can't have number
            #  of people with decimal
            number_people_affected = round(number_people_affected, 0)

            if self.areas_population[area_id] != 0:
                percent_people_affected = (
                    (number_people_affected / self.areas_population[area_id]) *
                    100)
            else:
                percent_people_affected = 0
            affected *= 1e8
            single_total_area *= 1e8

            impact_row = self.impact_row(
                area_id, affected, percent_affected,
                single_total_area, number_people_affected,
                percent_people_affected)

            table.add(impact_row)

        return table

    def head_row(self, row):
        """Set and return header row in impact summary

        :param row: The empty header row
        :type row: Row

        :return Header row with content
        :rtype Row
        """
        row.add(m.Cell(
            tr('Area Name'),
            header=True,
            align='right'))
        row.add(m.Cell(
            tr('Affected Area (ha)'),
            header=True,
            align='right'))
        row.add(m.Cell(
            tr('Affected Area (%)'),
            header=True,
            align='right'))
        row.add(m.Cell(
            tr('Total (ha)'),
            header=True,
            align='right'))
        row.add(m.Cell(
            tr('Affected People'),
            header=True,
            align='right'))
        row.add(m.Cell(
            tr('Affected People(%)'),
            header=True,
            align='right'))
        row.add(m.Cell(
            tr('Total Number of People'),
            header=True,
            align='right'))

        return row

    def row(
            self,
            row,
            total_affected_area,
            percentage_affected_area,
            total_area,
            total_affected_population,
            total_population):
        """Adds values to the second row columns

        :param row: an empty row
        :type row: Row

        :param total_affected_area: total affected area
        :type total_affected_area: float

        :param percentage_affected_area: percentage of
        affected area
        :type percentage_affected_area: float

        :param total_area: total area
        :type total_area: float

        :param total_affected_population: total affected
        population
        :type total_affected_population: float

        :param total_population: total population
        :type total_population:float

        :return row
        :rtype Row
        """
        row.add(m.Cell(
            format_int(int(total_affected_area)), align='right'))
        row.add(m.Cell(
            "%.0f%%" % percentage_affected_area, align='right'))
        row.add(m.Cell(
            format_int(int(total_area)), align='right'))
        row.add(m.Cell(
            format_int(int(total_affected_population)), align='right'))
        row.add(m.Cell(
            "%.0f%%" % percentage_affected_area, align='right'))
        row.add(m.Cell(
            format_int(int(total_population)), align='right'))

        return row

    def total_row(self, row):
        """Calculates the total of each single column

        :param row: row in the summary
        :type row: Row

        :return row:  row with total contents
        :rtype: row: Row
        """

        total_affected_area = self.total_affected_areas
        total_area = self.total_areas

        if total_area != 0:
            percentage_affected_area = (
                (total_affected_area / total_area) *
                100)
        else:
            percentage_affected_area = 0
        percentage_affected_area = round(percentage_affected_area, 1)

        total_affected_population = self.total_affected_population
        total_population = self.total_population

        total_affected_area *= 1e8
        total_affected_area = round(total_affected_area, 1)
        total_area *= 1e8
        total_area = round(total_area, 0)
        total_affected_population = round(total_affected_population, 0)
        total_population = round(total_population, 0)

        row = self.row(
            row,
            total_affected_area,
            percentage_affected_area,
            total_area,
            total_affected_population,
            total_population)

        return row

    def impact_row(
            self,
            area_id,
            affected,
            percent_affected,
            single_total_area,
            number_people_affected,
            percent_people_affected):
        """Adds the calculated results into respective impact row

        :param area_id: Area id
        :type area_id: int

        :param affected: table with first and second row
        :type affected: Table

        :param percent_affected: percentage of affected area
        :type percent_affected:float

        :param single_total_area: total area of the land
        :type single_total_area:float

        :param number_people_affected: number of people affected
        :type number_people_affected:float

        :param percent_people_affected: percentage of people affected
        in the area
        :type percent_people_affected:float

        :return row: the new impact row
        :rtype row: Row
        """
        area_name = self.area_name(area_id)
        row = m.Row()
        row.add(m.Cell(area_name))
        row.add(m.Cell(format_int(int(affected)), align='right'))
        row.add(m.Cell(
            "%.1f%%" % percent_affected, align='right'))
        row.add(m.Cell(
            format_int(int(single_total_area)), align='right'))
        row.add(m.Cell(
            format_int(int(number_people_affected)),
            align='right'))
        row.add(m.Cell("%.1f%%" % percent_people_affected, align='right'))
        row.add(m.Cell(
            format_int(int(self.areas_population[area_id])),
            align='right'))

        return row

    @property
    def affected_population(self):
        """Get the affected population counts.

        :returns: Affected population counts.
        :rtype: dict
        """
        if not hasattr(self, '_affected_population'):
            self._affected_population = OrderedDict()
        return self._affected_population

    @affected_population.setter
    def affected_population(self, affected_population):
        """Set the affected population counts.
        :param affected_population: The population counts.
        :type affected_population: dict
        """
        self._affected_population = affected_population

    @property
    def question(self):
        """Get the impact function question.

        :returns: The impact function question.
        :rtype: basestring
        """
        if not hasattr(self, '_question'):
            self._question = ''
        return self._question

    @question.setter
    def question(self, question):
        """Set the impact function question.

        :param question: The question.
        :type question: basestring
        """
        self._question = question

    @property
    def unaffected_population(self):
        """Get the unaffected population count.

        :returns: The unaffected population count.
        :returns: int
        """
        if not hasattr(self, '_unaffected_population'):
            self._unaffected_population = 0
        return self._unaffected_population

    @unaffected_population.setter
    def unaffected_population(self, unaffected_population):
        """Set the unaffected population count.

        :param unaffected_population: The unaffected population count.
        :return: int
        """
        self._unaffected_population = unaffected_population

    @property
    def affected_areas(self):
        """Get the affected areas.

        :returns: affected areas.
        :rtype: {}.
        """
        return self._affected_areas

    @affected_areas.setter
    def affected_areas(self, affected_areas):
        """Set the affected areas.

        :param affected_areas: affected areas.
        :type affected_areas:dict
        """
        self._affected_areas = affected_areas

    @property
    def total_affected_areas(self):
        """Get the total affected areas.

        :returns: Total affected areas.
        :rtype: int.
        """
        return sum(self.affected_areas.values())

    @property
    def areas_population(self):
        """Get the areas population.

        :returns: areas population.
        :rtype: dict.
        """
        return self._areas_population

    @areas_population.setter
    def areas_population(self, areas_population):
        """Set the areas population.

        :param areas_population: area population.
        :type areas_population:dict
        """
        self._areas_population = areas_population

    @property
    def total_areas_population(self):
        """Get the total affected areas.

        :returns: Total affected areas.
        :rtype: int.
        """
        return sum(self.areas_population.values())

    @property
    def total_areas(self):
        """Get the total area.

        :returns: Total area.
        :rtype: int.
        """
        return sum(self.areas.values())

    @property
    def areas(self):
        """Get the areas.

        :returns: areas.
        :rtype: dict.
        """
        return self._areas

    @areas.setter
    def areas(self, areas):
        """Set the areas.

        :param areas.
        :type areas: dict
        """
        self._areas = areas

    @property
    def total_affected_population(self):
        """Get the total affected population.

        :returns: Total affected population.
        :rtype: int.
        """
        return sum(self.affected_population.values())

    @property
    def total_population(self):
        """Get the total population.

        :returns: The total population.
        :rtype: int
        """
        if not hasattr(self, '_total_population'):
            self._total_population = 0
        return self._total_population

    @total_population.setter
    def total_population(self, total_population):
        """Set the total population.

        :param total_population: The total population count.
        :type total_population: int
        """
        self._total_population = total_population

    def area_name(self, area_id):
        """ Return the name of area.

        :param area_id: area id.
        :type area_id: int

        :returns area_name: name of the area
        :rtype area_name: string
        """

        area_name = self.areas_names[area_id]

        return area_name

    def hazard_table(self, hazard_table):
        """ Return updated hazard table.

        :param hazard_table: hazard table.
        :type hazard_table: Table

        :returns hazard_table: Updated Hazard Table
        :rtype area_name: Table
        """
        hazard_table.caption = None

        for key, value in self.hazard_levels.iteritems():

            name = self.hazard_class_mapping[key][0]
            # This skips reporting people not affected in No zone
            if key == 'wet':
                row = m.Row()
                row.add(m.Cell(tr(
                    'People within hazard field ("%s") of value "%s"')
                               % (self.hazard_class_field, name),
                               header=True))
                value = format_int(population_rounding(value))
                row.add(m.Cell(value, align='right'))
            elif key == 'dry':
                continue
            else:
                row = m.Row()
                row.add(m.Cell(name, header=True))
                value = format_int(population_rounding(value))
                row.add(m.Cell(value, align='right'))
            hazard_table.add(row)

        # Total affected population
        row = m.Row()
        row.add(m.Cell(
            tr('Total affected people'),
            header=True))
        affected = format_int(
            population_rounding(self.total_affected_population))
        row.add(m.Cell(affected, align='right'))
        hazard_table.add(row)

        # Non affected population
        row = m.Row()
        unaffected = format_int(
            population_rounding(self.unaffected_population))
        row.add(m.Cell(tr('Unaffected people'), header=True))
        row.add(m.Cell(unaffected, align='right'))
        hazard_table.add(row)

        # Total Population
        row = m.Row()
        total_population = format_int(
            population_rounding(self.total_population))
        row.add(m.Cell(tr('Total people'), header=True))
        row.add(m.Cell(total_population, align='right'))
        hazard_table.add(row)

        return hazard_table

    def hazard_level_name(self, id):
        """ Return name of level corresponding the id.

        :param id: hazard level id.
        :type id: int

        :returns level_name:Name of the hazard level
        :rtype level_name: string
        """
        if id is 1:
            level_name = "Low"
        elif id is 2:
            level_name = "Medium"
        elif id is 3:
            level_name = "High"
        else:
            level_name = None

        return level_name

    @property
    def minimum_needs(self):
        """Get the minimum needs as specified, or default.

        :returns: The minimum needs parameters.
        :rtype: list
        """
        if not hasattr(self, '_minimum_needs'):
            self._minimum_needs = []
        return self._minimum_needs

    @minimum_needs.setter
    def minimum_needs(self, minimum_needs):
        """Set the minimum needs parameters list.

        :param minimum_needs: Minimum needs
        :type minimum_needs: list
        """
        self._minimum_needs = minimum_needs
