# coding=utf-8
"""QGIS plugin test suite.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.utilities.i18n import tr
from safe.utilities.utilities import get_safe_impact_function

__author__ = 'tim@kartoza.com'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os

# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from qgis.gui import QgsMapCanvas
# noinspection PyUnresolvedReferences
import safe.test.sip_api_2
from PyQt4.QtGui import QWidget

from safe.test.utilities import get_qgis_app

# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gis.qgis_interface import QgisInterface
from safe.plugin import Plugin

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(pardir)


class PluginTest(unittest.TestCase):
    """Test suite for InaSAFE QGis plugin"""

    def Xtest_setup_i18n(self):
        """Gui translations are working."""

        unstranslated = 'Show/hide InaSAFE dock widget'
        expected = 'Tampilkan/hilangkan widget InaSAFE'
        parent = QWidget()
        canvas = QgsMapCanvas(parent)
        iface = QgisInterface(canvas)
        plugin = Plugin(iface)
        plugin.change_i18n('id')
        translation = plugin.tr(unstranslated)
        message = '\nTranslated: %s\nGot: %s\nExpected: %s' % \
            (unstranslated, translation, expected)
        assert translation == expected, message

    def Xtest_impact_function_i18n(self):
        """Library translations are working."""
        # Import this late so that i18n setup is already in place

        # Test indonesian too
        canvas = QgsMapCanvas(PARENT)
        iface = QgisInterface(canvas)
        plugin = Plugin(iface)
        plugin.change_i18n('id')  # indonesian
        expected = 'Letusan gunung berapi'
        translation = tr('A volcano eruption')
        message = '\nTranslated: %s\nGot: %s\nExpected: %s' % (
            'A volcano eruption', translation, expected)
        assert translation == expected, message

    def Xtest_afrikaans(self):
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
        # import PyQt4.QtCore.QObject.tr as tr
        untranslated = 'Temporarily Closed'
        expected = 'Tydelik gesluit'  # afrikaans
        translated = tr(untranslated)
        message = '\nTranslated: %s\nGot: %s\nExpected: %s' % \
                    (untranslated, translated, expected)
        assert translated == expected, message
        parent = QWidget()
        canvas = QgsMapCanvas(parent)
        iface = QgisInterface(canvas)
        # reload all inasafe modules so that i18n get picked up afresh
        # this is the part that produces bad side effects
        for mod in sys.modules.values():
            try:
                if 'storage' in str(mod) or 'impact' in str(mod):
                    print 'Reloading:', str(mod)
                    reload(mod)
            except NameError:
                pass
        plugin = Plugin(iface)
        plugin.change_i18n('af')  # afrikaans
        language = os.environ['LANG']
        assert language == 'af'
        # functions = get_safe_impact_function()
        # print functions
        functions = get_safe_impact_function('Tydelik gesluit')
        assert len(functions) > 0

if __name__ == '__main__':
    unittest.main()
