# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
 **Styling Tests.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@kartoza.com'
__date__ = '17/10/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import unittest
import os

from safe.utilities.styling import (
    set_vector_graduated_style,
    setRasterStyle,
    add_extrema_to_style,
    mmi_colour)
from safe.test.utilities import (
    standard_data_path,
    load_test_vector_layer,
    load_layer,
    get_qgis_app,
    clone_shp_layer)
from safe.common.exceptions import StyleError

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class StylingTest(unittest.TestCase):
    """Tests for qgis styling related functions.
    """

    def setUp(self):
        os.environ['LANG'] = 'en'

    def tearDown(self):
        pass

    def test_issue126(self):
        """Test that non integer transparency ranges fail gracefully.
        .. seealso:: https://github.com/AIFDR/inasafe/issues/126
        """
        # This dataset has all cells with value 1.3
        data_path = standard_data_path('other', 'issue126.tif')
        layer, _ = load_layer(data_path)

        # Note the float quantity values below
        style_info = {
            'style_classes': [
                dict(colour='#38A800', quantity=1.1, transparency=100),
                dict(colour='#38A800', quantity=1.4, transparency=0),
                dict(colour='#79C900', quantity=10.1, transparency=0)]}

        try:
            setRasterStyle(layer, style_info)
        except Exception, e:
            message = (
                'Setting style info with float based ranges should fail '
                'gracefully.')
            e.args = (e.args[0] + message,)
            raise
        # Now validate the transparency values were set to 255 because
        # they are floats and we cant specify pixel ranges to floats
        # Note we don't test on the exact interval because 464c6171dd55
        value1 = layer.renderer().rasterTransparency().alphaValue(1.2)
        value2 = layer.renderer().rasterTransparency().alphaValue(1.5)
        message = ('Transparency should be ignored when style class '
                   'quantities are floats')
        assert value1 == value2 == 255, message

        # Now run the same test again for int intervals
        style_info['style_classes'] = [
            dict(colour='#38A800', quantity=2, transparency=100),
            dict(colour='#38A800', quantity=4, transparency=0),
            dict(colour='#79C900', quantity=10, transparency=0)]
        message = ('Setting style info with generate valid transparent '
                   'pixel entries.')
        try:
            setRasterStyle(layer, style_info)
        except:
            raise Exception(message)
        # Now validate the transparency values were set to 255 because
        # they are floats and we cant specify pixel ranges to floats
        value1 = layer.renderer().rasterTransparency().alphaValue(1)
        value2 = layer.renderer().rasterTransparency().alphaValue(3)
        message1 = message + 'Expected 0 got %i' % value1
        message2 = message + 'Expected 255 got %i' % value2
        assert value1 == 0, message1
        assert value2 == 255, message2

        # Verify that setRasterStyle doesn't break when floats coincide with
        # integers
        # See https://github.com/AIFDR/inasafe/issues/126#issuecomment-5978416
        style_info['style_classes'] = [
            dict(colour='#38A800', quantity=2.0, transparency=100),
            dict(colour='#38A800', quantity=4.0, transparency=0),
            dict(colour='#79C900', quantity=10.0, transparency=0)]

        try:
            setRasterStyle(layer, style_info)
        except Exception, e:  # pylint: disable=broad-except
            message = (
                'Broken: Setting style info with generate valid transparent '
                'floating point pixel entries such as 2.0, 3.0')
            e.args = (e.args[0] + message,)
            raise

    def test_transparency_of_minimum_value(self):
        """Test that transparency of minimum value works when set to 100%
        """
        # This dataset has all cells with value 1.3
        data_path = standard_data_path('other', 'issue126.tif')
        layer, _ = load_layer(data_path)

        # Note the float quantity values below
        style_info = {
            'style_classes': [
                {'colour': '#FFFFFF', 'transparency': 100, 'quantity': 0.0},
                {'colour': '#38A800', 'quantity': 0.038362596547925065,
                 'transparency': 0, 'label': u'Rendah [0 orang/sel]'},
                {'colour': '#79C900', 'transparency': 0,
                 'quantity': 0.07672519309585013},
                {'colour': '#CEED00', 'transparency': 0,
                 'quantity': 0.1150877896437752},
                {'colour': '#FFCC00', 'quantity': 0.15345038619170026,
                 'transparency': 0, 'label': u'Sedang [0 orang/sel]'},
                {'colour': '#FF6600', 'transparency': 0,
                 'quantity': 0.19181298273962533},
                {'colour': '#FF0000', 'transparency': 0,
                 'quantity': 0.23017557928755039},
                {'colour': '#7A0000', 'quantity': 0.26853817583547546,
                 'transparency': 0, 'label': u'Tinggi [0 orang/sel]'}]}

        try:
            setRasterStyle(layer, style_info)
        except Exception, e:
            message = '\nCould not create raster style'
            e.args = (e.args[0] + message,)
            raise

        # message = ('Should get a single transparency class for first style '
        #             'class')
        transparency_list = (
            layer.renderer().rasterTransparency().
            transparentSingleValuePixelList())

        # 2 because there is a default transparency for value = 0
        self.assertEqual(len(transparency_list), 2)

    def test_issue_121(self):
        """Test that point symbol size can be set from style (issue 121).
        .. seealso:: https://github.com/AIFDR/inasafe/issues/121
        """
        layer = load_test_vector_layer(
            'hazard', 'volcano_point.geojson', clone=True)

        # Note the float quantity values below
        style_info = {
            'target_field': 'KEPADATAN',
            'style_classes': [
                {'opacity': 1, 'max': 200, 'colour': '#fecc5c',
                 'min': 45, 'label': 'Low', 'size': 1},
                {'opacity': 1, 'max': 350, 'colour': '#fd8d3c',
                 'min': 201, 'label': 'Medium', 'size': 2},
                {'opacity': 1, 'max': 539, 'colour': '#f31a1c',
                 'min': 351, 'label': 'High', 'size': 3}]}

        # print 'Setting style with point sizes should work.'
        set_vector_graduated_style(layer, style_info)

        # Now validate the size values were set as expected

        # new symbology - subclass of QgsFeatureRendererV2 class
        renderer = layer.rendererV2()
        layer_type = renderer.type()
        assert layer_type == 'graduatedSymbol'
        size = 1
        for renderer_range in renderer.ranges():
            symbol = renderer_range.symbol()
            symbol_layer = symbol.symbolLayer(0)
            actual_size = symbol_layer.size()
            message = ((
                'Expected symbol layer 0 for range %s to have'
                ' a size of %s, got %s') % (size, size, actual_size))
            assert size == actual_size, message
            size += 1

    def test_issue230(self):
        """Verify that we give informative errors when style is not correct
           .. seealso:: https://github.com/AIFDR/inasafe/issues/230
        """
        vector_layer = clone_shp_layer(
            name='polygons_for_styling',
            include_keywords=True,
            source_directory=standard_data_path('impact'))

        style = {
            'legend_title': u'Population Count',
            'target_field': 'population',
            'style_classes':
                [
                    {
                        'transparency': 0,
                        'min': [0],  # <--intentionally broken list not number!
                        'max': 139904.08186340332,
                        'colour': '#FFFFFF',
                        'size': 1,
                        'label': u'Nil'},
                    {
                        'transparency': 0,
                        'min': 139904.08186340332,
                        'max': 279808.16372680664,
                        'colour': '#38A800',
                        'size': 1,
                        'label': u'Low'},
                    {
                        'transparency': 0,
                        'min': 279808.16372680664,
                        'max': 419712.24559020996,
                        'colour': '#79C900',
                        'size': 1,
                        'label': u'Low'},
                    {
                        'transparency': 0,
                        'min': 419712.24559020996,
                        'max': 559616.32745361328,
                        'colour': '#CEED00',
                        'size': 1,
                        'label': u'Low'},
                    {
                        'transparency': 0,
                        'min': 559616.32745361328,
                        'max': 699520.4093170166,
                        'colour': '#FFCC00',
                        'size': 1,
                        'label': u'Medium'},
                    {
                        'transparency': 0,
                        'min': 699520.4093170166,
                        'max': 839424.49118041992,
                        'colour': '#FF6600',
                        'size': 1,
                        'label': u'Medium'},
                    {
                        'transparency': 0,
                        'min': 839424.49118041992,
                        'max': 979328.57304382324,
                        'colour': '#FF0000',
                        'size': 1,
                        'label': u'Medium'},
                    {
                        'transparency': 0,
                        'min': 979328.57304382324,
                        'max': 1119232.6549072266,
                        'colour': '#7A0000',
                        'size': 1,
                        'label': u'High'}]}
        try:
            set_vector_graduated_style(vector_layer, style)
        except StyleError:
            # Exactly what should have happened
            return
        except Exception, e:  # pylint: disable=broad-except
            print str(e)
        assert False, 'Incorrect handling of broken styles'

    def test_add_min_max_to_style(self):
        """Test our add min max to style function."""
        myClasses = [dict(colour='#38A800', quantity=2, transparency=0),
                     dict(colour='#38A800', quantity=5, transparency=50),
                     dict(colour='#79C900', quantity=10, transparency=50),
                     dict(colour='#CEED00', quantity=20, transparency=50),
                     dict(colour='#FFCC00', quantity=50, transparency=34),
                     dict(colour='#FF6600', quantity=100, transparency=77),
                     dict(colour='#FF0000', quantity=200, transparency=24),
                     dict(colour='#7A0000', quantity=300, transparency=22)]
        myExpectedClasses = [
            {'max': 2.0, 'colour': '#38A800', 'min': 0.0, 'transparency': 0,
             'quantity': 2},
            {'max': 5.0, 'colour': '#38A800', 'min': 2.0000000000000004,
             'transparency': 50, 'quantity': 5},
            {'max': 10.0, 'colour': '#79C900', 'min': 5.0000000000000009,
             'transparency': 50, 'quantity': 10},
            {'max': 20.0, 'colour': '#CEED00', 'min': 10.000000000000002,
             'transparency': 50, 'quantity': 20},
            {'max': 50.0, 'colour': '#FFCC00', 'min': 20.000000000000004,
             'transparency': 34, 'quantity': 50},
            {'max': 100.0, 'colour': '#FF6600', 'min': 50.000000000000007,
             'transparency': 77, 'quantity': 100},
            {'max': 200.0, 'colour': '#FF0000', 'min': 100.00000000000001,
             'transparency': 24, 'quantity': 200},
            {'max': 300.0, 'colour': '#7A0000', 'min': 200.00000000000003,
             'transparency': 22, 'quantity': 300}]

        myActualClasses = add_extrema_to_style(myClasses)
        self.maxDiff = None
        self.assertListEqual(myExpectedClasses, myActualClasses)

    def test_mmi_colour(self):
        """Test that we can get a colour given an mmi number."""
        values = range(0, 12)
        myExpectedResult = ['#FFFFFF', '#FFFFFF', '#209fff', '#00cfff',
                            '#55ffff', '#aaffff', '#fff000', '#ffa800',
                            '#ff7000', '#ff0000', '#D00', '#800']
        myResult = []
        for value in values:
            myResult.append(mmi_colour(value))
        message = 'Got:\n%s\nExpected:\n%s\n' % (myResult, myExpectedResult)
        assert myResult == myExpectedResult, message

if __name__ == '__main__':
    suite = unittest.makeSuite(StylingTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
