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
__author__ = 'Christian Christelis <christian@kartoza.com>'
__revision__ = '$Format:%H$'
__date__ = '05/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from collections import OrderedDict

from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.impact_reports.report_mixin_base import ReportMixin

from safe.impact_functions.core import (
    evacuated_population_needs,
    population_rounding)
import safe.messaging as m
from safe.messaging import styles


class PopulationExposureReportMixin(ReportMixin):
    """Population specific report.
    """

    def __init__(self):
        """Population specific report mixin.

        .. versionadded:: 3.2

        ..Notes::

            Expect affected population as following:

            _affected_population = OrderedDict([
                (impact level, amount),
            e.g.
                (People in high hazard area, 1000),
                (People in medium hazard area, 100),
                (People in low hazard area, 5),
            )]

        """
        self._question = ''
        self._total_population = 0
        self._unaffected_population = 0
        self._evacuation_category = 0
        self._evacuation_percentage = 0
        self._minimum_needs = []
        self._affected_population = {}
        self._other_population_counts = {}
        self._impact_category_ordering = []

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
        """Population action.

        :returns: The population breakdown report.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        message.add(m.Heading(tr('Action checklist'), **styles.INFO_STYLE))
        checklist = m.BulletedList()
        checklist.add(tr('How will warnings be disseminated?'))
        checklist.add(tr('How will we reach evacuated people?'))
        checklist.add(tr(
            'Are there enough shelters and relief items available '
            'for %s people?' % self.total_evacuated))
        checklist.add(tr(
            'If yes, where are they located and how will we distribute them?'))
        checklist.add(tr(
            'If no, where can we obtain additional relief items from '
            'and how will we transport them to here?'))
        message.add(checklist)
        return message

    def impact_summary(self):
        """The impact summary as per category

        :returns: The impact summary.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None
        row = m.Row()
        row.add(m.Cell(
            tr('Population needing evacuation <sup>1</sup>'),
            header=True))
        evacuated = format_int(population_rounding(self.total_evacuated))
        row.add(m.Cell(evacuated, align='right'))
        table.add(row)
        if len(self.impact_category_ordering):
            table.add(m.Row())  # add a blank line
            row = m.Row()
            row.add(m.Cell(
                tr('Total affected population'),
                header=True))
            affected = format_int(
                population_rounding(self.total_affected_population))
            row.add(m.Cell(affected, align='right'))
            table.add(row)

            for category in self.impact_category_ordering:
                population_in_category = self.lookup_category(category)
                population_in_category = format_int(population_rounding(
                    population_in_category
                ))
                row = m.Row()
                row.add(m.Cell(tr(category), header=True))
                row.add(m.Cell(population_in_category, align='right'))
                table.add(row)

        table.add(m.Row())  # add a blank line

        row = m.Row()
        unaffected = format_int(
            population_rounding(self.unaffected_population))
        row.add(m.Cell(tr('Unaffected population'), header=True))
        row.add(m.Cell(unaffected, align='right'))
        table.add(row)
        message.add(table)
        return message

    def minimum_needs_breakdown(self):
        """Breakdown by population.

        :returns: The population breakdown report.
        :rtype: list
        """
        message = m.Message(style_class='container')
        message.add(m.Heading(
            tr('Evacuated population minimum needs'),
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
    def impact_category_ordering(self):
        """Get the ordering of the impact categories.

        :returns: The categories by defined or default ordering.
        :rtype: list
        """
        if (
                not hasattr(self, '_impact_category_ordering') or
                not self._impact_category_ordering):
            self._impact_category_ordering = self.affected_population.keys()
        return self._impact_category_ordering

    @impact_category_ordering.setter
    def impact_category_ordering(self, impact_category_ordering):
        """Overwrite existing category ordering.

        :param impact_category_ordering: The new ordering.
        :type impact_category_ordering: list.
        """
        self._impact_category_ordering = impact_category_ordering

    @property
    def other_population_counts(self):
        """The population counts which are not explicitly included in affected.

        :returns: Population counts.
        :rtype: dict
        """
        if not hasattr(self, '_other_population_counts'):
            self._other_population_counts = {}
        return self._other_population_counts

    @other_population_counts.setter
    def other_population_counts(self, other_counts):
        """Set the other population counts.

        :param other_counts: Population counts.
        :type other_counts: dict
        """
        if not hasattr(self, '_other_population_counts'):
            self._other_population_counts = {}
        self._other_population_counts = other_counts

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
    def total_affected_population(self):
        """Get the total affected population.

        :returns: Total affected population.
        :rtype: int.
        """
        return sum(self.affected_population.values())

    def lookup_category(self, category):
        """Lookup a category by its name.

        :param category: The category to be looked up.
        :type category: basestring

        :returns: The category's count.
        :rtype: int

        .. note:: The category may be any valid category, but it also includes
            'Population Not Affected', 'Unaffected Population' for unaffected
            as well as 'Total Impacted', 'People impacted',
            'Total Population Affected' for total affected population. This
            diversity is to accodate existing usages, which have evolved
            separately. We may want to update these when we have decided on a
            single convention.
        """
        if category in self.affected_population.keys():
            return self.affected_population[category]
        if category in self.other_population_counts.keys():
            return self.other_population_counts[category]
        if category in [
                tr('Population Not Affected'),
                tr('Unaffected Population')]:
            return self.unaffected_population
        if category in [
                tr('Total Impacted'),
                tr('People impacted'),
                tr('Total Population Affected')]:
            return self.total_affected_population

    @property
    def total_needs(self):
        """Get the total minimum needs based on the total evacuated.

        :returns: Total minimum needs.
        :rtype: dict
        """
        total_population_evacuated = self.total_evacuated
        return evacuated_population_needs(
            total_population_evacuated, self.minimum_needs)

    @property
    def total_evacuated(self):
        """Get the total evacuated population.

        :returns: The total evacuated population.
        :rtype: int

        .. note:: The total evacuated is said to either the evacuated amount,
        failing that the total affected population and if applicable reduced
        by a evacuation percentage.
        """
        if hasattr(self, '_evacuation_category') and self._evacuation_category:
            evacuated_population = self.affected_population[
                self._evacuation_category]
        else:
            evacuated_population = self.total_affected_population
        if (
                hasattr(self, '_evacuation_percentage') and
                self._evacuation_percentage):
            evacuated_population = (
                evacuated_population * self._evacuation_percentage / 100)
        return int(evacuated_population)

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
