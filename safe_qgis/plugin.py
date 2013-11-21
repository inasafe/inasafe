# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid **QGIS plugin implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import logging
from safe_qgis.utilities import custom_logging

LOGGER = logging.getLogger('InaSAFE')

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import sys
import os

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import (
    QLocale,
    QTranslator,
    QCoreApplication,
    Qt,
    QSettings)
from PyQt4.QtGui import QAction, QIcon, QApplication, QMessageBox
try:
    # When upgrading, using the plugin manager, you may get an error when
    # doing the following import, so we wrap it in a try except
    # block and then display a friendly message to restart QGIS
    # noinspection PyUnresolvedReferences
    from safe_qgis.exceptions import TranslationLoadError
except ImportError:
    # Note we use translate directly but the string may still not translate
    # at this early stage since the i18n setup routines have not been called
    # yet.
    # noinspection PyTypeChecker,PyArgumentList
    myWarning = QCoreApplication.translate(
        'Plugin', 'Please restart QGIS to use this plugin.')
    # noinspection PyTypeChecker,PyArgumentList
    QMessageBox.warning(
        None, 'InaSAFE', myWarning)


# noinspection PyUnresolvedReferences
class Plugin:
    """The QGIS interface implementation for the InaSAFE plugin.

    This class acts as the 'glue' between QGIS and our custom logic.
    It creates a toolbar and menubar entry and launches the InaSAFE user
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
        self.translator = None
        self.toolbar = None
        self.actions = []  # list of all QActions we create for InaSAFE
        self.setup_i18n()
        #print self.tr('InaSAFE')
        custom_logging.setup_logger()
        # For enable/disable the keyword editor icon
        self.iface.currentLayerChanged.connect(self.layer_changed)

    #noinspection PyArgumentList
    def setup_i18n(self, preferred_locale=None):
        """Setup internationalisation for the plugin.

        See if QGIS wants to override the system locale
        and then see if we can get a valid translation file
        for whatever locale is effectively being used.

        :param preferred_locale: If set will override any other way of
            determining locale.
        :type preferred_locale: str, None
        :raises: TranslationLoadException
        """
        myOverrideFlag = QSettings().value('locale/overrideFlag', False)

        if preferred_locale is not None:
            myLocaleName = preferred_locale
        elif myOverrideFlag:
            myLocaleName = QSettings().value('locale/userLocale', '')
        else:
            myLocaleName = QLocale.system().name()
            # NOTES: we split the locale name because we need the first two
            # character i.e. 'id', 'af, etc
            myLocaleName = str(myLocaleName).split('_')[0]

        # Also set the system locale to the user overridden local
        # so that the inasafe library functions gettext will work
        # .. see:: :py:func:`common.utilities`
        os.environ['LANG'] = str(myLocaleName)

        LOGGER.debug('%s %s %s %s' % (
            preferred_locale,
            myOverrideFlag,
            QLocale.system().name(),
            os.environ['LANG']))

        myRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        myTranslationPath = os.path.join(
            myRoot, 'safe_qgis', 'i18n',
            'inasafe_' + str(myLocaleName) + '.qm')

        if os.path.exists(myTranslationPath):
            self.translator = QTranslator()
            myResult = self.translator.load(myTranslationPath)
            if not myResult:
                myMessage = 'Failed to load translation for %s' % myLocaleName
                raise TranslationLoadError(myMessage)
            # noinspection PyTypeChecker
            QCoreApplication.installTranslator(self.translator)

        LOGGER.debug('%s %s' % (
            myTranslationPath,
            os.path.exists(myTranslationPath)))

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList
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

    #noinspection PyCallByClass
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
        self.dockWidget = None
        #--------------------------------------
        # Create action for plugin dockable window (show/hide)
        #--------------------------------------
        # pylint: disable=W0201
        self.actionDock = QAction(
            QIcon(':/plugins/inasafe/icon.svg'),
            self.tr('Toggle InaSAFE Dock'), self.iface.mainWindow())
        self.actionDock.setObjectName('InaSAFEDockToggle')
        self.actionDock.setStatusTip(self.tr(
            'Show/hide InaSAFE dock widget'))
        self.actionDock.setWhatsThis(self.tr(
            'Show/hide InaSAFE dock widget'))
        self.actionDock.setCheckable(True)
        self.actionDock.setChecked(True)
        self.actionDock.triggered.connect(self.toggle_dock_visibility)
        self.add_action(self.actionDock)

        #--------------------------------------
        # Create action for keywords editor
        #--------------------------------------
        self.actionKeywordsDialog = QAction(
            QIcon(':/plugins/inasafe/show-keyword-editor.svg'),
            self.tr('InaSAFE Keyword Editor'),
            self.iface.mainWindow())
        self.actionKeywordsDialog.setStatusTip(self.tr(
            'Open InaSAFE keywords editor'))
        self.actionKeywordsDialog.setWhatsThis(self.tr(
            'Open InaSAFE keywords editor'))
        self.actionKeywordsDialog.setEnabled(False)

        self.actionKeywordsDialog.triggered.connect(self.show_keywords_editor)

        self.add_action(self.actionKeywordsDialog)

        #--------------------------------------
        # Create action for reset icon
        #--------------------------------------
        self.actionResetDock = QAction(
            QIcon(':/plugins/inasafe/reset-dock.svg'),
            self.tr('Reset Dock'), self.iface.mainWindow())
        self.actionResetDock.setStatusTip(self.tr(
            'Reset the InaSAFE Dock'))
        self.actionResetDock.setWhatsThis(self.tr(
            'Reset the InaSAFE Dock'))
        self.actionResetDock.triggered.connect(self.reset_dock)

        self.add_action(self.actionResetDock)

        #--------------------------------------
        # Create action for options dialog
        #--------------------------------------
        self.actionOptions = QAction(
            QIcon(':/plugins/inasafe/configure-inasafe.svg'),
            self.tr('InaSAFE Options'), self.iface.mainWindow())
        self.actionOptions.setStatusTip(self.tr(
            'Open InaSAFE options dialog'))
        self.actionOptions.setWhatsThis(self.tr(
            'Open InaSAFE options dialog'))
        self.actionOptions.triggered.connect(self.show_options)

        self.add_action(self.actionOptions)

        #--------------------------------------
        # Create action for impact functions doc dialog
        #--------------------------------------
        self.actionFunctionBrowser = QAction(
            QIcon(':/plugins/inasafe/show-impact-functions.svg'),
            self.tr('InaSAFE Impact Functions Browser'),
            self.iface.mainWindow())
        self.actionFunctionBrowser.setStatusTip(self.tr(
            'Open InaSAFE Impact Functions Browser'))
        self.actionFunctionBrowser.setWhatsThis(self.tr(
            'Open InaSAFE Impact Functions Browser'))
        self.actionFunctionBrowser.triggered.connect(
            self.show_function_browser)

        self.add_action(self.actionFunctionBrowser)

        # Short cut for Open Impact Functions Doc
        self.keyAction = QAction("Test Plugin", self.iface.mainWindow())
        self.iface.registerMainWindowAction(self.keyAction, "F7")
        self.keyAction.triggered.connect(self.shortcut_f7)

        #---------------------------------------
        # Create action for minimum needs dialog
        #---------------------------------------
        self.actionMinimumNeeds = QAction(
            QIcon(':/plugins/inasafe/show-minimum-needs.svg'),
            self.tr('InaSAFE Minimum Needs Tool'), self.iface.mainWindow())
        self.actionMinimumNeeds.setStatusTip(self.tr(
            'Open InaSAFE minimum needs tool'))
        self.actionMinimumNeeds.setWhatsThis(self.tr(
            'Open InaSAFE minimum needs tool'))
        self.actionMinimumNeeds.triggered.connect(self.show_minimum_needs)

        self.add_action(self.actionMinimumNeeds)

        #---------------------------------------
        # Create action for converter dialog
        #---------------------------------------
        self.actionConverter = QAction(
            QIcon(':/plugins/inasafe/show-converter-tool.svg'),
            self.tr('InaSAFE Converter'), self.iface.mainWindow())
        self.actionConverter.setStatusTip(self.tr(
            'Open InaSAFE Converter'))
        self.actionConverter.setWhatsThis(self.tr(
            'Open InaSAFE Converter'))
        self.actionConverter.triggered.connect(self.show_shakemap_importer)

        self.add_action(self.actionConverter)

        #---------------------------------------
        # Create action for batch runner dialog
        #---------------------------------------
        self.actionBatchRunner = QAction(
            QIcon(':/plugins/inasafe/show-batch-runner.svg'),
            self.tr('InaSAFE Batch Runner'), self.iface.mainWindow())
        self.actionBatchRunner.setStatusTip(self.tr(
            'Open InaSAFE Batch Runner'))
        self.actionBatchRunner.setWhatsThis(self.tr(
            'Open InaSAFE Batch Runner'))
        self.actionBatchRunner.triggered.connect(self.show_batch_runner)

        self.add_action(self.actionBatchRunner)

        #---------------------------------------
        # Create action for batch runner dialog
        #---------------------------------------
        self.actionSaveScenario = QAction(
            QIcon(':/plugins/inasafe/save-as-scenario.svg'),
            self.tr('Save current scenario'), self.iface.mainWindow())

        myMessage = self.tr('Save current scenario to text file')
        self.actionSaveScenario.setStatusTip(myMessage)
        self.actionSaveScenario.setWhatsThis(myMessage)
        # noinspection PyUnresolvedReferences
        self.actionSaveScenario.triggered.connect(self.save_scenario)
        self.add_action(self.actionSaveScenario)

        #--------------------------------------
        # Create action for import OSM Dialog
        #--------------------------------------
        self.actionImportDlg = QAction(
            QIcon(':/plugins/inasafe/show-osm-download.svg'),
            self.tr('InaSAFE OpenStreetMap Downloader'),
            self.iface.mainWindow())
        self.actionImportDlg.setStatusTip(self.tr(
            'InaSAFE OpenStreetMap Downloader'))
        self.actionImportDlg.setWhatsThis(self.tr(
            'InaSAFE OpenStreetMap Downloader'))
        self.actionImportDlg.triggered.connect(self.show_osm_downloader)

        self.add_action(self.actionImportDlg)

        #--------------------------------------
        # create dockwidget and tabify it with the legend
        #--------------------------------------
        self.dockWidget = Dock(self.iface)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget)
        myLegendTab = self.iface.mainWindow().findChild(QApplication, 'Legend')

        if myLegendTab:
            self.iface.mainWindow().tabifyDockWidget(
                myLegendTab, self.dockWidget)
            self.dockWidget.raise_()

        #
        # Hook up a slot for when the dock is hidden using its close button
        # or  view-panels
        #
        self.dockWidget.visibilityChanged.connect(self.toggle_inasafe_action)

        # pylint: disable=W0201

    def clear_modules(self):
        """Unload inasafe functions and try to return QGIS to before InaSAFE.
        """
        from safe.impact_functions import core

        core.unload_plugins()
        # next lets force remove any inasafe related modules
        myModules = []
        for myModule in sys.modules:
            if 'inasafe' in myModule:
                # Check if it is really one of our modules i.e. exists in the
                #  plugin directory
                myTokens = myModule.split('.')
                myPath = ''
                for myToken in myTokens:
                    myPath += os.path.sep + myToken
                myParent = os.path.abspath(os.path.join(
                    __file__, os.path.pardir, os.path.pardir))
                myFullPath = os.path.join(myParent, myPath + '.py')
                if os.path.exists(os.path.abspath(myFullPath)):
                    LOGGER.debug('Removing: %s' % myModule)
                    myModules.append(myModule)
        for myModule in myModules:
            del (sys.modules[myModule])
        for myModule in sys.modules:
            if 'inasafe' in myModule:
                print myModule

        # Lets also clean up all the path additions that were made
        myPackagePath = os.path.abspath(os.path.join(
            os.path.dirname(__file__), os.path.pardir))
        LOGGER.debug('Path to remove: %s' % myPackagePath)
        # We use a list comprehension to ensure duplicate entries are removed
        LOGGER.debug(sys.path)
        sys.path = [y for y in sys.path if myPackagePath not in y]
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
        self.iface.mainWindow().removeDockWidget(self.dockWidget)
        self.iface.mainWindow().removeToolBar(self.toolbar)
        self.dockWidget.setVisible(False)
        self.dockWidget.destroy()
        self.iface.currentLayerChanged.disconnect(self.layer_changed)

        self.clear_modules()

    def toggle_inasafe_action(self, checked):
        """Check or uncheck the toggle inaSAFE toolbar button.

        This slot is called when the user hides the inaSAFE panel using its
        close button or using view->panels.

        :param checked: True if the dock should be shown, otherwise False.
        :type checked: bool
        """

        self.actionDock.setChecked(checked)

    # Run method that performs all the real work
    def toggle_dock_visibility(self):
        """Show or hide the dock widget."""
        if self.dockWidget.isVisible():
            self.dockWidget.setVisible(False)
        else:
            self.dockWidget.setVisible(True)
            self.dockWidget.raise_()

    def show_minimum_needs(self):
        """Show the minimum needs dialog."""
        # import here only so that it is AFTER i18n set up
        from safe_qgis.tools.minimum_needs import MinimumNeeds

        dialog = MinimumNeeds(self.iface.mainWindow())
        dialog.exec_()  # modal

    def show_options(self):
        """Show the options dialog."""
        # import here only so that it is AFTER i18n set up
        from safe_qgis.tools.options_dialog import OptionsDialog

        dialog = OptionsDialog(
            self.iface,
            self.dockWidget,
            self.iface.mainWindow())
        dialog.exec_()  # modal

    def show_keywords_editor(self):
        """Show the keywords editor."""
        # import here only so that it is AFTER i18n set up
        from safe_qgis.tools.keywords_dialog import KeywordsDialog

        if self.iface.activeLayer() is None:
            return
        dialog = KeywordsDialog(
            self.iface.mainWindow(),
            self.iface,
            self.dockWidget)
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
        from safe_qgis.tools.shakemap_importer import ShakemapImporter

        dialog = ShakemapImporter(self.iface.mainWindow())
        dialog.exec_()  # modal

    def show_osm_downloader(self):
        """Show the OSM buildings downloader dialog."""
        from safe_qgis.tools.osm_downloader import OsmDownloader

        dialog = OsmDownloader(self.iface.mainWindow(), self.iface)
        dialog.exec_()  # modal

    def show_batch_runner(self):
        """Show the batch runner dialog."""
        from safe_qgis.batch.batch_dialog import BatchDialog

        dialog = BatchDialog(
            parent=self.iface.mainWindow(),
            iface=self.iface,
            dock=self.dockWidget)
        dialog.exec_()  # modal

    def save_scenario(self):
        """Save current scenario to text file,"""
        self.dockWidget.save_current_scenario()

    def reset_dock(self):
        """Reset the dock to its default state."""
        self.dockWidget.get_layers()

    def layer_changed(self, layer):
        """Enable or disable keywords editor icon when active layer changes.
        :param layer: The layer that is now active.
        :type layer: QgsMapLayer
        """
        if layer is None:
            self.actionKeywordsDialog.setEnabled(False)
        else:
            self.actionKeywordsDialog.setEnabled(True)

    def shortcut_f7(self):
        """Executed when user press F7 - will show the shakemap importer."""
        self.show_shakemap_importer()
