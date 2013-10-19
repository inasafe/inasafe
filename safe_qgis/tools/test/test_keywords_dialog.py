"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os
import shutil
# noinspection PyPackageRequirements
from nose import SkipTest
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

# this import required to enable PyQt API v2
import qgis  # pylint: disable=W0611

from PyQt4 import QtGui

from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
    QgsMapLayerRegistry)

from third_party.odict import OrderedDict
from safe_qgis.utilities.utilities_for_testing import (
    get_qgis_app, test_data_path)
from safe_qgis.safe_interface import (
    read_file_keywords,
    unique_filename,
    HAZDATA, TESTDATA)
from safe_qgis.tools.keywords_dialog import KeywordsDialog
from safe_qgis.exceptions import KeywordNotFoundError
from safe_qgis.utilities.utilities import breakdown_defaults, qgis_version


# Get QGis app handle
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


def makePadangLayer():
    """Helper function that returns a single predefined layer"""
    myFile = 'Shakemap_Padang_2009.asc'
    myPath = os.path.join(HAZDATA, myFile)
    myTitle = read_file_keywords(myPath, 'title')
    # myTitle = 'An earthquake in Padang like in 2009'
    myLayer = QgsRasterLayer(myPath, myTitle)
    if qgis_version() >= 10800:  # 1.8 or newer
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([myLayer])
    else:
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayer(myLayer)
    return myLayer


def makePadangLayerClone():
    """Helper function that copies padang keyword for testing and return it."""
    mySourceFileName = 'Shakemap_Padang_2009'
    myExts = ['.asc', '.asc.aux.xml', '.keywords',
              '.lic', '.prj', '.qml', '.sld']
    myFileName = unique_filename()
    # copy to temp file
    for ext in myExts:
        mySourcePath = os.path.join(HAZDATA, mySourceFileName + ext)
        myDestPath = os.path.join(HAZDATA, myFileName + ext)
        shutil.copy2(mySourcePath, myDestPath)
    # return a single predefined layer
    myFile = myFileName + '.asc'
    myPath = os.path.join(HAZDATA, myFile)
    myTitle = read_file_keywords(myPath, 'title')
    myLayer = QgsRasterLayer(myPath, myTitle)
    if qgis_version() >= 10800:  # 1.8 or newer
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([myLayer])
    else:
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayer(myLayer)
    return myLayer, myFileName


def makePolygonLayer():
    """Helper function that returns a single predefined layer"""
    myFile = 'kabupaten_jakarta_singlepart_3_good_attr.shp'
    myPath = os.path.join(TESTDATA, myFile)
    try:
        myTitle = read_file_keywords(myPath, 'title')
    except KeywordNotFoundError:
        myTitle = 'kabupaten_jakarta_singlepart_3_good_attr'
    myLayer = QgsVectorLayer(myPath, myTitle, 'ogr')
    if qgis_version() >= 10800:  # 1.8 or newer
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([myLayer])
    else:
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayer(myLayer)
    return myLayer


def makePointLayer():
    """Helper function that returns a single predefined layer"""
    myFile = 'test_buildings.shp'
    myPath = os.path.join(TESTDATA, myFile)
    try:
        myTitle = read_file_keywords(myPath, 'title')
    except KeywordNotFoundError:
        myTitle = 'kabupaten_jakarta_singlepart_3_good_attr'
    myLayer = QgsVectorLayer(myPath, myTitle, 'ogr')
    # noinspection PyArgumentList
    QgsMapLayerRegistry.instance().addMapLayer(myLayer)
    return myLayer


def remove_temp_file(file_name='temp_Shakemap_Padang_2009'):
    """Helper function that removes temp file that created during test
    :param file_name: File to remove.
    """
    #file_name = 'temp_Shakemap_Padang_2009'
    myExts = ['.asc', '.asc.aux.xml', '.keywords',
              '.lic', '.prj', '.qml', '.sld']
    for ext in myExts:
        os.remove(os.path.join(HAZDATA, file_name + ext))


def make_keywordless_layer():
    """Helper function that returns a single predefined keywordless layer"""
    myFile = 'keywordless_layer.tif'
    myBasePath = test_data_path('hazard')
    myPath = os.path.abspath(os.path.join(myBasePath, myFile))
    myTitle = 'Keywordless Layer'
    myLayer = QgsRasterLayer(myPath, myTitle)
    if qgis_version() >= 10800:  # 1.8 or newer
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([myLayer])
    else:
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayer(myLayer)
    return myLayer


def clearLayers():
    """Clear all the loaded layers"""
    # noinspection PyArgumentList
    for myLayer in QgsMapLayerRegistry.instance().mapLayers():
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().removeMapLayer(myLayer)


class KeywordsDialogTest(unittest.TestCase):
    """Test the InaSAFE keywords GUI"""

    def setUp(self):
        """Create fresh dialog for each test"""
        pass

    def tearDown(self):
        """Destroy the dialog after each test"""
        clearLayers()

    # This is how you skip a test when using unittest ...
    @unittest.skip('Skipping as this test hangs Jenkins if docs are not '
                   'found.')
    def test_showHelp(self):
        """Test that help button works"""
        # ... and this is how you skip it using nosetests
        #prevent unreachable code errors in pylint
        #pylint: disable=W0101
        raise SkipTest("This test hangs Jenkins.")
        # noinspection PyUnreachableCode
        myDialog = KeywordsDialog(PARENT, IFACE)
        myButton = myDialog.buttonBox.button(QtGui.QDialogButtonBox.Help)
        myButton.click()
        myMessage = 'Help dialog was not created when help button pressed'
        assert myDialog.helpDialog is not None, myMessage
        #pylint: enable=W0101

    def test_on_pbnAdvanced_toggled(self):
        """Test advanced button toggle behaviour works"""
        makePadangLayer()
        myDialog = KeywordsDialog(PARENT, IFACE)
        myButton = myDialog.pbnAdvanced
        myButton.setChecked(False)
        myButton.click()
        myState = myDialog.grpAdvanced.isHidden()
        myExpectedState = False
        myMessage = ('Advanced options did not become visible when'
                     ' the advanced button was clicked\nGot'
                     '%s\nExpected\n%s\n' % (myState, myExpectedState))

        assert myState == myExpectedState, myMessage

        # Now hide advanced again and test...
        myButton.click()
        myState = myDialog.grpAdvanced.isHidden()
        myExpectedState = True

        myMessage = ('Advanced options did not become hidden when'
                     ' the advanced button was clicked again\nGot'
                     '%s\nExpected\n%s\n' % (myState, myExpectedState))
        assert not myDialog.grpAdvanced.isVisible(), myMessage

    def test_on_radHazard_toggled(self):
        """Test hazard radio button toggle behaviour works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myButton = myDialog.radHazard
        myButton.setChecked(False)
        myButton.click()
        myMessage = ('Toggling the hazard radio did not add a category '
                     'to the keywords list.')
        assert myDialog.get_value_for_key('category') == 'hazard', myMessage

    def test_on_radPostprocessing_toggled(self):
        """Test hazard radio button toggle behaviour works"""
        myLayer = makePolygonLayer()
        myDefaults = breakdown_defaults()
        myDialog = KeywordsDialog(PARENT, IFACE, layer=myLayer)
        myButton = myDialog.radPostprocessing
        myButton.setChecked(False)
        myButton.click()
        myMessage = ('Toggling the postprocessing radio did not add a '
                     'category to the keywords list.')
        assert myDialog.get_value_for_key(
            'category') == 'postprocessing', myMessage

        myMessage = ('Toggling the postprocessing radio did not add an '
                     'aggregation attribute to the keywords list.')
        assert myDialog.get_value_for_key(
            myDefaults['AGGR_ATTR_KEY']) == 'KAB_NAME', myMessage

        myMessage = ('Toggling the postprocessing radio did not add a '
                     'female ratio attribute to the keywords list.')

        assert myDialog.get_value_for_key(
            myDefaults['FEM_RATIO_ATTR_KEY']) == myDialog.tr('Use default'), \
            myMessage

        myMessage = ('Toggling the postprocessing radio did not add a '
                     'female ratio default value to the keywords list.')
        assert float(myDialog.get_value_for_key(
            myDefaults['FEM_RATIO_KEY'])) == myDefaults['FEM_RATIO'], myMessage

    def test_on_dsbFemaleRatioDefault_valueChanged(self):
        """Test hazard radio button toggle behaviour works"""
        myLayer = makePolygonLayer()
        myDefaults = breakdown_defaults()
        myDialog = KeywordsDialog(PARENT, IFACE, layer=myLayer)
        myButton = myDialog.radPostprocessing
        myButton.setChecked(False)
        myButton.click()
        myFemaleRatioAttrBox = myDialog.cboFemaleRatioAttribute

        #set to Don't use
        myIndex = myFemaleRatioAttrBox.findText(
            myDialog.tr('Don\'t use'))
        myMessage = (myDialog.tr('Don\'t use') + ' not found')
        assert (myIndex != -1), myMessage
        myFemaleRatioAttrBox.setCurrentIndex(myIndex)

        myMessage = ('Toggling the female ratio attribute combo to'
                     ' "Don\'t use" did not add it to the keywords list.')
        assert myDialog.get_value_for_key(
            myDefaults['FEM_RATIO_ATTR_KEY']) == myDialog.tr('Don\'t use'), \
            myMessage

        myMessage = ('Toggling the female ratio attribute combo to'
                     ' "Don\'t use" did not disable dsbFemaleRatioDefault.')
        myIsEnabled = myDialog.dsbFemaleRatioDefault.isEnabled()
        assert not myIsEnabled, myMessage

        myMessage = ('Toggling the female ratio attribute combo to'
                     ' "Don\'t use" did not remove the keyword.')
        assert (myDialog.get_value_for_key(myDefaults['FEM_RATIO']) is None), \
            myMessage

        #set to TEST_REAL
        myIndex = myFemaleRatioAttrBox.findText('TEST_REAL')
        myMessage = 'TEST_REAL not found'
        assert (myIndex != -1), myMessage
        myFemaleRatioAttrBox.setCurrentIndex(myIndex)

        myMessage = ('Toggling the female ratio attribute combo to "TEST_REAL"'
                     ' did not add it to the keywords list.')
        assert myDialog.get_value_for_key(
            myDefaults['FEM_RATIO_ATTR_KEY']) == 'TEST_REAL', myMessage

        myMessage = ('Toggling the female ratio attribute combo to "TEST_REAL"'
                     ' did not disable dsbFemaleRatioDefault.')
        myIsEnabled = myDialog.dsbFemaleRatioDefault.isEnabled()
        assert not myIsEnabled, myMessage

        myMessage = ('Toggling the female ratio attribute combo to "TEST_REAL"'
                     ' did not remove the keyword.')
        assert (myDialog.get_value_for_key(myDefaults['FEM_RATIO']) is
                None), myMessage

    def Xtest_on_radExposure_toggled(self):
        """Test exposure radio button toggle behaviour works"""

        # Cannot get this test to work, but it works fine in the safe_qgis
        myDialog = KeywordsDialog(PARENT, IFACE)
        myButton = myDialog.radExposure
        myButton.setChecked(False)
        myButton.click()
        myMessage = ('Toggling the exposure radio did not add a category '
                     'to the keywords list.')
        assert myDialog.get_value_for_key('category') == 'exposure', myMessage

    def test_on_cboSubcategory_currentIndexChanged(self):
        """Test subcategory combo change event works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myButton = myDialog.radHazard
        myButton.setChecked(True)
        myButton = myDialog.radExposure
        myButton.click()
        myCombo = myDialog.cboSubcategory
        myCombo.setCurrentIndex(1)  # change from 'Not set' to 'structure'
        myMessage = ('Changing the subcategory did not add '
                     'to the keywords list for %s' %
                     myCombo.currentText())
        myKey = myDialog.get_value_for_key('subcategory')

        assert myKey is not None, myMessage
        assert myKey in str(myCombo.currentText()), myMessage

    def test_setSubcategoryList(self):
        """Test set subcategory list works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myList = OrderedDict([('population [density]',
                               'population [density]'),
                            ('population [count]',
                             'population [count]'),
                            ('building',
                             'building'),
                            ('building [osm]',
                             'building [osm]'),
                            ('building [sigab]',
                             'building [sigab]'),
                            ('roads',
                             'roads')])
        mySelectedItem = 'building'
        myDialog.set_subcategory_list(myList, mySelectedItem)
        myResult = str(myDialog.cboSubcategory.currentText())
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, mySelectedItem))

        assert myResult == mySelectedItem, myMessage

    def test_on_pbnAddToList1_clicked(self):
        """Test adding an item to the list using predefined form works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.radPredefined.setChecked(True)
        myDialog.cboKeyword.setCurrentIndex(2)
        myExpectedResult = 'foo'
        myDialog.lePredefinedValue.setText(myExpectedResult)
        myDialog.on_pbnAddToList1_clicked()
        myResult = myDialog.get_value_for_key('datatype')
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))

        assert myResult == myExpectedResult, myMessage

    def test_on_pbnAddToList2_clicked(self):
        """Test adding an item to the list using user defined form works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.radUserDefined.setChecked(True)
        myDialog.leKey.setText('foo')
        myDialog.leValue.setText('bar')
        myExpectedResult = 'bar'
        myDialog.lePredefinedValue.setText(myExpectedResult)
        myDialog.on_pbnAddToList2_clicked()
        myResult = myDialog.get_value_for_key('foo')
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        # print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_on_pbnRemove_clicked(self):
        """Test pressing remove works on key list"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)

        myResult = myDialog.lstKeywords.count()
        myExpectedResult = 0
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

        myDialog.add_list_entry('bar', 'foo')
        myResult = myDialog.lstKeywords.count()
        myExpectedResult = 1
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_addListEntry(self):
        """Test add entry to list works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.add_list_entry('bar', 'foo')
        myResult = myDialog.get_value_for_key('bar')
        myExpectedResult = 'foo'
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_addWarningsForColons(self):
        """Test add entry to list works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.add_list_entry('bar', 'fo:o')
        myResult = myDialog.get_value_for_key('bar')
        myExpectedResult = 'fo.o'
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage
        #
        # Check the user gets a message if they put colons in the value
        #
        myExpectedResult = 'Colons are not allowed, replaced with "."'
        myResult = str(myDialog.lblMessage.text())
        myMessage = ('lblMessage error \nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage
        #
        # Check the user gets a message if they put colons in the key
        #
        myDialog.add_list_entry('ba:r', 'foo')
        myExpectedResult = 'Colons are not allowed, replaced with "."'
        myResult = str(myDialog.lblMessage.text())
        myMessage = ('lblMessage error \nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_setCategory(self):
        """Test set category works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.set_category('hazard')
        myExpectedResult = 'hazard'
        myResult = myDialog.get_value_for_key('category')
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_reset(self):
        """Test form reset works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.leTitle.setText('Foo')
        myDialog.reset(False)
        myExpectedResult = ''
        myResult = myDialog.leTitle.text()
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        assert myResult == myExpectedResult, myMessage

    def test_removeItemByKey(self):
        """Test remove item by its key works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.add_list_entry('bar', 'foo')
        myDialog.remove_item_by_key('bar')
        myResult = myDialog.lstKeywords.count()
        myExpectedResult = 0
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_removeItemByValue(self):
        """Test remove item by its value works"""
        makePadangLayer()
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.remove_item_by_value('hazard')

        myKeywords = myDialog.get_keywords()
        myExpectedKeywords = {'source': 'USGS',
                              'title': 'An earthquake in Padang like in 2009',
                              'subcategory': 'earthquake',
                              'unit': 'MMI'}
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myKeywords, myExpectedKeywords))

        assert myKeywords == myExpectedKeywords, myMessage

    def test_getValueForKey(self):
        """Test get value for key works"""
        makePadangLayer()
        myDialog = KeywordsDialog(PARENT, IFACE)
        myExpectedValue = 'hazard'
        myValue = myDialog.get_value_for_key('category')
        myMessage = ('\nExpected key value of %s\nGot %s' %
                     (myExpectedValue, myValue))
        assert myValue == myExpectedValue, myMessage

    def test_loadStateFromKeywords(self):
        """Test load state from keywords works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myLayer = makePadangLayer()
        myDialog.layer = myLayer
        myDialog.load_state_from_keywords()
        myKeywords = myDialog.get_keywords()

        myExpectedKeywords = {'title': 'An earthquake in Padang like in 2009',
                              'category': 'hazard',
                              'source': 'USGS',
                              'subcategory': 'earthquake',
                              'unit': 'MMI'}
        myMessage = ('\nGot:\n%s\nExpected:\n%s\n' %
                     (myKeywords, myExpectedKeywords))
        assert myKeywords == myExpectedKeywords, myMessage

    def test_layer_without_keywords(self):
        """Test load state from keywords works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myLayer = make_keywordless_layer()
        myDialog.layer = myLayer
        myDialog.load_state_from_keywords()

    def test_addKeywordWhenPressOkButton(self):
        """Test add keyword when ok button is pressed."""
        #_, myFile = makePadangLayerClone()
        makePadangLayerClone()
        myDialog = KeywordsDialog(PARENT, IFACE)

        myDialog.radUserDefined.setChecked(True)
        myDialog.leKey.setText('foo')
        myDialog.leValue.setText('bar')
        okButton = myDialog.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        okButton.click()

        # delete temp file
        # removeTempFile(myFile)

        myExpectedResult = 'bar'
        myResult = myDialog.get_value_for_key('foo')
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        assert myExpectedResult == myResult, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(KeywordsDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
