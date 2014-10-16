# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid - **Postprocessor Manager**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '19/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import logging

from PyQt4 import QtCore

from qgis.core import QgsFeatureRequest

from collections import OrderedDict

from safe.common.utilities import unhumanize_number, format_int

from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.safe_interface import (
    safeTr,
    get_postprocessors,
    get_postprocessor_human_name,
    messaging as m,
    PostProcessorError,
    KeywordNotFoundError,
    styles)

LOGGER = logging.getLogger('InaSAFE')
#from pydev import pydevd


class PostprocessorManager(QtCore.QObject):
    """A manager for post processing of impact function results.
    """

    def __init__(self, aggregator):
        """Director for aggregation based operations.

        :param aggregator: Aggregator that will be used in conjunction with
            postprocessors.
        :type aggregator: Aggregator
        """

        super(PostprocessorManager, self).__init__()

        # Aggregation / post processing related items
        self.output = {}
        self.keyword_io = KeywordIO()
        self.error_message = None

        self.aggregator = aggregator
        self.current_output_postprocessor = None
        self.attribute_title = None
        self.function_parameters = None

    def _sum_field_name(self):
        return self.aggregator.sum_field_name()

    def _sort_no_data(self, data):
        """Check if the value field of the postprocessor is NO_DATA.

        This is used for sorting, it returns -1 if the value is NO_DATA, so
        that no data items can be put at the end of a list

        :param data: Value to be checked.
        :type data: list

        :returns: -1 if the value is NO_DATA else the value
        :rtype: int, float
        """

        post_processor = self.output[self.current_output_postprocessor]
        #get the key position of the value field
        key = post_processor[0][1].keys()[0]
        #get the value
        # data[1] is the orderedDict
        # data[1][myFirstKey] is the 1st indicator in the orderedDict
        if (data[1][key]['value'] == self.aggregator.get_default_keyword(
                'NO_DATA')):
            position = -1
        else:
            position = data[1][key]['value']
            position = unhumanize_number(position)

        return position

    def _generate_tables(self, aoi_mode=True):
        """Parses the postprocessing output as one table per postprocessor.

        TODO: This should rather return json and then have a helper method to
        make html from the JSON.

        :param aoi_mode: adds a Total in aggregation areas
        row to the calculated table
        :type aoi_mode: bool

        :returns: The html.
        :rtype: str
        """
        message = m.Message()

        for processor, results_list in self.output.iteritems():

            self.current_output_postprocessor = processor
            # results_list is for example:
            # [
            #    (PyQt4.QtCore.QString(u'Entire area'), OrderedDict([
            #        (u'Total', {'value': 977536, 'metadata': {}}),
            #        (u'Female population', {'value': 508319, 'metadata': {}}),
            #        (u'Weekly hygiene packs', {'value': 403453, 'metadata': {
            #         'description': 'Females hygiene packs for weekly use'}})
            #    ]))
            #]

            #sorting using the first indicator of a postprocessor
            sorted_results = sorted(
                results_list,
                key=self._sort_no_data,
                reverse=True)

            #init table
            has_no_data = False
            table = m.Table(
                style_class='table table-condensed table-striped')
            table.caption = self.tr('Detailed %s report') % (safeTr(
                get_postprocessor_human_name(processor)).lower())

            header = m.Row()
            header.add(str(self.attribute_title).capitalize())
            for calculation_name in sorted_results[0][1]:
                header.add(self.tr(calculation_name))
            table.add(header)

            # used to calculate the totals row as per issue #690
            postprocessor_totals = OrderedDict()

            for zone_name, calc in sorted_results:
                row = m.Row(zone_name)

                for indicator, calculation_data in calc.iteritems():
                    value = calculation_data['value']
                    value = str(unhumanize_number(value))
                    if value == self.aggregator.get_default_keyword('NO_DATA'):
                        has_no_data = True
                        value += ' *'
                        try:
                            postprocessor_totals[indicator] += 0
                        except KeyError:
                            postprocessor_totals[indicator] = 0
                    else:
                        value = int(value)
                        try:
                            postprocessor_totals[indicator] += value
                        except KeyError:
                            postprocessor_totals[indicator] = value
                    row.add(format_int(value))
                table.add(row)

            if not aoi_mode:
                # add the totals row
                row = m.Row(self.tr('Total in aggregation areas'))
                for _, total in postprocessor_totals.iteritems():
                    row.add(format_int(total))
                table.add(row)

            # add table to message
            message.add(table)
            if has_no_data:
                message.add(m.EmphasizedText(self.tr(
                    '* "%s" values mean that there where some problems while '
                    'calculating them. This did not affect the other '
                    'values.') % (
                        self.aggregator.get_default_keyword('NO_DATA'))))

        return message

    def _consolidate_multipart_stats(self):
        """Sums the values of multipart polygons together to display only one.
        """
        LOGGER.debug('Consolidating multipart postprocessing results')

        # copy needed because of
        # self.output[postprocessor].pop(corrected_index)
        output = self.output

        # iterate postprocessors
        for postprocessor, results_list in output.iteritems():
            #see self._generateTables to see details about results_list
            checked_polygon_names = {}
            parts_to_delete = []
            polygon_index = 0
            # iterate polygons
            for polygon_name, results in results_list:
                if polygon_name in checked_polygon_names.keys():
                    for result_name, result in results.iteritems():
                        first_part_index = checked_polygon_names[polygon_name]
                        first_part = self.output[postprocessor][
                            first_part_index]
                        first_part_results = first_part[1]
                        first_part_result = first_part_results[result_name]

                        # FIXME one of the parts was 'No data',
                        # is it matematically correct to do no_data = 0?
                        # see http://irclogs.geoapt.com/inasafe/
                        # %23inasafe.2013-08-09.log (at 22.29)

                        no_data = \
                            self.aggregator.get_default_keyword('NO_DATA')
                        # both are No data
                        value = first_part_result['value']
                        result_value = result['value']
                        if value == no_data and result_value == no_data:
                            new_result = no_data
                        else:
                            # one is No data
                            if value == no_data:
                                value = 0
                            # the other is No data
                            elif result_value == no_data:
                                result_value = 0
                            # here none is No data
                            new_result = (
                                unhumanize_number(value) +
                                unhumanize_number(result_value))

                        first_part_result['value'] = format_int(new_result)

                    parts_to_delete.append(polygon_index)

                else:
                    # add polygon to checked list
                    checked_polygon_names[polygon_name] = polygon_index

                polygon_index += 1

            # http://stackoverflow.com/questions/497426/
            # deleting-multiple-elements-from-a-list
            results_list = [res for j, res in enumerate(results_list)
                            if j not in parts_to_delete]
            self.output[postprocessor] = results_list

    def run(self):
        """Run any post processors requested by the impact function.
        """
        try:
            requested_postprocessors = self.function_parameters[
                'postprocessors']
            postprocessors = get_postprocessors(
                requested_postprocessors, self.aggregator.aoi_mode)
        except (TypeError, KeyError):
            # TypeError is for when function_parameters is none
            # KeyError is for when ['postprocessors'] is unavailable
            postprocessors = {}
        LOGGER.debug('Running this postprocessors: ' + str(postprocessors))

        feature_names_attribute = self.aggregator.attributes[
            self.aggregator.get_default_keyword('AGGR_ATTR_KEY')]
        if feature_names_attribute is None:
            self.attribute_title = self.tr('Aggregation unit')
        else:
            self.attribute_title = feature_names_attribute

        name_filed_index = self.aggregator.layer.fieldNameIndex(
            self.attribute_title)
        sum_field_index = self.aggregator.layer.fieldNameIndex(
            self._sum_field_name())

        user_defined_female_ratio = False
        female_ratio_field_index = None
        female_ratio = None
        user_defined_age_ratios = False
        youth_ratio_field_index = None
        youth_ratio = None
        adult_ratio_field_index = None
        adult_ratio = None
        elderly_ratio_field_index = None
        elderly_ratio = None

        if 'Gender' in postprocessors:
            # look if we need to look for a variable female ratio in a layer
            try:
                female_ratio_field = self.aggregator.attributes[
                    self.aggregator.get_default_keyword(
                        'FEMALE_RATIO_ATTR_KEY')]
                female_ratio_field_index = \
                    self.aggregator.layer.fieldNameIndex(female_ratio_field)

                # something went wrong finding the female ratio field,
                # use defaults from below except block
                if female_ratio_field_index == -1:
                    raise KeyError

                user_defined_female_ratio = True

            except KeyError:
                try:
                    female_ratio = self.keyword_io.read_keywords(
                        self.aggregator.layer,
                        self.aggregator.get_default_keyword(
                            'FEMALE_RATIO_KEY'))
                except KeywordNotFoundError:
                    female_ratio = \
                        self.aggregator.get_default_keyword('FEMALE_RATIO')

        if 'Age' in postprocessors:
            # look if we need to look for a variable age ratio in a layer
            try:
                youth_ratio_field = self.aggregator.attributes[
                    self.aggregator.get_default_keyword(
                        'YOUTH_RATIO_ATTR_KEY')]
                youth_ratio_field_index = \
                    self.aggregator.layer.fieldNameIndex(youth_ratio_field)
                adult_ratio_field = self.aggregator.attributes[
                    self.aggregator.get_default_keyword(
                        'ADULT_RATIO_ATTR_KEY')]
                adult_ratio_field_index = \
                    self.aggregator.layer.fieldNameIndex(adult_ratio_field)
                elderly_ratio_field = self.aggregator.attributes[
                    self.aggregator.get_default_keyword(
                        'ELDERLY_RATIO_ATTR_KEY')]
                elderly_ratio_field_index = \
                    self.aggregator.layer.fieldNameIndex(elderly_ratio_field)
                # something went wrong finding the youth ratio field,
                # use defaults from below except block
                if (youth_ratio_field_index == -1 or
                            adult_ratio_field_index == -1 or
                            elderly_ratio_field_index == -1):
                    raise KeyError

                user_defined_age_ratios = True

            except KeyError:
                try:
                    youth_ratio = self.keyword_io.read_keywords(
                        self.aggregator.layer,
                        self.aggregator.get_default_keyword(
                            'YOUTH_RATIO_KEY'))
                    adult_ratio = self.keyword_io.read_keywords(
                        self.aggregator.layer,
                        self.aggregator.get_default_keyword(
                            'ADULT_RATIO_KEY'))
                    elderly_ratio = self.keyword_io.read_keywords(
                        self.aggregator.layer,
                        self.aggregator.get_default_keyword(
                            'ELDERLY_RATIO_KEY'))

                except KeywordNotFoundError:
                    youth_ratio = \
                        self.aggregator.get_default_keyword('YOUTH_RATIO')
                    adult_ratio = \
                        self.aggregator.get_default_keyword('ADULT_RATIO')
                    elderly_ratio = \
                        self.aggregator.get_default_keyword('ELDERLY_RATIO')

        if 'BuildingType' or 'RoadType' in postprocessors:
            try:
                key_attribute = self.keyword_io.read_keywords(
                    self.aggregator.exposure_layer, 'key_attribute')
            except KeywordNotFoundError:
                #use 'type' as default
                key_attribute = 'type'

        # iterate zone features
        request = QgsFeatureRequest()
        request.setFlags(QgsFeatureRequest.NoGeometry)
        provider = self.aggregator.layer.dataProvider()
        # start data retrieval: fetch no geometry and all attributes for each
        # feature
        polygon_index = 0
        for feature in provider.getFeatures(request):
            # if a feature has no field called
            if name_filed_index == -1:
                zone_name = str(feature.id())
            else:
                zone_name = feature[name_filed_index]

            # create dictionary of attributes to pass to postprocessor
            general_params = {
                'target_field': self.aggregator.target_field,
                'function_params': self.function_parameters}

            if self.aggregator.statistics_type == 'class_count':
                general_params['impact_classes'] = (
                    self.aggregator.statistics_classes)
            elif self.aggregator.statistics_type == 'sum':
                impact_total = feature[sum_field_index]
                general_params['impact_total'] = impact_total

            try:
                general_params['impact_attrs'] = (
                    self.aggregator.impact_layer_attributes[polygon_index])
            except IndexError:
                # rasters and attributeless vectors have no attributes
                general_params['impact_attrs'] = None

            for key, value in postprocessors.iteritems():
                parameters = general_params
                try:
                    # look if params are available for this postprocessor
                    parameters.update(
                        self.function_parameters[
                            'postprocessors'][key]['params'])
                except KeyError:
                    pass

                if key == 'Gender':
                    if user_defined_female_ratio:
                        female_ratio = feature[female_ratio_field_index]
                        if female_ratio is None:
                            female_ratio = self.aggregator.defaults[
                                'FEMALE_RATIO']
                            LOGGER.warning('Data Driven Female ratio '
                                           'incomplete, using defaults for'
                                           ' aggregation unit'
                                           ' %s' % feature.id)

                    parameters['female_ratio'] = female_ratio

                if key == 'Age':
                    if user_defined_age_ratios:
                        youth_ratio = feature[youth_ratio_field_index]
                        adult_ratio = feature[adult_ratio_field_index]
                        elderly_ratio = feature[elderly_ratio_field_index]
                        if (youth_ratio is None or
                                    adult_ratio is None or
                                    elderly_ratio is None):
                            youth_ratio = self.aggregator.defaults[
                                'YOUTH_RATIO']
                            adult_ratio = self.aggregator.defaults[
                                'ADULT_RATIO']
                            elderly_ratio = self.aggregator.defaults[
                                'ELDERLY_RATIO']
                            LOGGER.warning('Data Driven Age ratios '
                                           'incomplete, using defaults for'
                                           ' aggregation unit'
                                           ' %s' % feature.id)

                    parameters['youth_ratio'] = youth_ratio
                    parameters['adult_ratio'] = adult_ratio
                    parameters['elderly_ratio'] = elderly_ratio

                if key == 'BuildingType' or key == 'RoadType':
                    parameters['key_attribute'] = key_attribute

                try:
                    value.setup(parameters)
                    value.process()
                    results = value.results()
                    value.clear()
    #                LOGGER.debug(results)

                    #this can raise a KeyError
                    self.output[key].append(
                        (zone_name, results))

                except PostProcessorError as e:
                    message = m.Message(
                        m.Heading(self.tr('%s postprocessor problem' % key),
                                  **styles.DETAILS_STYLE),
                        m.Paragraph(self.tr(str(e))))
                    self.error_message = message

                except KeyError:
                    self.output[key] = []
                    self.output[key].append(
                        (zone_name, results))
            # increment the index
            polygon_index += 1

    def get_output(self, aoi_mode):
        """Returns the results of the post processing as a table.

        :param aoi_mode: aoi mode of the aggregator.
        :type aoi_mode: bool

        :returns: str - a string containing the html in the requested format.
        """

        message = m.Message()
        if self.error_message is not None:
            message.add(
                m.Heading(
                    self.tr('Postprocessing report partially skipped'),
                    **styles.WARNING_STYLE))
            message.add(
                m.Paragraph(self.tr(
                    'Due to a problem while processing the results, part of '
                    'the detailed postprocessing report is unavailable:')))
            message.add(self.error_message)

        try:
            if (self.keyword_io.read_keywords(
                    self.aggregator.layer, 'had multipart polygon')):
                self._consolidate_multipart_stats()
        except KeywordNotFoundError:
            pass

        message.add(self._generate_tables(aoi_mode))
        return message
