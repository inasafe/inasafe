# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid **QGIS plugin implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import sys
import os
import logging

from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.utilities import is_raster_layer


LOGGER = logging.getLogger('InaSAFE')


# Import the PyQt and QGIS libraries
# noinspection PyPackageRequirements
from PyQt4.QtCore import (
    QLocale,
    QTranslator,
    QCoreApplication,
    Qt,
    QSettings
)
# noinspection PyPackageRequirements
from PyQt4.QtGui import QAction, QIcon, QApplication, QMessageBox
try:
    # When upgrading, using the plugin manager, you may get an error when
    # doing the following import, so we wrap it in a try except
    # block and then display a friendly message to restart QGIS
    # noinspection PyUnresolvedReferences
    from safe_qgis.exceptions import (
        TranslationLoadError,
        UnsupportedProviderError,
        NoKeywordsFoundError,
        InvalidParameterError)
except ImportError:
    # Note we use translate directly but the string may still not translate
    # at this early stage since the i18n setup routines have not been called
    # yet.
    # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
    myWarning = QCoreApplication.translate(
        'Plugin', 'Please restart QGIS to use this plugin.')
    # noinspection PyTypeChecker,PyArgumentList
    QMessageBox.warning(
        None, 'InaSAFE', myWarning)


# noinspection PyUnresolvedReferences
class Plugin:
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
        self.action_import_dialog = None
        self.action_save_scenario = None
        self.action_batch_runner = None
        self.action_shake_converter = None
        self.action_minimum_needs = None
        self.action_impact_merge_dlg = None
        self.key_action = None
        self.action_function_browser = None
        self.action_options = None
        self.action_keywords_dialog = None
        self.action_keywords_wizard = None
        self.translator = None
        self.toolbar = None
        self.actions = []  # list of all QActions we create for InaSAFE
        self.action_dock = None
        self.action_toggle_rubberbands = None
        #print self.tr('InaSAFE')
        # For enable/disable the keyword editor icon
        self.iface.currentLayerChanged.connect(self.layer_changed)

    #noinspection PyArgumentList
    def change_i18n(self, new_locale):
        """Change internationalisation for the plugin.

        Override the system locale  and then see if we can get a valid
        translation file for whatever locale is effectively being used.

        :param new_locale: the new locale i.e. 'id', 'af', etc.
        :type new_locale: str

        :raises: TranslationLoadException
        """

        os.environ['LANG'] = str(new_locale)

        LOGGER.debug('%s %s %s' % (
            new_locale,
            QLocale.system().name(),
            os.environ['LANG']))

        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        translation_path = os.path.join(
            root, 'safe_qgis', 'i18n',
            'inasafe_' + str(new_locale) + '.qm')

        if os.path.exists(translation_path):
            self.translator = QTranslator()
            result = self.translator.load(translation_path)
            if not result:
                message = 'Failed to load translation for %s' % new_locale
                raise TranslationLoadError(message)
            # noinspection PyTypeChecker,PyCallByClass
            QCoreApplication.installTranslator(self.translator)

        LOGGER.debug('%s %s' % (
            translation_path,
            os.path.exists(translation_path)))

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

    def add_action(self, action, add_to_toolbar=True):
        """Add a toolbar icon to the InaSAFE toolbar.

        :param action: The action that should be added to the toolbar.
        :type action: QAction

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the InaSAFE toolbar. Defaults to True.
        :type add_to_toolbar: bool

        """
        # store in the class list of actions for easy plugin unloading
        self.actions.append(action)
        self.iface.addPluginToMenu(self.tr('InaSAFE'), action)
        if add_to_toolbar:
            self.toolbar.addAction(action)

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
        # Import dock here as it needs to be imported AFTER i18n is set up
        from safe_qgis.widgets.dock import Dock
        self.dock_widget = None
        #--------------------------------------
        # Create action for plugin dockable window (show/hide)
        #--------------------------------------
        # pylint: disable=W0201
        self.action_dock = QAction(
            QIcon(':/plugins/inasafe/icon.svg'),
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

        #--------------------------------------
        # Create action for keywords editor
        #--------------------------------------
        self.action_keywords_dialog = QAction(
            QIcon(':/plugins/inasafe/show-keyword-editor.svg'),
            self.tr('InaSAFE Keyword Editor'),
            self.iface.mainWindow())
        self.action_keywords_dialog.setStatusTip(self.tr(
            'Open InaSAFE keywords editor'))
        self.action_keywords_dialog.setWhatsThis(self.tr(
            'Open InaSAFE keywords editor'))
        self.action_keywords_dialog.setEnabled(False)

        self.action_keywords_dialog.triggered.connect(
            self.show_keywords_editor)

        self.add_action(self.action_keywords_dialog)

        #--------------------------------------
        # Create action for keywords creation wizard
        #--------------------------------------
        self.action_keywords_wizard = QAction(
            QIcon(':/plugins/inasafe/show-keyword-wizard.svg'),
            self.tr('InaSAFE Keywords Creation Wizard'),
            self.iface.mainWindow())
        self.action_keywords_wizard.setStatusTip(self.tr(
            'Open InaSAFE keywords creation wizard'))
        self.action_keywords_wizard.setWhatsThis(self.tr(
            'Open InaSAFE keywords creation wizard'))
        self.action_keywords_wizard.setEnabled(False)

        self.action_keywords_wizard.triggered.connect(
            self.show_keywords_wizard)

        self.add_action(self.action_keywords_wizard)

        #--------------------------------------
        # Create action for options dialog
        #--------------------------------------
        self.action_options = QAction(
            QIcon(':/plugins/inasafe/configure-inasafe.svg'),
            self.tr('InaSAFE Options'), self.iface.mainWindow())
        self.action_options.setStatusTip(self.tr(
            'Open InaSAFE options dialog'))
        self.action_options.setWhatsThis(self.tr(
            'Open InaSAFE options dialog'))
        self.action_options.triggered.connect(self.show_options)

        self.add_action(self.action_options)

        #--------------------------------------
        # Create action for impact functions doc dialog
        #--------------------------------------
        self.action_function_browser = QAction(
            QIcon(':/plugins/inasafe/show-impact-functions.svg'),
            self.tr('InaSAFE Impact Functions Browser'),
            self.iface.mainWindow())
        self.action_function_browser.setStatusTip(self.tr(
            'Open InaSAFE Impact Functions Browser'))
        self.action_function_browser.setWhatsThis(self.tr(
            'Open InaSAFE Impact Functions Browser'))
        self.action_function_browser.triggered.connect(
            self.show_function_browser)

        self.add_action(self.action_function_browser)

        # Short cut for Open Impact Functions Doc
        self.key_action = QAction("Test Plugin", self.iface.mainWindow())
        self.iface.registerMainWindowAction(self.key_action, "F7")
        self.key_action.triggered.connect(self.shortcut_f7)

        #---------------------------------------
        # Create action for minimum needs dialog
        #---------------------------------------
        self.action_minimum_needs = QAction(
            QIcon(':/plugins/inasafe/show-minimum-needs.svg'),
            self.tr('InaSAFE Minimum Needs Tool'), self.iface.mainWindow())
        self.action_minimum_needs.setStatusTip(self.tr(
            'Open InaSAFE minimum needs tool'))
        self.action_minimum_needs.setWhatsThis(self.tr(
            'Open InaSAFE minimum needs tool'))
        self.action_minimum_needs.triggered.connect(self.show_minimum_needs)

        self.add_action(self.action_minimum_needs)

        #---------------------------------------
        # Create action for converter dialog
        #---------------------------------------
        self.action_shake_converter = QAction(
            QIcon(':/plugins/inasafe/show-converter-tool.svg'),
            self.tr('InaSAFE Converter'), self.iface.mainWindow())
        self.action_shake_converter.setStatusTip(self.tr(
            'Open InaSAFE Converter'))
        self.action_shake_converter.setWhatsThis(self.tr(
            'Open InaSAFE Converter'))
        self.action_shake_converter.triggered.connect(
            self.show_shakemap_importer)

        self.add_action(self.action_shake_converter)

        #---------------------------------------
        # Create action for batch runner dialog
        #---------------------------------------
        self.action_batch_runner = QAction(
            QIcon(':/plugins/inasafe/show-batch-runner.svg'),
            self.tr('InaSAFE Batch Runner'), self.iface.mainWindow())
        self.action_batch_runner.setStatusTip(self.tr(
            'Open InaSAFE Batch Runner'))
        self.action_batch_runner.setWhatsThis(self.tr(
            'Open InaSAFE Batch Runner'))
        self.action_batch_runner.triggered.connect(self.show_batch_runner)

        self.add_action(self.action_batch_runner)

        #---------------------------------------
        # Create action for batch runner dialog
        #---------------------------------------
        self.action_save_scenario = QAction(
            QIcon(':/plugins/inasafe/save-as-scenario.svg'),
            self.tr('Save current scenario'), self.iface.mainWindow())

        message = self.tr('Save current scenario to text file')
        self.action_save_scenario.setStatusTip(message)
        self.action_save_scenario.setWhatsThis(message)
        # noinspection PyUnresolvedReferences
        self.action_save_scenario.triggered.connect(self.save_scenario)
        self.add_action(self.action_save_scenario)

        #--------------------------------------
        # Create action for import OSM Dialog
        #--------------------------------------
        self.action_import_dialog = QAction(
            QIcon(':/plugins/inasafe/show-osm-download.svg'),
            self.tr('InaSAFE OpenStreetMap Downloader'),
            self.iface.mainWindow())
        self.action_import_dialog.setStatusTip(self.tr(
            'InaSAFE OpenStreetMap Downloader'))
        self.action_import_dialog.setWhatsThis(self.tr(
            'InaSAFE OpenStreetMap Downloader'))
        self.action_import_dialog.triggered.connect(self.show_osm_downloader)

        self.add_action(self.action_import_dialog)

        #--------------------------------------
        # Create action for impact layer merge Dialog
        #--------------------------------------
        self.action_impact_merge_dlg = QAction(
            QIcon(':/plugins/inasafe/show-impact-merge.svg'),
            self.tr('InaSAFE Impact Layer Merge'),
            self.iface.mainWindow())
        self.action_impact_merge_dlg.setStatusTip(self.tr(
            'InaSAFE Impact Layer Merge'))
        self.action_impact_merge_dlg.setWhatsThis(self.tr(
            'InaSAFE Impact Layer Merge'))
        self.action_impact_merge_dlg.triggered.connect(self.show_impact_merge)

        self.add_action(self.action_impact_merge_dlg)

        #--------------------------------------
        # create dockwidget and tabify it with the legend
        #--------------------------------------
        self.dock_widget = Dock(self.iface)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        myLegendTab = self.iface.mainWindow().findChild(QApplication, 'Legend')

        if myLegendTab:
            self.iface.mainWindow().tabifyDockWidget(
                myLegendTab, self.dock_widget)
            self.dock_widget.raise_()

        #
        # Hook up a slot for when the dock is hidden using its close button
        # or  view-panels
        #
        self.dock_widget.visibilityChanged.connect(self.toggle_inasafe_action)
        # pylint: disable=W0201

        #---------------------------------------
        # Create action for toggling rubber bands
        #---------------------------------------
        self.action_toggle_rubberbands = QAction(
            QIcon(':/plugins/inasafe/toggle-rubber-bands.svg'),
            self.tr('Toggle scenario outlines'), self.iface.mainWindow())

        message = self.tr('Toggle rubber bands showing scenarion extents.')
        self.action_toggle_rubberbands.setStatusTip(message)
        self.action_toggle_rubberbands.setWhatsThis(message)
        # Set initial state
        self.action_toggle_rubberbands.setCheckable(True)
        settings = QSettings()
        flag = bool(settings.value(
            'inasafe/showRubberBands', False, type=bool))
        self.action_toggle_rubberbands.setChecked(flag)
        # noinspection PyUnresolvedReferences
        self.action_toggle_rubberbands.triggered.connect(
            self.dock_widget.toggle_rubber_bands)
        self.add_action(self.action_toggle_rubberbands)

    # noinspection PyMethodMayBeStatic
    def clear_modules(self):
        """Unload inasafe functions and try to return QGIS to before InaSAFE.
        """
        from safe.impact_functions import core

        core.unload_plugins()
        # next lets force remove any inasafe related modules
        modules = []
        for myModule in sys.modules:
            if 'inasafe' in myModule:
                # Check if it is really one of our modules i.e. exists in the
                #  plugin directory
                tokens = myModule.split('.')
                path = ''
                for myToken in tokens:
                    path += os.path.sep + myToken
                parent = os.path.abspath(os.path.join(
                    __file__, os.path.pardir, os.path.pardir))
                full_path = os.path.join(parent, path + '.py')
                if os.path.exists(os.path.abspath(full_path)):
                    LOGGER.debug('Removing: %s' % myModule)
                    modules.append(myModule)
        for myModule in modules:
            del (sys.modules[myModule])
        for myModule in sys.modules:
            if 'inasafe' in myModule:
                print myModule

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
        for myAction in self.actions:
            self.iface.removePluginMenu(self.tr('InaSAFE'), myAction)
            self.iface.removeToolBarIcon(myAction)
        self.iface.mainWindow().removeDockWidget(self.dock_widget)
        self.iface.mainWindow().removeToolBar(self.toolbar)
        self.dock_widget.setVisible(False)
        self.dock_widget.destroy()
        self.iface.currentLayerChanged.disconnect(self.layer_changed)

        self.clear_modules()

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

    def show_minimum_needs(self):
        """Show the minimum needs dialog."""
        # import here only so that it is AFTER i18n set up
        from safe_qgis.tools.minimum_needs import MinimumNeeds

        dialog = MinimumNeeds(self.iface.mainWindow())
        dialog.exec_()  # modal

    def show_impact_merge(self):
        """Show the impact layer merge dialog."""
        # import here only so that it is AFTER i18n set up
        from safe_qgis.tools.impact_merge_dialog import ImpactMergeDialog

        dialog = ImpactMergeDialog(self.iface.mainWindow())
        dialog.exec_()  # modal

    def show_options(self):
        """Show the options dialog."""
        # import here only so that it is AFTER i18n set up
        from safe_qgis.tools.options_dialog import OptionsDialog

        dialog = OptionsDialog(
            self.iface,
            self.dock_widget,
            self.iface.mainWindow())
        dialog.exec_()  # modal

    def show_keywords_editor(self):
        """Show the keywords editor."""
        # import here only so that it is AFTER i18n set up
        from safe_qgis.tools.keywords_dialog import KeywordsDialog

        # Next block is a fix for #776
        if self.iface.activeLayer() is None:
            return

        try:
            keyword_io = KeywordIO()
            keyword_io.read_keywords(self.iface.activeLayer())
        except UnsupportedProviderError:
            # noinspection PyUnresolvedReferences,PyCallByClass
            # noinspection PyTypeChecker,PyArgumentList
            QMessageBox.warning(
                None,
                self.tr('Unsupported layer type'),
                self.tr(
                    'The layer you have selected cannot be used for '
                    'analysis because its data type is unsupported.'))
            return
        # End of fix for #776
        # Fix for #793
        except NoKeywordsFoundError:
            # we will create them from scratch in the dialog
            pass
        # End of fix for #793
        # Fix for filtered-layer
        except InvalidParameterError, e:
            # noinspection PyTypeChecker,PyTypeChecker
            QMessageBox.warning(
                None,
                self.tr('Invalid Layer'),
                e.message)
            return

        dialog = KeywordsDialog(
            self.iface.mainWindow(),
            self.iface,
            self.dock_widget)
        dialog.exec_()  # modal

    def show_keywords_wizard(self):
        """Show the keywords creation wizard."""
        # import here only so that it is AFTER i18n set up
        from safe_qgis.tools.wizard_dialog import WizardDialog

        if self.iface.activeLayer() is None:
            return
        dialog = WizardDialog(
            self.iface.mainWindow(),
            self.iface,
            self.dock_widget)
        dialog.exec_()  # modal

    def show_function_browser(self):
        """Show the impact function browser tool."""
        # import here only so that it is AFTER i18n set up
        from safe_qgis.tools.function_browser import FunctionBrowser

        dialog = FunctionBrowser(self.iface.mainWindow())
        dialog.exec_()  # modal

    def show_shakemap_importer(self):
        """Show the converter dialog."""
        # import here only so that it is AFTER i18n set up
        from safe_qgis.tools.shake_grid.shakemap_importer import (
            ShakemapImporter)

        dialog = ShakemapImporter(self.iface.mainWindow())
        dialog.exec_()  # modal

    def show_osm_downloader(self):
        """Show the OSM buildings downloader dialog."""
        from safe_qgis.tools.osm_downloader import OsmDownloader

        dialog = OsmDownloader(self.iface.mainWindow(), self.iface)
        dialog.exec_()  # modal

    def show_batch_runner(self):
        """Show the batch runner dialog."""
        from safe_qgis.tools.batch.batch_dialog import BatchDialog

        dialog = BatchDialog(
            parent=self.iface.mainWindow(),
            iface=self.iface,
            dock=self.dock_widget)
        dialog.exec_()  # modal

    def save_scenario(self):
        """Save current scenario to text file"""
        from safe_qgis.tools.save_scenario import SaveScenarioDialog

        dialog = SaveScenarioDialog(
            iface=self.iface,
            dock=self.dock_widget)
        dialog.save_scenario()

    def _disable_keyword_tools(self):
        """Internal helper to disable the keyword and wizard actions."""
        self.action_keywords_dialog.setEnabled(False)
        self.action_keywords_wizard.setEnabled(False)

    def layer_changed(self, layer):
        """Enable or disable keywords editor icon when active layer changes.

        :param layer: The layer that is now active.
        :type layer: QgsMapLayer
        """
        if not layer:
            self._disable_keyword_tools()
            return
        if not hasattr(layer, 'providerType'):
            self._disable_keyword_tools()
            return
        if layer.providerType() == 'wms':
            self._disable_keyword_tools()
            return
        if is_raster_layer(layer) and layer.bandCount() > 1:
            self._disable_keyword_tools()
            return

        self.action_keywords_dialog.setEnabled(True)
        self.action_keywords_wizard.setEnabled(True)

    def shortcut_f7(self):
        """Executed when user press F7 - will show the shakemap importer."""
        self.show_shakemap_importer()
