"""**Tests for map creation in QGIS plugin.**

"""

__author__ = 'Tim Sutton <tim@linfiniti.com>'
__revision__ = '$Format:%H$'
__date__ = '17/10/2010'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import re
import unittest
import logging

LOGGER = logging.getLogger('InaSAFE')


class TestInit(unittest.TestCase):
    """Test that the plugin init is usable for QGIS.

    Based heavily on the validator class by Alessandro
    Passoti available here:

    http://github.com/qgis/qgis-django/blob/master/qgis-app/
             plugins/validator.py

    """

    def testReadInit(self):
        """Test that the plugin __init__ will validate on plugins.qgis.org."""

        # You should update this list according to the latest in
        # https://github.com/qgis/qgis-django/blob/master/qgis-app/
        #        plugins/validator.py

        myRequiredMetadata = ['name',
                              'description',
                              'version',
                              'qgisMinimumVersion',
                              'email',
                              'author']

        myFilePath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                  os.pardir,
                                  '__init__.py'))
        LOGGER.info(myFilePath)
        myFile = file(myFilePath, 'rt')
        myContent = myFile.read()
        myFile.close()
        myMetadata = []
        myCounter = 0
        myLines = myContent.split('\n')
        while myCounter < len(myLines):
            if re.search('def\s+([^\(]+)', myLines[myCounter]):
                myMatch = re.search('def\s+([^\(]+)',
                                  myLines[myCounter]).groups()[0]
                myCounter += 1
                while myCounter < len(myLines) and myLines[myCounter] != '':
                    if re.search('return\s+["\']?([^"\']+)["\']?',
                                 myLines[myCounter]):
                        myMetadata.append((myMatch,
                                re.search('return\s+["\']?([^"\']+)["\']?',
                                myLines[myCounter]).groups()[0]))
                        break
                    myCounter += 1
            myCounter += 1
        if not len(myMetadata):
            assert False, 'Metadata could not be read'

        for myItem in myRequiredMetadata:
            if not myItem in dict(myMetadata) or not dict(myMetadata)[myItem]:
                assert False, ('Cannot find myMetadata "%s" '
                'in myMetadata source (%s). Please bear in mind '
                'that the current implementation of the __init__.py '
                'validator is based on regular expressions, check that '
                'your myMetadata functions directly return myMetadata values '
                'as strings.') % (
                    myItem, dict(myMetadata).get('metadata_source'))

if __name__ == '__main__':
    unittest.main()
