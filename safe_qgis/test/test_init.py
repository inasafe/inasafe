# coding=utf-8
"""**Tests for map creation in QGIS plugin.**

"""

__author__ = 'Tim Sutton <tim@linfiniti.com>'
__revision__ = '$Format:%H$'
__date__ = '17/10/2010'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import unittest
import logging
import ConfigParser

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

        myFilePath = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir,
                         '../metadata.txt'))
        LOGGER.info(myFilePath)
        myMetadata = []
        parser = ConfigParser.ConfigParser()
        parser.optionxform = str
        parser.read(myFilePath)
        message = 'Cannot find a section named "general" in %s' % myFilePath
        assert parser.has_section('general'), message
        myMetadata.extend(parser.items('general'))

        for md in myRequiredMetadata:
            message = 'Cannot find myMetadata "%s" '\
                        'in myMetadata source (%s).' % (md, myFilePath)
            assert md in dict(myMetadata) or dict(myMetadata)[md], \
                message

if __name__ == '__main__':
    unittest.main()
