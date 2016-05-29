# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Function Centric Wizard Step: Summary

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '16/03/2016'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from collections import OrderedDict

from safe.common.resource_parameter import ResourceParameter
from safe_extras.parameters.group_parameter import GroupParameter

from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcSummary(WizardStep, FORM_CLASS):
    """Function Centric Wizard Step: Summary"""

    if_params = None

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_params
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_analysis
        return new_step

    def set_widgets(self):
        """Set widgets on the Summary tab"""
        def format_postprocessor(pp):
            """ make nested OrderedDicts more flat"""
            if isinstance(pp, OrderedDict):
                result = []
                for v in pp:
                    if isinstance(pp[v], OrderedDict):
                        # omit the v key and unpack the dict directly
                        result += [u'%s: %s' % (unicode(k), unicode(pp[v][k]))
                                   for k in pp[v]]
                    else:
                        result += [u'%s: %s' % (unicode(v), unicode(pp[v]))]
                return u', '.join(result)
            elif isinstance(pp, list):
                result = []
                for i in pp:
                    name = i.serialize()['name']
                    val = i.serialize()['value']
                    if isinstance(val, bool):
                        val = val and self.tr('Enabled') or self.tr('Disabled')
                    if isinstance(i, GroupParameter):
                        # val is a list od *Parameter instances
                        jresult = []
                        for j in val:
                            jname = j.serialize()['name']
                            jval = j.serialize()['value']
                            if isinstance(jval, bool):
                                jval = (jval and self.tr('Enabled') or
                                        self.tr('Disabled'))
                            else:
                                jval = unicode(jval)
                            jresult += [u'%s: %s' % (jname, jval)]
                        val = u', '.join(jresult)
                    else:
                        val = unicode(val)
                    if pp.index(i) == 0:
                        result += [val]
                    else:
                        result += [u'%s: %s' % (name, val)]
                return u', '.join(result)
            else:
                return unicode(pp)

        parameter_dialog = self.parent.step_fc_params.parameter_dialog
        self.if_params = parameter_dialog.parse_input(parameter_dialog.values)

        # (IS) Set the current impact function to use parameter from user.
        # We should do it prettier (put it on analysis or impact calculator
        impact_function_id = self.parent.step_fc_function.\
            selected_function()['id']
        impact_function = self.impact_function_manager.get(
            impact_function_id)
        if not impact_function:
            return
        impact_function.parameters = self.if_params

        params = []
        for p in self.if_params:
            if isinstance(self.if_params[p], OrderedDict):
                subparams = [
                    u'<tr><td>%s &nbsp;</td><td>%s</td></tr>' % (
                        unicode(pp),
                        format_postprocessor(self.if_params[p][pp]))
                    for pp in self.if_params[p]
                ]
                if subparams:
                    subparams = ''.join(subparams)
                    subparams = '<table border="0">%s</table>' % subparams
            elif isinstance(self.if_params[p], GroupParameter):
                subparams = format_postprocessor([self.if_params[p]])
            elif isinstance(self.if_params[p], list) and p == 'minimum needs':
                subparams = ''
                for need in self.if_params[p]:
                    # concatenate all ResourceParameter
                    name = unicode(need.serialize()['name'])
                    val = unicode(need.serialize()['value'])
                    if isinstance(need, ResourceParameter):
                        if need.unit and need.unit.abbreviation:
                            val += need.unit.abbreviation
                    subparams += u'<tr><td>%s &nbsp;</td><td>%s</td></tr>' % (
                        name, val)
                if subparams:
                    subparams = '<table border="0">%s</table>' % subparams
                else:
                    subparams = 'Not applicable'
            elif isinstance(self.if_params[p], list):
                subparams = ', '.join([unicode(i) for i in self.if_params[p]])
            else:
                subparams = unicode(self.if_params[p].serialize()['value'])

            params += [(p, subparams)]

        if self.parent.aggregation_layer:
            aggr = self.parent.aggregation_layer.name()
        else:
            aggr = self.tr('no aggregation')

        html = self.tr('Please ensure the following information '
                       'is correct and press Run.')

        # TODO: update this to use InaSAFE message API rather...
        html += '<br/><table cellspacing="4">'
        html += ('<tr>'
                 '  <td><b>%s</b></td><td width="10"></td><td>%s</td>'
                 '</tr><tr>'
                 '  <td colspan="3"></td>'
                 '</tr><tr>'
                 '  <td><b>%s</b></td><td></td><td>%s</td>'
                 '</tr><tr>'
                 '  <td><b>%s</b></td><td></td><td>%s</td>'
                 '</tr><tr>'
                 '  <td><b>%s</b></td><td></td><td>%s</td>'
                 '</tr><tr>'
                 '  <td colspan="3"></td>'
                 '</tr>' % (
                     self.tr('impact function').capitalize().replace(
                         ' ', '&nbsp;'),
                     self.parent.step_fc_function.selected_function()['name'],
                     self.tr('hazard layer').capitalize().replace(
                         ' ', '&nbsp;'),
                     self.parent.hazard_layer.name(),
                     self.tr('exposure layer').capitalize().replace(
                         ' ', '&nbsp;'),
                     self.parent.exposure_layer.name(),
                     self.tr('aggregation layer').capitalize().replace(
                         ' ', '&nbsp;'), aggr))

        def humanize(my_string):
            """Humanize string.

            :param my_string: A not human friendly string

            :type my_string: str

            :returns: A human friendly string
            :rtype: str
            """
            my_string = my_string.replace('_', ' ')
            my_string = my_string.capitalize()
            return my_string

        for p in params:
            html += (
                '<tr>'
                '  <td><b>%s</b></td><td></td><td>%s</td>'
                '</tr>' % (humanize(p[0]), p[1]))
        html += '</table>'

        self.lblSummary.setText(html)
