# coding=utf-8
"""Tests for the keyword wizard."""
import shutil
import unittest
# noinspection PyUnresolvedReferences
import qgis
from PyQt4 import QtCore
from PyQt4.QtCore import Qt
# noinspection PyPackageRequirements
from safe.common.utilities import temp_dir
from safe.test.utilities import (
    clone_raster_layer,
    clone_shp_layer,
    get_qgis_app,
    standard_data_path,
    load_test_vector_layer)
# AG: get_qgis_app() should be called before importing modules from
# safe.gui.tools.wizard
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
from safe.definitionsv4.versions import inasafe_keyword_version
from safe.definitionsv4.layer_modes import (
    layer_mode_continuous, layer_mode_classified)
from safe.definitionsv4.layer_purposes import (
    layer_purpose_hazard, layer_purpose_exposure, layer_purpose_aggregation)
from safe.definitionsv4.hazard import hazard_volcano
from safe.definitionsv4.exposure import exposure_structure, exposure_population
from safe.definitionsv4.hazard_category import hazard_category_multiple_event
from safe.definitionsv4.hazard_classifications import volcano_hazard_classes
from safe.definitionsv4.constants import no_field
from safe.definitionsv4.fields import (
    hazard_name_field,
    aggregation_name_field,
    population_count_field,
    exposure_type_field,
    hazard_value_field)
from safe.definitionsv4.layer_geometry import layer_geometry_polygon
from safe.definitionsv4.exposure_classifications import (
    generic_structure_classes)
from safe.definitionsv4.units import count_exposure_unit

from safe.gui.tools.wizard.wizard_dialog import WizardDialog
from safe.utilities.keyword_io import KeywordIO
from safe.definitionsv4.utilities import definition, get_compulsory_fields

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

source = u'Source'
source_scale = u'Source Scale'
source_url = u'Source Url'
# noinspection PyCallByClass
# source_date = QtCore.QDateTime.fromString('06-12-2015', 'dd-MM-yyyy')
from  datetime import datetime
source_date = datetime.strptime('06-12-2015', '%d-%m-%Y')
source_license = u'Source License'
layer_title = u'Layer Title'


# noinspection PyTypeChecker
class TestKeywordWizard(unittest.TestCase):
    """Test the InaSAFE keyword wizard GUI"""
    maxDiff = None

    def tearDown(self):
        """Run after each test."""
        # Remove the mess that we made on each test
        shutil.rmtree(temp_dir(sub_dir='test'))

    def check_list(self, expected_list, list_widget):
        """Helper function to check that list_widget is equal to expected_list.

        :param expected_list: List of expected values to be found.
        :type expected_list: list

        :param list_widget: List widget that wants to be checked.
        :type expected_list: QListWidget
        """
        real_list = []
        for i in range(list_widget.count()):
            real_list.append(list_widget.item(i).text())
        self.assertItemsEqual(expected_list, real_list)

    def check_current_step(self, expected_step):
        """Helper function to check the current step is expected_step

        :param expected_step: The expected current step.
        :type expected_step: WizardStep instance
        """
        current_step = expected_step.parent.get_current_step()
        message = 'Should be step %s but it got %s' % (
            expected_step.__class__.__name__, current_step.__class__.__name__)
        self.assertEqual(expected_step, current_step, message)

    def check_current_text(self, expected_text, list_widget):
        """Check the current text in list widget is expected_text

        :param expected_text: The expected current step.
        :type expected_text: str

        :param list_widget: List widget that wants to be checked.
        :type list_widget: QListWidget
        """
        try:
            # noinspection PyUnresolvedReferences
            current_text = list_widget.currentItem().text()
            self.assertEqual(expected_text, current_text)
        except AttributeError:
            options = [
                list_widget.item(i).text()
                for i in range(list_widget.count())
            ]
            message = 'There is no %s in the available option %s' % (
                expected_text, options)
            self.assertFalse(True, message)

    # noinspection PyUnresolvedReferences
    def select_from_list_widget(self, option, list_widget):
        """Helper function to select option from list_widget

        :param option: Option to be chosen
        :type option: str

        :param list_widget: List widget that wants to be checked.
        :type list_widget: QListWidget
        """
        available_options = []
        for i in range(list_widget.count()):
            if list_widget.item(i).text() == option:
                list_widget.setCurrentRow(i)
                return
            else:
                available_options.append(list_widget.item(i).text())
        message = (
            'There is no %s in the list widget. The available options are %'
            's' % (option, available_options))

        raise Exception(message)

    def test_invalid_keyword_layer(self):
        layer = clone_raster_layer(
            name='invalid_keyword_xml',
            include_keywords=True,
            source_directory=standard_data_path('other'),
            extension='.tif')

        # check the environment first
        self.assertIsNotNone(layer.dataProvider())
        # Initialize dialog
        # noinspection PyTypeChecker
        dialog = WizardDialog()
        # It shouldn't raise any exception although the xml is invalid
        dialog.set_keywords_creation_mode(layer)

    def test_hazard_volcano_polygon_keyword(self):
        """Test keyword wizard for volcano hazard polygon"""
        layer = clone_shp_layer(
            name='volcano_krb',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))

        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # Check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Select hazard
        self.select_from_list_widget(
            layer_purpose_hazard['name'], dialog.step_kw_purpose.lstCategories)

        # Click next to select hazard
        dialog.pbnNext.click()

        # Check if in select hazard step
        self.check_current_step(dialog.step_kw_subcategory)

        # select volcano
        self.select_from_list_widget(
            hazard_volcano['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select volcano
        dialog.pbnNext.click()

        # Check if in select hazard category step
        self.check_current_step(dialog.step_kw_hazard_category)

        # select multiple_event
        self.select_from_list_widget(
            hazard_category_multiple_event['name'],
            dialog.step_kw_hazard_category.lstHazardCategories)

        # Click next to select multiple event
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # select classified mode
        self.select_from_list_widget(
            layer_mode_classified['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select classified
        dialog.pbnNext.click()

        # Check if in select classification step
        self.check_current_step(dialog.step_kw_classification)

        # select volcano vector hazard classes classification
        self.select_from_list_widget(
            volcano_hazard_classes['name'],
            dialog.step_kw_classification.lstClassifications)

        # Click next to select volcano classes
        dialog.pbnNext.click()

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # select KRB field
        self.select_from_list_widget('KRB', dialog.step_kw_field.lstFields)

        # Click next to select KRB
        dialog.pbnNext.click()

        # Check if in classify step
        self.check_current_step(dialog.step_kw_classify)

        # select value map
        classification = dialog.step_kw_classification.\
            selected_classification()
        default_classes = classification['classes']
        unassigned_values = []  # no need to check actually, not save in file
        assigned_values = {
            'low': ['Kawasan Rawan Bencana I'],
            'medium': ['Kawasan Rawan Bencana II'],
            'high': ['Kawasan Rawan Bencana III']
        }
        dialog.step_kw_classify.populate_classified_values(
            unassigned_values, assigned_values, default_classes)

        # Click next to finish value mapping
        dialog.pbnNext.click()

        # select inasafe fields step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Get the parameter widget for hazard name
        hazard_name_parameter_widget = dialog.step_kw_inasafe_fields.\
            parameter_container.get_parameter_widget_by_guid(
                hazard_name_field['key'])

        # Check if it's set to no field at the beginning
        self.assertEqual(
            no_field, hazard_name_parameter_widget.get_parameter().value)

        # Select volcano
        hazard_name_parameter_widget.set_choice('volcano')

        # Check if it's set to volcano
        self.assertEqual(
            'volcano', hazard_name_parameter_widget.get_parameter().value)

        # Check if in InaSAFE field step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Click next to finish inasafe fields step and go to inasafe default
        # field step
        dialog.pbnNext.click()

        # Check if in InaSAFE Default field step
        self.check_current_step(dialog.step_kw_default_inasafe_fields)

        # Click next to finish InaSAFE Default Field step and go to source step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.step_kw_source.leSource.setText(source)
        dialog.step_kw_source.leSource_scale.setText(source_scale)
        dialog.step_kw_source.leSource_url.setText(source_url)
        dialog.step_kw_source.ckbSource_date.setChecked(True)
        dialog.step_kw_source.dtSource_date.setDateTime(source_date)
        dialog.step_kw_source.leSource_license.setText(source_license)

        # Click next to finish source step and go to title step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_title)

        dialog.step_kw_title.leTitle.setText(layer_title)

        # Click next to finish title step and go to kw summary step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_summary)

        # Click finish
        dialog.pbnNext.click()

        # Checking Keyword Created
        expected_keyword = {
            'scale': source_scale,
            'hazard_category': hazard_category_multiple_event['key'],
            'license': source_license,
            'source': source,
            'url': source_url,
            'title': layer_title,
            'hazard': hazard_volcano['key'],
            'inasafe_fields':
                {
                    hazard_value_field['key']: u'KRB',
                    hazard_name_field['key']: u'volcano',
                 },
            'inasafe_default_values': {},
            'value_map': assigned_values,
            'date': source_date,
            'classification': volcano_hazard_classes['key'],
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'layer_mode': layer_mode_classified['key']
        }

        real_keywords = dialog.get_keywords()
        self.assertDictEqual(real_keywords, expected_keyword)

    def test_existing_keywords_hazard_volcano_polygon(self):
        """Test existing keyword for hazard volcano polygon."""
        layer = load_test_vector_layer(
            'hazard', 'volcano_krb.shp', clone=True)
        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # Check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Check if hazard is selected
        self.check_current_text(
            layer_purpose_hazard['name'], dialog.step_kw_purpose.lstCategories)

        # Click next to select hazard
        dialog.pbnNext.click()

        # Check if in select hazard step
        self.check_current_step(dialog.step_kw_subcategory)

        # Check if volcano is selected
        self.check_current_text(
            hazard_volcano['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select volcano
        dialog.pbnNext.click()

        # Check if in select hazard category step
        self.check_current_step(dialog.step_kw_hazard_category)

        # Check if multiple event is selected
        self.check_current_text(
            hazard_category_multiple_event['name'],
            dialog.step_kw_hazard_category.lstHazardCategories)

        # Click next to select multiple event
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # Check if classified is selected
        self.check_current_text(
            layer_mode_classified['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select classified
        dialog.pbnNext.click()

        # Check if in select classification step
        self.check_current_step(dialog.step_kw_classification)

        # Check if volcano class is selected
        self.check_current_text(
            volcano_hazard_classes['name'],
            dialog.step_kw_classification.lstClassifications)

        # Click next to select volcano classes
        dialog.pbnNext.click()

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # Check if KRB is selected
        self.check_current_text('KRB', dialog.step_kw_field.lstFields)

        # Click next to select KRB
        dialog.pbnNext.click()

        # Check if in classify step
        self.check_current_step(dialog.step_kw_classify)

        # Click next to finish value mapping
        dialog.pbnNext.click()

        # select additional keywords / inasafe fields step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Check inasafe fields
        parameters = dialog.step_kw_inasafe_fields. \
            parameter_container.get_parameters(True)

        # Get layer's inasafe_fields
        inasafe_fields = layer.keywords.get('inasafe_fields')
        self.assertIsNotNone(inasafe_fields)
        for key, value in inasafe_fields.items():
            # Not check if it's hazard_class_field
            if key == get_compulsory_fields(
                    layer_purpose_hazard['key'])['key']:
                continue
            # Check if existing key in parameters guid
            self.assertIn(key, [p.guid for p in parameters])
            # Iterate through all parameter to get parameter value
            for parameter in parameters:
                if parameter.guid == key:
                    # Check the value is the same
                    self.assertEqual(value, parameter.value)
                    break

        for parameter in parameters:
            # If not available is chosen, inasafe_fields shouldn't have it
            if parameter.value == no_field:
                self.assertNotIn(parameter.guid, inasafe_fields.keys())
            # If not available is not chosen, inasafe_fields should have it
            else:
                self.assertIn(parameter.guid, inasafe_fields.keys())

        # Click next to finish inasafe fields step and go to inasafe default
        # field step
        dialog.pbnNext.click()

        # Check if in InaSAFE Default field step
        self.check_current_step(dialog.step_kw_default_inasafe_fields)

        # Click next to finish InaSAFE Default Field step and go to source step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        self.assertTrue(dialog.pbnNext.isEnabled())
        self.assertEqual(dialog.step_kw_source.leSource.text(), '')
        self.assertEqual(dialog.step_kw_source.leSource_url.text(), '')
        self.assertFalse(dialog.step_kw_source.ckbSource_date.isChecked())
        self.assertEqual(dialog.step_kw_source.leSource_scale.text(), '')

        # Click next to finish source step and go to title step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_title)

        self.assertEqual(
            'Volcano KRB', dialog.step_kw_title.leTitle.text())
        self.assertTrue(dialog.pbnNext.isEnabled())

        # Click finish
        dialog.pbnNext.click()

        self.assertDictEqual(
            layer.keywords['value_map'], dialog.get_keywords()['value_map'])

    def test_exposure_structure_polygon_keyword(self):
        """Test keyword wizard for exposure structure polygon"""
        layer = clone_shp_layer(
            name='buildings',
            include_keywords=False,
            source_directory=standard_data_path('exposure'))
        self.assertIsNotNone(layer)

        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # Check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Select exposure
        self.select_from_list_widget(
            layer_purpose_exposure['name'],
            dialog.step_kw_purpose.lstCategories)

        # Click next to select exposure
        dialog.pbnNext.click()

        # Check if in select exposure step
        self.check_current_step(dialog.step_kw_subcategory)

        # select structure
        self.select_from_list_widget(
            exposure_structure['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select structure
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # select classified mode
        self.select_from_list_widget(
            layer_mode_classified['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select classified
        dialog.pbnNext.click()

        # Check if in select classification step
        self.check_current_step(dialog.step_kw_classification)

        # select generic structure classes classification
        self.select_from_list_widget(
            generic_structure_classes['name'],
            dialog.step_kw_classification.lstClassifications)

        # Click next to select the classifications
        dialog.pbnNext.click()

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # select TYPE field
        self.select_from_list_widget(
            'TYPE', dialog.step_kw_field.lstFields)

        # Click next to select TYPE
        dialog.pbnNext.click()

        # Check if in classify step
        self.check_current_step(dialog.step_kw_classify)

        default_classes = generic_structure_classes['classes']
        unassigned_values = []  # no need to check actually, not save in file
        assigned_values = {
            u'residential': [u'Residential'],
            u'education': [u'School'],
            u'health': [u'Clinic/Doctor'],
            u'transport': [],
            u'place of worship': [u'Place of Worship - Islam'],
            u'government': [u'Government'],
            u'commercial': [u'Commercial', u'Industrial'],
            u'recreation': [],
            u'public facility': [],
            u'other': []
        }
        dialog.step_kw_classify.populate_classified_values(
            unassigned_values, assigned_values, default_classes)

        # Click next to finish value mapping
        dialog.pbnNext.click()

        # Check if in InaSAFE field step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Click next to finish inasafe fields step and go to inasafe default
        # field step
        dialog.pbnNext.click()

        # Check if in InaSAFE Default field step
        self.check_current_step(dialog.step_kw_default_inasafe_fields)

        # Click next to finish InaSAFE Default Field step and go to source step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.step_kw_source.leSource.setText(source)
        dialog.step_kw_source.leSource_scale.setText(source_scale)
        dialog.step_kw_source.leSource_url.setText(source_url)
        dialog.step_kw_source.ckbSource_date.setChecked(True)
        dialog.step_kw_source.dtSource_date.setDateTime(source_date)
        dialog.step_kw_source.leSource_license.setText(source_license)

        # Click next to finish source step and go to title step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_title)

        dialog.step_kw_title.leTitle.setText(layer_title)

        # Click next to finish title step and go to kw summary step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_summary)

        # Click finish
        dialog.pbnNext.click()

        # Checking Keyword Created
        expected_keyword = {
            'scale': source_scale,
            'license': source_license,
            'source': source,
            'url': source_url,
            'title': layer_title,
            'exposure': exposure_structure['key'],
            'inasafe_fields':
                {
                    exposure_type_field['key']: u'TYPE',
                },
            'inasafe_default_values': {},
            # No value will be omitted.
            'value_map': dict((k, v) for k, v in assigned_values.items() if v),
            'date': source_date,
            'classification': generic_structure_classes['key'],
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_exposure['key'],
            'layer_mode': layer_mode_classified['key']
        }

        real_keywords = dialog.get_keywords()

        self.assertDictEqual(real_keywords, expected_keyword)

    def test_existing_keywords_exposure_structure_polygon(self):
        """Test existing keyword for exposure structure polygon."""
        layer = load_test_vector_layer(
            'exposure', 'buildings.shp', clone=True)
        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # Check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Check if hazard is selected
        self.check_current_text(
            layer_purpose_exposure['name'],
            dialog.step_kw_purpose.lstCategories)

        # Click next to select exposure
        dialog.pbnNext.click()

        # Check if in select exposure step
        self.check_current_step(dialog.step_kw_subcategory)

        # Check if structure is selected
        self.check_current_text(
            exposure_structure['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select structure
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # Check if classified is selected
        self.check_current_text(
            layer_mode_classified['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select classified
        dialog.pbnNext.click()

        # Check if in select classification step
        self.check_current_step(dialog.step_kw_classification)

        # Check if generic structure classes is selected.
        self.check_current_text(
            generic_structure_classes['name'],
            dialog.step_kw_classification.lstClassifications)

        # Click next to select the classifications
        dialog.pbnNext.click()

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # Check if TYPE is selected
        self.check_current_text('TYPE', dialog.step_kw_field.lstFields)

        # Click next to select TYPE
        dialog.pbnNext.click()

        # Check if in classify step
        self.check_current_step(dialog.step_kw_classify)

        # Click next to finish value mapping
        dialog.pbnNext.click()

        # select additional keywords / inasafe fields step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Check inasafe fields
        parameters = dialog.step_kw_inasafe_fields. \
            parameter_container.get_parameters(True)

        # Get layer's inasafe_fields
        inasafe_fields = layer.keywords.get('inasafe_fields')
        self.assertIsNotNone(inasafe_fields)
        for key, value in inasafe_fields.items():
            # Not check if it's hazard_value_field
            if key == get_compulsory_fields(
                    layer_purpose_exposure['key'])['key']:
                continue
            # Check if existing key in parameters guid
            self.assertIn(key, [p.guid for p in parameters])
            # Iterate through all parameter to get parameter value
            for parameter in parameters:
                if parameter.guid == key:
                    # Check the value is the same
                    self.assertEqual(value, parameter.value)
                    break

        for parameter in parameters:
            # If not available is chosen, inasafe_fields shouldn't have it
            if parameter.value == no_field:
                self.assertNotIn(parameter.guid, inasafe_fields.keys())
            # If not available is not chosen, inasafe_fields should have it
            else:
                self.assertIn(parameter.guid, inasafe_fields.keys())

        # Click next to finish inasafe fields step and go to inasafe default
        # field step
        dialog.pbnNext.click()

        # Check if in InaSAFE Default field step
        self.check_current_step(dialog.step_kw_default_inasafe_fields)

        # Click next to finish InaSAFE Default Field step and go to source step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        self.assertTrue(dialog.pbnNext.isEnabled())
        self.assertEqual(
            dialog.step_kw_source.leSource.text(),
            layer.keywords.get('source'))
        self.assertEqual(dialog.step_kw_source.leSource_url.text(), '')
        self.assertFalse(dialog.step_kw_source.ckbSource_date.isChecked())
        self.assertEqual(dialog.step_kw_source.leSource_scale.text(), '')

        # Click next to finish source step and go to title step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_title)

        self.assertEqual(
            'Buildings', dialog.step_kw_title.leTitle.text())
        self.assertTrue(dialog.pbnNext.isEnabled())

        # Click finish
        dialog.pbnNext.click()

        self.assertDictEqual(
            layer.keywords['value_map'], dialog.get_keywords()['value_map'])

    def test_aggregation_keyword(self):
        """Test Aggregation Keywords"""
        layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson', clone_to_memory=True)
        layer.keywords = {}

        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # Check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Select aggregation
        self.select_from_list_widget(
            layer_purpose_aggregation['name'],
            dialog.step_kw_purpose.lstCategories)

        # Click next to select aggregation
        dialog.pbnNext.click()

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # select area_name field
        area_name = 'area_name'
        self.select_from_list_widget(
            area_name, dialog.step_kw_field.lstFields)

        # Click next to select area_name
        dialog.pbnNext.click()

        # select inasafe fields step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Click next to finish inasafe fields step and go to inasafe default
        # field step
        dialog.pbnNext.click()

        # Check if in InaSAFE Default field step
        self.check_current_step(dialog.step_kw_default_inasafe_fields)

        # Click next to finish InaSAFE Default Field step and go to source step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        # Click next to finish source step and go to title step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_title)

        layer_title = 'Layer Title'
        dialog.step_kw_title.leTitle.setText(layer_title)

        # Click next to finish title step and go to kw summary step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_summary)

        # Click finish
        dialog.pbnNext.click()

        expected_keyword = {
            'inasafe_default_values': {},
            'inasafe_fields': {aggregation_name_field['key']: area_name},
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_aggregation['key'],
            'title': layer_title
        }
        # Check the keywords
        real_keywords = dialog.get_keywords()
        self.assertDictEqual(real_keywords, expected_keyword)

    def test_existing_aggregation_keyword(self):
        """Test Aggregation Keywords"""
        layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson', clone_to_memory=True)

        area_name = 'area_name'
        expected_keyword = {
            'inasafe_default_values': {},
            'inasafe_fields': {aggregation_name_field['key']: area_name},
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_aggregation['key'],
            'title': layer_title
        }
        # Assigning dummy keyword
        layer.keywords = expected_keyword

        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # Check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Select aggregation
        self.check_current_text(
            layer_purpose_aggregation['name'],
            dialog.step_kw_purpose.lstCategories)

        # Click next to select aggregation
        dialog.pbnNext.click()

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # select area_name field
        self.check_current_text(
            area_name, dialog.step_kw_field.lstFields)

        # Click next to select KRB
        dialog.pbnNext.click()

        # select inasafe fields step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Click next to finish inasafe fields step and go to inasafe default
        # field step
        dialog.pbnNext.click()

        # Check if in InaSAFE Default field step
        self.check_current_step(dialog.step_kw_default_inasafe_fields)

        # Click next to finish InaSAFE Default Field step and go to source step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        # Click next to finish source step and go to title step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_title)

        # Check if the title is already filled
        self.assertEqual(dialog.step_kw_title.leTitle.text(), layer_title)

        # Click next to finish title step and go to kw summary step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_summary)

        # Click finish
        dialog.pbnNext.click()

        # Check the keywords
        real_keywords = dialog.get_keywords()
        self.assertDictEqual(real_keywords, expected_keyword)

    def test_exposure_population_polygon_keyword(self):
        """Test exposure population polygon keyword"""
        layer = load_test_vector_layer(
            'gisv4', 'exposure', 'census.geojson', clone_to_memory=True)
        layer.keywords = {}

        self.assertIsNotNone(layer)

        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # Check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Select exposure
        self.select_from_list_widget(
            layer_purpose_exposure['name'],
            dialog.step_kw_purpose.lstCategories)

        # Click next to select exposure
        dialog.pbnNext.click()

        # Check if in select exposure step
        self.check_current_step(dialog.step_kw_subcategory)

        # select population
        self.select_from_list_widget(
            exposure_population['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select population
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # Select continuous
        self.select_from_list_widget(
            layer_mode_continuous['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select continuous
        dialog.pbnNext.click()

        # Check if in select unit step
        self.check_current_step(dialog.step_kw_unit)

        # Select count
        self.select_from_list_widget(
            count_exposure_unit['name'],
            dialog.step_kw_unit.lstUnits)

        # Click next to select count
        dialog.pbnNext.click()

        # Check if in select unit step
        self.check_current_step(dialog.step_kw_field)

        # select population field
        population_field = 'population'
        self.select_from_list_widget(
            population_field, dialog.step_kw_field.lstFields)

        # Click next to select population
        dialog.pbnNext.click()

        # Check if in InaSAFE field step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Click next to finish inasafe fields step and go to inasafe default
        # field step
        dialog.pbnNext.click()

        # Check if in InaSAFE Default field step
        self.check_current_step(dialog.step_kw_default_inasafe_fields)

        # Click next to finish InaSAFE Default Field step and go to source step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.step_kw_source.leSource.setText(source)
        dialog.step_kw_source.leSource_scale.setText(source_scale)
        dialog.step_kw_source.leSource_url.setText(source_url)
        dialog.step_kw_source.ckbSource_date.setChecked(True)
        dialog.step_kw_source.dtSource_date.setDateTime(source_date)
        dialog.step_kw_source.leSource_license.setText(source_license)

        # Click next to finish source step and go to title step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_title)

        dialog.step_kw_title.leTitle.setText(layer_title)

        # Click next to finish title step and go to kw summary step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_summary)

        # Click finish
        dialog.pbnNext.click()

        # Checking Keyword Created
        expected_keyword = {
            'scale': source_scale,
            'license': source_license,
            'source': source,
            'url': source_url,
            'title': layer_title,
            'exposure': exposure_population['key'],
            'exposure_unit': count_exposure_unit['key'],
            'inasafe_fields':
                {
                    population_count_field['key']: u'population',
                },
            'inasafe_default_values': {},
            # No value will be omitted.
            'date': source_date,
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_exposure['key'],
            'layer_mode': layer_mode_continuous['key']
        }

        real_keywords = dialog.get_keywords()

        self.assertDictEqual(real_keywords, expected_keyword)

    def test_existing_exposure_population_polygon_keyword(self):
        """Test existing exposure population polygon keyword"""
        layer = load_test_vector_layer(
            'gisv4', 'exposure', 'census.geojson', clone_to_memory=True)
        expected_keyword = {
            'scale': source_scale,
            'license': source_license,
            'source': source,
            'url': source_url,
            'title': layer_title,
            'exposure': exposure_population['key'],
            'exposure_unit': count_exposure_unit['key'],
            'inasafe_fields':
                {
                    population_count_field['key']: u'population',
                },
            'inasafe_default_values': {},
            # No value will be omitted.
            'date': source_date,
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_exposure['key'],
            'layer_mode': layer_mode_continuous['key']
        }
        layer.keywords = expected_keyword

        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # Check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Check if exposure is selected
        self.select_from_list_widget(
            layer_purpose_exposure['name'],
            dialog.step_kw_purpose.lstCategories)

        # Click next to select exposure
        dialog.pbnNext.click()

        # Check if in select exposure step
        self.check_current_step(dialog.step_kw_subcategory)

        # Check if population is selected
        self.check_current_text(
            exposure_population['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select population
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # Check if continuous is selected
        self.check_current_text(
            layer_mode_continuous['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select continuous
        dialog.pbnNext.click()

        # Check if in select unit step
        self.check_current_step(dialog.step_kw_unit)

        # Check if count is selected
        self.check_current_text(
            count_exposure_unit['name'],
            dialog.step_kw_unit.lstUnits)

        # Click next to select count
        dialog.pbnNext.click()

        # Check if in select unit step
        self.check_current_step(dialog.step_kw_field)

        # Check if population is selected
        population_field = 'population'
        self.check_current_text(
            population_field, dialog.step_kw_field.lstFields)

        # Click next to select population
        dialog.pbnNext.click()

        # Check if in InaSAFE field step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Click next to finish inasafe fields step and go to inasafe default
        # field step
        dialog.pbnNext.click()

        # Check if in InaSAFE Default field step
        self.check_current_step(dialog.step_kw_default_inasafe_fields)

        # Click next to finish InaSAFE Default Field step and go to source step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        self.assertEqual(dialog.step_kw_source.leSource.text(), source)
        self.assertEqual(
            dialog.step_kw_source.leSource_scale.text(), source_scale)
        self.assertEqual(
            dialog.step_kw_source.ckbSource_date.isChecked(), True)
        self.assertEqual(
            dialog.step_kw_source.dtSource_date.dateTime(), source_date)
        self.assertEqual(
            dialog.step_kw_source.leSource_license.text(), source_license)

        # Click next to finish source step and go to title step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_title)

        self.assertEqual(dialog.step_kw_title.leTitle.text(), layer_title)

        # Click next to finish title step and go to kw summary step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_summary)

        # Click finish
        dialog.pbnNext.click()

        # Checking Keyword Created
        real_keywords = dialog.get_keywords()

        self.assertDictEqual(real_keywords, expected_keyword)

    # noinspection PyTypeChecker
    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_unit_building_generic(self):
        """Test for case existing building generic unit for structure."""
        layer = clone_shp_layer(
            name='buildings',
            include_keywords=True,
            source_directory=standard_data_path('exposure'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # go to subcategory

        self.check_current_step(dialog.step_kw_subcategory)
        dialog.pbnNext.click()  # go to layer mode

        self.check_current_step(dialog.step_kw_layermode)
        dialog.pbnNext.click()  # go to field

        self.check_current_step(dialog.step_kw_field)
        dialog.pbnNext.click()  # go to classify

        # check if in step classify
        self.check_current_step(dialog.step_kw_classify)
        dialog.pbnNext.click()  # go to source

        # check if in step source
        self.check_current_step(dialog.step_kw_source)
        dialog.pbnNext.click()  # go to title

        # check if in step title
        self.check_current_step(dialog.step_kw_title)

        dialog.pbnNext.click()  # finishing

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_unknown_unit(self):
        """Checking that it works for unknown unit."""
        layer = clone_shp_layer(
            name='volcano_krb',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # choose hazard
        dialog.pbnNext.click()  # choose volcano
        dialog.pbnNext.click()  # choose Multiple event
        dialog.step_kw_unit.lstUnits.setCurrentRow(1)
        self.check_current_text(
            'Classified', dialog.step_kw_layermode.lstLayerModes)
        dialog.pbnNext.click()  # choose classified

        # check if in step classification
        self.check_current_step(dialog.step_kw_classification)
        dialog.pbnNext.click()  # accept classification

        dialog.step_kw_field.lstFields.setCurrentRow(0)  # Choose KRB
        self.check_current_text('KRB', dialog.step_kw_field.lstFields)
        dialog.pbnNext.click()  # choose KRB

        # check if in step classify
        self.check_current_step(dialog.step_kw_classify)
        dialog.pbnNext.click()  # accept mapping

        # check if in step extra keywords
        self.check_current_step(dialog.step_kw_inasafe_fields)
        dialog.step_kw_inasafe_fields.cboExtraKeyword1.setCurrentIndex(2)
        dialog.pbnNext.click()  # accept extra keywords

        # check if in step source
        self.check_current_step(dialog.step_kw_source)
        dialog.pbnNext.click()  # accept source

        # check if in step title
        self.check_current_step(dialog.step_kw_title)

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_point_layer(self):
        """Wizard for point layer."""
        layer = clone_shp_layer(
            name='volcano_point',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # choose hazard
        dialog.pbnNext.click()  # choose Multiple event
        dialog.pbnNext.click()  # choose volcano
        dialog.step_kw_layermode.lstLayerModes.setCurrentRow(0)  # choose none
        dialog.pbnNext.click()  # choose none
        # choose NAME
        dialog.step_kw_inasafe_fields.cboExtraKeyword1.setCurrentIndex(4)
        dialog.pbnNext.click()  # choose NAME

        # check if in step source
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnNext.click()  # choose volcano  go to title step

        # check if in step title
        self.check_current_step(dialog.step_kw_title)
        dialog.accept()

    def test_auto_select_one_item(self):
        """Test auto select if there is only one item in a list."""
        layer = clone_shp_layer(
            name='buildings',
            include_keywords=True,
            source_directory=standard_data_path('exposure'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # choose exposure
        self.assertEquals(
            dialog.step_kw_subcategory.lstSubcategories.currentRow(), 2)
        num_item = dialog.step_kw_subcategory.lstSubcategories.count()
        self.assertTrue(num_item == 3)

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_integrated_point(self):
        """Test for point layer and all possibilities."""
        layer = clone_shp_layer(
            name='volcano_point',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        expected_categories = ['Hazard', 'Exposure']
        self.check_list(
            expected_categories, dialog.step_kw_purpose.lstCategories)

        self.select_from_list_widget(
            'Hazard', dialog.step_kw_purpose.lstCategories)

        self.check_current_text('Hazard', dialog.step_kw_purpose.lstCategories)

        dialog.pbnNext.click()  # go to subcategory

        # check if in step subcategory
        self.check_current_step(dialog.step_kw_subcategory)

        expected_subcategories = ['Volcano']
        self.check_list(
            expected_subcategories,
            dialog.step_kw_subcategory.lstSubcategories)

        self.check_current_text(
            'Volcano', dialog.step_kw_subcategory.lstSubcategories)

        dialog.pbnNext.click()  # go to hazard category

        expected_hazard_categories = ['Multiple event', 'Single event']
        self.check_list(
            expected_hazard_categories,
            dialog.step_kw_hazard_category.lstHazardCategories)

        self.check_current_text(
            'Multiple event',
            dialog.step_kw_hazard_category.lstHazardCategories)

        dialog.pbnNext.click()  # go to layer mode

        self.check_current_step(dialog.step_kw_layermode)

        # select the Classified mode
        dialog.step_kw_layermode.lstLayerModes.setCurrentRow(0)

        dialog.pbnNext.click()  # go to extra keywords
        self.check_current_step(dialog.step_kw_inasafe_fields)
        dialog.step_kw_inasafe_fields.cboExtraKeyword1.setCurrentIndex(4)
        expected_field = 'NAME (String)'
        actual_field = dialog.step_kw_inasafe_fields.cboExtraKeyword1.\
            currentText()
        self.assertEqual(actual_field, expected_field)

        dialog.pbnNext.click()  # go to source

        # check if in step source
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnNext.click()  # go to title

        # check if in step title
        self.check_current_step(dialog.step_kw_title)

        dialog.pbnCancel.click()

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_integrated_raster(self):
        """Test for raster layer and all possibilities."""
        layer = clone_raster_layer(
            name='earthquake',
            extension='.tif',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        expected_categories = ['Hazard', 'Exposure']
        self.check_list(
            expected_categories, dialog.step_kw_purpose.lstCategories)

        # check if hazard option is selected
        expected_category = -1
        category_index = dialog.step_kw_purpose.lstCategories.currentRow()
        self.assertEqual(expected_category, category_index)

        # choosing hazard
        self.select_from_list_widget(
            'Hazard', dialog.step_kw_purpose.lstCategories)

        dialog.pbnNext.click()  # Go to subcategory

        # check if in step subcategory
        self.check_current_step(dialog.step_kw_subcategory)

        # check the values of subcategories options
        expected_subcategories = [
            u'Earthquake',
            u'Flood',
            u'Volcanic ash',
            u'Tsunami',
            u'Volcano',
            u'Generic']
        self.check_list(
            expected_subcategories,
            dialog.step_kw_subcategory.lstSubcategories
        )

        # check if no option is selected
        expected_subcategory_index = -1
        subcategory_index = dialog.step_kw_subcategory.lstSubcategories.\
            currentRow()
        self.assertEqual(expected_subcategory_index, subcategory_index)

        # choosing flood
        self.select_from_list_widget(
            'Flood', dialog.step_kw_subcategory.lstSubcategories)

        dialog.pbnNext.click()  # Go to hazard category

        self.check_current_step(dialog.step_kw_hazard_category)
        self.select_from_list_widget(
            'Single event', dialog.step_kw_hazard_category.lstHazardCategories)

        dialog.pbnNext.click()  # Go to layer mode

        # check if in step layer mode
        self.check_current_step(dialog.step_kw_layermode)

        # check the values of subcategories options
        expected_layer_modes = ['Continuous', 'Classified']
        self.check_list(
            expected_layer_modes, dialog.step_kw_layermode.lstLayerModes)

        # check if the default option is selected
        expected_layer_mode = 'Continuous'
        layer_mode = dialog.step_kw_layermode.lstLayerModes.\
            currentItem().text()
        self.assertEqual(expected_layer_mode, layer_mode)

        dialog.pbnNext.click()  # Go to unit

        # check if in step unit
        self.check_current_step(dialog.step_kw_unit)

        # check the values of units options
        expected_units = [u'Feet', u'Metres', u'Generic']
        self.check_list(expected_units, dialog.step_kw_unit.lstUnits)

        # choosing metres
        self.select_from_list_widget('Metres', dialog.step_kw_unit.lstUnits)

        dialog.pbnNext.click()  # Go to source

        # check if in step source
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnBack.click()  # back to step unit
        dialog.pbnBack.click()  # back to step data_type
        dialog.pbnBack.click()  # back to step hazard_category
        dialog.pbnBack.click()  # back to step subcategory

        # check if in step subcategory
        self.check_current_step(dialog.step_kw_subcategory)

        # check if flood is selected
        expected_subcategory = 'Flood'
        subcategory = dialog.step_kw_subcategory.lstSubcategories.\
            currentItem().text()
        self.assertEqual(expected_subcategory, subcategory)

        # choosing earthquake
        self.select_from_list_widget(
            'Earthquake', dialog.step_kw_subcategory.lstSubcategories)

        dialog.pbnNext.click()  # Go to hazard category

        # choosing Single event
        self.select_from_list_widget(
            'Single event', dialog.step_kw_hazard_category.lstHazardCategories)

        dialog.pbnNext.click()  # Go to layer mode

        # check if in step layer mode
        self.check_current_step(dialog.step_kw_layermode)

        # check the values of subcategories options
        expected_layer_modes = ['Continuous', 'Classified']
        self.check_list(
            expected_layer_modes, dialog.step_kw_layermode.lstLayerModes)

        # check if the default option is selected
        expected_layer_mode = 'Continuous'
        layer_mode = dialog.step_kw_layermode.lstLayerModes.currentItem().\
            text()
        self.assertEqual(expected_layer_mode, layer_mode)

        dialog.pbnNext.click()  # Go to unit

        # check if in step unit
        self.check_current_step(dialog.step_kw_unit)

        # check the values of units options
        # Notes, I changed this because this is how the metadata works. We
        # should find another method to filter the unit based on hazard type
        # or change the data test keywords. Ismail.
        expected_units = [u'Generic', u'MMI']
        self.check_list(expected_units, dialog.step_kw_unit.lstUnits)

        # choosing MMI
        self.select_from_list_widget('MMI', dialog.step_kw_unit.lstUnits)

        dialog.pbnNext.click()  # Go to source

        # check if in step source
        self.check_current_step(dialog.step_kw_source)

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_integrated_line(self):
        """Test for line layer and all possibilities."""
        layer = clone_shp_layer(
            name='roads',
            include_keywords=True,
            source_directory=standard_data_path('exposure'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        expected_categories = ['Exposure']
        self.check_list(
            expected_categories, dialog.step_kw_purpose.lstCategories)

        self.check_current_text(
            'Exposure', dialog.step_kw_purpose.lstCategories)

        dialog.pbnNext.click()  # go to subcategory

        # check if in step subcategory
        self.check_current_step(dialog.step_kw_subcategory)

        expected_subcategories = ['Roads']
        self.check_list(
            expected_subcategories,
            dialog.step_kw_subcategory.lstSubcategories
        )

        self.check_current_text(
            'Roads', dialog.step_kw_subcategory.lstSubcategories)

        dialog.pbnNext.click()  # go to laywr mode

        # check if in step layer mode
        self.check_current_step(dialog.step_kw_layermode)

        expected_modes = [
            layer_mode_classified['name'],
            layer_mode_continuous['name']
        ]
        self.check_list(expected_modes, dialog.step_kw_layermode.lstLayerModes)

        self.check_current_text(
            expected_modes[0], dialog.step_kw_layermode.lstLayerModes)

        dialog.pbnNext.click()  # go to fields
        expected_fields = ['NAME', 'OSM_TYPE', 'TYPE']
        self.check_list(expected_fields, dialog.step_kw_field.lstFields)
        self.select_from_list_widget('TYPE', dialog.step_kw_field.lstFields)

        dialog.pbnNext.click()  # go to classify

        # check if in step classify
        self.check_current_step(dialog.step_kw_classify)

        dialog.pbnNext.click()  # go to source

        # check if in step source
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnNext.click()  # go to title step

        dialog.pbnCancel.click()  # cancel

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_integrated_polygon(self):
        """Test for polygon layer and all possibilities."""
        layer = clone_shp_layer(
            name='flood_multipart_polygons',
            source_directory=standard_data_path('hazard'),
            include_keywords=False)
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        expected_categories = ['Hazard', 'Exposure', 'Aggregation']
        self.check_list(
            expected_categories, dialog.step_kw_purpose.lstCategories)

        # choosing exposure
        self.select_from_list_widget(
            'Exposure', dialog.step_kw_purpose.lstCategories)

        dialog.pbnNext.click()  # Go to subcategory

        # check number of subcategories
        expected_subcategories = ['Structures', 'Population', 'Land cover']
        self.check_list(
            expected_subcategories,
            dialog.step_kw_subcategory.lstSubcategories
        )

        # check if automatically select the only option

        self.select_from_list_widget(
            'Structures', dialog.step_kw_subcategory.lstSubcategories)

        self.check_current_text(
            'Structures', dialog.step_kw_subcategory.lstSubcategories)

        dialog.pbnNext.click()  # Go to layer mode

        # check if in step layer mode
        self.check_current_step(dialog.step_kw_layermode)

        # check the values of modes options
        expected_modes = [
            layer_mode_classified['name'],
            layer_mode_continuous['name']
        ]
        self.check_list(expected_modes, dialog.step_kw_layermode.lstLayerModes)

        # choosing classified
        self.select_from_list_widget(
            layer_mode_classified['name'],
            dialog.step_kw_layermode.lstLayerModes)

        dialog.pbnNext.click()  # Go to field

        # check if in step extrakeywords
        self.check_current_step(dialog.step_kw_field)
        self.select_from_list_widget(
            'FLOODPRONE', dialog.step_kw_field.lstFields)

        dialog.pbnNext.click()  # go to classify

        # check if in step classify
        self.check_current_step(dialog.step_kw_classify)

        dialog.pbnNext.click()  # Go to source

        # check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnBack.click()  # back to classify step
        dialog.pbnBack.click()  # back to field step
        dialog.pbnBack.click()  # back to layer_mode step
        dialog.pbnBack.click()  # back to subcategory step
        dialog.pbnBack.click()  # back to category step

        # choosing hazard
        self.select_from_list_widget(
            'Hazard', dialog.step_kw_purpose.lstCategories)
        dialog.pbnNext.click()  # Go to subcategory

        # check the values of subcategories options
        # expected_subcategories = ['flood', 'tsunami']
        # Notes: IS, the generic IF makes the expected sub categories like this
        expected_subcategories = [
            'Flood',
            'Tsunami',
            'Earthquake',
            'Volcano',
            'Volcanic ash',
            'Generic']
        self.check_list(
            expected_subcategories,
            dialog.step_kw_subcategory.lstSubcategories
        )

        # select flood
        self.select_from_list_widget(
            'Flood', dialog.step_kw_subcategory.lstSubcategories)
        dialog.pbnNext.click()  # go to hazard category

        # choosing Single event scenario
        self.select_from_list_widget(
            'Single event', dialog.step_kw_hazard_category.lstHazardCategories)
        dialog.pbnNext.click()  # Go to mode

        # select classified
        self.check_current_step(dialog.step_kw_layermode)
        self.select_from_list_widget(
            layer_mode_classified['name'],
            dialog.step_kw_layermode.lstLayerModes)
        dialog.pbnNext.click()  # go to classifications

        self.check_current_step(dialog.step_kw_classification)

        expected_values = ['Flood classes', 'Generic classes']
        self.check_list(
            expected_values, dialog.step_kw_classification.lstClassifications)
        self.select_from_list_widget(
            'Flood classes', dialog.step_kw_classification.lstClassifications)

        dialog.pbnNext.click()  # go to field

        self.check_current_step(dialog.step_kw_field)
        expected_fields = [
            'OBJECTID',
            'KAB_NAME',
            'KEC_NAME',
            'KEL_NAME',
            'RW',
            'FLOODPRONE']
        self.check_list(expected_fields, dialog.step_kw_field.lstFields)

        # select FLOODPRONE
        self.select_from_list_widget(
            'FLOODPRONE', dialog.step_kw_field.lstFields)

        dialog.pbnNext.click()  # go to classify

        self.check_current_step(dialog.step_kw_classify)

        # check unclassified
        expected_unique_values = []  # no unclassified values
        self.check_list(
            expected_unique_values, dialog.step_kw_classify.lstUniqueValues)

        # check classified
        root = dialog.step_kw_classify.treeClasses.invisibleRootItem()
        expected_classes = ['wet', 'dry']
        child_count = root.childCount()
        self.assertEqual(len(expected_classes), child_count)
        for i in range(child_count):
            item = root.child(i)
            class_name = item.text(0)
            self.assertIn(class_name, expected_classes)
            if class_name == 'wet':
                expected_num_child = 1
                num_child = item.childCount()
                self.assertEqual(expected_num_child, num_child)
            if class_name == 'dry':
                expected_num_child = 1
                num_child = item.childCount()
                self.assertEqual(expected_num_child, num_child)

        dialog.pbnNext.click()  # Go to source
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnBack.click()  # back to classify
        dialog.pbnBack.click()  # back to field
        dialog.pbnBack.click()  # back to classification
        dialog.pbnBack.click()  # back to layer mode
        dialog.pbnBack.click()  # back to hazard category
        dialog.pbnBack.click()  # back to subcategory

        # Currently we don't have any continuous units for polygons to test.
        # self.select_from_list_widget('metres', dialog.step_kw_unit.lstUnits)
        # dialog.pbnNext.click()  # go to field

        # check in field step
        # self.check_current_step(dialog.step_kw_field)

        # check if all options are disabled
        # for i in range(dialog.step_kw_field.lstFields.count()):
        #    item_flag = dialog.step_kw_field.lstFields.item(i).flags()
        #    self.assertTrue(item_flag & ~QtCore.Qt.ItemIsEnabled)

        # dialog.pbnBack.click()  # back to unit
        # dialog.pbnBack.click()  # back to subcategory

        # self.select_from_list_widget(
        # 'tsunami', dialog.step_kw_subcategory.lstSubcategories)
        # dialog.pbnNext.click()  # go to unit
        # self.check_current_step(dialog.step_kw_unit)

        # back again since tsunami similar to flood
        # dialog.pbnBack.click()  # back to subcategory

        self.check_current_step(dialog.step_kw_subcategory)
        self.select_from_list_widget(
            'Volcano', dialog.step_kw_subcategory.lstSubcategories)
        dialog.pbnNext.click()  # go to hazard category

        self.check_current_step(dialog.step_kw_hazard_category)
        self.select_from_list_widget(
            'Multiple event',
            dialog.step_kw_hazard_category.lstHazardCategories)
        dialog.pbnNext.click()  # go to mode

        self.check_current_step(dialog.step_kw_layermode)
        self.select_from_list_widget(
            'Classified', dialog.step_kw_layermode.lstLayerModes)
        dialog.pbnNext.click()  # go to classifications

        self.check_current_step(dialog.step_kw_classification)
        self.select_from_list_widget(
            'Volcano classes',
            dialog.step_kw_classification.lstClassifications)
        dialog.pbnNext.click()  # go to field

        self.check_current_step(dialog.step_kw_field)
        self.select_from_list_widget(
            'FLOODPRONE', dialog.step_kw_field.lstFields)
        dialog.pbnNext.click()  # go to classify

        self.check_current_step(dialog.step_kw_classify)

        # check unclassified
        expected_unique_values = ['NO', 'YES']  # Unclassified value
        self.check_list(
            expected_unique_values, dialog.step_kw_classify.lstUniqueValues)

        # check classified
        root = dialog.step_kw_classify.treeClasses.invisibleRootItem()
        expected_classes = [
            'Low Hazard Zone',
            'Medium Hazard Zone',
            'High Hazard Zone'
        ]
        child_count = root.childCount()
        self.assertEqual(len(expected_classes), child_count)
        for i in range(child_count):
            item = root.child(i)
            class_name = item.text(0)
            self.assertIn(class_name, expected_classes)
            expected_num_child = 0
            num_child = item.childCount()
            self.assertEqual(expected_num_child, num_child)

        dialog.pbnNext.click()  # go to extra keywords
        self.check_current_step(dialog.step_kw_inasafe_fields)
        dialog.step_kw_inasafe_fields.cboExtraKeyword1.setCurrentIndex(5)
        dialog.step_kw_inasafe_fields.cboExtraKeyword2.setCurrentIndex(1)

        dialog.pbnNext.click()  # go to source
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnCancel.click()

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_allow_resample(self):
        """Test the allow resample step"""

        # Initialize dialog
        layer = clone_raster_layer(
            name='people_allow_resampling_false',
            extension='.tif',
            include_keywords=False,
            source_directory=standard_data_path('exposure'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)
        dialog.suppress_warning_dialog = True

        # step_kw_purpose
        self.check_current_step(dialog.step_kw_purpose)
        self.select_from_list_widget(
            'Exposure', dialog.step_kw_purpose.lstCategories)
        dialog.pbnNext.click()

        # step_kw_subcategory
        self.check_current_step(dialog.step_kw_subcategory)
        self.select_from_list_widget(
            'Population', dialog.step_kw_subcategory.lstSubcategories)
        dialog.pbnNext.click()

        # step_kw_layermode
        self.check_current_step(dialog.step_kw_layermode)
        self.select_from_list_widget(
            'Continuous', dialog.step_kw_layermode.lstLayerModes)
        dialog.pbnNext.click()

        # step_kw_unit
        self.check_current_step(dialog.step_kw_unit)
        self.select_from_list_widget('Count', dialog.step_kw_unit.lstUnits)
        dialog.pbnNext.click()

        # step_kw_resample
        self.check_current_step(dialog.step_kw_resample)
        dialog.step_kw_resample.chkAllowResample.setChecked(True)
        dialog.pbnNext.click()

        # step_kw_source
        self.check_current_step(dialog.step_kw_source)
        dialog.pbnNext.click()

        # step_kw_title
        self.check_current_step(dialog.step_kw_title)
        dialog.pbnNext.click()

        # step_kw_summary
        self.check_current_step(dialog.step_kw_summary)
        dialog.pbnNext.click()

if __name__ == '__main__':
    suite = unittest.makeSuite(TestKeywordWizard)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
