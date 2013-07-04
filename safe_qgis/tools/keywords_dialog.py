"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**GUI Keywords Dialog.**

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
from safe_qgis.help import Help
from safe_qgis.utilities.utilities import (
    getErrorMessage,
    isPolygonLayer,
    getLayerAttributeNames,
    getDefaults)

from safe_qgis.exceptions import InvalidParameterError, HashNotFoundError

LOGGER = logging.getLogger('InaSAFE')


class KeywordsDialog(QtGui.QDialog, Ui_KeywordsDialogBase):
    """Dialog implementation class for the InaSAFE keywords editor."""

    def __init__(self, parent, iface, theDock=None, theLayer=None):
        """Constructor for the dialog.
        .. note:: In QtDesigner the advanced editor's predefined keywords
           list should be shown in english always, so when adding entries to
           cboKeyword, be sure to choose :safe_qgis:`Properties<<` and untick
           the :safe_qgis:`translatable` property.

        Args:
           * parent - parent widget of this dialog
           * iface - a Quantum GIS QGisAppInterface instance.
           * theDock - Optional dock widget instance that we can notify of
             changes to the keywords.

        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr(
            'InaSAFE %1 Keywords Editor').arg(get_version()))
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
        self.dock = theDock

        QtCore.QObject.connect(self.lstKeywords,
                               QtCore.SIGNAL("itemClicked(QListWidgetItem *)"),
                               self.makeKeyValueEditable)

        # Set up help dialog showing logic.
        self.helpDialog = None
        myButton = self.buttonBox.button(QtGui.QDialogButtonBox.Help)
        QtCore.QObject.connect(myButton, QtCore.SIGNAL('clicked()'),
                               self.showHelp)

        # set some inital ui state:
        self.defaults = getDefaults()
        self.pbnAdvanced.setChecked(True)
        self.pbnAdvanced.toggle()
        self.radPredefined.setChecked(True)
        self.dsbFemaleRatioDefault.blockSignals(True)
        self.dsbFemaleRatioDefault.setValue(self.defaults[
            'FEM_RATIO'])
        self.dsbFemaleRatioDefault.blockSignals(False)
        #myButton = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        #myButton.setEnabled(False)
        if theLayer is None:
            self.layer = self.iface.activeLayer()
        else:
            self.layer = theLayer
        if self.layer:
            self.loadStateFromKeywords()

        #add a reload from keywords button
        myButton = self.buttonBox.addButton(self.tr('Reload'),
                                            QtGui.QDialogButtonBox.ActionRole)
        QtCore.QObject.connect(myButton, QtCore.SIGNAL('clicked()'),
                               self.loadStateFromKeywords)

    def setLayer(self, theLayer):
        """

        :param theLayer:
        """
        self.layer = theLayer
        self.loadStateFromKeywords()

    def showHelp(self):
        """Load the help text for the keywords safe_qgis"""
        if self.helpDialog:
            del self.helpDialog
        self.helpDialog = Help(self.iface.mainWindow(), 'keywords')

    def togglePostprocessingWidgets(self):
        """Hide or show the post processing widgets depending on context.
        """
        LOGGER.debug('togglePostprocessingWidgets')
        isPostprocessingOn = self.radPostprocessing.isChecked()
        self.cboSubcategory.setVisible(not isPostprocessingOn)
        self.lblSubcategory.setVisible(not isPostprocessingOn)
        self.showAggregationAttribute(isPostprocessingOn)
        self.showFemaleRatioAttribute(isPostprocessingOn)
        self.showFemaleRatioDefault(isPostprocessingOn)

    def showAggregationAttribute(self, theFlag):
        theBox = self.cboAggregationAttribute
        theBox.blockSignals(True)
        theBox.clear()
        theBox.blockSignals(False)
        if theFlag:
            currentKeyword = self.getValueForKey(
                self.defaults['AGGR_ATTR_KEY'])
            fields, attributePosition = getLayerAttributeNames(
                self.layer,
                [QtCore.QVariant.Int, QtCore.QVariant.String],
                currentKeyword)
            theBox.addItems(fields)
            if attributePosition is None:
                theBox.setCurrentIndex(0)
            else:
                theBox.setCurrentIndex(attributePosition)

        theBox.setVisible(theFlag)
        self.lblAggregationAttribute.setVisible(theFlag)

    def showFemaleRatioAttribute(self, theFlag):
        theBox = self.cboFemaleRatioAttribute
        theBox.blockSignals(True)
        theBox.clear()
        theBox.blockSignals(False)
        if theFlag:
            currentKeyword = self.getValueForKey(
                self.defaults['FEM_RATIO_ATTR_KEY'])
            fields, attributePosition = getLayerAttributeNames(
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
        theBox.setVisible(theFlag)
        self.lblFemaleRatioAttribute.setVisible(theFlag)

    def showFemaleRatioDefault(self, theFlag):
        theBox = self.dsbFemaleRatioDefault
        if theFlag:
            currentValue = self.getValueForKey(
                self.defaults['FEM_RATIO_KEY'])
            if currentValue is None:
                val = self.defaults['FEM_RATIO']
            else:
                val = float(currentValue)
            theBox.setValue(val)

        theBox.setVisible(theFlag)
        self.lblFemaleRatioDefault.setVisible(theFlag)

    # prevents actions being handled twice
    @pyqtSignature('int')
    def on_cboAggregationAttribute_currentIndexChanged(self, theIndex=None):
        del theIndex
        self.addListEntry(self.defaults['AGGR_ATTR_KEY'],
                          self.cboAggregationAttribute.currentText())

    # prevents actions being handled twice
    @pyqtSignature('int')
    def on_cboFemaleRatioAttribute_currentIndexChanged(self, theIndex=None):
        del theIndex
        text = self.cboFemaleRatioAttribute.currentText()
        if text == self.tr('Use default'):
            self.dsbFemaleRatioDefault.setEnabled(True)
            currentDefault = self.getValueForKey(
                self.defaults['FEM_RATIO_KEY'])
            if currentDefault is None:
                self.addListEntry(self.defaults['FEM_RATIO_KEY'],
                                  self.dsbFemaleRatioDefault.value())
        else:
            self.dsbFemaleRatioDefault.setEnabled(False)
            self.removeItemByKey(self.defaults['FEM_RATIO_KEY'])
        self.addListEntry(self.defaults['FEM_RATIO_ATTR_KEY'], text)

    # prevents actions being handled twice
    @pyqtSignature('double')
    def on_dsbFemaleRatioDefault_valueChanged(self, theValue):
        del theValue
        theBox = self.dsbFemaleRatioDefault
        if theBox.isEnabled():
            self.addListEntry(self.defaults['FEM_RATIO_KEY'],
                              theBox.value())

    # prevents actions being handled twice
    @pyqtSignature('bool')
    def on_pbnAdvanced_toggled(self, theFlag):
        """Automatic slot executed when the advanced button is toggled.

        .. note:: some of the behaviour for hiding widgets is done using
           the signal/slot editor in designer, so if you are trying to figure
           out how the interactions work, look there too!

        Args:
           theFlag - boolean indicating the new checked state of the button
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        self.toggleAdvanced(theFlag)

    def toggleAdvanced(self, theFlag):
        if theFlag:
            self.pbnAdvanced.setText(self.tr('Hide advanced editor'))
        else:
            self.pbnAdvanced.setText(self.tr('Show advanced editor'))
        self.grpAdvanced.setVisible(theFlag)
        self.resizeDialog()

    # prevents actions being handled twice
    @pyqtSignature('bool')
    def on_radHazard_toggled(self, theFlag):
        """Automatic slot executed when the hazard radio is toggled.

        Args:
           theFlag - boolean indicating the new checked state of the button
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        if not theFlag:
            return
        self.setCategory('hazard')
        self.updateControlsFromList()

    # prevents actions being handled twice
    @pyqtSignature('bool')
    def on_radExposure_toggled(self, theFlag):
        """Automatic slot executed when the hazard radio is toggled on.

        Args:
           theFlag - boolean indicating the new checked state of the button
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        if not theFlag:
            return
        self.setCategory('exposure')
        self.updateControlsFromList()

    # prevents actions being handled twice
    @pyqtSignature('bool')
    def on_radPostprocessing_toggled(self, theFlag):
        """Automatic slot executed when the hazard radio is toggled on.

        Args:
           theFlag - boolean indicating the new checked state of the button
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        if not theFlag:
            self.removeItemByKey(self.defaults['AGGR_ATTR_KEY'])
            self.removeItemByKey(self.defaults['FEM_RATIO_ATTR_KEY'])
            self.removeItemByKey(self.defaults['FEM_RATIO_KEY'])
            return
        self.setCategory('postprocessing')
        self.updateControlsFromList()

    # prevents actions being handled twice
    @pyqtSignature('int')
    def on_cboSubcategory_currentIndexChanged(self, theIndex=None):
        """Automatic slot executed when the subcategory is changed.

        When the user changes the subcategory, we will extract the
        subcategory and dataype or unit (depending on if it is a hazard
        or exposure subcategory) from the [] after the name.

        Args:
           None
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        del theIndex
        myItem = self.cboSubcategory.itemData(
            self.cboSubcategory.currentIndex()).toString()
        myText = str(myItem)
        # I found that myText is 'Not Set' for every language
        if myText == self.tr('Not Set') or myText == 'Not Set':
            self.removeItemByKey('subcategory')
            return
        myTokens = myText.split(' ')
        if len(myTokens) < 1:
            self.removeItemByKey('subcategory')
            return
        mySubcategory = myTokens[0]
        self.addListEntry('subcategory', mySubcategory)

        # Some subcategories e.g. roads have no units or datatype
        if len(myTokens) == 1:
            return
        if myTokens[1].find('[') < 0:
            return
        myCategory = self.getValueForKey('category')
        if 'hazard' == myCategory:
            myUnits = myTokens[1].replace('[', '').replace(']', '')
            self.addListEntry('unit', myUnits)
        if 'exposure' == myCategory:
            myDataType = myTokens[1].replace('[', '').replace(']', '')
            self.addListEntry('datatype', myDataType)
            # prevents actions being handled twice

    def setSubcategoryList(self, theEntries, theSelectedItem=None):
        """Helper to populate the subcategory list based on category context.

        Args:

           * theEntries - an OrderedDict of subcategories. The dict entries
             should be ('earthquake', self.tr('earthquake')). See
             http://www.voidspace.org.uk/python/odict.html for info on
             OrderedDict.
           * theSelectedItem - optional parameter indicating which item
             should be selected in the combo. If the selected item is not
             in theList, it will be appended to it.

        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        # To aoid triggering on_cboSubcategory_currentIndexChanged
        # we block signals from the combo while updating it
        self.cboSubcategory.blockSignals(True)
        self.cboSubcategory.clear()
        theSelectedItemNone = theSelectedItem is not None
        theSelectedItemInValues = theSelectedItem not in theEntries.values()
        theSelectedItemInKeys = theSelectedItem not in theEntries.keys()
        if (theSelectedItemNone and theSelectedItemInValues and
                theSelectedItemInKeys):
            # Add it to the OrderedList
            theEntries[theSelectedItem] = theSelectedItem
        myIndex = 0
        mySelectedIndex = 0
        for myKey, myValue in theEntries.iteritems():
            if (myValue == theSelectedItem or myKey == theSelectedItem):
                mySelectedIndex = myIndex
            myIndex += 1
            self.cboSubcategory.addItem(myValue, myKey)
        self.cboSubcategory.setCurrentIndex(mySelectedIndex)
        self.cboSubcategory.blockSignals(False)

    # prevents actions being handled twice
    @pyqtSignature('')
    def on_pbnAddToList1_clicked(self):
        """Automatic slot executed when the pbnAddToList1 button is pressed.

        Args:
           None
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        if (not self.lePredefinedValue.text().isEmpty() and
                not self.cboKeyword.currentText().isEmpty()):
            myCurrentKey = self.tr(self.cboKeyword.currentText())
            myCurrentValue = self.lePredefinedValue.text()
            self.addListEntry(myCurrentKey, myCurrentValue)
            self.lePredefinedValue.setText('')
            self.updateControlsFromList()

    # prevents actions being handled twice
    @pyqtSignature('')
    def on_pbnAddToList2_clicked(self):
        """Automatic slot executed when the pbnAddToList2 button is pressed.

        Args:
           None
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""

        myCurrentKey = self.leKey.text()
        myCurrentValue = self.leValue.text()
        if myCurrentKey == 'category' and myCurrentValue == 'hazard':
            self.radHazard.blockSignals(True)
            self.radHazard.setChecked(True)
            self.setSubcategoryList(self.standardHazardList)
            self.radHazard.blockSignals(False)
        elif myCurrentKey == 'category' and myCurrentValue == 'exposure':
            self.radExposure.blockSignals(True)
            self.radExposure.setChecked(True)
            self.setSubcategoryList(self.standardExposureList)
            self.radExposure.blockSignals(False)
        elif myCurrentKey == 'category':
            #.. todo:: notify the user their category is invalid
            pass
        self.addListEntry(myCurrentKey, myCurrentValue)
        self.leKey.setText('')
        self.leValue.setText('')
        self.updateControlsFromList()

    # prevents actions being handled twice
    @pyqtSignature('')
    def on_pbnRemove_clicked(self):
        """Automatic slot executed when the pbnRemove button is pressed.

        It will remove any selected items in the keywords list.

        Args:
           None
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        for myItem in self.lstKeywords.selectedItems():
            self.lstKeywords.takeItem(self.lstKeywords.row(myItem))
        self.leKey.setText('')
        self.leValue.setText('')
        self.updateControlsFromList()

    def addListEntry(self, theKey, theValue):
        """Add an item to the keywords list given its key/value.

        The key and value must both be valid, non empty strings
        or an InvalidKVPError will be raised.

        If an entry with the same key exists, it's value will be
        replaced with theValue.

        It will add the current key/value pair to the list if it is not
        already present. The kvp will also be stored in the data of the
        listwidgetitem as a simple string delimited with a bar ('|').

        Args:

           * theKey - string representing the key part of the key
             value pair (kvp)
           * theValue - string representing the value part of the key
             value pair (kvp)

        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        if theKey is None or theKey == '':
            return
        if theValue is None or theValue == '':
            return

        # make sure that both key and value is string
        theKey = str(theKey)
        theValue = str(theValue)
        myMessage = ''
        if ':' in theKey:
            theKey = theKey.replace(':', '.')
            myMessage = self.tr('Colons are not allowed, replaced with "."')
        if ':' in theValue:
            theValue = theValue.replace(':', '.')
            myMessage = self.tr('Colons are not allowed, replaced with "."')
        if myMessage == '':
            self.lblMessage.setText('')
            self.lblMessage.hide()
        else:
            self.lblMessage.setText(myMessage)
            self.lblMessage.show()
        myItem = QtGui.QListWidgetItem(theKey + ':' + theValue)
        # We are going to replace, so remove it if it exists already
        self.removeItemByKey(theKey)
        myData = theKey + '|' + theValue
        myItem.setData(QtCore.Qt.UserRole, myData)
        self.lstKeywords.insertItem(0, myItem)

    def setCategory(self, theCategory):
        """Set the category radio button based on theCategory.

        Args:
           theCategory - a string which must be either 'hazard' or 'exposure'
            or 'postprocessing'.
        Returns:
           False if the radio button could not be updated
        Raises:
           no exceptions explicitly raised."""
        # convert from QString if needed
        myCategory = str(theCategory)
        if self.getValueForKey('category') == myCategory:
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
            self.removeItemByKey('subcategory')
            self.removeItemByKey('datatype')
            self.addListEntry('category', 'hazard')
            myList = self.standardHazardList
            self.setSubcategoryList(myList)

        elif myCategory == 'exposure':
            self.reset()
            self.radExposure.blockSignals(True)
            self.radExposure.setChecked(True)
            self.radExposure.blockSignals(False)
            self.removeItemByKey('subcategory')
            self.removeItemByKey('unit')
            self.addListEntry('category', 'exposure')
            myList = self.standardExposureList
            self.setSubcategoryList(myList)

        else:
            self.reset()
            self.radPostprocessing.blockSignals(True)
            self.radPostprocessing.setChecked(True)
            self.radPostprocessing.blockSignals(False)
            self.removeItemByKey('subcategory')
            self.addListEntry('category', 'postprocessing')

        return True

    def reset(self, thePrimaryKeywordsOnlyFlag=True):
        """Reset all controls to a blank state.

        Args:
            thePrimaryKeywordsOnlyFlag - if True (the default), only
            reset Subcategory, datatype and units.
        Returns:
            None
        Raises:
           no exceptions explicitly raised."""

        self.cboSubcategory.clear()
        self.removeItemByKey('subcategory')
        self.removeItemByKey('datatype')
        self.removeItemByKey('unit')
        if not thePrimaryKeywordsOnlyFlag:
            # Clear everything else too
            self.lstKeywords.clear()
            self.leKey.clear()
            self.leValue.clear()
            self.lePredefinedValue.clear()
            self.leTitle.clear()

    def removeItemByKey(self, theKey):
        """Remove an item from the kvp list given its key.

        Args:
            theKey - key of item to be removed.
        Returns:
            None
        Raises:
           no exceptions explicitly raised."""
        for myCounter in range(self.lstKeywords.count()):
            myExistingItem = self.lstKeywords.item(myCounter)
            myText = myExistingItem.text()
            myTokens = myText.split(':')
            if len(myTokens) < 2:
                break
            myKey = myTokens[0]
            if myKey == theKey:
                # remove it since the key is already present
                self.lstKeywords.takeItem(myCounter)
                break

    def removeItemByValue(self, theValue):
        """Remove an item from the kvp list given its key.

        Args:
            theValue - value of item to be removed.
        Returns:
            None
        Raises:
           no exceptions explicitly raised."""
        for myCounter in range(self.lstKeywords.count()):
            myExistingItem = self.lstKeywords.item(myCounter)
            myText = myExistingItem.text()
            myTokens = myText.split(':')
            myValue = myTokens[1]
            if myValue == theValue:
                # remove it since the key is already present
                self.lstKeywords.takeItem(myCounter)
                break

    def getValueForKey(self, theKey):
        """Check if our key list contains a specific key,
        and return its value if present.

        Args:
           theKey- String representing the key to search for
        Returns:
           Value of key if matched otherwise none
        Raises:
           no exceptions explicitly raised."""
        for myCounter in range(self.lstKeywords.count()):
            myExistingItem = self.lstKeywords.item(myCounter)
            myText = myExistingItem.text()
            myTokens = myText.split(':')
            myKey = str(myTokens[0]).strip()
            myValue = str(myTokens[1]).strip()
            if myKey == theKey:
                return myValue
        return None

    def loadStateFromKeywords(self):
        """Set the ui state to match the keywords of the
           currently active layer.

        Args:
           None
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        # In case the layer has no keywords or any problem occurs reading them,
        # start with a blank slate so that subcategory gets populated nicely &
        # we will assume exposure to start with.
        myKeywords = {'category': 'exposure'}

        try:
            # Now read the layer with sub layer if needed
            myKeywords = self.keywordIO.readKeywords(self.layer)
        except (InvalidParameterError, HashNotFoundError):
            pass

        myLayerName = self.layer.name()
        if 'title' not in myKeywords:
            self.leTitle.setText(myLayerName)
        self.lblLayerName.setText(self.tr('Keywords for %s' % myLayerName))
        #if we have a category key, unpack it first so radio button etc get set
        if 'category' in myKeywords:
            self.setCategory(myKeywords['category'])
            myKeywords.pop('category')

        for myKey in myKeywords.iterkeys():
            self.addListEntry(myKey, str(myKeywords[myKey]))

        # now make the rest of the safe_qgis reflect the list entries
        self.updateControlsFromList()

    def updateControlsFromList(self):
        """Set the ui state to match the keywords of the
           currently active layer.

        Args:
           None
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        mySubcategory = self.getValueForKey('subcategory')
        myUnits = self.getValueForKey('unit')
        myType = self.getValueForKey('datatype')
        myTitle = self.getValueForKey('title')
        if myTitle is not None:
            self.leTitle.setText(myTitle)
        elif self.layer is not None:
            myLayerName = self.layer.name()
            self.lblLayerName.setText(self.tr('Keywords for %s' % myLayerName))
        else:
            self.lblLayerName.setText('')

        if not isPolygonLayer(self.layer):
            self.radPostprocessing.setEnabled(False)

        #adapt gui if we are in postprocessing category
        self.togglePostprocessingWidgets()

        if self.radExposure.isChecked():
            if mySubcategory is not None and myType is not None:
                self.setSubcategoryList(self.standardExposureList,
                                        mySubcategory + ' [' + myType + ']')
            elif mySubcategory is not None:
                self.setSubcategoryList(self.standardExposureList,
                                        mySubcategory)
            else:
                self.setSubcategoryList(self.standardExposureList,
                                        self.tr('Not Set'))
        elif self.radHazard.isChecked():
            if mySubcategory is not None and myUnits is not None:
                self.setSubcategoryList(self.standardHazardList,
                                        mySubcategory + ' [' + myUnits + ']')
            elif mySubcategory is not None:
                self.setSubcategoryList(self.standardHazardList,
                                        mySubcategory)
            else:
                self.setSubcategoryList(self.standardHazardList,
                                        self.tr('Not Set'))

        self.resizeDialog()

    def resizeDialog(self):
        # noinspection PyArgumentList
        QtCore.QCoreApplication.processEvents()
        LOGGER.debug('adjust ing dialog size')
        self.adjustSize()

    # prevents actions being handled twice
    @pyqtSignature('QString')
    def on_leTitle_textEdited(self, theText):
        """Update the keywords list whenever the user changes the title.
        This slot is not called is the title is changed programmatically.

        Args:
           None
        Returns:
           dict - a dictionary of keyword reflecting the state of the dialog.
        Raises:
           no exceptions explicitly raised."""
        self.addListEntry('title', str(theText))

    def getKeywords(self):
        """Obtain the state of the dialog as a keywords dict

        Args:
           None
        Returns:
           dict - a dictionary of keyword reflecting the state of the dialog.
        Raises:
           no exceptions explicitly raised."""
        #make sure title is listed
        if str(self.leTitle.text()) != '':
            self.addListEntry('title', str(self.leTitle.text()))

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

        Args:
           None
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        self.applyPendingChanges()
        myKeywords = self.getKeywords()
        try:
            self.keywordIO.writeKeywords(theLayer=self.layer,
                                         theKeywords=myKeywords)
        except InaSAFEError, e:
            myErrorMessage = getErrorMessage(e)
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QtGui.QMessageBox.warning(
                self, self.tr('InaSAFE'),
                ((self.tr(
                    'An error was encountered when saving the keywords:\n'
                    '%s' % myErrorMessage.to_html()))))
        if self.dock is not None:
            self.dock.getLayers()
        self.done(QtGui.QDialog.Accepted)

    def applyPendingChanges(self):
        """Apply any pending changes e.g. keywords entered without being added.
        See https://github.com/AIFDR/inasafe/issues/249

        Args: None

        Returns: None

        Raises: None
        """

        if self.radPredefined.isChecked():
            self.on_pbnAddToList1_clicked()
        else:
            self.on_pbnAddToList2_clicked()

    def makeKeyValueEditable(self, theItem):
        """Set leKey and leValue to the clicked item in the lstKeywords.

        Args: None

        Returns: None

        Raises: None
        """
        myTempKey = theItem.text().split(':')[0]
        myTempValue = theItem.text().split(':')[1]
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
