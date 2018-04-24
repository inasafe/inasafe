# coding=utf-8

"""Tests for the keyword wizard."""


import shutil
import unittest
import os
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
from datetime import datetime
from safe.definitions.constants import big_number
from safe.definitions.layer_modes import (
    layer_mode_continuous, layer_mode_classified)
from safe.definitions.layer_purposes import (
    layer_purpose_hazard, layer_purpose_exposure, layer_purpose_aggregation)
from safe.definitions.hazard import (
    hazard_volcano, hazard_flood, hazard_earthquake, hazard_cyclone)
from safe.definitions.exposure import (
    exposure_structure,
    exposure_population,
    exposure_land_cover,
    exposure_place,
)
from safe.definitions.hazard_category import hazard_category_multiple_event
from safe.definitions.hazard_classifications import (
    flood_hazard_classes,
    volcano_hazard_classes,
    cyclone_au_bom_hazard_classes,
    earthquake_mmi_scale)
from safe.definitions.constants import no_field
from safe.definitions.extra_keywords import (extra_keyword_earthquake_depth)
from safe.definitions.fields import (
    aggregation_name_field,
    exposure_type_field,
    hazard_name_field,
    hazard_value_field,
    population_count_field,
    female_count_field,
)
from safe.definitions.layer_geometry import (
    layer_geometry_polygon, layer_geometry_raster, layer_geometry_point)
from safe.definitions.exposure_classifications import (
    generic_structure_classes, generic_place_classes)
from safe.definitions.units import (
    count_exposure_unit, unit_metres, unit_mmi, unit_kilometres_per_hour)
from safe.gui.tools.wizard.wizard_dialog import WizardDialog
from safe.definitions.utilities import (
    get_compulsory_fields, default_classification_thresholds)
from safe.utilities.str import byteify

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# Some default values for testing
source = 'Source'
source_scale = 'Source Scale'
source_url = 'Source Url'
source_date = datetime.strptime('06-12-2015', '%d-%m-%Y')
source_license = 'Source License'
layer_title = 'Layer Title'


# noinspection PyTypeChecker
class TestKeywordWizard(unittest.TestCase):

    """Test the InaSAFE keyword wizard GUI."""

    maxDiff = None

    def tearDown(self):
        """Run after each test."""
        # Remove the mess that we made on each test
        try:
            shutil.rmtree(temp_dir(sub_dir='test'))
        except BaseException:
            pass

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
        """Helper function to check the current step is expected_step.

        :param expected_step: The expected current step.
        :type expected_step: WizardStep instance
        """
        current_step = expected_step.parent.get_current_step()
        message = 'Should be step %s but it got %s' % (
            expected_step.__class__.__name__, current_step.__class__.__name__)
        self.assertEqual(expected_step, current_step, message)

    def check_current_text(self, expected_text, list_widget):
        """Check the current text in list widget is expected_text.

        :param expected_text: The expected current step.
        :type expected_text: str

        :param list_widget: List widget that wants to be checked.
        :type list_widget: QListWidget
        """
        try:
            selected_items = list_widget.selectedItems()
            selected_texts = [item.text() for item in selected_items]
            if isinstance(expected_text, str):
                expected_text = [expected_text]
                self.assertListEqual(expected_text, selected_texts)
        except AttributeError:
            options = [
                list_widget.item(i).text()
                for i in range(list_widget.count())
            ]
            message = 'There is no %s in the available option %s' % (
                expected_text, options)
            self.assertFalse(True, message)

    # noinspection PyUnresolvedReferences
    @staticmethod
    def select_from_list_widget(option, list_widget):
        """Helper function to select option from list_widget.

        :param option: Option to be chosen.
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
            'There is no %s in the list widget. The available options are '
            '%s' % (option, available_options))

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
        dialog = WizardDialog(iface=IFACE)
        # It shouldn't raise any exception although the xml is invalid
        dialog.set_keywords_creation_mode(layer)

    def test_hazard_without_inasafe_fields(self):
        """Test keyword wizard for layer without inasafe fields."""
        # cloning layer that has no inasafe fields
        layer = load_test_vector_layer(
            'hazard', 'classified_generic_polygon.shp', clone=True)

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.set_keywords_creation_mode(layer)

        # check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Select hazard
        self.select_from_list_widget(
            layer_purpose_hazard['name'], dialog.step_kw_purpose.lstCategories)

        # Click next to select hazard
        dialog.pbnNext.click()

        # Check if in select hazard step
        self.check_current_step(dialog.step_kw_subcategory)

        # select earthquake
        self.select_from_list_widget(
            hazard_earthquake['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select earthquake
        dialog.pbnNext.click()

        # Check if in select hazard category step
        self.check_current_step(dialog.step_kw_hazard_category)

        # select multiple event
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

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # select h_zone field
        self.select_from_list_widget(
            'h_zone',
            dialog.step_kw_field.lstFields)

        # Click next to select h_zone
        dialog.pbnNext.click()

        # Check if in multi classification step
        self.check_current_step(dialog.step_kw_multi_classifications)

        # Click next to finish multi classifications step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        # Fill source form
        dialog.step_kw_source.leSource.setText(source)
        dialog.step_kw_source.leSource_scale.setText(source_scale)
        dialog.step_kw_source.leSource_url.setText(source_url)
        dialog.step_kw_source.ckbSource_date.setChecked(True)
        dialog.step_kw_source.dtSource_date.setDateTime(source_date)
        dialog.step_kw_source.leSource_license.setText(source_license)

        # Click next to finish source step and go to extra keywords step
        dialog.pbnNext.click()

        # Check if in extra keywords step
        self.check_current_step(dialog.step_kw_extra_keywords)

        self.assertTrue(dialog.step_kw_extra_keywords.widgets_dict)

        # Click next to finish extra keywords step and go to title step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_title)

        # Fill title form
        dialog.step_kw_title.leTitle.setText(layer_title)

        # Click next to finish title step and go to summary step
        dialog.pbnNext.click()

        # Check if in summary step
        self.check_current_step(dialog.step_kw_summary)

        # Click finish
        dialog.pbnNext.click()

        # Checking keyword created
        expected_keyword = {
            'scale': source_scale,
            'hazard_category': hazard_category_multiple_event['key'],
            'license': source_license,
            'source': source,
            'url': source_url,
            'title': layer_title,
            'hazard': hazard_earthquake['key'],
            'inasafe_fields':
                {hazard_value_field['key']: 'h_zone'},
            'value_maps': layer.keywords['value_maps'],
            'date': source_date,
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'layer_mode': layer_mode_classified['key']
        }

        real_keywords = dialog.get_keywords()
        self.assertDictEqual(real_keywords, expected_keyword)

    def test_aggregation_without_inasafe_fields(self):
        """Test keyword wizard for layer without inasafe fields."""
        layer = load_test_vector_layer(
            'aggregation', 'district_osm_jakarta.geojson', clone=True)

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.set_keywords_creation_mode(layer)

        # check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Check aggregation
        self.check_current_text(
            layer_purpose_aggregation['name'],
            dialog.step_kw_purpose.lstCategories)

        # Click next
        dialog.pbnNext.click()

        # check if in step field
        self.check_current_step(dialog.step_kw_field)

        # Check aggregation
        self.check_current_text(
            layer.keywords['inasafe_fields']['aggregation_name_field'],
            dialog.step_kw_field.lstFields)

        # Click next
        dialog.pbnNext.click()

        # Check field mapping steps
        self.check_current_step(dialog.step_kw_fields_mapping)

        # Click next to continue
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        # Click next
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_title)

        # Click next
        dialog.pbnNext.click()

        # Check if in summary step
        self.check_current_step(dialog.step_kw_summary)

        # Click next
        dialog.pbnNext.click()

    def test_hazard_volcano_polygon_keyword(self):
        """Test keyword wizard for volcano hazard polygon."""
        layer = clone_shp_layer(
            name='volcano_krb',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
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

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # select KRB field
        self.select_from_list_widget('KRB', dialog.step_kw_field.lstFields)

        # Click next to select KRB
        dialog.pbnNext.click()

        # Check if in multi classification step
        self.check_current_step(dialog.step_kw_multi_classifications)

        # Change combo box
        dialog.step_kw_multi_classifications.exposure_combo_boxes[
            0].setCurrentIndex(1)

        # Click save
        dialog.step_kw_multi_classifications.save_button.click()

        # Click next to finish multi classifications step
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

        # Click next to finish InaSAFE Field step and go to source step
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

        # Check if in summary step
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
                    hazard_value_field['key']: 'KRB',
                    hazard_name_field['key']: 'volcano',
            },
            'value_maps': {
                exposure_land_cover['key']: {
                    volcano_hazard_classes['key']: {
                        'active': True,
                        'classes': {
                            'high': ['Kawasan Rawan Bencana III'],
                            'low': ['Kawasan Rawan Bencana I'],
                            'medium': ['Kawasan Rawan Bencana II']
                        }
                    }
                }
            },
            'date': source_date,
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'layer_mode': layer_mode_classified['key']
        }

        real_keywords = dialog.get_keywords()
        self.assertDictEqual(real_keywords, expected_keyword)

    def test_hazard_volcano_polygon_existing_keywords(self):
        """Test existing keyword for hazard volcano polygon."""
        layer = load_test_vector_layer(
            'hazard', 'volcano_krb.shp', clone=True)

        default_classes = {
            'high': ['Kawasan Rawan Bencana III'],
            'low': ['Kawasan Rawan Bencana I'],
            'medium': ['Kawasan Rawan Bencana II']
        }
        keywords = {
            'hazard': hazard_volcano['key'],
            'hazard_category': hazard_category_multiple_event['key'],
            'inasafe_fields': {
                hazard_name_field['key']: 'volcano',
                hazard_value_field['key']: 'KRB'
            },
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_mode': layer_mode_classified['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'title': 'Volcano KRB',
            'value_maps': {
                exposure_land_cover['key']: {
                    volcano_hazard_classes['key']: {
                        'active': True,
                        'classes': default_classes
                    }
                },
                'population': {
                    'volcano_hazard_classes': {
                        'active': True,
                        'classes': default_classes
                    }
                },
                'road': {
                    'volcano_hazard_classes': {
                        'active': True,
                        'classes': default_classes
                    }
                },
                'structure': {
                    'volcano_hazard_classes': {
                        'active': True,
                        'classes': default_classes
                    }
                }
            }
        }

        layer.keywords = keywords

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.set_keywords_creation_mode(layer, keywords)

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

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # Check if KRB is selected
        self.check_current_text('KRB', dialog.step_kw_field.lstFields)

        # Click next to select KRB
        dialog.pbnNext.click()

        # Check if in select classification step
        self.check_current_step(dialog.step_kw_multi_classifications)

        # Click next to finish multi classifications step
        dialog.pbnNext.click()

        # select additional keywords / inasafe fields step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Check inasafe fields
        parameters = dialog.step_kw_inasafe_fields. \
            parameter_container.get_parameters(True)

        # Get layer's inasafe_fields
        inasafe_fields = layer.keywords.get('inasafe_fields')
        self.assertIsNotNone(inasafe_fields)
        for key, value in list(inasafe_fields.items()):
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
                self.assertNotIn(parameter.guid, list(inasafe_fields.keys()))
            # If not available is not chosen, inasafe_fields should have it
            else:
                self.assertIn(parameter.guid, list(inasafe_fields.keys()))

        # Click next to finish inasafe fields step and go to source step
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
            keywords['value_maps'], dialog.get_keywords()['value_maps'])

        self.assertDictEqual(keywords, dialog.get_keywords())

    def test_exposure_structure_polygon_keyword(self):
        """Test keyword wizard for exposure structure polygon."""
        layer = clone_shp_layer(
            name='buildings',
            include_keywords=False,
            source_directory=standard_data_path('exposure'))
        self.assertIsNotNone(layer)

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.qsettings = None
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

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # select TYPE field
        self.select_from_list_widget(
            'TYPE', dialog.step_kw_field.lstFields)

        # Click next to select TYPE
        dialog.pbnNext.click()

        # Check if in select classification step
        self.check_current_step(dialog.step_kw_classification)

        # select generic structure classes classification
        self.select_from_list_widget(
            generic_structure_classes['name'],
            dialog.step_kw_classification.lstClassifications)

        # Click next to select the classifications
        dialog.pbnNext.click()

        # Check if in classify step
        self.check_current_step(dialog.step_kw_classify)

        default_classes = generic_structure_classes['classes']
        unassigned_values = []  # no need to check actually, not save in file
        assigned_values = {
            'residential': ['Residential'],
            'education': ['School'],
            'health': ['Clinic/Doctor'],
            'transport': [],
            'place of worship': ['Place of Worship - Islam'],
            'government': ['Government'],
            'commercial': ['Commercial', 'Industrial'],
            'recreation': [],
            'public facility': [],
            'evacuation centre': [],
            'other': []
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
        # This step is disabled until we activate again value/rate fields.
        # self.check_current_step(dialog.step_kw_default_inasafe_fields)

        # Click next to finish InaSAFE Default Field step and go to source step
        # dialog.pbnNext.click()

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
            'inasafe_fields': {
                exposure_type_field['key']: 'TYPE',
            },
            'value_map': dict(
                (k,
                 v) for k,
                v in list(
                    assigned_values.items()) if v),
            'date': source_date,
            'classification': generic_structure_classes['key'],
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_exposure['key'],
            'layer_mode': layer_mode_classified['key']}

        real_keywords = dialog.get_keywords()

        self.assertDictEqual(real_keywords, expected_keyword)

    def test_exposure_structure_polygon_existing_keywords(self):
        """Test existing keyword for exposure structure polygon."""
        layer = load_test_vector_layer(
            'exposure', 'buildings.shp', clone=True)
        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
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

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # Check if TYPE is selected
        self.check_current_text('TYPE', dialog.step_kw_field.lstFields)

        # Click next to select TYPE
        dialog.pbnNext.click()

        # Check if in select classification step
        self.check_current_step(dialog.step_kw_classification)

        # Check if generic structure classes is selected.
        self.check_current_text(
            generic_structure_classes['name'],
            dialog.step_kw_classification.lstClassifications)

        # Click next to select the classifications
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
        for key, value in list(inasafe_fields.items()):
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
                self.assertNotIn(parameter.guid, list(inasafe_fields.keys()))
            # If not available is not chosen, inasafe_fields should have it
            else:
                self.assertIn(parameter.guid, list(inasafe_fields.keys()))

        # Click next to finish inasafe fields step and go to inasafe default
        # field step
        dialog.pbnNext.click()

        # Check if in InaSAFE Default field step
        # This step is disabled until we activate again value/rate fields.
        # self.check_current_step(dialog.step_kw_default_inasafe_fields)

        # Click next to finish InaSAFE Default Field step and go to source step
        # dialog.pbnNext.click()

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
        """Test Aggregation Keywords."""
        layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson', clone_to_memory=True)
        layer.keywords = {}

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
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

        # Check field mapping steps
        self.check_current_step(dialog.step_kw_fields_mapping)

        # Click next to continue
        dialog.pbnNext.click()

        # select inasafe fields step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Check behaviour
        self.check_radio_button_behaviour(
            dialog.step_kw_default_inasafe_fields)

        # Click next to finish inasafe fields step and go to source step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

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

        expected_keyword = {
            'inasafe_fields': {aggregation_name_field['key']: area_name},
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_aggregation['key'],
            'title': layer_title
        }
        # Check the keywords
        real_keywords = dialog.get_keywords()
        self.assertDictEqual(real_keywords, expected_keyword)

    def test_aggregation_existing_keyword(self):
        """Test Keyword wizard for aggregation layer with keywords."""
        layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson', clone_to_memory=True)

        area_name = 'area_name'
        expected_keyword = {
            'inasafe_fields': {aggregation_name_field['key']: area_name},
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_aggregation['key'],
            'title': layer_title
        }

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.set_keywords_creation_mode(layer, expected_keyword)

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

        # Check field mapping steps
        self.check_current_step(dialog.step_kw_fields_mapping)

        # Click next to continue
        dialog.pbnNext.click()

        # Check inasafe fields step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Check behaviour
        self.check_radio_button_behaviour(
            dialog.step_kw_default_inasafe_fields)

        # Click next to finish inasafe fields step and go to source step
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
        """Test exposure population polygon keyword."""
        layer = load_test_vector_layer(
            'exposure', 'census.geojson', clone_to_memory=True)
        layer.keywords = {}

        self.assertIsNotNone(layer)

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
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

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # select population field
        population_field = 'population'
        self.select_from_list_widget(
            population_field, dialog.step_kw_field.lstFields)

        # Click next to select population
        dialog.pbnNext.click()

        # Check field mapping steps
        self.check_current_step(dialog.step_kw_fields_mapping)

        # Click next to continue
        dialog.pbnNext.click()

        # Check if in InaSAFE field step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Click next to finish InaSAFE Field step and go to source step
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
                    population_count_field['key']: ['population'],
            },
            'date': source_date,
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_exposure['key'],
            'layer_mode': layer_mode_continuous['key']
        }

        real_keywords = dialog.get_keywords()

        self.assertDictEqual(real_keywords, expected_keyword)

    def test_exposure_population_polygon_existing_keyword(self):
        """Test existing exposure population polygon with keyword."""
        layer = load_test_vector_layer(
            'exposure', 'census.geojson', clone_to_memory=True)
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
                    # Dummy, select more than fields to show we can do it.
                    population_count_field['key']: ['population', 'id'],
            },
            'date': source_date,
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_exposure['key'],
            'layer_mode': layer_mode_continuous['key']
        }

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.set_keywords_creation_mode(layer, expected_keyword)

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
        population_field = expected_keyword['inasafe_fields'][
            population_count_field['key']]
        self.check_current_text(
            population_field, dialog.step_kw_field.lstFields)

        # Click next to select population
        dialog.pbnNext.click()

        # Check field mapping steps
        self.check_current_step(dialog.step_kw_fields_mapping)

        # Click next to continue
        dialog.pbnNext.click()

        # Check if in InaSAFE field step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Click next to finish inasafe fields step and go to source step
        # field step
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

    def test_exposure_population_raster(self):
        """Test keyword wizard for population raster."""
        path = standard_data_path(
            'exposure', 'people_allow_resampling_true.tif')
        message = "Path %s is not found" % path
        self.assertTrue(os.path.exists(path), message)
        layer = clone_raster_layer(
            name='people_allow_resampling_true',
            extension='.tif',
            include_keywords=False,
            source_directory=standard_data_path('exposure'))
        self.assertIsNotNone(layer)
        layer.keywords = {}

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
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

        # Check if in select band step
        self.check_current_step(dialog.step_kw_band_selector)

        # Click next to select Band 1 (default)
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

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        # Click next to finish source step and go to title step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_title)

        # Click next to finish title step and go to kw summary step
        dialog.pbnNext.click()

        # Check if in title step
        self.check_current_step(dialog.step_kw_summary)

        # Click finish
        dialog.pbnNext.click()

        real_keywords = dialog.get_keywords()

        self.assertEqual(1, real_keywords['active_band'])

    def test_clean_keyword_wizard(self):
        """Test for having the clean state when we run keyword wizard."""
        layer = load_test_vector_layer(
            'gisv4',
            'exposure',
            'population_multi_fields.geojson',
            clone_to_memory=True)
        self.assertIsNotNone(layer)
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
                    # Dummy, select more than fields to show we can do it.
                    population_count_field['key']: [
                        'right_hand',
                        'left_hand'
                    ],
                    female_count_field['key']: [
                        'F_0_4',
                        'F_5_9',
                        'F_9_15',
                        'F_15_30',
                        'F_30_60',
                        'F_60_100'
                    ]

            },
            'date': source_date,
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_exposure['key'],
            'layer_mode': layer_mode_continuous['key']
        }
        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.set_keywords_creation_mode(layer, expected_keyword)

        # Check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Click next to select exposure
        dialog.pbnNext.click()

        # Click next to select population
        dialog.pbnNext.click()

        # Click next to select continuous
        dialog.pbnNext.click()

        # Click next to select count
        dialog.pbnNext.click()

        # Click next to select population
        dialog.pbnNext.click()

        # Click next to continue
        dialog.pbnNext.click()

        # Click next to finish inasafe fields step and go to source step
        # field step
        dialog.pbnNext.click()

        # Click next to finish source step and go to title step
        dialog.pbnNext.click()

        # Click next to finish title step and go to kw summary step
        dialog.pbnNext.click()

        # Check if in summary step
        self.check_current_step(dialog.step_kw_summary)

        # Click finish
        dialog.pbnNext.click()

        # Checking Keyword Created
        real_keywords = dialog.get_keywords()

        self.assertDictEqual(byteify(real_keywords), byteify(expected_keyword))

        # Now we try to use the same dialog object for assigning another layer.
        # This is replication of #4200

        hazard_layer = load_test_vector_layer(
            'hazard', 'volcano_krb.shp', clone=True)

        hazard_expected_keyword = {
            'scale': source_scale,
            'hazard_category': hazard_category_multiple_event['key'],
            'license': source_license,
            'source': source,
            'url': source_url,
            'title': layer_title,
            'hazard': hazard_volcano['key'],
            'inasafe_fields':
                {
                    hazard_value_field['key']: 'KRB',
                    hazard_name_field['key']: 'volcano',
            },
            'value_maps': {
                exposure_land_cover['key']: {
                    volcano_hazard_classes['key']: {
                        'active': True,
                        'classes': {
                            'high': ['Kawasan Rawan Bencana III'],
                            'low': ['Kawasan Rawan Bencana I'],
                            'medium': ['Kawasan Rawan Bencana II']
                        }
                    }
                }
            },
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'layer_mode': layer_mode_classified['key']
        }

        # noinspection PyTypeChecker
        dialog.set_keywords_creation_mode(
            hazard_layer, hazard_expected_keyword)

        # Click next to select hazard
        dialog.pbnNext.click()

        # Click next to select volcano
        dialog.pbnNext.click()

        # Click next to select multiple event
        dialog.pbnNext.click()

        # Click next to select classified
        dialog.pbnNext.click()

        # Click next to select KRB
        dialog.pbnNext.click()

        # Click next to finish multi classifications step
        dialog.pbnNext.click()

        # Click next to finish InaSAFE Field step and go to source step
        dialog.pbnNext.click()

        # Click next to finish source step and go to title step
        dialog.pbnNext.click()

        # Click next to finish title step and go to kw summary step
        dialog.pbnNext.click()

        # Check if in summary step
        self.check_current_step(dialog.step_kw_summary)

        # Click finish
        dialog.pbnNext.click()

        real_keywords = dialog.get_keywords()
        self.assertDictEqual(hazard_expected_keyword, real_keywords)

    def test_exposure_multi_fields_existing_keyword(self):
        """Test for exposure layer with multiple fields."""
        layer = load_test_vector_layer(
            'gisv4',
            'exposure',
            'population_multi_fields.geojson',
            clone_to_memory=True)
        self.assertIsNotNone(layer)
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
                    # Dummy, select more than fields to show we can do it.
                    population_count_field['key']: [
                        'right_hand',
                        'left_hand'
                    ],
                    female_count_field['key']: [
                        'F_0_4',
                        'F_5_9',
                        'F_9_15',
                        'F_15_30',
                        'F_30_60',
                        'F_60_100'
                    ]

            },
            'date': source_date,
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_purpose': layer_purpose_exposure['key'],
            'layer_mode': layer_mode_continuous['key']
        }
        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.set_keywords_creation_mode(layer, expected_keyword)

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

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # Check if population field is selected
        population_field = expected_keyword['inasafe_fields'][
            population_count_field['key']]
        self.check_current_text(
            population_field, dialog.step_kw_field.lstFields)

        # Click next to select population field
        dialog.pbnNext.click()

        # Check field mapping steps
        self.check_current_step(dialog.step_kw_fields_mapping)

        # Click next to continue
        dialog.pbnNext.click()

        # Check if in InaSAFE field step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        # Click next to finish inasafe fields step and go to source step
        # field step
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

        self.assertDictEqual(byteify(real_keywords), byteify(expected_keyword))

    def test_exposure_place_population(self):
        """Test for place with population exposure."""
        layer = load_test_vector_layer(
            'gisv4',
            'exposure',
            'places.geojson',
            clone_to_memory=True)
        self.assertIsNotNone(layer)

        expected_keyword = {
            'scale': source_scale,
            'license': source_license,
            'source': source,
            'url': source_url,
            'title': layer_title,
            'exposure': exposure_place['key'],
            'inasafe_fields':
                {
                    exposure_type_field['key']: 'Type',
                    population_count_field['key']: 'Population',
            },
            'date': source_date,
            'layer_geometry': layer_geometry_point['key'],
            'layer_purpose': layer_purpose_exposure['key'],
            'layer_mode': layer_mode_classified['key'],
            'classification': generic_place_classes['key'],
        }

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.set_keywords_creation_mode(layer, expected_keyword)

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

        # Check if place is selected
        self.check_current_text(
            exposure_place['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select place
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # Check if classified is selected
        self.check_current_text(
            layer_mode_classified['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select classified
        dialog.pbnNext.click()

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # Check if place type field is selected
        place_type_field = expected_keyword['inasafe_fields'][
            exposure_type_field['key']]
        self.check_current_text(
            place_type_field, dialog.step_kw_field.lstFields)

        # Click next to select place type field
        dialog.pbnNext.click()

        # Check if in select classification step
        self.check_current_step(dialog.step_kw_classification)

        # Check if generic structure classes is selected.
        self.check_current_text(
            generic_place_classes['name'],
            dialog.step_kw_classification.lstClassifications)

        # Click next to select the classifications
        dialog.pbnNext.click()

        # Check if in classify step
        self.check_current_step(dialog.step_kw_classify)

        # Click next to finish value mapping
        dialog.pbnNext.click()

        # select additional keywords / inasafe fields step
        self.check_current_step(dialog.step_kw_inasafe_fields)

        current_inasafe_field = dialog.step_kw_inasafe_fields.\
            get_inasafe_fields()

        population_field = current_inasafe_field.get(
            population_count_field['key'])

        expected_population_field = expected_keyword['inasafe_fields'][
            population_count_field['key']]

        # Check if the population field is set.
        self.assertEqual(population_field, expected_population_field)

        # Click next to finish set the InaSAFE fields
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

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

        self.assertDictEqual(byteify(real_keywords), byteify(expected_keyword))

    def test_classified_raster_keywords(self):
        """Test keyword wizard for classified raster."""
        path = standard_data_path('hazard', 'classified_flood_20_20.asc')
        message = "Path %s is not found" % path
        self.assertTrue(os.path.exists(path), message)
        layer = clone_raster_layer(
            name='classified_flood_20_20',
            extension='.asc',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))
        self.assertIsNotNone(layer)
        layer.keywords = {}

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
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

        # select flood
        self.select_from_list_widget(
            hazard_flood['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select flood
        dialog.pbnNext.click()

        # Check if in select hazard category step
        self.check_current_step(dialog.step_kw_hazard_category)

        # select multiple_event
        self.select_from_list_widget(
            hazard_category_multiple_event['name'],
            dialog.step_kw_hazard_category.lstHazardCategories)

        # Click next to select multiple event
        dialog.pbnNext.click()

        # Check if in select band step
        self.check_current_step(dialog.step_kw_band_selector)

        # Click next to select Band 1 (default)
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # select classified mode
        self.select_from_list_widget(
            layer_mode_classified['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select classified
        dialog.pbnNext.click()

        # Check if in multi classification step
        self.check_current_step(dialog.step_kw_multi_classifications)

        # Change combo box
        dialog.step_kw_multi_classifications.exposure_combo_boxes[
            0].setCurrentIndex(1)

        # Click save
        dialog.step_kw_multi_classifications.save_button.click()

        # Click next to finish multi classifications step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.step_kw_source.leSource.setText(source)
        dialog.step_kw_source.leSource_scale.setText(source_scale)
        dialog.step_kw_source.leSource_url.setText(source_url)
        dialog.step_kw_source.ckbSource_date.setChecked(True)
        dialog.step_kw_source.dtSource_date.setDateTime(source_date)
        dialog.step_kw_source.leSource_license.setText(source_license)

        # Click next to finish source step and go to extra keywords step
        dialog.pbnNext.click()

        self.check_current_step(dialog.step_kw_extra_keywords)

        # Click next to finish extra keywords step and go to title step
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
            'active_band': 1,
            'scale': source_scale,
            'hazard_category': hazard_category_multiple_event['key'],
            'license': source_license,
            'source': source,
            'url': source_url,
            'title': layer_title,
            'hazard': hazard_flood['key'],
            'date': source_date,
            'layer_geometry': layer_geometry_raster['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'layer_mode': layer_mode_classified['key'],
            'value_maps': {
                exposure_land_cover['key']: {
                    flood_hazard_classes['key']: {
                        'active': True,
                        'classes': {
                            'wet': [1.0, 2.0, 3.0]
                        }
                    }
                }
            }
        }

        real_keywords = dialog.get_keywords()
        self.assertDictEqual(real_keywords, expected_keyword)

    def test_classified_raster_existing_keywords(self):
        """Test keyword wizard for existing keywords classified raster."""
        layer = clone_raster_layer(
            name='classified_flood_20_20',
            extension='.asc',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))
        self.assertIsNotNone(layer)

        expected_keyword = {
            'active_band': 1,
            'scale': source_scale,
            'hazard_category': hazard_category_multiple_event['key'],
            'license': source_license,
            'source': source,
            'url': source_url,
            'title': layer_title,
            'hazard': hazard_flood['key'],
            'value_maps': {},
            'date': source_date,
            'layer_geometry': layer_geometry_raster['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'layer_mode': layer_mode_classified['key']
        }

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.set_keywords_creation_mode(layer, expected_keyword)

        # Check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Check if hazard is selected
        self.check_current_text(
            layer_purpose_hazard['name'], dialog.step_kw_purpose.lstCategories)

        # Click next to select hazard
        dialog.pbnNext.click()

        # Check if in select hazard step
        self.check_current_step(dialog.step_kw_subcategory)

        # Check if flood is selected
        self.check_current_text(
            hazard_flood['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select flood
        dialog.pbnNext.click()

        # Check if in select hazard category step
        self.check_current_step(dialog.step_kw_hazard_category)

        # Check if multiple event is selected
        self.check_current_text(
            hazard_category_multiple_event['name'],
            dialog.step_kw_hazard_category.lstHazardCategories)

        # Click next to select multiple event
        dialog.pbnNext.click()

        # Check if in select band step
        self.check_current_step(dialog.step_kw_band_selector)

        # Click next to select Band 1 (default)
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
        self.check_current_step(dialog.step_kw_multi_classifications)

        # Change combo box
        dialog.step_kw_multi_classifications.exposure_combo_boxes[
            0].setCurrentIndex(1)

        # Click save
        dialog.step_kw_multi_classifications.save_button.click()

        # Click next to finish multi classifications step
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

        # Click next to finish source step and go to extra keywords step
        dialog.pbnNext.click()

        self.check_current_step(dialog.step_kw_extra_keywords)

        # Click next to finish extra keywords step and go to title step
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

    def test_continuous_raster_keywords(self):
        """Test keyword wizard for continuous raster."""
        path = standard_data_path('hazard', 'continuous_flood_20_20.asc')
        message = "Path %s is not found" % path
        self.assertTrue(os.path.exists(path), message)
        layer = clone_raster_layer(
            name='continuous_flood_20_20',
            extension='.asc',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))
        self.assertIsNotNone(layer)
        layer.keywords = {}

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
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

        # select flood
        self.select_from_list_widget(
            hazard_flood['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select flood
        dialog.pbnNext.click()

        # Check if in select hazard category step
        self.check_current_step(dialog.step_kw_hazard_category)

        # select multiple_event
        self.select_from_list_widget(
            hazard_category_multiple_event['name'],
            dialog.step_kw_hazard_category.lstHazardCategories)

        # Click next to select multiple event
        dialog.pbnNext.click()

        # Check if in select band step
        self.check_current_step(dialog.step_kw_band_selector)

        # Click next to select Band 1 (default)
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # select continuous mode
        self.select_from_list_widget(
            layer_mode_continuous['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select continuous
        dialog.pbnNext.click()

        # Check if in select unit step
        self.check_current_step(dialog.step_kw_unit)

        # select unit metres
        self.select_from_list_widget(
            unit_metres['name'],
            dialog.step_kw_unit.lstUnits)

        # Click next to select unit metres
        dialog.pbnNext.click()

        # Check if in select multi classifications step
        self.check_current_step(dialog.step_kw_multi_classifications)

        # Change combo box
        dialog.step_kw_multi_classifications.exposure_combo_boxes[
            0].setCurrentIndex(1)

        # Click save
        dialog.step_kw_multi_classifications.save_button.click()

        # Click next to finish multi classifications step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.step_kw_source.leSource.setText(source)
        dialog.step_kw_source.leSource_scale.setText(source_scale)
        dialog.step_kw_source.leSource_url.setText(source_url)
        dialog.step_kw_source.ckbSource_date.setChecked(True)
        dialog.step_kw_source.dtSource_date.setDateTime(source_date)
        dialog.step_kw_source.leSource_license.setText(source_license)

        # Click next to finish source step and go to extra keywords step
        dialog.pbnNext.click()

        self.check_current_step(dialog.step_kw_extra_keywords)

        # Click next to finish extra keywords step and go to title step
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
            'active_band': 1,
            'continuous_hazard_unit': 'metres',
            'date': source_date,
            'hazard': hazard_flood['key'],
            'hazard_category': hazard_category_multiple_event['key'],
            'layer_geometry': layer_geometry_raster['key'],
            'layer_mode': layer_mode_continuous['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'license': source_license,
            'scale': source_scale,
            'source': source,
            'title': layer_title,
            'url': source_url,
            'thresholds': {
                exposure_land_cover['key']: {
                    flood_hazard_classes['key']: {
                        'active': True,
                        'classes': {
                            'dry': [0.0, 1.0],
                            'wet': [1.0, big_number]
                        }
                    }
                }
            }
        }

        real_keywords = dialog.get_keywords()
        self.assertDictEqual(byteify(real_keywords), byteify(expected_keyword))

    def test_continuous_raster_existing_keywords(self):
        """Test keyword wizard for continuous raster with assigned keyword."""
        path = standard_data_path('hazard', 'continuous_flood_20_20.asc')
        message = "Path %s is not found" % path
        self.assertTrue(os.path.exists(path), message)
        layer = clone_raster_layer(
            name='continuous_flood_20_20',
            extension='.asc',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))
        self.assertIsNotNone(layer)
        original_keywords = {
            'active_band': 1,
            'continuous_hazard_unit': 'metres',
            'date': source_date,
            'hazard': hazard_flood['key'],
            'hazard_category': hazard_category_multiple_event['key'],
            'layer_geometry': layer_geometry_raster['key'],
            'layer_mode': layer_mode_continuous['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'license': source_license,
            'scale': source_scale,
            'source': source,
            'thresholds': {
                exposure_land_cover['key']: {
                    flood_hazard_classes['key']: {
                        'classes': {
                            'dry': [0, 1],
                            'wet': [1, 9999999999]
                        },
                        'active': True
                    }
                },
            },
            'title': layer_title,
            'url': source_url,
        }
        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.set_keywords_creation_mode(layer, original_keywords)

        # Check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Select hazard
        self.select_from_list_widget(
            layer_purpose_hazard['name'], dialog.step_kw_purpose.lstCategories)

        # Click next to select hazard
        dialog.pbnNext.click()

        # Check if in select hazard step
        self.check_current_step(dialog.step_kw_subcategory)

        # select flood
        self.select_from_list_widget(
            hazard_flood['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select flood
        dialog.pbnNext.click()

        # Check if in select hazard category step
        self.check_current_step(dialog.step_kw_hazard_category)

        # select multiple_event
        self.select_from_list_widget(
            hazard_category_multiple_event['name'],
            dialog.step_kw_hazard_category.lstHazardCategories)

        # Click next to select multiple event
        dialog.pbnNext.click()

        # Check if in select band step
        self.check_current_step(dialog.step_kw_band_selector)

        # Click next to select Band 1 (default)
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # select continuous mode
        self.select_from_list_widget(
            layer_mode_continuous['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select continuous
        dialog.pbnNext.click()

        # Check if in select unit step
        self.check_current_step(dialog.step_kw_unit)

        # select unit metres
        self.select_from_list_widget(
            unit_metres['name'],
            dialog.step_kw_unit.lstUnits)

        # Click next to select unit metres
        dialog.pbnNext.click()

        # Check if in select multi classifications step
        self.check_current_step(dialog.step_kw_multi_classifications)

        # Click next to finish multi classifications step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.step_kw_source.leSource.setText(source)
        dialog.step_kw_source.leSource_scale.setText(source_scale)
        dialog.step_kw_source.leSource_url.setText(source_url)
        dialog.step_kw_source.ckbSource_date.setChecked(True)
        dialog.step_kw_source.dtSource_date.setDateTime(source_date)
        dialog.step_kw_source.leSource_license.setText(source_license)

        # Click next to finish source step and go to extra keywords step
        dialog.pbnNext.click()

        self.check_current_step(dialog.step_kw_extra_keywords)

        # Click next to finish extra keywords step and go to title step
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

        real_keywords = dialog.get_keywords()
        self.assertDictEqual(
            byteify(real_keywords), byteify(original_keywords))

    def test_continuous_vector(self):
        """Test continuous vector for keyword wizard."""
        layer = load_test_vector_layer(
            'hazard', 'continuous_vector.geojson', clone_to_memory=True)
        layer.keywords = {}

        self.assertIsNotNone(layer)

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.set_keywords_creation_mode(layer)

        # Check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Select hazard
        self.select_from_list_widget(
            layer_purpose_hazard['name'],
            dialog.step_kw_purpose.lstCategories)

        # Click next to select hazard
        dialog.pbnNext.click()

        # Check if in select hazard step
        self.check_current_step(dialog.step_kw_subcategory)

        # select flood
        self.select_from_list_widget(
            hazard_flood['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select population
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

        # Select continuous
        self.select_from_list_widget(
            layer_mode_continuous['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select continuous
        dialog.pbnNext.click()

        # Check if in select unit step
        self.check_current_step(dialog.step_kw_unit)

        # Select metres
        self.select_from_list_widget(
            unit_metres['name'],
            dialog.step_kw_unit.lstUnits)

        # Click next to select metres
        dialog.pbnNext.click()

        # Check if in select field step
        self.check_current_step(dialog.step_kw_field)

        # select population field
        depth_field = 'depth'
        self.select_from_list_widget(
            depth_field, dialog.step_kw_field.lstFields)

        # Click next to select depth
        dialog.pbnNext.click()

        # Check if in multi classification step
        self.check_current_step(dialog.step_kw_multi_classifications)

        # Change combo box
        dialog.step_kw_multi_classifications.exposure_combo_boxes[
            0].setCurrentIndex(1)

        # Click save
        dialog.step_kw_multi_classifications.save_button.click()

        # Click next to finish multi classifications step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.step_kw_source.leSource.setText(source)
        dialog.step_kw_source.leSource_scale.setText(source_scale)
        dialog.step_kw_source.leSource_url.setText(source_url)
        dialog.step_kw_source.ckbSource_date.setChecked(True)
        dialog.step_kw_source.dtSource_date.setDateTime(source_date)
        dialog.step_kw_source.leSource_license.setText(source_license)

        # Click next to finish source step and go to extra keywords step
        dialog.pbnNext.click()

        self.check_current_step(dialog.step_kw_extra_keywords)

        # Click next to finish extra keywords step and go to title step
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
            'continuous_hazard_unit': unit_metres['key'],
            'date': source_date,
            'hazard': hazard_flood['key'],
            'hazard_category': hazard_category_multiple_event['key'],
            'inasafe_fields': {hazard_value_field['key']: depth_field},
            'layer_geometry': layer_geometry_polygon['key'],
            'layer_mode': layer_mode_continuous['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'license': source_license,
            'scale': source_scale,
            'source': source,
            'thresholds': {
                exposure_land_cover['key']: {
                    flood_hazard_classes['key']: {
                        'classes': {
                            'dry': [0, 1],
                            'wet': [1, big_number]
                        },
                        'active': True
                    }
                },
            },
            'title': layer_title,
            'url': source_url
        }

        real_keywords = dialog.get_keywords()

        self.assertDictEqual(real_keywords, expected_keyword)

    # @unittest.skip(
    #     'This test is hanging for a unknown reason since a few times.')
    def test_auto_select_one_item(self):
        """Test auto select if there is only one item in a list."""
        layer = clone_shp_layer(
            name='buildings',
            include_keywords=True,
            source_directory=standard_data_path('exposure'))
        dialog = WizardDialog(iface=IFACE)
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # choose exposure
        self.assertEqual(
            dialog.step_kw_subcategory.lstSubcategories.currentRow(), 2)
        num_item = dialog.step_kw_subcategory.lstSubcategories.count()
        dialog.close()
        self.assertTrue(num_item == 3)

    def test_earthquake_raster(self):
        """Test for Earthquake raster keyword wizard."""
        path = standard_data_path('hazard', 'earthquake.tif')
        message = "Path %s is not found" % path
        self.assertTrue(os.path.exists(path), message)
        layer = clone_raster_layer(
            name='earthquake',
            extension='.tif',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))
        self.assertIsNotNone(layer)
        layer.keywords = {}

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
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

        # select EQ
        self.select_from_list_widget(
            hazard_earthquake['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select EQ
        dialog.pbnNext.click()

        # Check if in select hazard category step
        self.check_current_step(dialog.step_kw_hazard_category)

        # select multiple_event
        self.select_from_list_widget(
            hazard_category_multiple_event['name'],
            dialog.step_kw_hazard_category.lstHazardCategories)

        # Click next to select multiple event
        dialog.pbnNext.click()

        # Check if in select band step
        self.check_current_step(dialog.step_kw_band_selector)

        # Click next to select Band 1 (default)
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # select continuous mode
        self.select_from_list_widget(
            layer_mode_continuous['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select continuous
        dialog.pbnNext.click()

        # Check if in unit step
        self.check_current_step(dialog.step_kw_unit)

        # select MMI
        self.select_from_list_widget(
            unit_mmi['name'],
            dialog.step_kw_unit.lstUnits)

        # Click next to select MMI
        dialog.pbnNext.click()

        # Check if in multi classification step
        self.check_current_step(dialog.step_kw_multi_classifications)

        # Click next to finish multi classifications step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.step_kw_source.leSource.setText(source)
        dialog.step_kw_source.leSource_scale.setText(source_scale)
        dialog.step_kw_source.leSource_url.setText(source_url)
        dialog.step_kw_source.ckbSource_date.setChecked(True)
        dialog.step_kw_source.dtSource_date.setDateTime(source_date)
        dialog.step_kw_source.leSource_license.setText(source_license)

        # Click next to finish source step and go to extra keywords step
        dialog.pbnNext.click()

        # Check if in extra keywords step
        self.check_current_step(dialog.step_kw_extra_keywords)

        self.assertTrue(dialog.step_kw_extra_keywords.widgets_dict)

        # Click next to finish extra keywords step and go to title step
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
            'active_band': 1,
            'continuous_hazard_unit': unit_mmi['key'],
            'scale': source_scale,
            'hazard_category': hazard_category_multiple_event['key'],
            'license': source_license,
            'source': source,
            'url': source_url,
            'title': layer_title,
            'hazard': hazard_earthquake['key'],
            'date': source_date,
            'layer_geometry': layer_geometry_raster['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'layer_mode': layer_mode_continuous['key'],
            'thresholds': {
                exposure_population['key']: {
                    earthquake_mmi_scale['key']: {
                        'active': True,
                        'classes': default_classification_thresholds(
                            earthquake_mmi_scale)
                    }
                }
            }
        }

        real_keywords = dialog.get_keywords()
        self.assertDictEqual(real_keywords, expected_keyword)

    def test_earthquake_raster_dirty_keywords(self):
        """Test for Earthquake raster keyword wizard."""
        path = standard_data_path('hazard', 'earthquake.tif')
        message = "Path %s is not found" % path
        self.assertTrue(os.path.exists(path), message)
        layer = clone_raster_layer(
            name='earthquake',
            extension='.tif',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))
        self.assertIsNotNone(layer)

        expected_keyword = {
            'continuous_hazard_unit': unit_mmi['key'],
            'scale': source_scale,
            'hazard_category': hazard_category_multiple_event['key'],
            'license': source_license,
            'source': source,
            'url': source_url,
            'title': layer_title,
            'hazard': hazard_earthquake['key'],
            'date': source_date,
            'layer_geometry': layer_geometry_raster['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'layer_mode': layer_mode_continuous['key'],
            'thresholds': {
                exposure_population['key']: {
                    earthquake_mmi_scale['key']: {
                        'active': True,
                        'classes': default_classification_thresholds(
                            earthquake_mmi_scale)
                    }
                },
                exposure_land_cover['key']: {
                    earthquake_mmi_scale['key']: {
                        'active': True,
                        'classes': default_classification_thresholds(
                            earthquake_mmi_scale)
                    }
                }
            },
            'extra_keywords': {
                extra_keyword_earthquake_depth['key']: 10
            }
        }

        layer.keywords = expected_keyword

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.set_keywords_creation_mode(layer, expected_keyword)

        # Check if in select purpose step
        self.check_current_step(dialog.step_kw_purpose)

        # Select hazard
        self.select_from_list_widget(
            layer_purpose_hazard['name'], dialog.step_kw_purpose.lstCategories)

        # Click next to select hazard
        dialog.pbnNext.click()

        # Check if in select hazard step
        self.check_current_step(dialog.step_kw_subcategory)

        # select EQ
        self.select_from_list_widget(
            hazard_earthquake['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select EQ
        dialog.pbnNext.click()

        # Check if in select hazard category step
        self.check_current_step(dialog.step_kw_hazard_category)

        # select multiple_event
        self.select_from_list_widget(
            hazard_category_multiple_event['name'],
            dialog.step_kw_hazard_category.lstHazardCategories)

        # Click next to select multiple event
        dialog.pbnNext.click()

        # Check if in select band step
        self.check_current_step(dialog.step_kw_band_selector)

        # Click next to select Band 1 (default)
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # select continuous mode
        self.select_from_list_widget(
            layer_mode_continuous['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select continuous
        dialog.pbnNext.click()

        # Check if in unit step
        self.check_current_step(dialog.step_kw_unit)

        # select MMI
        self.select_from_list_widget(
            unit_mmi['name'],
            dialog.step_kw_unit.lstUnits)

        # Click next to select MMI
        dialog.pbnNext.click()

        # Check if in multi classification step
        self.check_current_step(dialog.step_kw_multi_classifications)

        # Click next to finish multi classifications step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.step_kw_source.leSource.setText(source)
        dialog.step_kw_source.leSource_scale.setText(source_scale)
        dialog.step_kw_source.leSource_url.setText(source_url)
        dialog.step_kw_source.ckbSource_date.setChecked(True)
        dialog.step_kw_source.dtSource_date.setDateTime(source_date)
        dialog.step_kw_source.leSource_license.setText(source_license)

        # Click next to finish source step and go to extra keywords step
        dialog.pbnNext.click()

        # Check if in extra keywords step
        self.check_current_step(dialog.step_kw_extra_keywords)

        self.assertTrue(dialog.step_kw_extra_keywords.widgets_dict)

        # Click next to finish extra keywords step and go to title step
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
        real_keywords = dialog.get_keywords()
        # Check if classification for land cover is not exist anymore #4214
        self.assertNotIn(
            exposure_land_cover['key'],
            list(real_keywords['thresholds'].keys())
        )
        # Check if the extra keywords remain
        extra_keywords = real_keywords['extra_keywords']
        self.assertDictEqual(
            extra_keywords, expected_keyword['extra_keywords'])

    def test_cyclone_raster(self):
        """Test for cyclone raster keyword wizard when we have many units."""
        path = standard_data_path('gisv4', 'hazard', 'cyclone_AUBOM_km_h.asc')
        message = "Path %s is not found" % path
        self.assertTrue(os.path.exists(path), message)
        layer = clone_raster_layer(
            name='cyclone_AUBOM_km_h',
            extension='.asc',
            include_keywords=False,
            source_directory=standard_data_path('gisv4', 'hazard'))
        self.assertIsNotNone(layer)
        layer.keywords = {}

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
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

        # select cyclone
        self.select_from_list_widget(
            hazard_cyclone['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select EQ
        dialog.pbnNext.click()

        # Check if in select hazard category step
        self.check_current_step(dialog.step_kw_hazard_category)

        # select multiple_event
        self.select_from_list_widget(
            hazard_category_multiple_event['name'],
            dialog.step_kw_hazard_category.lstHazardCategories)

        # Click next to select multiple event
        dialog.pbnNext.click()

        # Check if in select band step
        self.check_current_step(dialog.step_kw_band_selector)

        # Click next to select Band 1 (default)
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # select continuous mode
        self.select_from_list_widget(
            layer_mode_continuous['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select continuous
        dialog.pbnNext.click()

        # Check if in unit step
        self.check_current_step(dialog.step_kw_unit)

        # select MMI
        self.select_from_list_widget(
            unit_kilometres_per_hour['name'],
            dialog.step_kw_unit.lstUnits)

        # Click next to select MMI
        dialog.pbnNext.click()

        # Check if in select multi classifications step
        self.check_current_step(dialog.step_kw_multi_classifications)

        # Change combo box
        dialog.step_kw_multi_classifications.exposure_combo_boxes[
            0].setCurrentIndex(1)

        # Click save
        dialog.step_kw_multi_classifications.save_button.click()

        # Click next to finish multi classifications step
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
            'active_band': 1,
            'continuous_hazard_unit': unit_kilometres_per_hour['key'],
            'scale': source_scale,
            'hazard_category': hazard_category_multiple_event['key'],
            'license': source_license,
            'source': source,
            'url': source_url,
            'title': layer_title,
            'hazard': hazard_cyclone['key'],
            'date': source_date,
            'layer_geometry': layer_geometry_raster['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'layer_mode': layer_mode_continuous['key'],
            'thresholds': {
                exposure_land_cover['key']: {
                    cyclone_au_bom_hazard_classes['key']: {
                        'active': True,
                        'classes': default_classification_thresholds(
                            cyclone_au_bom_hazard_classes,
                            unit_kilometres_per_hour['key'])
                    }
                }
            }
        }

        real_keywords = dialog.get_keywords()
        self.assertDictEqual(real_keywords, expected_keyword)

    def test_earthquake_raster_invalid_key(self):
        """Test for Earthquake raster keyword wizard."""
        path = standard_data_path('hazard', 'earthquake.tif')
        message = "Path %s is not found" % path
        self.assertTrue(os.path.exists(path), message)
        layer = clone_raster_layer(
            name='earthquake',
            extension='.tif',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))
        self.assertIsNotNone(layer)
        layer.keywords = {
            'thresholds': {
                exposure_structure['key']: {
                    'dummy': {
                        'active': True,
                        'classes': default_classification_thresholds(
                            earthquake_mmi_scale)
                    }
                }
            }
        }

        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
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

        # select EQ
        self.select_from_list_widget(
            hazard_earthquake['name'],
            dialog.step_kw_subcategory.lstSubcategories)

        # Click next to select EQ
        dialog.pbnNext.click()

        # Check if in select hazard category step
        self.check_current_step(dialog.step_kw_hazard_category)

        # select multiple_event
        self.select_from_list_widget(
            hazard_category_multiple_event['name'],
            dialog.step_kw_hazard_category.lstHazardCategories)

        # Click next to select multiple event
        dialog.pbnNext.click()

        # Check if in select band step
        self.check_current_step(dialog.step_kw_band_selector)

        # Click next to select Band 1 (default)
        dialog.pbnNext.click()

        # Check if in select layer mode step
        self.check_current_step(dialog.step_kw_layermode)

        # select continuous mode
        self.select_from_list_widget(
            layer_mode_continuous['name'],
            dialog.step_kw_layermode.lstLayerModes)

        # Click next to select continuous
        dialog.pbnNext.click()

        # Check if in unit step
        self.check_current_step(dialog.step_kw_unit)

        # select MMI
        self.select_from_list_widget(
            unit_mmi['name'],
            dialog.step_kw_unit.lstUnits)

        # Click next to select MMI
        dialog.pbnNext.click()

        # Check if in multi classification step
        self.check_current_step(dialog.step_kw_multi_classifications)

        # Click next to finish multi classifications step
        dialog.pbnNext.click()

        # Check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.step_kw_source.leSource.setText(source)
        dialog.step_kw_source.leSource_scale.setText(source_scale)
        dialog.step_kw_source.leSource_url.setText(source_url)
        dialog.step_kw_source.ckbSource_date.setChecked(True)
        dialog.step_kw_source.dtSource_date.setDateTime(source_date)
        dialog.step_kw_source.leSource_license.setText(source_license)

        # Click next to finish source step and go to extra keywords step
        dialog.pbnNext.click()

        # Check if in extra keywords step
        self.check_current_step(dialog.step_kw_extra_keywords)

        self.assertTrue(dialog.step_kw_extra_keywords.widgets_dict)

        # Click next to finish extra keywords step and go to title step
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
            'active_band': 1,
            'continuous_hazard_unit': unit_mmi['key'],
            'scale': source_scale,
            'hazard_category': hazard_category_multiple_event['key'],
            'license': source_license,
            'source': source,
            'url': source_url,
            'title': layer_title,
            'hazard': hazard_earthquake['key'],
            'date': source_date,
            'layer_geometry': layer_geometry_raster['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'layer_mode': layer_mode_continuous['key'],
            'thresholds': {
                exposure_population['key']: {
                    earthquake_mmi_scale['key']: {
                        'active': True,
                        'classes': default_classification_thresholds(
                            earthquake_mmi_scale)
                    }
                }
            }
        }

        real_keywords = dialog.get_keywords()
        self.assertDictEqual(real_keywords, expected_keyword)

    def check_radio_button_behaviour(self, inasafe_default_dialog):
        """Test radio button behaviour so they are disabled when user set the
           ratio field and enabled when there is no field selected.
        """
        # Get the parameter container from dialog.
        parameter_container = (
            inasafe_default_dialog.parameter_container.get_parameter_widgets())
        # Check every parameter widgets on the container.
        for parameter_widget in parameter_container:
            parameter_widget = parameter_widget.widget()

            # Locate the 'Do not report' radio button.
            dont_use_button = (
                parameter_widget.default_input_button_group.button(
                    len(parameter_widget._parameter.default_values) - 2))
            # 'Do not report' button should be selected since the default
            # selected input is 'No Field'.
            self.assertTrue(dont_use_button.isChecked())
            # Select ratio field on input.
            current_index = parameter_widget.input.currentIndex()
            parameter_widget.input.setCurrentIndex(current_index + 1)
            self.assertFalse(dont_use_button.isChecked())

            parameter_widget.input.setCurrentIndex(current_index)
            self.assertTrue(dont_use_button.isChecked())


if __name__ == '__main__':
    suite = unittest.makeSuite(TestKeywordWizard)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
