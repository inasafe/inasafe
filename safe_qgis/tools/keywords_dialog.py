# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid **GUI Keywords Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import logging
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature

from third_party.odict import OrderedDict

from safe_qgis.safe_interface import InaSAFEError, get_version
from safe_qgis.ui.keywords_dialog_base import Ui_KeywordsDialogBase
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.help import show_context_help
from safe_qgis.utilities.utilities import (
    get_error_message,
    is_polygon_layer,
    layer_attribute_names,
    breakdown_defaults)

from safe_qgis.exceptions import (
    InvalidParameterError, HashNotFoundError, NoKeywordsFoundError)

LOGGER = logging.getLogger('InaSAFE')


class KeywordsDialog(QtGui.QDialog, Ui_KeywordsDialogBase):
    """Dialog implementation class for the InaSAFE keywords editor."""

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
        self.setWindowTitle(self.tr(
            'InaSAFE %s Keywords Editor') % (get_version()))
        self.keywordIO = KeywordIO()
        # note the keys should remain untranslated as we need to write
        # english to the keywords file. The keys will be written as user data
        # in the combo entries.
        # .. seealso:: http://www.voidspace.org.uk/python/odict.html
        self.standardExposureList = OrderedDict(
            [('population', self.tr('population')),
             ('structure', self.tr('structure')),
             ('Not Set', self.tr('Not Set'))])
        self.standardHazardList = OrderedDict(
            [('earthquake [MMI]', self.tr('earthquake [MMI]')),
             ('tsunami [m]', self.tr('tsunami [m]')),
             ('tsunami [wet/dry]', self.tr('tsunami [wet/dry]')),
             ('tsunami [feet]', self.tr('tsunami [feet]')),
             ('flood [m]', self.tr('flood [m]')),
             ('flood [wet/dry]', self.tr('flood [wet/dry]')),
             ('flood [feet]', self.tr('flood [feet]')),
             ('tephra [kg2/m2]', self.tr('tephra [kg2/m2]')),
             ('volcano', self.tr('volcano')),
             ('Not Set', self.tr('Not Set'))])
        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        self.dock = dock

        self.lstKeywords.itemClicked.connect(self.edit_key_value_pair)

        # Set up help dialog showing logic.
        self.helpDialog = None
        helpButton = self.buttonBox.button(QtGui.QDialogButtonBox.Help)
        helpButton.clicked.connect(self.show_help)

        # set some inital ui state:
        self.defaults = breakdown_defaults()
        self.pbnAdvanced.setChecked(True)
        self.pbnAdvanced.toggle()
        self.radPredefined.setChecked(True)
        self.dsbFemaleRatioDefault.blockSignals(True)
        self.dsbFemaleRatioDefault.setValue(self.defaults[
            'FEM_RATIO'])
        self.dsbFemaleRatioDefault.blockSignals(False)
        #myButton = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        #myButton.setEnabled(False)
        if layer is None:
            self.layer = self.iface.activeLayer()
        else:
            self.layer = layer
        if self.layer:
            self.load_state_from_keywords()

        # add a reload from keywords button
        reloadButton = self.buttonBox.addButton(
            self.tr('Reload'), QtGui.QDialogButtonBox.ActionRole)
        reloadButton.clicked.connect(self.load_state_from_keywords)

    def set_layer(self, layer):
        """Set the layer associated with the keyword editor.

        :param layer: Layer whose keywords should be edited.
        :type layer: QgsMapLayer
        """
        self.layer = layer
        self.load_state_from_keywords()

    def show_help(self):
        """Load the help text for the keywords dialog."""
        show_context_help(context='keywords')

    def toggle_postprocessing_widgets(self):
        """Hide or show the post processing widgets depending on context.
        """
        LOGGER.debug('togglePostprocessingWidgets')
        isPostprocessingOn = self.radPostprocessing.isChecked()
        self.cboSubcategory.setVisible(not isPostprocessingOn)
        self.lblSubcategory.setVisible(not isPostprocessingOn)
        self.show_aggregation_attribute(isPostprocessingOn)
        self.show_female_ratio_attribute(isPostprocessingOn)
        self.show_female_ratio_default(isPostprocessingOn)

    def show_aggregation_attribute(self, visible_flag):
        """Hide or show the aggregation attribute in the keyword editor dialog.

        :param visible_flag: Flag indicating if the aggregation attribute
            should be hidden or shown.
        :type visible_flag: bool
        """
        theBox = self.cboAggregationAttribute
        theBox.blockSignals(True)
        theBox.clear()
        theBox.blockSignals(False)
        if visible_flag:
            currentKeyword = self.get_value_for_key(
                self.defaults['AGGR_ATTR_KEY'])
            fields, attributePosition = layer_attribute_names(
                self.layer,
                [QtCore.QVariant.Int, QtCore.QVariant.String],
                currentKeyword)
            theBox.addItems(fields)
            if attributePosition is None:
                theBox.setCurrentIndex(0)
            else:
                theBox.setCurrentIndex(attributePosition)

        theBox.setVisible(visible_flag)
        self.lblAggregationAttribute.setVisible(visible_flag)

    def show_female_ratio_attribute(self, visible_flag):
        """Hide or show the female ratio attribute in the dialog.

        :param visible_flag: Flag indicating if the female ratio attribute
            should be hidden or shown.
        :type visible_flag: bool
        """
        theBox = self.cboFemaleRatioAttribute
        theBox.blockSignals(True)
        theBox.clear()
        theBox.blockSignals(False)
        if visible_flag:
            currentKeyword = self.get_value_for_key(
                self.defaults['FEM_RATIO_ATTR_KEY'])
            fields, attributePosition = layer_attribute_names(
                self.layer,
                [QtCore.QVariant.Double],
                currentKeyword)
            fields.insert(0, self.tr('Use default'))
            fields.insert(1, self.tr('Don\'t use'))
            theBox.addItems(fields)
            if currentKeyword == self.tr('Use default'):
                theBox.setCurrentIndex(0)
            elif currentKeyword == self.tr('Don\'t use'):
                theBox.setCurrentIndex(1)
            elif attributePosition is None:
                # currentKeyword was not found in the attribute table.
                # Use default
                theBox.setCurrentIndex(0)
            else:
                # + 2 is because we add use defaults and don't use
                theBox.setCurrentIndex(attributePosition + 2)
        theBox.setVisible(visible_flag)
        self.lblFemaleRatioAttribute.setVisible(visible_flag)

    def show_female_ratio_default(self, visible_flag):
        """Hide or show the female ratio default attribute in the dialog.

        :param visible_flag: Flag indicating if the female ratio
            default attribute should be hidden or shown.
        :type visible_flag: bool
        """
        theBox = self.dsbFemaleRatioDefault
        if visible_flag:
            currentValue = self.get_value_for_key(
                self.defaults['FEM_RATIO_KEY'])
            if currentValue is None:
                val = self.defaults['FEM_RATIO']
            else:
                val = float(currentValue)
            theBox.setValue(val)

        theBox.setVisible(visible_flag)
        self.lblFemaleRatioDefault.setVisible(visible_flag)

    # prevents actions being handled twice
    @pyqtSignature('int')
    def on_cboAggregationAttribute_currentIndexChanged(self, index=None):
        """Handler for aggregation attribute combo change.

        :param index: Not used but required for slot.
        """
        del index
        self.add_list_entry(
            self.defaults['AGGR_ATTR_KEY'],
            self.cboAggregationAttribute.currentText())

    # prevents actions being handled twice
    @pyqtSignature('int')
    def on_cboFemaleRatioAttribute_currentIndexChanged(self, index=None):
        """Handler for female ratio attribute change.

        :param index: Not used but required for slot.
        """
        del index
        text = self.cboFemaleRatioAttribute.currentText()
        if text == self.tr('Use default'):
            self.dsbFemaleRatioDefault.setEnabled(True)
            currentDefault = self.get_value_for_key(
                self.defaults['FEM_RATIO_KEY'])
            if currentDefault is None:
                self.add_list_entry(
                    self.defaults['FEM_RATIO_KEY'],
                    self.dsbFemaleRatioDefault.value())
        else:
            self.dsbFemaleRatioDefault.setEnabled(False)
            self.remove_item_by_key(self.defaults['FEM_RATIO_KEY'])
        self.add_list_entry(self.defaults['FEM_RATIO_ATTR_KEY'], text)

    # prevents actions being handled twice
    @pyqtSignature('double')
    def on_dsbFemaleRatioDefault_valueChanged(self, value):
        """Handler for female ration default value changing.

        :param value: Not used but required for slot.
        """
        del value
        box = self.dsbFemaleRatioDefault
        if box.isEnabled():
            self.add_list_entry(
                self.defaults['FEM_RATIO_KEY'],
                box.value())

    # prevents actions being handled twice
    @pyqtSignature('bool')
    def on_pbnAdvanced_toggled(self, flag):
        """Automatic slot executed when the advanced button is toggled.

        .. note:: some of the behaviour for hiding widgets is done using
           the signal/slot editor in designer, so if you are trying to figure
           out how the interactions work, look there too!

        :param flag: Flag indicating the new checked state of the button.
        :type flag: bool
        """
        self.toggle_advanced(flag)

    def toggle_advanced(self, flag):
        """Hide or show advanced editor.

        :param flag: Desired state for advanced editor visibility.
        :type flag: bool
        """
        if flag:
            self.pbnAdvanced.setText(self.tr('Hide advanced editor'))
        else:
            self.pbnAdvanced.setText(self.tr('Show advanced editor'))
        self.grpAdvanced.setVisible(flag)
        self.resize_dialog()

    # prevents actions being handled twice
    @pyqtSignature('bool')
    def on_radHazard_toggled(self, flag):
        """Automatic slot executed when the hazard radio is toggled.

        :param flag: Flag indicating the new checked state of the button.
        :type flag: bool
        """
        if not flag:
            return
        self.set_category('hazard')
        self.update_controls_from_list()

    # prevents actions being handled twice
    @pyqtSignature('bool')
    def on_radExposure_toggled(self, theFlag):
        """Automatic slot executed when the hazard radio is toggled on.

        :param theFlag: Flag indicating the new checked state of the button.
        :type theFlag: bool
        """
        if not theFlag:
            return
        self.set_category('exposure')
        self.update_controls_from_list()

    # prevents actions being handled twice
    @pyqtSignature('bool')
    def on_radPostprocessing_toggled(self, flag):
        """Automatic slot executed when the hazard radio is toggled on.

        :param flag: Flag indicating the new checked state of the button.
        :type flag: bool
        """
        if not flag:
            self.remove_item_by_key(self.defaults['AGGR_ATTR_KEY'])
            self.remove_item_by_key(self.defaults['FEM_RATIO_ATTR_KEY'])
            self.remove_item_by_key(self.defaults['FEM_RATIO_KEY'])
            return
        self.set_category('postprocessing')
        self.update_controls_from_list()

    # prevents actions being handled twice
    @pyqtSignature('int')
    def on_cboSubcategory_currentIndexChanged(self, index=None):
        """Automatic slot executed when the subcategory is changed.

        When the user changes the subcategory, we will extract the
        subcategory and dataype or unit (depending on if it is a hazard
        or exposure subcategory) from the [] after the name.

        :param index: Not used but required for Qt slot.
        """
        del index
        myItem = self.cboSubcategory.itemData(
            self.cboSubcategory.currentIndex())
        myText = str(myItem)
        # I found that myText is 'Not Set' for every language
        if myText == self.tr('Not Set') or myText == 'Not Set':
            self.remove_item_by_key('subcategory')
            return
        myTokens = myText.split(' ')
        if len(myTokens) < 1:
            self.remove_item_by_key('subcategory')
            return
        mySubcategory = myTokens[0]
        self.add_list_entry('subcategory', mySubcategory)

        # Some subcategories e.g. roads have no units or datatype
        if len(myTokens) == 1:
            return
        if myTokens[1].find('[') < 0:
            return
        myCategory = self.get_value_for_key('category')
        if 'hazard' == myCategory:
            myUnits = myTokens[1].replace('[', '').replace(']', '')
            self.add_list_entry('unit', myUnits)
        if 'exposure' == myCategory:
            myDataType = myTokens[1].replace('[', '').replace(']', '')
            self.add_list_entry('datatype', myDataType)
            # prevents actions being handled twice

    def set_subcategory_list(self, entries, selected_item=None):
        """Helper to populate the subcategory list based on category context.

        :param entries: An OrderedDict of subcategories. The dict entries
             should be in the form ('earthquake', self.tr('earthquake')). See
             http://www.voidspace.org.uk/python/odict.html for info on
             OrderedDict.
        :type entries: OrderedDict

        :param selected_item: Which item should be selected in the combo. If
            the selected item is not in entries, it will be appended to it.
            This is optional.
        :type selected_item: str
        """
        # To avoid triggering on_cboSubcategory_currentIndexChanged
        # we block signals from the combo while updating it
        self.cboSubcategory.blockSignals(True)
        self.cboSubcategory.clear()
        theSelectedItemNone = selected_item is not None
        theSelectedItemInValues = selected_item not in entries.values()
        theSelectedItemInKeys = selected_item not in entries.keys()
        if (theSelectedItemNone and theSelectedItemInValues and
                theSelectedItemInKeys):
            # Add it to the OrderedList
            entries[selected_item] = selected_item
        myIndex = 0
        mySelectedIndex = 0
        for myKey, myValue in entries.iteritems():
            if myValue == selected_item or myKey == selected_item:
                mySelectedIndex = myIndex
            myIndex += 1
            self.cboSubcategory.addItem(myValue, myKey)
        self.cboSubcategory.setCurrentIndex(mySelectedIndex)
        self.cboSubcategory.blockSignals(False)

    # prevents actions being handled twice
    @pyqtSignature('')
    def on_pbnAddToList1_clicked(self):
        """Automatic slot executed when the pbnAddToList1 button is pressed.
        """
        if (self.lePredefinedValue.text() != "" and
                self.cboKeyword.currentText() != ""):
            myCurrentKey = self.tr(self.cboKeyword.currentText())
            myCurrentValue = self.lePredefinedValue.text()
            self.add_list_entry(myCurrentKey, myCurrentValue)
            self.lePredefinedValue.setText('')
            self.update_controls_from_list()

    # prevents actions being handled twice
    @pyqtSignature('')
    def on_pbnAddToList2_clicked(self):
        """Automatic slot executed when the pbnAddToList2 button is pressed.
        """

        myCurrentKey = self.leKey.text()
        myCurrentValue = self.leValue.text()
        if myCurrentKey == 'category' and myCurrentValue == 'hazard':
            self.radHazard.blockSignals(True)
            self.radHazard.setChecked(True)
            self.set_subcategory_list(self.standardHazardList)
            self.radHazard.blockSignals(False)
        elif myCurrentKey == 'category' and myCurrentValue == 'exposure':
            self.radExposure.blockSignals(True)
            self.radExposure.setChecked(True)
            self.set_subcategory_list(self.standardExposureList)
            self.radExposure.blockSignals(False)
        elif myCurrentKey == 'category':
            #.. todo:: notify the user their category is invalid
            pass
        self.add_list_entry(myCurrentKey, myCurrentValue)
        self.leKey.setText('')
        self.leValue.setText('')
        self.update_controls_from_list()

    # prevents actions being handled twice
    @pyqtSignature('')
    def on_pbnRemove_clicked(self):
        """Automatic slot executed when the pbnRemove button is pressed.

        Any selected items in the keywords list will be removed.
        """
        for myItem in self.lstKeywords.selectedItems():
            self.lstKeywords.takeItem(self.lstKeywords.row(myItem))
        self.leKey.setText('')
        self.leValue.setText('')
        self.update_controls_from_list()

    def add_list_entry(self, key, value):
        """Add an item to the keywords list given its key/value.

        The key and value must both be valid, non empty strings
        or an InvalidKVPError will be raised.

        If an entry with the same key exists, it's value will be
        replaced with value.

        It will add the current key/value pair to the list if it is not
        already present. The kvp will also be stored in the data of the
        listwidgetitem as a simple string delimited with a bar ('|').

        :param key: The key part of the key value pair (kvp).
        :type key: str

        :param value: Value part of the key value pair (kvp).
        :type value: str
        """
        if key is None or key == '':
            return
        if value is None or value == '':
            return

        # make sure that both key and value is string
        key = str(key)
        value = str(value)
        myMessage = ''
        if ':' in key:
            key = key.replace(':', '.')
            myMessage = self.tr('Colons are not allowed, replaced with "."')
        if ':' in value:
            value = value.replace(':', '.')
            myMessage = self.tr('Colons are not allowed, replaced with "."')
        if myMessage == '':
            self.lblMessage.setText('')
            self.lblMessage.hide()
        else:
            self.lblMessage.setText(myMessage)
            self.lblMessage.show()
        myItem = QtGui.QListWidgetItem(key + ':' + value)
        # We are going to replace, so remove it if it exists already
        self.remove_item_by_key(key)
        myData = key + '|' + value
        myItem.setData(QtCore.Qt.UserRole, myData)
        self.lstKeywords.insertItem(0, myItem)

    def set_category(self, category):
        """Set the category radio button based on category.

        :param category: Either 'hazard', 'exposure' or 'postprocessing'.
        :type category: str

        :returns: False if radio button could not be updated, otherwise True.
        :rtype: bool
        """
        # convert from QString if needed
        myCategory = str(category)
        if self.get_value_for_key('category') == myCategory:
            #nothing to do, go home
            return True
        if myCategory not in ['hazard', 'exposure', 'postprocessing']:
            # .. todo:: report an error to the user
            return False
            # Special case when category changes, we start on a new slate!

        if myCategory == 'hazard':
            # only cause a toggle if we actually changed the category
            # This will only really be apparent if user manually enters
            # category as a keyword
            self.reset()
            self.radHazard.blockSignals(True)
            self.radHazard.setChecked(True)
            self.radHazard.blockSignals(False)
            self.remove_item_by_key('subcategory')
            self.remove_item_by_key('datatype')
            self.add_list_entry('category', 'hazard')
            myList = self.standardHazardList
            self.set_subcategory_list(myList)

        elif myCategory == 'exposure':
            self.reset()
            self.radExposure.blockSignals(True)
            self.radExposure.setChecked(True)
            self.radExposure.blockSignals(False)
            self.remove_item_by_key('subcategory')
            self.remove_item_by_key('unit')
            self.add_list_entry('category', 'exposure')
            myList = self.standardExposureList
            self.set_subcategory_list(myList)

        else:
            self.reset()
            self.radPostprocessing.blockSignals(True)
            self.radPostprocessing.setChecked(True)
            self.radPostprocessing.blockSignals(False)
            self.remove_item_by_key('subcategory')
            self.add_list_entry('category', 'postprocessing')

        return True

    def reset(self, primary_keywords_only=True):
        """Reset all controls to a blank state.

        :param primary_keywords_only: If True (the default), only reset
            Subcategory, datatype and units.
        :type primary_keywords_only: bool
        """

        self.cboSubcategory.clear()
        self.remove_item_by_key('subcategory')
        self.remove_item_by_key('datatype')
        self.remove_item_by_key('unit')
        self.remove_item_by_key('source')
        if not primary_keywords_only:
            # Clear everything else too
            self.lstKeywords.clear()
            self.leKey.clear()
            self.leValue.clear()
            self.lePredefinedValue.clear()
            self.leTitle.clear()

    def remove_item_by_key(self, key):
        """Remove an item from the kvp list given its key.

        :param key: Key of item to be removed.
        :type key: str
        """
        for myCounter in range(self.lstKeywords.count()):
            myExistingItem = self.lstKeywords.item(myCounter)
            myText = myExistingItem.text()
            myTokens = myText.split(':')
            if len(myTokens) < 2:
                break
            myKey = myTokens[0]
            if myKey == key:
                # remove it since the key is already present
                self.lstKeywords.takeItem(myCounter)
                break

    def remove_item_by_value(self, value):
        """Remove an item from the kvp list given its key.

        :param value: Value of item to be removed.
        :type value: str
        """
        for myCounter in range(self.lstKeywords.count()):
            myExistingItem = self.lstKeywords.item(myCounter)
            myText = myExistingItem.text()
            myTokens = myText.split(':')
            myValue = myTokens[1]
            if myValue == value:
                # remove it since the key is already present
                self.lstKeywords.takeItem(myCounter)
                break

    def get_value_for_key(self, key):
        """If key list contains a specific key, return its value.

        :param key: The key to search for
        :type key: str

        :returns: Value of key if matched otherwise none.
        :rtype: str
        """
        for myCounter in range(self.lstKeywords.count()):
            myExistingItem = self.lstKeywords.item(myCounter)
            myText = myExistingItem.text()
            myTokens = myText.split(':')
            myKey = str(myTokens[0]).strip()
            myValue = str(myTokens[1]).strip()
            if myKey == key:
                return myValue
        return None

    def load_state_from_keywords(self):
        """Set the ui state to match the keywords of the active layer.

        In case the layer has no keywords or any problem occurs reading them,
        start with a blank slate so that subcategory gets populated nicely &
        we will assume exposure to start with.
        """
        myKeywords = {'category': 'exposure'}

        try:
            # Now read the layer with sub layer if needed
            myKeywords = self.keywordIO.read_keywords(self.layer)
        except (InvalidParameterError,
                HashNotFoundError,
                NoKeywordsFoundError):
            pass

        myLayerName = self.layer.name()
        if 'title' not in myKeywords:
            self.leTitle.setText(myLayerName)
        self.lblLayerName.setText(self.tr('Keywords for %s' % myLayerName))
        # if we have a category key, unpack it first
        # so radio button etc get set
        if 'category' in myKeywords:
            self.set_category(myKeywords['category'])
            myKeywords.pop('category')

        for myKey in myKeywords.iterkeys():
            self.add_list_entry(myKey, str(myKeywords[myKey]))

        # now make the rest of the safe_qgis reflect the list entries
        self.update_controls_from_list()

    def update_controls_from_list(self):
        """Set the ui state to match the keywords of the active layer."""
        mySubcategory = self.get_value_for_key('subcategory')
        myUnits = self.get_value_for_key('unit')
        myType = self.get_value_for_key('datatype')
        myTitle = self.get_value_for_key('title')
        if myTitle is not None:
            self.leTitle.setText(myTitle)
        elif self.layer is not None:
            myLayerName = self.layer.name()
            self.lblLayerName.setText(self.tr('Keywords for %s' % myLayerName))
        else:
            self.lblLayerName.setText('')

        if not is_polygon_layer(self.layer):
            self.radPostprocessing.setEnabled(False)

        # adapt gui if we are in postprocessing category
        self.toggle_postprocessing_widgets()

        if self.radExposure.isChecked():
            if mySubcategory is not None and myType is not None:
                self.set_subcategory_list(
                    self.standardExposureList,
                    mySubcategory + ' [' + myType + ']')
            elif mySubcategory is not None:
                self.set_subcategory_list(
                    self.standardExposureList, mySubcategory)
            else:
                self.set_subcategory_list(
                    self.standardExposureList,
                    self.tr('Not Set'))
        elif self.radHazard.isChecked():
            if mySubcategory is not None and myUnits is not None:
                self.set_subcategory_list(
                    self.standardHazardList,
                    mySubcategory + ' [' + myUnits + ']')
            elif mySubcategory is not None:
                self.set_subcategory_list(
                    self.standardHazardList,
                    mySubcategory)
            else:
                self.set_subcategory_list(
                    self.standardHazardList,
                    self.tr('Not Set'))

        self.resize_dialog()

    def resize_dialog(self):
        """Resize the dialog to fit its contents."""
        # noinspection PyArgumentList
        QtCore.QCoreApplication.processEvents()
        LOGGER.debug('adjust ing dialog size')
        self.adjustSize()

    # prevents actions being handled twice
    @pyqtSignature('QString')
    def on_leTitle_textEdited(self, title):
        """Update the keywords list whenever the user changes the title.

        This slot is not called if the title is changed programmatically.

        :param title: New title keyword for the layer.
        :type title: str
        """
        self.add_list_entry('title', str(title))

    def get_keywords(self):
        """Obtain the state of the dialog as a keywords dict.

        :returns: Keywords reflecting the state of the dialog.
        :rtype: dict
        """
        #make sure title is listed
        if str(self.leTitle.text()) != '':
            self.add_list_entry('title', str(self.leTitle.text()))

        myKeywords = {}
        for myCounter in range(self.lstKeywords.count()):
            myExistingItem = self.lstKeywords.item(myCounter)
            myText = myExistingItem.text()
            myTokens = myText.split(':')
            myKey = str(myTokens[0]).strip()
            myValue = str(myTokens[1]).strip()
            myKeywords[myKey] = myValue
        return myKeywords

    def accept(self):
        """Automatic slot executed when the ok button is pressed.

        It will write out the keywords for the layer that is active.
        """
        self.apply_changes()
        myKeywords = self.get_keywords()
        try:
            self.keywordIO.write_keywords(
                layer=self.layer, keywords=myKeywords)
        except InaSAFEError, e:
            myErrorMessage = get_error_message(e)
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QtGui.QMessageBox.warning(
                self, self.tr('InaSAFE'),
                ((self.tr(
                    'An error was encountered when saving the keywords:\n'
                    '%s' % myErrorMessage.to_html()))))
        if self.dock is not None:
            self.dock.get_layers()
        self.done(QtGui.QDialog.Accepted)

    def apply_changes(self):
        """Apply any pending changes e.g. keywords entered without being added.

        See https://github.com/AIFDR/inasafe/issues/249
        """

        if self.radPredefined.isChecked():
            self.on_pbnAddToList1_clicked()
        else:
            self.on_pbnAddToList2_clicked()

    def edit_key_value_pair(self, item):
        """Set leKey and leValue to the clicked item in the lstKeywords.

        :param item: A Key Value pair expressed as a string where the first
            colon in the string delimits the key from the value.
        :type item: str
        """
        myTempKey = item.text().split(':')[0]
        myTempValue = item.text().split(':')[1]
        if myTempKey == 'category':
            return
        if self.radUserDefined.isChecked():
            self.leKey.setText(myTempKey)
            self.leValue.setText(myTempValue)
        elif self.radPredefined.isChecked():
            idxKey = self.cboKeyword.findText(myTempKey)
            if idxKey > -1:
                self.cboKeyword.setCurrentIndex(idxKey)
                self.lePredefinedValue.setText(myTempValue)
            else:
                self.radUserDefined.setChecked(True)
                self.leKey.setText(myTempKey)
                self.leValue.setText(myTempValue)
