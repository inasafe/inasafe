# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid **GUI InaSAFE Wizard Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import logging
import re
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QListWidgetItem, QPixmap

# from third_party.odict import OrderedDict

from safe_qgis.safe_interface import InaSAFEError
from safe_qgis.ui.wizard_dialog_base import Ui_WizardDialogBase
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.utilities import (
    get_error_message,
    is_raster_layer)


LOGGER = logging.getLogger('InaSAFE')


class WizardDialog(QtGui.QDialog, Ui_WizardDialogBase):
    """Dialog implementation class for the InaSAFE keywords wizard."""

    def __init__(self, parent, iface, dock=None, layer=None):
        """Constructor for the dialog.

        .. note:: In QtDesigner the advanced editor's predefined keywords
           list should be shown in english always, so when adding entries to
           cboKeyword, be sure to choose :safe_qgis:`Properties<<` and untick
           the :safe_qgis:`translatable` property.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget

        :param iface: Quantum GIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param dock: Dock widget instance that we can notify of changes to
            the keywords. Optional.
        :type dock: Dock
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle('InaSAFE')
        # Note the keys should remain untranslated as we need to write
        # english to the keywords file.

        # variables for units of measure
        metres_text = self.tr(
            '<b>metres</b> are a metric unit of measure. There are 100 '
            'centimetres in 1 metre. In this case <b>metres</b> are used to '
            'describe the water depth.')
        feet_text = self.tr(
            '<b>Feet</b> are an imperial unit of measure. There are 12 '
            'inches in 1 foot and 3 feet in 1 yard. '
            'In this case <b>feet</b> are used to describe the water depth.')
        wetdry_text = self.tr(
            'This is a binary description for an area. The area is either '
            '<b>wet</b> (affected by flood water) or <b>dry</b> (not affected '
            'by flood water). This unit does not describe how <b>wet</b> or '
            '<b>dry</b> an area is.')
        mmi_text = self.tr(
            'The <b>Modified Mercalli Intensity (MMI)</b> scale describes '
            'the intensity of ground shaking from a earthquake based on the '
            'effects observed by people at the surface.')
        notset_text = self.tr(
            '<b>Not Set</b> is the default setting for when no units are '
            'selected.')
        kgm2_text = self.tr(
            '<b>Kilograms per square metre</b> describes the weight in '
            'kilograms by area in square metres.')
        count_text = self.tr(
            '<b>Count</b> is the number of features.')
        density_text = self.tr(
            '<b>Density</b> is the number of features within a defined '
            'area. For example <b>population density</b> might be measured '
            'as the number of people per square kilometre.')

        # variables for hazard
        flood_desc = self.tr(
            'A <b>flood</b> describes the inundation of land that is '
            'normally dry by a large amount of water. '
            'For example: A <b>flood</b> can occur after heavy rainfall, '
            'when a river overflows its banks or when a dam breaks. '
            'The effect of a <b>flood</b> is for land that is normally dry '
            'to become wet.')
        tsunami_desc = self.tr(
            'A <b>tsunami</b> describes a large ocean wave or series or '
            'waves usually caused by an under water earthquake or volcano.'
            'A <b>tsunami</b> at sea may go unnoticed but a <b>tsunami</b> '
            'wave that strikes land may cause massive destruction and '
            'flooding.')
        earthquake_desc = self.tr(
            'An <b>earthquake</b> describes the sudden violent shaking of the '
            'ground that occurs as a result of volcanic activity or movement '
            'in the earth\'s crust.')
        tephra_desc = self.tr(
            '<b>Tephra</b> describes the material, such as rock fragments and '
            'ash particles ejected by a volcanic eruption.')
        volcano_desc = self.tr(
            'A <b>volcano</b> describes a mountain which has a vent through '
            'which rock fragments, ash, lava, steam and gases can be ejected '
            'from below the earth\'s surface. The type of material '
            'ejected depends on the type of <b>volcano</b>.')

        # variables for exposure
        population_desc = self.tr(
            'The <b>population</b> describes the people that might be '
            'exposed to a particular hazard.')
        structure_desc = self.tr(
            'A <b>structure</b> can be any relatively permanent man '
            'made feature such as a building (an enclosed structure '
            'with walls and a roof) or a telecommunications facility or a '
            'bridge.')
        road_desc = self.tr(
            'A <b>road</b> is a defined route used by a vehicle or people to '
            'travel between two or more points.')

        self.standard_categories = [{
            'value': 'hazard',
            'name': self.tr('hazard'),
            'description': self.tr(
                'A <b>hazard</b> layer represents '
                'something that will impact on the people or infrastructure '
                'in an area. For example; flood, earthquake, tsunami and  '
                'volcano are all examples of hazards.'),
            'subcategory_question': self.tr(
                'What kind of hazard does this '
                'layer represent? The choice you make here will determine '
                'which impact functions this hazard layer can be used with. '
                'For example, if you choose <b>flood</b> you will be '
                'able to use this hazard layer with impact functions such '
                'as <b>flood impact on population</b>.'),
            'subcategories': [{
                'value': 'flood',
                'name': self.tr('flood'),
                'description': flood_desc,
                'units': [{
                    'value': 'metres',
                    'name': self.tr('metres'),
                    'description': metres_text,
                    'attr_question': self.tr('flood depth in meters')
                }, {
                    'value': 'feet',
                    'name': self.tr('feet'),
                    'description': feet_text,
                    'attr_question': self.tr('flood depth in feet')
                }, {
                    'value': 'wet/dry',
                    'name': self.tr('wet/dry'),
                    'description': wetdry_text,
                    'attr_question': self.tr('flood extent as wet/dry')
                }]
            }, {
                'value': 'tsunami',
                'name': self.tr('tsunami'),
                'description': tsunami_desc,
                'units': [{
                    'value': 'metres',
                    'name': self.tr('metres'),
                    'description': metres_text,
                    'attr_question': self.tr('tsunami depth in meters')
                }, {
                    'value': 'feet',
                    'name': self.tr('feet'),
                    'description': feet_text,
                    'attr_question': self.tr('tsunami depth in feet')
                }, {
                    'value': 'wet/dry',
                    'name': self.tr('wet/dry'),
                    'description': wetdry_text,
                    'attr_question': self.tr('tsunami extent as wet/dry')
                }]
            }, {
                'value': 'earthquake',
                'name': self.tr('earthquake'),
                'description': earthquake_desc,
                'units': [{
                    'value': 'MMI',
                    'name': self.tr('MMI'),
                    'description': mmi_text,
                    'attr_question': self.tr('earthquake intensity in MMI')
                }, {
                    'value': '',
                    'name': self.tr('Not Set'),
                    'description': notset_text,
                    'attr_question': self.tr(
                        'earthquake intensity in unknown units')
                }]
            }, {
                'value': 'tephra',
                'name': self.tr('tephra'),
                'description': tephra_desc,
                'units': [{
                    'value': 'kg/m2',
                    'name': self.tr('kg/m2'),
                    'description': kgm2_text,
                    'attr_question': self.tr(
                        'tephra intensity in kg/m<sup>2</sup>')
                }, {
                    'value': '',
                    'name': self.tr('Not Set'),
                    'description': notset_text,
                    'attr_question': self.tr(
                        'tephra intensity in unknown units')
                }]
            }, {
                'value': 'volcano',
                'name': self.tr('volcano'),
                'description': volcano_desc
            }, {
                'value': '',
                'name': self.tr('Not Set'),
                'description': notset_text
            }]
        }, {
            'value': 'exposure',
            'name': self.tr('exposure'),
            'description': self.tr(
                'An <b>exposure</b> layer represents '
                'people, property or infrastructure that may be affected '
                'in the event of a flood, earthquake, volcano etc.'),
            'subcategory_question': self.tr(
                'What kind of exposure does this '
                'layer represent? The choice you make here will determine '
                'which impact functions this exposure layer can be used with. '
                'For example, if you choose <b>population</b> you will be '
                'able to use this exposure layer with impact functions such '
                'as <b>flood impact on population</b>.'),
            'subcategories': [{
                'value': 'population',
                'name': self.tr('population'),
                'description': population_desc,
                'units': [{
                    'value': 'people',
                    'name': self.tr('people'),
                    'description': count_text,
                    'attr_question': self.tr('the number of people')
                }, {
                    'value': 'people/km2',
                    'name': self.tr('people/km2'),
                    'description': density_text,
                    'attr_question': self.tr(
                        'people density in people/km<sup>2</sup>')
                }]
            }, {
                'value': 'structure',
                'name': self.tr('structure'),
                'description': structure_desc
            }, {
                'value': 'road',
                'name': self.tr('road'),
                'description': road_desc
            }]
        }, {
            'value': 'aggregation',
            'name': self.tr('aggregation'),
            'description': self.tr(
                'An <b>aggregation</b> layer represents '
                'regions you can use to summarise the results by. For '
                'example, we might summarise the affected people after'
                'a flood according to city districts.')
        }]

        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        self.dock = dock

        self.layer = layer or self.iface.mapCanvas().currentLayer()

        # Set widgets on the first tab
        self.lblSelectCategory.setText(self.tr(
            'By following the simple steps in this wizard, you can assign '
            'keywords to your layer: <b>%s</b>. First you need to define '
            'the category of your layer.') % self.layer.name())

        for i in self.standard_categories:
            item = QListWidgetItem(i['name'], self.lstCategories)
            item.setData(QtCore.Qt.UserRole, i['value'])
            self.lstCategories.addItem(item)
        self.lblDescribeCategory.setText('')
        self.lblIconCategory.setText('')

        self.pbnBack.setEnabled(False)
        self.pbnNext.setEnabled(False)

        self.pbnCancel.released.connect(self.reject)

        self.go_to_step(1)

    def selected_category(self):
        """Obtain the category selected by user.

        :returns: Metadata of the selected category
        :rtype: dict or None
        """
        if self.lstCategories.selectedIndexes():
            row = self.lstCategories.selectedIndexes()[0].row()
            return self.standard_categories[row]
        else:
            return None

    def selected_subcategory(self):
        """Obtain the subcategory selected by user.

        :returns: Metadata of the selected subcategory
        :rtype: dict or None
        """
        if self.lstSubcategories.selectedIndexes():
            row = self.lstSubcategories.selectedIndexes()[0].row()
            return self.selected_category()['subcategories'][row]
        else:
            return None

    def selected_unit(self):
        """Obtain the unit selected by user.

        :returns: Metadata of the selected unit
        :rtype: dict or None
        """
        if self.lstUnits.selectedIndexes():
            row = self.lstUnits.selectedIndexes()[0].row()
            return self.selected_subcategory()['units'][row]
        else:
            return None

    # prevents actions being handled twice
    @pyqtSignature('')
    def on_lstCategories_itemSelectionChanged(self):
        """Automatic slot executed when category change. Set description label
           and subcategory widgets according to the selected category
        """
        self.lstFields.clear()

        category = self.selected_category()
        # Exit if no selection
        if not category:
            return

        # Set description label
        self.lblDescribeCategory.setText(category['description'])
        self.lblIconCategory.setPixmap(
            QPixmap(':/plugins/inasafe/keyword-category-%s.svg'
                    % (category['value'] or 'notset')))
        # Set subcategory tab widgets
        self.lstSubcategories.clear()
        self.lstUnits.clear()
        self.lstFields.clear()
        self.lblDescribeSubcategory.setText('')
        self.lblIconSubcategory.setPixmap(QPixmap())
        if 'subcategory_question' in category.keys():
            self.lblSelectSubcategory.setText(category['subcategory_question'])
            for i in category['subcategories']:
                item = QListWidgetItem(i['name'], self.lstSubcategories)
                item.setData(QtCore.Qt.UserRole, i['value'])
                self.lstSubcategories.addItem(item)
        elif category['value'] == 'aggregation' \
                and not is_raster_layer(self.layer):
            # Hardcoded vector-based aggregation!
            self.set_field_tab_widgets()

        # Enable the next button
        self.pbnNext.setEnabled(True)

    def on_lstSubcategories_itemSelectionChanged(self):
        """Automatic slot executed when subcategory change. Set description
          label and unit widgets according to the selected category
        """
        category = self.selected_category()
        subcategory = self.selected_subcategory()

        # Exit if no selection
        if not subcategory:
            return

        # Set description label
        self.lblDescribeSubcategory.setText(subcategory['description'])
        self.lblIconSubcategory.setPixmap(QPixmap(
            ':/plugins/inasafe/keyword-subcategory-%s.svg'
            % (subcategory['value'] or 'notset')))
        # Set unit tab widgets
        self.lblSelectUnit.setText(self.tr(
            'You have selected <b>%s</b> '
            'for this <b>%s</b> layer type. We need to know what units the '
            'data are in. For example in a raster layer, each cell might '
            'represent depth in metres or depth in feet. If the dataset '
            'is a vector layer, each polygon might represent an inundated '
            'area, while ares with no polygon coverage would be assumed '
            'to be dry.') % (subcategory['name'], category['name']))
        self.lblDescribeUnit.setText('')
        self.lstUnits.clear()
        self.lstFields.clear()
        if 'units' in subcategory.keys():
            for i in subcategory['units']:
                item = QListWidgetItem(i['name'], self.lstUnits)
                item.setData(QtCore.Qt.UserRole, i['value'])
                self.lstUnits.addItem(item)

        # Enable the next button
        self.pbnNext.setEnabled(True)

    def on_lstUnits_itemSelectionChanged(self):
        """Automatic slot executed when unit change. Set description label
           and field widgets according to the selected category
        """
        unit = self.selected_unit()
        # Exit if no selection
        if not unit:
            return

        self.lblDescribeUnit.setText(unit['description'])

        # Set field tab widgets
        self.set_field_tab_widgets()

        # Enable the next button
        self.pbnNext.setEnabled(True)

    def on_lstFields_itemSelectionChanged(self):
        """Automatic slot executed when field change.
           Unlocks the Next button.
        """
        # Enable the next button
        self.pbnNext.setEnabled(True)

    def on_leSource_textChanged(self):
        """Automatic slot executed when the source change.
           Unlocks the Next button.
        """
        # Enable the next button
        self.pbnNext.setEnabled(bool(self.leSource.text()))

    def on_leTitle_textChanged(self):
        """Automatic slot executed when the title change.
           Unlocks the Next button.
        """
        # Enable the next button
        self.pbnNext.setEnabled(bool(self.leTitle.text()))

    def set_field_tab_widgets(self):
        """Set widgets on the Field tab (lblSelectField and lstFields)
        """
        if self.selected_category()['value'] == 'aggregation':
            self.lblSelectField.setText(self.tr(
                'You have selected an aggregation layer, and it is a vector '
                'layer. Please select the attribute in this layer that '
                'represents names of the aggregation areas.'))
        else:
            self.lblSelectField.setText(self.tr(
                'You have selected a <b>%s %s</b> layer measured in '
                '<b>%s</b>, and the selected layer is vector layer. Please '
                'select the attribute in this layer that represents %s.')
                % (self.selected_subcategory()['name'],
                   self.selected_category()['name'],
                   self.selected_unit()['name'],
                   self.selected_unit()['attr_question']))
        self.lstFields.clear()
        if self.layer and not is_raster_layer(self.layer):
            for field in self.layer.dataProvider().fields():
                field_name = field.name()
                item = QListWidgetItem(field_name, self.lstFields)
                item.setData(QtCore.Qt.UserRole, field_name)
                if re.match('.{0,2}id$', field_name, re.I):
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)

    def go_to_step(self, step):
        """Set the stacked widget to the given step

        :param step: The step number to be moved to
        :type step: int
        """
        self.stackedWidget.setCurrentIndex(step-1)
        self.lblStep.setText(self.tr('step %d') % step)
        self.pbnBack.setEnabled(step > 1)

    # prevents actions being handled twice
    @pyqtSignature('')
    def on_pbnNext_released(self):
        """Automatic slot executed when the pbnNext button is released."""
        current_step = self.stackedWidget.currentIndex() + 1
        # Determine the new step to be switched
        if current_step == 1:
            category = self.selected_category()
            if 'subcategories' in category.keys() \
                    and category['subcategories']:
                new_step = current_step + 1
            elif category['value'] == 'aggregation' \
                    and not is_raster_layer(self.layer):
                # Hardcoded vector-based aggregation!
                new_step = 4
            else:
                new_step = 5
        elif current_step == 2:
            subcategory = self.selected_subcategory()
            if 'units' in subcategory.keys() and subcategory['units']:
                new_step = current_step + 1
            else:
                new_step = 5
        elif current_step == 3:
            if self.lstFields.count():
                new_step = current_step + 1
            else:
                new_step = 5
        elif current_step in (4, 5):
            new_step = current_step + 1
        elif current_step == self.stackedWidget.count():
            # step 6
            self.accept()
            return
        else:
            raise Exception('Unexpected number of steps')

        # Set Next button label
        if new_step == self.stackedWidget.count():
            self.pbnNext.setText(self.tr('Finish'))
        # Disable the Next button unless new data already entered
        self.pbnNext.setEnabled(self.is_ready_to_next_step(new_step))
        self.go_to_step(new_step)

    # prevents actions being handled twice
    @pyqtSignature('')
    def on_pbnBack_released(self):
        """Automatic slot executed when the pbnBack button is released."""
        current_step = self.stackedWidget.currentIndex() + 1
        # Determine the new step to be switched
        if current_step == 5:
            if self.selected_unit() and self.lstFields.selectedIndexes():
                # Note the fields list may be obsolete if no unit selected
                new_step = 4
            elif self.selected_unit():
                new_step = 3
            elif self.selected_subcategory():
                new_step = 2
            else:
                new_step = 1
        elif current_step == 4 \
                and self.selected_category()['value'] == 'aggregation':
            # Hardcoded vector-based aggregation!
            new_step = 1
        else:
            new_step = current_step - 1

        # Set Next button label
        self.pbnNext.setText(self.tr('Next'))
        self.pbnNext.setEnabled(True)
        self.go_to_step(new_step)

    def is_ready_to_next_step(self, step):
        """Check if widgets are filled an new step can be enabled

        :param step: The present step number
        :type step: int

        :returns: True if new step may be enabled
        :rtype: bool
        """
        if step == 1:
            return bool(self.selected_category())
        if step == 2:
            return bool(self.selected_subcategory())
        if step == 3:
            return bool(self.selected_unit())
        if step == 4:
            return bool(len(self.lstFields.selectedIndexes())
                        or not self.lstFields.count())
        # The 'source' keyword is not required
        # if step == 5: return bool(self.leSource.text())
        if step == 5:
            return True
        if step == 6:
            return bool(self.leTitle.text())

    def get_keywords(self):
        """Obtain the state of the dialog as a keywords dict.

        :returns: Keywords reflecting the state of the dialog.
        :rtype: dict
        """
        my_keywords = {}
        my_keywords['category'] = self.selected_category()['value']
        if self.selected_subcategory() \
                and self.selected_subcategory()['value']:
            my_keywords['subcategory'] = self.selected_subcategory()['value']
        if self.selected_unit() and self.selected_unit()['value']:
            my_keywords['unit'] = self.selected_unit()['value']
        if self.lstFields.currentItem():
            my_keywords['field'] = self.lstFields.currentItem().text()
        if self.leSource.text():
            my_keywords['source'] = self.leSource.text()
        if self.leTitle.text():
            my_keywords['title'] = self.leTitle.text()
        return my_keywords

    def accept(self):
        """Automatic slot executed when the Finish button is pressed.

        It will write out the keywords for the layer that is active.
        This method is based on the KeywordsDialog class.
        """
        self.keyword_io = KeywordIO()
        my_keywords = self.get_keywords()
        try:
            self.keyword_io.write_keywords(
                layer=self.layer, keywords=my_keywords)
        except InaSAFEError, e:
            myErrorMessage = get_error_message(e)
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QtGui.QMessageBox.warning(
                self, self.tr('InaSAFE'),
                ((self.tr(
                    'An error was encountered when saving the keywords:\n'
                    '%s') % myErrorMessage.to_html())))
        if self.dock is not None:
            self.dock.get_layers()
        self.done(QtGui.QDialog.Accepted)
