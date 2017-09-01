# coding=utf-8

import unittest
import os
import sys
from subprocess import Popen, PIPE


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestPythonPep(unittest.TestCase):

    def test_pep8(self):
        """Test if the code is PEP8 compliant."""
        if os.environ.get('ON_TRAVIS', False):
            root = './'
            command = ['make', 'pep8']
            output = Popen(command, stdout=PIPE, cwd=root).communicate()[0]
            default_number_lines = 5
        elif sys.platform.startswith('win'):
            root = '../../'
            command = [
                'pep8.exe',
                '--repeat',
                '--ignore=E203,E121,E122,E123,E124,E125,E126,E127,E128,E402',
                '--exclude=venv,pydev,safe_extras,keywords_dialog_base.py,'
                'wizard_dialog_base.py,dock_base.py,options_dialog_base.py,'
                'minimum_needs_configuration.py,resources_rc.py,help_base.py,'
                'xml_tools.py,system_tools.py,data_audit.py,'
                'data_audit_wrapper.py',
                'safe']
            # Shamelessly hardcoded path for now..TS
            path = (
                "C:\\PROGRA~1\\QGIS2~1.14\\apps\\Python27\\scripts")
            path = os.path.normpath(path)
            output = Popen(
                command,
                stdout=PIPE,
                cwd=root,
                executable=os.path.join(path, 'pep8.exe')).communicate()[0]
            default_number_lines = 0

        else:
            # OSX and linux just delegate to make
            root = '../../'
            command = ['make', 'pep8']
            output = Popen(command, stdout=PIPE, cwd=root).communicate()[0]
            default_number_lines = 5

        # make pep8 produces some extra lines by default.
        lines = len(output.splitlines()) - default_number_lines
        print output
        message = (
            'Hey mate, go back to your keyboard :) (expected %s, got %s '
            'lines from PEP8.)' % (default_number_lines, lines))
        self.assertEquals(lines, 0, message)

    # The test is broken on travis
    @unittest.skip('Bash command for pep257 is not found on travis')
    def test_pep257(self):
        """Test if docstrings are PEP257 compliant."""
        if os.environ.get('ON_TRAVIS', False):
            root = './'
            command = ['make', 'pep257']
            output = Popen(command, stdout=PIPE, cwd=root).communicate()[0]
            default_number_lines = 4
        elif sys.platform.startswith('win'):
            root = '../../'
            command = [
                'pep257',
                '--ignore=D100,D101,D102,D103,D104,D105,D200,D201,D202,D203,'
                'D204,D205,D206,D209,D210,D211,D300,D301,D302,D400,D401,D402,'
                'D403,D404',
                '--count',
                'safe/']
            # Shamelessly hardcoded path for now..TS
            path = (
                "C:\\PROGRA~1\\QGIS2~1.14\\apps\\Python27\\scripts")
            path = os.path.normpath(path)
            output = Popen(
                command,
                stdout=PIPE,
                cwd=root,
                executable=os.path.join(path, 'pep257.exe')).communicate()[0]
            default_number_lines = 1

        else:
            # OSX and linux just delegate to make
            root = '../../'
            command = ['make', 'pep257']
            output = Popen(command, stdout=PIPE, cwd=root).communicate()[0]
            default_number_lines = 6

        # make pep257 produces some extra lines by default.
        lines = len(output.splitlines()) - default_number_lines
        print output
        message = (
            'Hey mate, go back to your keyboard :) (expected %s, got %s '
            'lines from PEP257.)' % (default_number_lines, lines))
        self.assertEquals(lines, 0, message)
