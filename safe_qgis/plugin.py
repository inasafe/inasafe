"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **QGIS plugin implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import logging

LOGGER = logging.getLogger('InaSAFE')

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import (QObject,
                          QLocale,
                          QTranslator,
                          SIGNAL,
                          QCoreApplication,
                          Qt,
                          QSettings,
                          QVariant)
from PyQt4.QtGui import QAction, QIcon, QApplication, QMessageBox
try:
    # When upgrading, using the plugin manager, you may get an error when
    # doing the following import, so we wrap it in a try except
    # block and then display a friendly message to restart QGIS
    from safe_qgis.exceptions import TranslationLoadError
except ImportError:
    # Note these strings cant be translated.
    QMessageBox.warning(
        None, 'InaSAFE', 'Please restart QGIS to use this plugin.')
import custom_logging


class Plugin:
    """The QGIS interface implementation for the Risk in a box plugin.

    This class acts as the 'glue' between QGIS and our custom logic.
    It creates a toolbar and menubar entry and launches the InaSAFE user
    interface if these are activated.
    """

    def __init__(self, iface):
        """Class constructor.

        On instantiation, the plugin instance will be assigned a copy
        of the QGIS iface object which will allow this plugin to access and
        manipulate the running QGIS instance that spawned it.

        Args:
            iface - a Quantum GIS QGisAppInterface instance. This instance
                is automatically passed to the plugin by QGIS when it loads the
                plugin.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """

        # Save reference to the QGIS interface
        self.iface = iface
        self.translator = None
        self.toolbar = None
        self.actions = []  # list of all QActions we create for InaSAFE
        self.setupI18n()
        #print self.tr('InaSAFE')
        custom_logging.setupLogger()

    #noinspection PyArgumentList
    def setupI18n(self, thePreferredLocale=None):
        """Setup internationalisation for the plugin.

        See if QGIS wants to override the system locale
        and then see if we can get a valid translation file
        for whatever locale is effectively being used.

        Args:
           thePreferredLocale - optional parameter which if set
           will override any other way of determining locale..
        Returns:
           None.
        Raises:
           TranslationLoadException
        """
        myOverrideFlag = QSettings().value(
            'locale/overrideFlag',
            QVariant(False)).toBool()

        if thePreferredLocale is not None:
            myLocaleName = thePreferredLocale
        elif myOverrideFlag:
            myLocaleName = QSettings().value('locale/userLocale',
                                             QVariant('')).toString()
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
            thePreferredLocale,
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
            QCoreApplication.installTranslator(self.translator)

        LOGGER.debug('%s %s' % (
            myTranslationPath,
            os.path.exists(myTranslationPath)))

    def tr(self, theString):
        """Get the translation for a string.

        We implement this ourself since we do not inherit QObject.

        Args:
           theString - string for translation.
        Returns:
           Translated version of theString.
        Raises:
           no exceptions explicitly raised.
        """
        return QCoreApplication.translate('Plugin', theString)

    def addToolBarIcon(self, theAction):
        """Add a toolbar icon to the InaSAFE toolbar.

        Args:
            theAction QAction - the action that should be added to the toolbar.

        Returns:
            None

        Raises:
            None
        """
        self.toolbar.addAction(theAction)

    #noinspection PyCallByClass
    def initGui(self):
        """Gui initialisation procedure (for QGIS plugin api).

        This method is called by QGIS and should be used to set up
        any graphical user interface elements that should appear in QGIS by
        default (i.e. before the user performs any explicit action with the
        plugin).

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        self.toolbar = self.iface.addToolBar('InaSAFE')
        # Import dock here as it needs to be imported AFTER i18n is set up
        from safe_qgis.dock import Dock
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
        QObject.connect(
            self.actionDock, SIGNAL('triggered()'),
            self.showHideDockWidget)
        # add to plugin toolbar
        self.addToolBarIcon(self.actionDock)
        # add to plugin menu
        self.iface.addPluginToMenu(
            self.tr('InaSAFE'),
            self.actionDock)

        self.actions.append(self.actionDock)

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

        QObject.connect(
            self.actionKeywordsDialog, SIGNAL('triggered()'),
            self.showKeywordsEditor)

        self.addToolBarIcon(self.actionKeywordsDialog)
        self.iface.addPluginToMenu(
            self.tr('InaSAFE'),
            self.actionKeywordsDialog)

        self.actions.append(self.actionKeywordsDialog)

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
        QObject.connect(
            self.actionResetDock, SIGNAL('triggered()'),
            self.resetDock)

        self.addToolBarIcon(self.actionResetDock)
        self.iface.addPluginToMenu(
            self.tr('InaSAFE'),
            self.actionResetDock)

        self.actions.append(self.actionResetDock)

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
        QObject.connect(
            self.actionOptions, SIGNAL('triggered()'),
            self.showOptions)

        self.addToolBarIcon(self.actionOptions)
        self.iface.addPluginToMenu(
            self.tr('InaSAFE'),
            self.actionOptions)

        self.actions.append(self.actionOptions)

        #--------------------------------------
        # Create action for impact functions doc dialog
        #--------------------------------------
        self.actionImpactFunctionsDoc = QAction(
            QIcon(':/plugins/inasafe/show-impact-functions.svg'),
            self.tr('InaSAFE Impact Functions Browser'),
            self.iface.mainWindow())
        self.actionImpactFunctionsDoc.setStatusTip(self.tr(
            'Open InaSAFE Impact Functions Browser'))
        self.actionImpactFunctionsDoc.setWhatsThis(self.tr(
            'Open InaSAFE Impact Functions Browser'))
        QObject.connect(
            self.actionImpactFunctionsDoc, SIGNAL('triggered()'),
            self.showImpactFunctionsDoc)

        self.addToolBarIcon(self.actionImpactFunctionsDoc)
        self.iface.addPluginToMenu(self.tr('InaSAFE'),
                                   self.actionImpactFunctionsDoc)

        # Short cut for Open Impact Functions Doc
        self.keyAction = QAction("Test Plugin", self.iface.mainWindow())
        self.iface.registerMainWindowAction(self.keyAction, "F7")
        QObject.connect(self.keyAction, SIGNAL("triggered()"),
                        self.keyActionF7)

        self.actions.append(self.actionImpactFunctionsDoc)

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
        QObject.connect(self.actionMinimumNeeds, SIGNAL('triggered()'),
                        self.showMinimumNeeds)

        self.addToolBarIcon(self.actionMinimumNeeds)
        self.iface.addPluginToMenu(self.tr('InaSAFE'),
                                   self.actionMinimumNeeds)

        self.actions.append(self.actionMinimumNeeds)

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
        QObject.connect(self.actionConverter, SIGNAL('triggered()'),
                        self.showConverter)

        self.addToolBarIcon(self.actionConverter)
        self.iface.addPluginToMenu(self.tr('InaSAFE'),
                                   self.actionConverter)

        self.actions.append(self.actionConverter)

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
        QObject.connect(
            self.actionBatchRunner,
            SIGNAL('triggered()'),
            self.showScriptDialog)

        self.addToolBarIcon(self.actionBatchRunner)
        self.iface.addPluginToMenu(
            self.tr('InaSAFE'), self.actionBatchRunner)

        self.actions.append(self.actionBatchRunner)

        #---------------------------------------
        # Create action for batch runner dialog
        #---------------------------------------
        self.actionSaveScenario = QAction(
            QIcon(':/plugins/inasafe/save-as-scenario.svg'),
            self.tr('Save current scenario'), self.iface.mainWindow())

        myMessage = self.tr('Save current scenario to text file')
        self.actionSaveScenario.setStatusTip(myMessage)
        self.actionSaveScenario.setWhatsThis(myMessage)
        self.actionSaveScenario.triggered.connect(self.saveScenario)

        self.addToolBarIcon(self.actionSaveScenario)
        self.iface.addPluginToMenu(
            self.tr('InaSAFE'), self.actionSaveScenario)

        self.actions.append(self.actionSaveScenario)

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
        QObject.connect(
            self.actionImportDlg, SIGNAL('triggered()'),
            self.showImportDlg)

        self.addToolBarIcon(self.actionImportDlg)
        self.iface.addPluginToMenu(
            self.tr('InaSAFE'),
            self.actionImportDlg)

        self.actions.append(self.actionImportDlg)

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
        # Hook up a slot for when the current layer is changed
        #
        QObject.connect(
            self.iface,
            SIGNAL("currentLayerChanged(QgsMapLayer*)"),
            self.layerChanged)

        #
        # Hook up a slot for when the dock is hidden using its close button
        # or  view-panels
        #
        QObject.connect(
            self.dockWidget,
            SIGNAL("visibilityChanged (bool)"),
            self.toggleActionDock)

        # pylint: disable=W0201

    def unload(self):
        """Gui breakdown procedure (for QGIS plugin api).

        This method is called by QGIS and should be used to *remove*
        any graphical user interface elements that should appear in QGIS.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        # Remove the plugin menu item and icon
        for myAction in self.actions:
            self.iface.removePluginMenu(self.tr('InaSAFE'), myAction)
            self.iface.removeToolBarIcon(myAction)
        self.iface.mainWindow().removeDockWidget(self.dockWidget)
        self.iface.mainWindow().removeToolBar(self.toolbar)
        self.dockWidget.setVisible(False)
        self.dockWidget.destroy()
        self.toolbar.destroy()
        QObject.disconnect(
            self.iface,
            SIGNAL("currentLayerChanged(QgsMapLayer*)"),
            self.layerChanged)

    def toggleActionDock(self, checked):
        """check or uncheck the toggle inaSAFE toolbar button.

        This slot is called when the user hides the inaSAFE panel using its
        close button or using view->panels

        .. see also:: :func:`Plugin.initGui`.

        Args:
           checked - if actionDock has to be checked or not
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """

        self.actionDock.setChecked(checked)

    # Run method that performs all the real work
    def showHideDockWidget(self):
        """Show or hide the dock widget.

        This slot is called when the user clicks the toolbar icon or
        menu item associated with this plugin. It will hide or show
        the dock depending on its current state.

        .. see also:: :func:`Plugin.initGui`.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        if self.dockWidget.isVisible():
            self.dockWidget.setVisible(False)
        else:
            self.dockWidget.setVisible(True)
            self.dockWidget.raise_()

    def showMinimumNeeds(self):
        """Show the minimum needs dialog.

        This slot is called when the user clicks the minimum needs toolbar
        icon or menu item associated with this plugin.

        .. see also:: :func:`Plugin.initGui`.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        # import here only so that it is AFTER i18n set up
        from safe_qgis.minimum_needs import MinimumNeeds

        myDialog = MinimumNeeds(self.iface.mainWindow())
        myDialog.show()

    def showOptions(self):
        """Show the options dialog.

        This slot is called when the user clicks the options toolbar
        icon or menu item associated with this plugin

        .. see also:: :func:`Plugin.initGui`.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        # import here only so that it is AFTER i18n set up
        from safe_qgis.options_dialog import OptionsDialog

        myDialog = OptionsDialog(
            self.iface.mainWindow(),
            self.iface,
            self.dockWidget)
        myDialog.show()

    def showKeywordsEditor(self):
        """Show the keywords editor.

        This slot is called when the user clicks the keyword editor toolbar
        icon or menu item associated with this plugin

        .. see also:: :func:`Plugin.initGui`.

        Args:
           None.

        Returns:
           None.

        Raises:
           no exceptions explicitly raised.
        """
        # import here only so that it is AFTER i18n set up
        from safe_qgis.keywords_dialog import KeywordsDialog

        if self.iface.activeLayer() is None:
            return
        myDialog = KeywordsDialog(
            self.iface.mainWindow(),
            self.iface,
            self.dockWidget)
        myDialog.setModal(True)
        myDialog.show()

    def showImpactFunctionsDoc(self):
        """Show the impact function doc

        This slot is called when the user clicks the impact functions
        toolbar icon or menu item associated with this plugin

        .. see also:: :func:`Plugin.initGui`.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        # import here only so that it is AFTER i18n set up
        from safe_qgis.impact_functions_doc import ImpactFunctionsDoc

        myDialog = ImpactFunctionsDoc(self.iface.mainWindow())
        myDialog.show()

    def showConverter(self):
        """Show the converter dialog.

        This slot is called when the user clicks the impact functions
        toolbar icon or menu item associated with this plugin

        .. see also:: :func:`Plugin.initGui`.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        # import here only so that it is AFTER i18n set up
        from safe_qgis.converter_dialog import ConverterDialog

        myDialog = ConverterDialog(self.iface.mainWindow())
        myDialog.show()

    def showImportDlg(self):
        from safe_qgis.import_dialog import ImportDialog

        dlg = ImportDialog(self.iface.mainWindow(), self.iface)
        dlg.setModal(True)
        dlg.show()

    def showScriptDialog(self):
        """Show Script Dialog"""
        from safe_qgis.script_dialog import ScriptDialog

        myDialog = ScriptDialog(self.iface.mainWindow(), self.iface)
        myDialog.setModal(True)
        myDialog.show()

    def saveScenario(self):
        """Save current scenario to text file"""
        self.dockWidget.saveCurrentScenario()

    def resetDock(self):
        """Reset the dock to its default state.

        This slot is called when the user clicks the reset icon in the toolbar
        or the reset menu item associated with this plugin

        .. see also:: :func:`Plugin.initGui`.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        self.dockWidget.getLayers()

    def layerChanged(self, theLayer):
        """Enable or disable the keywords editor icon.

        This slot is called when the user clicks the keyword editor toolbar
        icon or menu item associated with this plugin

        .. see also:: :func:`Plugin.initGui`.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        if theLayer is None:
            self.actionKeywordsDialog.setEnabled(False)
        else:
            self.actionKeywordsDialog.setEnabled(True)
        self.dockWidget.layerChanged(theLayer)

    def keyActionF7(self):
        '''Executed when user press F7'''
        self.showConverter()
