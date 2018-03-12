# coding=utf-8
"""InaSAFE Plugin."""

import sys
import os
from functools import partial
from distutils.version import StrictVersion

# noinspection PyUnresolvedReferences
import qgis  # NOQA pylint: disable=unused-import
# Import the PyQt and QGIS libraries
from qgis.core import (
    QgsRectangle,
    QgsRasterLayer,
    QgsMapLayerRegistry,
    QgsMapLayer,
    QgsExpression,
    QgsProject,
)
# noinspection PyPackageRequirements
from PyQt4.QtCore import (
    QCoreApplication,
    Qt,
)
# noinspection PyPackageRequirements
from PyQt4.QtGui import (
    QAction,
    QIcon,
    QApplication,
    QToolButton,
    QMenu,
    QLineEdit,
    QInputDialog,
)

from safe.common.custom_logging import LOGGER
from safe.utilities.expressions import qgis_expressions
from safe.definitions.versions import inasafe_release_status, inasafe_version
from safe.common.exceptions import (
    KeywordNotFoundError,
    NoKeywordsFoundError,
    MetadataReadError,
)
from safe.common.signals import send_static_message
from safe.utilities.resources import resources_path
from safe.utilities.gis import is_raster_layer
from safe.definitions.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard
)
from safe.definitions.utilities import get_field_groups
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import is_keyword_version_supported
from safe.utilities.settings import setting, set_setting

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class Plugin(object):

    """The QGIS interface implementation for the InaSAFE plugin.

    This class acts as the 'glue' between QGIS and our custom logic.
    It creates a toolbar and menu bar entry and launches the InaSAFE user
    interface if these are activated.
    """

    def __init__(self, iface):
        """Class constructor.

        On instantiation, the plugin instance will be assigned a copy
        of the QGIS iface object which will allow this plugin to access and
        manipulate the running QGIS instance that spawned it.

        :param iface:Quantum GIS iface instance. This instance is
            automatically passed to the plugin by QGIS when it loads the
            plugin.
        :type iface: QGisAppInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.dock_widget = None

        # Actions
        self.action_add_layers = None
        self.action_add_osm_layer = None
        self.action_add_petabencana_layer = None
        self.action_batch_runner = None
        self.action_dock = None
        self.action_extent_selector = None
        self.action_field_mapping = None
        self.action_multi_exposure = None
        self.action_function_centric_wizard = None
        self.action_import_dialog = None
        self.action_keywords_wizard = None
        self.action_minimum_needs = None
        self.action_minimum_needs_config = None
        self.action_multi_buffer = None
        self.action_options = None
        self.action_run_tests = None
        self.action_save_scenario = None
        self.action_shake_converter = None
        self.action_show_definitions = None
        self.action_toggle_rubberbands = None
        self.action_metadata_converter = None

        self.translator = None
        self.toolbar = None
        self.wizard = None
        self.actions = []  # list of all QActions we create for InaSAFE

        self.message_bar_item = None
        # Flag indicating if toolbar should show only common icons or not
        self.full_toolbar = False
        # print self.tr('InaSAFE')
        # For enable/disable the keyword editor icon
        self.iface.currentLayerChanged.connect(self.layer_changed)

        developer_mode = setting(
            'developer_mode', False, expected_type=bool)
        self.hide_developer_buttons = (
            inasafe_release_status == 'final' and not developer_mode)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Plugin', message)

    def add_action(self, action, add_to_toolbar=True, add_to_legend=False):
        """Add a toolbar icon to the InaSAFE toolbar.

        :param action: The action that should be added to the toolbar.
        :type action: QAction

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the InaSAFE toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param add_to_legend: Flag indicating whether the action should also
            be added to the layer legend menu. Default to False.
        :type add_to_legend: bool
        """
        # store in the class list of actions for easy plugin unloading
        self.actions.append(action)
        self.iface.addPluginToMenu(self.tr('InaSAFE'), action)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_legend:
            # The id is the action name without spaces, tabs ...
            self.iface.legendInterface().addLegendLayerAction(
                action,
                self.tr('InaSAFE'),
                ''.join(action.text().split()),
                QgsMapLayer.VectorLayer,
                True)
            self.iface.legendInterface().addLegendLayerAction(
                action,
                self.tr('InaSAFE'),
                ''.join(action.text().split()),
                QgsMapLayer.RasterLayer,
                True)

    def _create_dock_toggle_action(self):
        """Create action for plugin dockable window (show/hide)."""
        # pylint: disable=W0201
        icon = resources_path('img', 'icons', 'icon.svg')
        self.action_dock = QAction(
            QIcon(icon),
            self.tr('Toggle InaSAFE Dock'), self.iface.mainWindow())
        self.action_dock.setObjectName('InaSAFEDockToggle')
        self.action_dock.setStatusTip(self.tr(
            'Show/hide InaSAFE dock widget'))
        self.action_dock.setWhatsThis(self.tr(
            'Show/hide InaSAFE dock widget'))
        self.action_dock.setCheckable(True)
        self.action_dock.setChecked(True)
        self.action_dock.triggered.connect(self.toggle_dock_visibility)
        self.add_action(self.action_dock)

        # --------------------------------------
        # Create action for keywords creation wizard
        # -------------------------------------

    def _create_keywords_wizard_action(self):
        """Create action for keywords creation wizard."""
        icon = resources_path('img', 'icons', 'show-keyword-wizard.svg')
        self.action_keywords_wizard = QAction(
            QIcon(icon),
            self.tr('Keywords Creation Wizard'),
            self.iface.mainWindow())
        self.action_keywords_wizard.setStatusTip(self.tr(
            'Open InaSAFE keywords creation wizard'))
        self.action_keywords_wizard.setWhatsThis(self.tr(
            'Open InaSAFE keywords creation wizard'))
        self.action_keywords_wizard.setEnabled(False)
        self.action_keywords_wizard.triggered.connect(
            self.show_keywords_wizard)
        self.add_action(self.action_keywords_wizard, add_to_legend=True)

    def _create_analysis_wizard_action(self):
        """Create action for IF-centric wizard."""
        icon = resources_path('img', 'icons', 'show-wizard.svg')
        self.action_function_centric_wizard = QAction(
            QIcon(icon),
            self.tr('Impact Function Centric Wizard'),
            self.iface.mainWindow())
        self.action_function_centric_wizard.setStatusTip(self.tr(
            'Open InaSAFE impact function centric wizard'))
        self.action_function_centric_wizard.setWhatsThis(self.tr(
            'Open InaSAFE impact function centric wizard'))
        self.action_function_centric_wizard.setEnabled(True)
        self.action_function_centric_wizard.triggered.connect(
            self.show_function_centric_wizard)
        self.add_action(self.action_function_centric_wizard)

    def _create_options_dialog_action(self):
        """Create action for options dialog."""
        icon = resources_path('img', 'icons', 'configure-inasafe.svg')
        self.action_options = QAction(
            QIcon(icon),
            self.tr('Options'), self.iface.mainWindow())
        self.action_options.setStatusTip(self.tr(
            'Open InaSAFE options dialog'))
        self.action_options.setWhatsThis(self.tr(
            'Open InaSAFE options dialog'))
        self.action_options.triggered.connect(self.show_options)
        self.add_action(self.action_options, add_to_toolbar=self.full_toolbar)

    def _create_minimum_needs_action(self):
        """Create action for minimum needs dialog."""
        icon = resources_path('img', 'icons', 'show-minimum-needs.svg')
        self.action_minimum_needs = QAction(
            QIcon(icon),
            self.tr('Minimum Needs Calculator'), self.iface.mainWindow())
        self.action_minimum_needs.setStatusTip(self.tr(
            'Open InaSAFE minimum needs calculator'))
        self.action_minimum_needs.setWhatsThis(self.tr(
            'Open InaSAFE minimum needs calculator'))
        self.action_minimum_needs.triggered.connect(self.show_minimum_needs)
        self.add_action(
            self.action_minimum_needs, add_to_toolbar=self.full_toolbar)

    def _create_multi_buffer_action(self):
        """Create action for multi buffer dialog."""
        icon = resources_path('img', 'icons', 'show-multi-buffer.svg')
        self.action_multi_buffer = QAction(
            QIcon(icon),
            self.tr('Multi Buffer'), self.iface.mainWindow())
        self.action_multi_buffer.setStatusTip(self.tr(
            'Open InaSAFE multi buffer'))
        self.action_multi_buffer.setWhatsThis(self.tr(
            'Open InaSAFE multi buffer'))
        self.action_multi_buffer.triggered.connect(self.show_multi_buffer)
        self.add_action(
            self.action_multi_buffer,
            add_to_toolbar=self.full_toolbar)

    def _create_minimum_needs_options_action(self):
        """Create action for global minimum needs dialog."""
        icon = resources_path('img', 'icons', 'show-global-minimum-needs.svg')
        self.action_minimum_needs_config = QAction(
            QIcon(icon),
            self.tr('Minimum Needs Configuration'),
            self.iface.mainWindow())
        self.action_minimum_needs_config.setStatusTip(self.tr(
            'Open InaSAFE minimum needs configuration'))
        self.action_minimum_needs_config.setWhatsThis(self.tr(
            'Open InaSAFE minimum needs configuration'))
        self.action_minimum_needs_config.triggered.connect(
            self.show_minimum_needs_configuration)
        self.add_action(
            self.action_minimum_needs_config, add_to_toolbar=self.full_toolbar)

    def _create_shakemap_converter_action(self):
        """Create action for converter dialog."""
        icon = resources_path('img', 'icons', 'show-converter-tool.svg')
        self.action_shake_converter = QAction(
            QIcon(icon),
            self.tr('Shakemap Converter'), self.iface.mainWindow())
        self.action_shake_converter.setStatusTip(self.tr(
            'Open InaSAFE Converter'))
        self.action_shake_converter.setWhatsThis(self.tr(
            'Open InaSAFE Converter'))
        self.action_shake_converter.triggered.connect(
            self.show_shakemap_importer)
        self.add_action(
            self.action_shake_converter, add_to_toolbar=self.full_toolbar)

    def _create_batch_runner_action(self):
        """Create action for batch runner dialog."""
        icon = resources_path('img', 'icons', 'show-batch-runner.svg')
        self.action_batch_runner = QAction(
            QIcon(icon),
            self.tr('Batch Runner'), self.iface.mainWindow())
        self.action_batch_runner.setStatusTip(self.tr(
            'Open Batch Runner'))
        self.action_batch_runner.setWhatsThis(self.tr(
            'Open Batch Runner'))
        self.action_batch_runner.triggered.connect(self.show_batch_runner)
        self.add_action(
            self.action_batch_runner, add_to_toolbar=self.full_toolbar)

    def _create_save_scenario_action(self):
        """Create action for save scenario dialog."""
        icon = resources_path('img', 'icons', 'save-as-scenario.svg')
        self.action_save_scenario = QAction(
            QIcon(icon),
            self.tr('Save Current Scenario'), self.iface.mainWindow())
        message = self.tr('Save current scenario to text file')
        self.action_save_scenario.setStatusTip(message)
        self.action_save_scenario.setWhatsThis(message)
        # noinspection PyUnresolvedReferences
        self.action_save_scenario.triggered.connect(self.save_scenario)
        self.add_action(
            self.action_save_scenario, add_to_toolbar=self.full_toolbar)

    def _create_osm_downloader_action(self):
        """Create action for import OSM Dialog."""
        icon = resources_path('img', 'icons', 'show-osm-download.svg')
        self.action_import_dialog = QAction(
            QIcon(icon),
            self.tr('OpenStreetMap Downloader'),
            self.iface.mainWindow())
        self.action_import_dialog.setStatusTip(self.tr(
            'OpenStreetMap Downloader'))
        self.action_import_dialog.setWhatsThis(self.tr(
            'OpenStreetMap Downloader'))
        self.action_import_dialog.triggered.connect(self.show_osm_downloader)
        self.add_action(self.action_import_dialog, add_to_toolbar=True)

    def _create_geonode_uploader_action(self):
        """Create action for Geonode uploader dialog."""
        icon = resources_path('img', 'icons', 'geonode.png')
        label = tr('Geonode Uploader')
        self.action_geonode = QAction(
            QIcon(icon), label, self.iface.mainWindow())
        self.action_geonode.setStatusTip(label)
        self.action_geonode.setWhatsThis(label)
        self.action_geonode.triggered.connect(self.show_geonode_uploader)
        self.add_action(self.action_geonode, add_to_toolbar=False)

    def _create_add_osm_layer_action(self):
        """Create action for import OSM Dialog."""
        icon = resources_path('img', 'icons', 'add-osm-tiles-layer.svg')
        self.action_add_osm_layer = QAction(
            QIcon(icon),
            self.tr('Add OpenStreetMap Tile Layer'),
            self.iface.mainWindow())
        self.action_add_osm_layer.setStatusTip(self.tr(
            'Add OpenStreetMap Tile Layer'))
        self.action_add_osm_layer.setWhatsThis(self.tr(
            'Use this to add an OSM layer to your map. '
            'It needs internet access to function.'))
        self.action_add_osm_layer.triggered.connect(self.add_osm_layer)
        self.add_action(self.action_add_osm_layer, add_to_toolbar=True)

    def _create_show_definitions_action(self):
        """Create action for showing definitions / help."""
        icon = resources_path('img', 'icons', 'show-inasafe-help.svg')
        self.action_show_definitions = QAction(
            QIcon(icon),
            self.tr('InaSAFE Help'),
            self.iface.mainWindow())
        self.action_show_definitions.setStatusTip(self.tr(
            'Show InaSAFE Help'))
        self.action_show_definitions.setWhatsThis(self.tr(
            'Use this to show a document describing all InaSAFE concepts.'))
        self.action_show_definitions.triggered.connect(
            self.show_definitions)
        self.add_action(
            self.action_show_definitions,
            add_to_toolbar=True)

    def _create_metadata_converter_action(self):
        """Create action for showing metadata converter dialog."""
        icon = resources_path('img', 'icons', 'show-metadata-converter.svg')
        self.action_metadata_converter = QAction(
            QIcon(icon),
            self.tr('InaSAFE Metadata Converter'),
            self.iface.mainWindow())
        self.action_metadata_converter.setStatusTip(self.tr(
            'Convert metadata from version 4.3 to version 3.5.'))
        self.action_metadata_converter.setWhatsThis(self.tr(
            'Use this tool to convert metadata 4.3 to version 3.5'))
        self.action_metadata_converter.triggered.connect(
            self.show_metadata_converter)
        self.add_action(
            self.action_metadata_converter, add_to_toolbar=self.full_toolbar)

    def _create_field_mapping_action(self):
        """Create action for showing field mapping dialog."""
        icon = resources_path('img', 'icons', 'show-mapping-tool.svg')
        self.action_field_mapping = QAction(
            QIcon(icon),
            self.tr('InaSAFE Field Mapping Tool'),
            self.iface.mainWindow())
        self.action_field_mapping.setStatusTip(self.tr(
            'Assign field mapping to layer.'))
        self.action_field_mapping.setWhatsThis(self.tr(
            'Use this tool to assign field mapping in layer.'))
        self.action_field_mapping.setEnabled(False)
        self.action_field_mapping.triggered.connect(self.show_field_mapping)
        self.add_action(
            self.action_field_mapping, add_to_toolbar=self.full_toolbar)

    def _create_multi_exposure_action(self):
        """Create action for showing the multi exposure tool."""
        self.action_multi_exposure = QAction(
            QIcon(resources_path('img', 'icons', 'show-multi-exposure.svg')),
            self.tr('InaSAFE Multi Exposure Tool'),
            self.iface.mainWindow())
        self.action_multi_exposure.setStatusTip(self.tr(
            'Open the multi exposure tool.'))
        self.action_multi_exposure.setWhatsThis(self.tr(
            'Open the multi exposure tool.'))
        self.action_multi_exposure.setEnabled(True)
        self.action_multi_exposure.triggered.connect(self.show_multi_exposure)
        self.add_action(
            self.action_multi_exposure, add_to_toolbar=self.full_toolbar)

    def _create_add_petabencana_layer_action(self):
        """Create action for import OSM Dialog."""
        icon = resources_path('img', 'icons', 'add-petabencana-layer.svg')
        self.action_add_petabencana_layer = QAction(
            QIcon(icon),
            self.tr('Add PetaBencana Flood Layer'),
            self.iface.mainWindow())
        self.action_add_petabencana_layer.setStatusTip(self.tr(
            'Add PetaBencana Flood Layer'))
        self.action_add_petabencana_layer.setWhatsThis(self.tr(
            'Use this to add a PetaBencana layer to your map. '
            'It needs internet access to function.'))
        self.action_add_petabencana_layer.triggered.connect(
            self.add_petabencana_layer)
        self.add_action(
            self.action_add_petabencana_layer,
            add_to_toolbar=self.full_toolbar)

    def _create_rubber_bands_action(self):
        """Create action for toggling rubber bands."""
        icon = resources_path('img', 'icons', 'toggle-rubber-bands.svg')
        self.action_toggle_rubberbands = QAction(
            QIcon(icon),
            self.tr('Toggle Scenario Outlines'), self.iface.mainWindow())
        message = self.tr('Toggle rubber bands showing scenario extents.')
        self.action_toggle_rubberbands.setStatusTip(message)
        self.action_toggle_rubberbands.setWhatsThis(message)
        # Set initial state
        self.action_toggle_rubberbands.setCheckable(True)
        flag = setting('showRubberBands', False, expected_type=bool)
        self.action_toggle_rubberbands.setChecked(flag)
        # noinspection PyUnresolvedReferences
        self.action_toggle_rubberbands.triggered.connect(
            self.dock_widget.toggle_rubber_bands)
        self.add_action(self.action_toggle_rubberbands)

    def _create_analysis_extent_action(self):
        """Create action for analysis extent dialog."""
        icon = resources_path('img', 'icons', 'set-extents-tool.svg')
        self.action_extent_selector = QAction(
            QIcon(icon),
            self.tr('Set Analysis Area'),
            self.iface.mainWindow())
        self.action_extent_selector.setStatusTip(self.tr(
            'Set the analysis area for InaSAFE'))
        self.action_extent_selector.setWhatsThis(self.tr(
            'Set the analysis area for InaSAFE'))
        self.action_extent_selector.triggered.connect(
            self.show_extent_selector)
        self.add_action(self.action_extent_selector)

    def _create_test_layers_action(self):
        """Create action for adding layers (developer mode, non final only)."""
        if self.hide_developer_buttons:
            return

        icon = resources_path('img', 'icons', 'add-test-layers.svg')
        self.action_add_layers = QAction(
            QIcon(icon),
            self.tr('Add Test Layers'),
            self.iface.mainWindow())
        self.action_add_layers.setStatusTip(self.tr(
            'Add test layers'))
        self.action_add_layers.setWhatsThis(self.tr(
            'Add test layers'))
        self.action_add_layers.triggered.connect(
            self.add_test_layers)

        self.add_action(self.action_add_layers)

    def _create_run_test_action(self):
        """Create action for running tests (developer mode, non final only)."""
        if self.hide_developer_buttons:
            return

        default_package = unicode(
            setting('testPackage', 'safe', expected_type=str))
        msg = self.tr('Run tests in %s' % default_package)

        self.test_button = QToolButton()
        self.test_button.setMenu(QMenu())
        self.test_button.setPopupMode(QToolButton.MenuButtonPopup)

        icon = resources_path('img', 'icons', 'run-tests.svg')
        self.action_run_tests = QAction(
            QIcon(icon), msg, self.iface.mainWindow())

        self.action_run_tests.setStatusTip(msg)
        self.action_run_tests.setWhatsThis(msg)
        self.action_run_tests.triggered.connect(self.run_tests)

        self.test_button.menu().addAction(self.action_run_tests)
        self.test_button.setDefaultAction(self.action_run_tests)

        self.action_select_package = QAction(
            QIcon(icon), self.tr('Select package'), self.iface.mainWindow())

        self.action_select_package.setStatusTip(self.tr('Select Test Package'))
        self.action_select_package.setWhatsThis(self.tr('Select Test Package'))
        self.action_select_package.triggered.connect(
            self.select_test_package)
        self.test_button.menu().addAction(self.action_select_package)
        self.toolbar.addWidget(self.test_button)

        self.add_action(self.action_run_tests, add_to_toolbar=False)
        self.add_action(self.action_select_package, add_to_toolbar=False)

    def _create_dock(self):
        """Create dockwidget and tabify it with the legend."""
        # Import dock here as it needs to be imported AFTER i18n is set up
        from safe.gui.widgets.dock import Dock
        self.dock_widget = Dock(self.iface)
        self.dock_widget.setObjectName('InaSAFE-Dock')
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        legend_tab = self.iface.mainWindow().findChild(QApplication, 'Legend')
        if legend_tab:
            self.iface.mainWindow().tabifyDockWidget(
                legend_tab, self.dock_widget)
            self.dock_widget.raise_()

    # noinspection PyPep8Naming
    def initGui(self):
        """Gui initialisation procedure (for QGIS plugin api).

        .. note:: Don't change the name of this method from initGui!

        This method is called by QGIS and should be used to set up
        any graphical user interface elements that should appear in QGIS by
        default (i.e. before the user performs any explicit action with the
        plugin).
        """
        self.toolbar = self.iface.addToolBar('InaSAFE')
        self.toolbar.setObjectName('InaSAFEToolBar')
        self.dock_widget = None
        # Now create the actual dock
        self._create_dock()
        # And all the menu actions
        # Configuration Group
        self._create_dock_toggle_action()
        self._create_options_dialog_action()
        self._create_minimum_needs_options_action()
        self._create_analysis_extent_action()
        self._create_rubber_bands_action()
        self._add_spacer_to_menu()
        self._create_keywords_wizard_action()
        self._create_analysis_wizard_action()
        self._add_spacer_to_menu()
        self._create_field_mapping_action()
        self._create_multi_exposure_action()
        self._create_metadata_converter_action()
        self._create_osm_downloader_action()
        self._create_add_osm_layer_action()
        self._create_add_petabencana_layer_action()
        self._create_geonode_uploader_action()
        self._create_shakemap_converter_action()
        self._create_minimum_needs_action()
        self._create_multi_buffer_action()
        self._create_test_layers_action()
        self._create_run_test_action()
        self._add_spacer_to_menu()
        self._create_batch_runner_action()
        self._create_save_scenario_action()
        self._add_spacer_to_menu()
        self._create_show_definitions_action()

        # Hook up a slot for when the dock is hidden using its close button
        # or  view-panels
        #
        self.dock_widget.visibilityChanged.connect(self.toggle_inasafe_action)
        # Also deal with the fact that on start of QGIS dock may already be
        # hidden.
        self.action_dock.setChecked(self.dock_widget.isVisible())

        self.iface.initializationCompleted.connect(
            partial(self.show_welcome_message)
        )

    def _add_spacer_to_menu(self):
        """Create a spacer to the menu to separate action groups."""
        separator = QAction(self.iface.mainWindow())
        separator.setSeparator(True)
        self.iface.addPluginToMenu(self.tr('InaSAFE'), separator)

    @staticmethod
    def clear_modules():
        """Unload inasafe functions and try to return QGIS to before InaSAFE.

        .. todo:: I think this function can be removed. TS.
        """
        # next lets force remove any inasafe related modules
        modules = []
        for module in sys.modules:
            if 'inasafe' in module:
                # Check if it is really one of our modules i.e. exists in the
                # plugin directory
                tokens = module.split('.')
                path = ''
                for myToken in tokens:
                    path += os.path.sep + myToken
                parent = os.path.abspath(os.path.join(
                    __file__, os.path.pardir, os.path.pardir))
                full_path = os.path.join(parent, path + '.py')
                if os.path.exists(os.path.abspath(full_path)):
                    LOGGER.debug('Removing: %s' % module)
                    modules.append(module)
        for module in modules:
            del (sys.modules[module])
        for module in sys.modules:
            if 'inasafe' in module:
                print module

        # Lets also clean up all the path additions that were made
        package_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), os.path.pardir))
        LOGGER.debug('Path to remove: %s' % package_path)
        # We use a list comprehension to ensure duplicate entries are removed
        LOGGER.debug(sys.path)
        sys.path = [y for y in sys.path if package_path not in y]
        LOGGER.debug(sys.path)

    def unload(self):
        """GUI breakdown procedure (for QGIS plugin api).

        .. note:: Don't change the name of this method from unload!

        This method is called by QGIS and should be used to *remove*
        any graphical user interface elements that should appear in QGIS.
        """
        # Remove the plugin menu item and icon
        if self.wizard:
            self.wizard.deleteLater()
        for myAction in self.actions:
            self.iface.removePluginMenu(self.tr('InaSAFE'), myAction)
            self.iface.removeToolBarIcon(myAction)
            self.iface.legendInterface().removeLegendLayerAction(myAction)
        self.iface.mainWindow().removeDockWidget(self.dock_widget)
        self.iface.mainWindow().removeToolBar(self.toolbar)
        self.dock_widget.setVisible(False)
        self.dock_widget.destroy()
        self.iface.currentLayerChanged.disconnect(self.layer_changed)

        # Unload QGIS expressions loaded by the plugin.
        for qgis_expression in qgis_expressions().keys():
            QgsExpression.unregisterFunction(qgis_expression)

    def toggle_inasafe_action(self, checked):
        """Check or un-check the toggle inaSAFE toolbar button.

        This slot is called when the user hides the inaSAFE panel using its
        close button or using view->panels.

        :param checked: True if the dock should be shown, otherwise False.
        :type checked: bool
        """
        self.action_dock.setChecked(checked)

    # Run method that performs all the real work
    def toggle_dock_visibility(self):
        """Show or hide the dock widget."""
        if self.dock_widget.isVisible():
            self.dock_widget.setVisible(False)
        else:
            self.dock_widget.setVisible(True)
            self.dock_widget.raise_()

    def add_test_layers(self):
        """Add standard test layers."""
        from safe.test.utilities import load_standard_layers
        load_standard_layers()
        rect = QgsRectangle(106.806, -6.195, 106.837, -6.167)
        self.iface.mapCanvas().setExtent(rect)

    def select_test_package(self):
        """Select the test package."""
        default_package = 'safe'
        user_package = unicode(
            setting('testPackage', default_package, expected_type=str))

        test_package, _ = QInputDialog.getText(
            self.iface.mainWindow(),
            self.tr('Select the python test package'),
            self.tr('Select the python test package'),
            QLineEdit.Normal,
            user_package)

        if test_package == '':
            test_package = default_package

        set_setting('testPackage', test_package)
        msg = self.tr('Run tests in %s' % test_package)
        self.action_run_tests.setWhatsThis(msg)
        self.action_run_tests.setText(msg)

    def run_tests(self):
        """Run unit tests in the python console."""
        from PyQt4.QtGui import QDockWidget
        main_window = self.iface.mainWindow()
        action = main_window.findChild(QAction, 'mActionShowPythonDialog')
        action.trigger()
        package = unicode(setting('testPackage', 'safe', expected_type=str))
        for child in main_window.findChildren(QDockWidget, 'PythonConsole'):
            if child.objectName() == 'PythonConsole':
                child.show()
                for widget in child.children():
                    if 'PythonConsoleWidget' in str(widget.__class__):
                        # print "Console widget found"
                        shell = widget.shell
                        shell.runCommand(
                            'from inasafe.test_suite import test_package')
                        shell.runCommand('test_package(\'%s\')' % package)
                        break

    def show_extent_selector(self):
        """Show the extent selector widget for defining analysis extents."""
        # import here only so that it is AFTER i18n set up
        from safe.gui.tools.extent_selector_dialog import ExtentSelectorDialog
        widget = ExtentSelectorDialog(
            self.iface,
            self.iface.mainWindow(),
            extent=self.dock_widget.extent.user_extent,
            crs=self.dock_widget.extent.crs)
        widget.clear_extent.connect(
            self.dock_widget.extent.clear_user_analysis_extent)
        widget.extent_defined.connect(
            self.dock_widget.define_user_analysis_extent)
        # This ensures that run button state is updated on dialog close
        widget.extent_selector_closed.connect(
            self.dock_widget.validate_impact_function)
        # Needs to be non modal to support hide -> interact with map -> show
        widget.show()  # non modal

    def show_minimum_needs(self):
        """Show the minimum needs dialog."""
        # import here only so that it is AFTER i18n set up
        from safe.gui.tools.minimum_needs.needs_calculator_dialog import (
            NeedsCalculatorDialog
        )

        dialog = NeedsCalculatorDialog(self.iface.mainWindow())
        dialog.exec_()

    def show_minimum_needs_configuration(self):
        """Show the minimum needs dialog."""
        # import here only so that it is AFTER i18n set up
        from safe.gui.tools.minimum_needs.needs_manager_dialog import (
            NeedsManagerDialog)

        dialog = NeedsManagerDialog(
            parent=self.iface.mainWindow(),
            dock=self.dock_widget)
        dialog.exec_()  # modal

    def show_options(self):
        """Show the options dialog."""
        # import here only so that it is AFTER i18n set up
        from safe.gui.tools.options_dialog import OptionsDialog

        dialog = OptionsDialog(
            iface=self.iface,
            parent=self.iface.mainWindow())
        dialog.show_option_dialog()
        if dialog.exec_():  # modal
            self.dock_widget.read_settings()
            from safe.gui.widgets.message import getting_started_message
            send_static_message(self.dock_widget, getting_started_message())
            # Issue #4734, make sure to update the combobox after update the
            # InaSAFE option
            self.dock_widget.get_layers()

    def show_welcome_message(self):
        """Show the welcome message."""
        # import here only so that it is AFTER i18n set up
        from safe.gui.tools.options_dialog import OptionsDialog

        # Do not show by default
        show_message = False

        previous_version = StrictVersion(setting('previous_version'))
        current_version = StrictVersion(inasafe_version)

        # Set previous_version to the current inasafe_version
        set_setting('previous_version', inasafe_version)

        if setting('always_show_welcome_message', expected_type=bool):
            # Show if it the setting said so
            show_message = True
        elif previous_version < current_version:
            # Always show if the user installed new version
            show_message = True

        if show_message:
            dialog = OptionsDialog(
                iface=self.iface,
                parent=self.iface.mainWindow())
            dialog.show_welcome_dialog()
            if dialog.exec_():  # modal
                self.dock_widget.read_settings()

    def show_keywords_wizard(self):
        """Show the keywords creation wizard."""
        # import here only so that it is AFTER i18n set up
        from safe.gui.tools.wizard.wizard_dialog import WizardDialog

        if self.iface.activeLayer() is None:
            return

        # Don't break an existing wizard session if accidentally clicked
        if self.wizard and self.wizard.isVisible():
            return

        # Prevent spawning multiple copies since the IFCW is non modal
        if not self.wizard:
            self.wizard = WizardDialog(
                self.iface.mainWindow(),
                self.iface,
                self.dock_widget)
        self.wizard.set_keywords_creation_mode()
        self.wizard.exec_()  # modal

    def show_function_centric_wizard(self):
        """Show the function centric wizard."""
        # import here only so that it is AFTER i18n set up
        from safe.gui.tools.wizard.wizard_dialog import WizardDialog

        # Don't break an existing wizard session if accidentally clicked
        if self.wizard and self.wizard.isVisible():
            return

        # Prevent spawning multiple copies since it is non modal
        if not self.wizard:
            self.wizard = WizardDialog(
                self.iface.mainWindow(),
                self.iface,
                self.dock_widget)
        self.wizard.set_function_centric_mode()
        # non-modal in order to hide for selecting user extent
        self.wizard.show()

    def show_shakemap_importer(self):
        """Show the converter dialog."""
        # import here only so that it is AFTER i18n set up
        from safe.gui.tools.shake_grid.shakemap_converter_dialog import (
            ShakemapConverterDialog)

        dialog = ShakemapConverterDialog(
            self.iface.mainWindow(), self.iface, self.dock_widget)
        dialog.exec_()  # modal

    def show_multi_buffer(self):
        """Show the multi buffer tool."""
        from safe.gui.tools.multi_buffer_dialog import (
            MultiBufferDialog)

        dialog = MultiBufferDialog(
            self.iface.mainWindow(), self.iface, self.dock_widget)
        dialog.exec_()  # modal

    def show_osm_downloader(self):
        """Show the OSM buildings downloader dialog."""
        from safe.gui.tools.osm_downloader_dialog import OsmDownloaderDialog

        dialog = OsmDownloaderDialog(self.iface.mainWindow(), self.iface)
        dialog.show()  # non modal

    def show_geonode_uploader(self):
        """Show the Geonode uploader dialog."""
        from safe.gui.tools.geonode_uploader import GeonodeUploaderDialog

        dialog = GeonodeUploaderDialog(self.iface.mainWindow())
        dialog.show()  # non modal

    def add_osm_layer(self):
        """Add OSM tile layer to the map.

        This uses a gdal wrapper around the OSM tile service - see the
        WorldOSM.gdal file for how it is constructed.
        """
        path = resources_path('osm', 'WorldOSM.gdal')
        layer = QgsRasterLayer(path, self.tr('OpenStreetMap'))
        registry = QgsMapLayerRegistry.instance()

        # Try to add it as the last layer in the list
        # False flag prevents layer being added to legend
        registry.addMapLayer(layer, False)
        root = QgsProject.instance().layerTreeRoot()
        index = len(root.findLayers()) + 1
        # LOGGER.info('Inserting layer %s at position %s' % (
        #    layer.source(), index))
        root.insertLayer(index, layer)
        QgsMapLayerRegistry.instance().addMapLayer(layer)

    def show_definitions(self):
        """Show InaSAFE Definitions (a report showing all key metadata)."""
        from safe.gui.tools.help_dialog import HelpDialog
        from safe.gui.tools.help import definitions_help
        dialog = HelpDialog(
            self.iface.mainWindow(),
            definitions_help.definitions_help())
        dialog.show()  # non modal

    def show_field_mapping(self):
        """Show InaSAFE Field Mapping."""
        from safe.gui.tools.field_mapping_dialog import FieldMappingDialog
        dialog = FieldMappingDialog(
            parent=self.iface.mainWindow(),
            iface=self.iface,)
        if dialog.exec_():  # modal
            LOGGER.debug('Show field mapping accepted')
            self.dock_widget.layer_changed(self.iface.activeLayer())
        else:
            LOGGER.debug('Show field mapping not accepted')

    def show_metadata_converter(self):
        """Show InaSAFE Metadata Converter."""
        from safe.gui.tools.metadata_converter_dialog import (
            MetadataConverterDialog)
        dialog = MetadataConverterDialog(
            parent=self.iface.mainWindow(),
            iface=self.iface,
        )
        dialog.exec_()

    def show_multi_exposure(self):
        """Show InaSAFE Multi Exposure."""
        from safe.gui.tools.multi_exposure_dialog import MultiExposureDialog
        dialog = MultiExposureDialog(
            self.iface.mainWindow(), self.iface)
        dialog.exec_()  # modal

    def add_petabencana_layer(self):
        """Add petabencana layer to the map.

        This uses the PetaBencana API to fetch the latest floods in JK. See
        https://data.petabencana.id/floods
        """
        from safe.gui.tools.peta_bencana_dialog import PetaBencanaDialog
        dialog = PetaBencanaDialog(self.iface.mainWindow(), self.iface)
        dialog.show()  # non modal

    def show_batch_runner(self):
        """Show the batch runner dialog."""
        from safe.gui.tools.batch.batch_dialog import BatchDialog

        dialog = BatchDialog(
            parent=self.iface.mainWindow(),
            iface=self.iface,
            dock=self.dock_widget)
        dialog.exec_()  # modal

    def save_scenario(self):
        """Save current scenario to text file."""
        from safe.gui.tools.save_scenario import SaveScenarioDialog

        dialog = SaveScenarioDialog(
            iface=self.iface,
            dock=self.dock_widget)
        dialog.save_scenario()

    def layer_changed(self, layer):
        """Enable or disable keywords editor icon when active layer changes.

        :param layer: The layer that is now active.
        :type layer: QgsMapLayer
        """
        if not layer:
            enable_keyword_wizard = False
        elif not hasattr(layer, 'providerType'):
            enable_keyword_wizard = False
        elif layer.providerType() == 'wms':
            enable_keyword_wizard = False
        else:
            enable_keyword_wizard = True

        try:
            if layer:
                if is_raster_layer(layer):
                    enable_field_mapping_tool = False
                else:
                    keywords = KeywordIO().read_keywords(layer)
                    keywords_version = keywords.get('keyword_version')
                    if not keywords_version:
                        supported = False
                    else:
                        supported = (
                            is_keyword_version_supported(keywords_version))
                    if not supported:
                        enable_field_mapping_tool = False
                    else:
                        layer_purpose = keywords.get('layer_purpose')

                        if not layer_purpose:
                            enable_field_mapping_tool = False
                        else:
                            if layer_purpose == layer_purpose_exposure['key']:
                                layer_subcategory = keywords.get('exposure')
                            elif layer_purpose == layer_purpose_hazard['key']:
                                layer_subcategory = keywords.get('hazard')
                            else:
                                layer_subcategory = None
                            field_groups = get_field_groups(
                                layer_purpose, layer_subcategory)
                            if len(field_groups) == 0:
                                # No field group, disable field mapping tool.
                                enable_field_mapping_tool = False
                            else:
                                enable_field_mapping_tool = True
            else:
                enable_field_mapping_tool = False
        except (KeywordNotFoundError, NoKeywordsFoundError, MetadataReadError):
            # No keywords, disable field mapping tool.
            enable_field_mapping_tool = False

        self.action_keywords_wizard.setEnabled(enable_keyword_wizard)
        self.action_field_mapping.setEnabled(enable_field_mapping_tool)

    def shortcut_f7(self):
        """Executed when user press F7 - will show the shakemap importer."""
        self.show_shakemap_importer()
