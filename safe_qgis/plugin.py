"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **QGIS plugin implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
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
from PyQt4.QtGui import QAction, QIcon, QApplication
from safe_qgis.exceptions import TranslationLoadException


# See if we can import pydev - see development docs for details
try:
    from pydevd import *  # pylint: disable=F0401
    print 'Remote debugging is enabled.'
    DEBUG = True
except ImportError:
    print 'Debugging was disabled'


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
        self.setupI18n()
        #print self.tr('InaSAFE')

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
           no exceptions explicitly raised.
        """
        myOverrideFlag = QSettings().value('locale/overrideFlag',
                                            QVariant(False)).toBool()
        myLocaleName = None
        if thePreferredLocale is not None:
            myLocaleName = thePreferredLocale
        elif myOverrideFlag:
            myLocaleName = QSettings().value('locale/userLocale',
                                             QVariant('')).toString()
        else:
            myLocaleName = QLocale.system().name()
        # Also set the system locale to the user overridden local
        # so that the inasafe library functions gettext will work
        # .. see:: :py:func:`common.utilities`
        os.environ['LANG'] = str(myLocaleName)

        myRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        myTranslationPath = os.path.join(myRoot, 'safe_qgis', 'i18n',
                        'inasafe_' + str(myLocaleName) + '.qm')
        if os.path.exists(myTranslationPath):
            self.translator = QTranslator()
            myResult = self.translator.load(myTranslationPath)
            if not myResult:
                myMessage = 'Failed to load translation for %s' % myLocaleName
                raise TranslationLoadException(myMessage)
            QCoreApplication.installTranslator(self.translator)

    def tr(self, theString):
        """We implement this ourself since we do not inherit QObject.

        Args:
           theString - string for translation.
        Returns:
           Translated version of theString.
        Raises:
           no exceptions explicitly raised.
        """
        return QCoreApplication.translate('Plugin', theString)

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
        # Import dock here as it needs to be imported AFTER i18n is set up
        from safe_qgis.dock import Dock
        self.dockWidget = None
        #--------------------------------------
        # Create action for plugin dockable window (show/hide)
        #--------------------------------------
        # pylint: disable=W0201
        self.actionDock = QAction(QIcon(':/plugins/inasafe/icon.png'),
                    self.tr('Toggle InaSAFE Dock'), self.iface.mainWindow())
        self.actionDock.setStatusTip(self.tr(
                            'Show/hide InaSAFE dock widget'))
        self.actionDock.setWhatsThis(self.tr(
                            'Show/hide InaSAFE dock widget'))
        self.actionDock.setCheckable(True)
        self.actionDock.setChecked(True)
        QObject.connect(self.actionDock, SIGNAL('triggered()'),
                        self.showHideDockWidget)
        # add to plugin toolbar
        self.iface.addToolBarIcon(self.actionDock)
        # add to plugin menu
        self.iface.addPluginToMenu(self.tr('InaSAFE'),
                                   self.actionDock)

        #--------------------------------------
        # Create action for keywords editor
        #--------------------------------------
        self.actionKeywordsDialog = QAction(
                            QIcon(':/plugins/inasafe/keywords.png'),
                            self.tr('Keyword Editor'), self.iface.mainWindow())
        self.actionKeywordsDialog.setStatusTip(self.tr(
                                    'Open the keywords editor'))
        self.actionKeywordsDialog.setWhatsThis(self.tr(
                                    'Open the keywords editor'))
        QObject.connect(self.actionKeywordsDialog, SIGNAL('triggered()'),
                        self.showKeywordsEditor)

        self.iface.addToolBarIcon(self.actionKeywordsDialog)
        self.iface.addPluginToMenu(self.tr('InaSAFE'),
                                   self.actionKeywordsDialog)
        #--------------------------------------
        # Create action for reset icon
        #--------------------------------------
        self.actionResetDock = QAction(
                            QIcon(':/plugins/inasafe/reload.png'),
                            self.tr('Reset Dock'), self.iface.mainWindow())
        self.actionResetDock.setStatusTip(self.tr(
                                    'Reset the InaSAFE Dock'))
        self.actionResetDock.setWhatsThis(self.tr(
                                    'Reset the InaSAFE Dock'))
        QObject.connect(self.actionResetDock, SIGNAL('triggered()'),
                        self.resetDock)

        self.iface.addToolBarIcon(self.actionResetDock)
        self.iface.addPluginToMenu(self.tr('InaSAFE'),
                                   self.actionResetDock)

        #--------------------------------------
        # Create action for options dialog
        #--------------------------------------
        self.actionOptions = QAction(
                        QIcon(':/plugins/inasafe/options.png'),
                        self.tr('InaSAFE Options'), self.iface.mainWindow())
        self.actionOptions.setStatusTip(self.tr(
                                    'Open InaSAFE options dialog'))
        self.actionOptions.setWhatsThis(self.tr(
                                    'Open InaSAFE options dialog'))
        QObject.connect(self.actionOptions, SIGNAL('triggered()'),
                        self.showOptions)

        self.iface.addToolBarIcon(self.actionOptions)
        self.iface.addPluginToMenu(self.tr('InaSAFE'),
                                   self.actionOptions)

        #--------------------------------------
        # Create action for impact functions doc dialog
        #--------------------------------------
        self.actionImpactFunctionsDoc = QAction(
                        QIcon(':/plugins/inasafe/functions-table.png'),
                        self.tr('InaSAFE Impact Functions Doc'),
                        self.iface.mainWindow())
        self.actionImpactFunctionsDoc.setStatusTip(self.tr(
                                    'Open InaSAFE impact functions doc'))
        self.actionImpactFunctionsDoc.setWhatsThis(self.tr(
                                    'Open InaSAFE impact functions doc'))
        QObject.connect(self.actionImpactFunctionsDoc, SIGNAL('triggered()'),
                        self.showImpactFunctionsDoc)

        self.iface.addToolBarIcon(self.actionImpactFunctionsDoc)
        self.iface.addPluginToMenu(self.tr('InaSAFE'),
                                   self.actionImpactFunctionsDoc)

        # Short cut for Open Impact Functions Doc
        self.keyAction = QAction("Test Plugin", self.iface.mainWindow())
        self.iface.registerMainWindowAction(self.keyAction, "F7")
        self.iface.addPluginToMenu("&Test plugins", self.keyAction)
        QObject.connect(self.keyAction, SIGNAL("triggered()"),
                        self.keyActionF7)

        #--------------------------------------
        # create dockwidget and tabify it with the legend
        #--------------------------------------
        self.dockWidget = Dock(self.iface)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)
        myLegendTab = self.iface.mainWindow().findChild(QApplication, 'Legend')
        if myLegendTab:
            self.iface.mainWindow().tabifyDockWidget(
                                            myLegendTab, self.dockWidget)
            self.dockWidget.raise_()

        #
        # Hook up a slot for when the current layer is changed
        #
        QObject.connect(self.iface,
            SIGNAL("currentLayerChanged(QgsMapLayer*)"),
            self.layerChanged)

        #
        # Hook up a slot for when the dock is hidden using its close button
        # or  view-panels
        #
        QObject.connect(self.dockWidget,
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
        self.iface.removePluginMenu(self.tr('InaSAFE'),
                                    self.actionDock)
        self.iface.removeToolBarIcon(self.actionDock)
        self.iface.removePluginMenu(self.tr('InaSAFE'),
                                    self.actionKeywordsDialog)
        self.iface.removeToolBarIcon(self.actionKeywordsDialog)
        self.iface.removePluginMenu(self.tr('InaSAFE'),
                                    self.actionResetDock)
        self.iface.removeToolBarIcon(self.actionResetDock)
        self.iface.removePluginMenu(self.tr('InaSAFE'),
                                    self.actionOptions)
        self.iface.removeToolBarIcon(self.actionOptions)
        self.iface.removePluginMenu(self.tr('InaSAFE'),
                                    self.actionImpactFunctionsDoc)
        self.iface.removeToolBarIcon(self.actionImpactFunctionsDoc)
        self.iface.mainWindow().removeDockWidget(self.dockWidget)
        self.dockWidget.setVisible(False)
        self.dockWidget.destroy()
        QObject.disconnect(self.iface,
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

        myDialog = OptionsDialog(self.iface.mainWindow(),
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
        myDialog = KeywordsDialog(self.iface.mainWindow(),
                                      self.iface,
                                      self.dockWidget)
        myDialog.show()

    def showImpactFunctionsDoc(self):
        """Show the keywords editor.

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
        self.showImpactFunctionsDoc()
