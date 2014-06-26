# coding=utf-8
"""QGIS plugin test suite.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(pardir)


from PyQt4.QtGui import QWidget

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.gui import QgsMapCanvas
from safe.common.qgis_interface import QgisInterface
from safe_qgis.plugin import Plugin
from safe_qgis.safe_interface import safeTr


class PluginTest(unittest.TestCase):
    """Test suite for InaSAFE QGis plugin"""

    def Xtest_setupI18n(self):
        """Gui translations are working."""

        myUntranslatedString = 'Show/hide InaSAFE dock widget'
        myExpectedString = 'Tampilkan/hilangkan widget InaSAFE'
        myParent = QWidget()
        myCanvas = QgsMapCanvas(myParent)
        myIface = QgisInterface(myCanvas)
        myPlugin = Plugin(myIface)
        myPlugin.change_i18n('id')
        myTranslation = myPlugin.tr(myUntranslatedString)
        message = '\nTranslated: %s\nGot: %s\nExpected: %s' % \
                    (myUntranslatedString, myTranslation, myExpectedString)
        assert myTranslation == myExpectedString, message

    def Xtest_ImpactFunctionI18n(self):
        """Library translations are working."""
        # Import this late so that i18n setup is already in place

        # Test indonesian too
        myCanvas = QgsMapCanvas(PARENT)
        myIface = QgisInterface(myCanvas)
        myPlugin = Plugin(myIface)
        myPlugin.change_i18n('id')  # indonesian
        myExpectedString = 'Letusan gunung berapi'
        myTranslation = safeTr('A volcano eruption')
        message = '\nTranslated: %s\nGot: %s\nExpected: %s' % \
                    ('A volcano eruption', myTranslation, myExpectedString)
        assert myTranslation == myExpectedString, message

    def Xtest_Afrikaans(self):
        """Test that Afrikaans translations are working"""

        # Note this has really bad side effects - lots of tests suddenly start
        # breaking when this test is enabled....disabled for now, but I have
        # left the test here for now as it illustrates one potential avenue
        # that can be pursued if dynamically changing the language to unit test
        # different locales ever becomes a requirement.
        # Be sure nose tests all run cleanly before reintroducing this!

        # This is part test and part demonstrator of how to reload inasafe
        # Now see if the same function is delivered for the function
        # Because of the way impact plugins are loaded in inasafe
        # (see http://effbot.org/zone/metaclass-plugins.htm)
        # lang in the context of the ugettext function in inasafe libs
        # must be imported late so that i18n is set up already
        from safe.common.utilities import ugettext as tr
        myUntranslatedString = 'Temporarily Closed'
        myExpectedString = 'Tydelik gesluit'  # afrikaans
        myTranslation = tr(myUntranslatedString)
        message = '\nTranslated: %s\nGot: %s\nExpected: %s' % \
                    (myUntranslatedString, myTranslation, myExpectedString)
        assert myTranslation == myExpectedString, message
        myParent = QWidget()
        myCanvas = QgsMapCanvas(myParent)
        myIface = QgisInterface(myCanvas)
        # reload all inasafe modules so that i18n get picked up afresh
        # this is the part that produces bad side effects
        for myMod in sys.modules.values():
            try:
                if 'storage' in str(myMod) or 'impact' in str(myMod):
                    print 'Reloading:', str(myMod)
                    reload(myMod)
            except NameError:
                pass
        myPlugin = Plugin(myIface)
        myPlugin.change_i18n('af')  # afrikaans
        myLang = os.environ['LANG']
        assert myLang == 'af'
        from safe_qgis.safe_interface import get_safe_impact_function
        #myFunctions = get_safe_impact_function()
        #print myFunctions
        myFunctions = get_safe_impact_function('Tydelik gesluit')
        assert len(myFunctions) > 0

if __name__ == '__main__':
    unittest.main()
