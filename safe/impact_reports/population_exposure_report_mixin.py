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

from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.impact_reports.report_mixin_base import ReportMixin

from safe.impact_functions.core import (
    evacuated_population_needs,
    population_rounding)


class PopulationExposureReportMixin(ReportMixin):
    """Building specific report.
    """

    def __init__(self):
        """Population specific report mixin.

        .. versionadded:: 3.3

        ..Notes:
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
        self._total_population = None
        self._unaffected_population = None
        self._evacuation_category = None
        self._evacuation_percentage = None
        self._minimum_needs = []
        self._affected_population = {}
        self._other_population_counts = {}
        self._impact_category_ordering = []

    def generate_report(self):
        """Breakdown by building type.

        :returns: The report.
        :rtype: list
        """
        report = [{'content': self.question}]
        report += [self.blank_line]  # Blank line to separate report sections
        report += self.impact_summary()
        report += [self.blank_line]
        report += self.minimum_needs_breakdown()
        report += [self.blank_line]
        report += self.action_checklist()
        report += [self.blank_line]
        report += self.notes()
        return report

    def action_checklist(self):
        """Breakdown by building type.

        :returns: The buildings breakdown report.
        :rtype: list
        """

        return [
            {
                'content': tr('Action checklist'),
                'header': True
            },
            {
                'content': tr('How will warnings be disseminated?')
            },
            {
                'content': tr('How will we reach evacuated people?')
            },
            {
                'content': tr(
                    'Are there enough shelters and relief items available '
                    'for %s people?' % self.total_evacuated)
            },
            {
                'content': tr(
                    'If yes, where are they located and how will we '
                    'distribute them?')
            },
            {
                'content': tr(
                    'If no, where can we obtain additional relief items from '
                    'and how will we transport them to here?')
            }
        ]

    def impact_summary(self):
        """The impact summary as per category

        :returns: The impact summary.
        :rtype: list
        """
        impact_summary_report = [(
            {
                'content': [
                    tr('Population needing evacuation <sup>1</sup>'),
                    '%s' % population_rounding(self.total_evacuated)],
                'header': True
            })]
        if len(self.impact_category_ordering) > 1:
            impact_summary_report.append(self.blank_line)
            impact_summary_report.append({
                'content': [
                    tr('Total affected population'),
                    format_int(population_rounding(
                        self.total_affected_population))],
                'header': True
            })
            for category in self.impact_category_ordering:
                population_in_category = self.lookup_category(category)
                population_in_category = format_int(population_rounding(
                    population_in_category
                ))
                impact_summary_report.append(
                    {'content': [tr(category), population_in_category]})
        impact_summary_report.append(self.blank_line)
        impact_summary_report.append({
            'content': [
                tr('Unaffected population'),
                format_int(population_rounding(self.unaffected_population))],
            'header': True
        })
        return impact_summary_report

    def minimum_needs_breakdown(self):
        """Breakdown by building type.

        :returns: The buildings breakdown report.
        :rtype: list
        """
        minimum_needs_breakdown_report = [{
            'content': tr('Evacuated population minimum needs'),
            'header': True
        }]
        total_needs = self.total_needs
        for frequency, needs in total_needs.items():
            minimum_needs_breakdown_report.append(
                {
                    'content': [
                        tr('Needs that should be provided %s' % frequency),
                        tr('Total')],
                    'header': True
                })
            for resource in needs:
                minimum_needs_breakdown_report.append(
                    {
                        'content': [
                            tr(resource['table name']),
                            tr(format_int(resource['amount']))]
                    })
        return minimum_needs_breakdown_report

    @property
    def impact_category_ordering(self):
        if not hasattr(self, '_impact_category_ordering'):
            self._impact_category_ordering = self.affected_population.keys()
        return self._impact_category_ordering

    @impact_category_ordering.setter
    def impact_category_ordering(self, impact_category_ordering):
        self._impact_category_ordering = impact_category_ordering

    @property
    def other_population_counts(self):
        if not hasattr(self, '_other_population_counts'):
            self._other_population_counts = {}
        return self._other_population_counts

    @other_population_counts.setter
    def other_population_counts(self):
        if not hasattr(self, '_other_population_counts'):
            self._other_population_counts = {}
        return self._other_population_counts

    @property
    def affected_population(self):
        if not hasattr(self, '_affected_population'):
            self._affected_population = {}
        return self._affected_population

    @affected_population.setter
    def affected_population(self, affected_population):
        self._affected_population = affected_population

    @property
    def question(self):
        if not hasattr(self, '_question'):
            self._question = ''
        return self._question

    @question.setter
    def question(self, question):
        self._question = question

    @property
    def unaffected_population(self):
        if not hasattr(self, '_unaffected_population'):
            self._unaffected_population = 0
        return self._unaffected_population

    @unaffected_population.setter
    def unaffected_population(self, unaffected_population):
        self._unaffected_population = unaffected_population

    @property
    def total_affected_population(self):
        return sum(self.affected_population.values())

    def lookup_category(self, category):
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
        total_population_evacuated = self.total_evacuated
        return evacuated_population_needs(
            total_population_evacuated, self.minimum_needs)

    @property
    def total_evacuated(self):
        if hasattr(self, '_evacuation_category') and self._evacuation_category:
            evacuated_population = self.affected_population[
                self._evacuation_category]
        else:
            evacuated_population = self.total_affected_population
        if (
                hasattr(self, '_evacuation_percentage') and
                self._evacuation_percentage):
            evacuated_population = (
                evacuated_population * self._evacuation_percentage)
        return evacuated_population

    @property
    def total_population(self):
        if not hasattr(self, '_total_population'):
            self._total_population = 0
        return self._total_population

    @total_population.setter
    def total_population(self, total_population):
        self._total_population = total_population

    @property
    def minimum_needs(self):
        if not hasattr(self, '_minimum_needs'):
            self._minimum_needs = []
        return self._minimum_needs

    @minimum_needs.setter
    def minimum_needs(self, minimum_needs):
        self._minimum_needs = minimum_needs
