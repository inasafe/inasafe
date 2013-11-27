"""Library of styles that can be used by impact functions

E.g.::

    from impact_functions.styles import flood_population_style as style_info
    from impact_functions.core import get_function_title

    # Create raster object with this style and return
    R = Raster(
        I,
        projection=inundation.get_projection(),
        geotransform=inundation.get_geotransform(),
        name='Penduduk yang %s' % (get_function_title(self)),
        keywords={'impact_summary': impact_summary},
        style_info=style_info)

    return R

"""

import colorsys
from safe.common.utilities import ugettext as tr

# Flood population impact raster style
style_classes = [dict(colour='#FFFFFF', quantity=2, transparency=100),
                 dict(label=tr('Low'), colour='#38A800', quantity=5,
                      transparency=0),
                 dict(colour='#79C900', quantity=10, transparency=0),
                 dict(colour='#CEED00', quantity=20, transparency=0),
                 dict(label=tr('Medium'), colour='#FFCC00', quantity=50,
                      transparency=0),
                 dict(colour='#FF6600', quantity=100, transparency=0),
                 dict(colour='#FF0000', quantity=200, transparency=0),
                 dict(label=tr('High'), colour='#7A0000', quantity=1100,
                      transparency=0)]
flood_population_style = dict(target_field=None,
                              legend_title=None,
                              style_classes=style_classes)

# Earthquake fatality raster style
# FIXME (Ole): The styler cannot handle floats yet. Issue #126
#style_classes = [dict(colour='#FFFFFF', quantity=0.0, transparency=100),
#                 dict(colour='#0000FF', quantity=4, transparency=0),
#                 dict(colour='#0000EE', quantity=6, transparency=0),
#                 dict(colour='#79C900', quantity=8, transparency=0),
#                 dict(colour='#79C900', quantity=17, transparency=0),
#                 dict(colour='#79C900', quantity=26, transparency=0),
#                 dict(colour='#CEED00', quantity=34, transparency=0),
#                 dict(colour='#FFCC00', quantity=43, transparency=0),
#                 dict(colour='#FF6600', quantity=52, transparency=0),
#                 dict(colour='#EE0000', quantity=61, transparency=0),
#                 dict(colour='#AA0000', quantity=69, transparency=0),
#                 dict(colour='#7A0000', quantity=78, transparency=0),
#                 dict(label=tr('High'), colour='#500000', quantity=100,
#                      transparency=0)]
#earthquake_fatality_style = dict(target_field=None,
#                                 style_classes=style_classes)

# Earthquake fatality raster style
# Obtain the min and max fatalities and scale accordingly
    #style_classes = [dict(colour='#FFFFFF', quantity=0.0, transparency=100),
    #            dict(colour='#F713FF', quantity=, transparency=20),
    #            dict(colour='#D50DC3', quantity=, transparency=20),
    #            dict(colour='#79C900', quantity=, transparency=20),
    #            dict(colour='#79C900', quantity=, transparency=20),
    #            dict(colour='#79C900', quantity=, transparency=20),
#            dict(colour='#CEED00', quantity=, transparency=20),


style_classes = [dict(colour='#EEFFEE', quantity=0.01, transparency=100,
                      label=tr('Low')),
                 dict(colour='#38A800', quantity=1.05, transparency=0),
                 dict(colour='#79C900', quantity=2.08, transparency=0),
                 dict(colour='#CEED00', quantity=3.12, transparency=0),
                 dict(colour='#FFCC00', quantity=4.15, transparency=0,
                      label=tr('Mid')),
                 dict(colour='#FF6600', quantity=5.19, transparency=0),
                 dict(colour='#FF0000', quantity=6.22, transparency=0),
                 dict(colour='#7A0000', quantity=7.26, transparency=0),
                 dict(colour='#660000', quantity=8.30, transparency=0,
                      label=tr('High'))]
earthquake_fatality_style = dict(target_field=None,
                                 style_classes=style_classes)


def categorical_style(target_field,
                      categories,
                      no_data_value,
                      no_data_label,
                      data_defined_saturation_field=None,
                      max_impact_value=None):
    """Style with equidistant hue and optional data defined saturation
    :param target_field: field name that needs to be classified
    :type: target_field, str

    :param categories: values of target_field
    :type: categories, list

    :param no_data_value: value for no data
    :type: no_data_value, int, str

    :param no_data_label: label for the no data category
    :type: no_data_label, str

    :param data_defined_saturation_field: field for saturation for the
        generated colors.
    :type: data_defined_saturation_field, None, str

    :param max_impact_value: maximum value in data_defined_saturation_field,
        used to normalize saturation values for the generated colors.
    :type: max_impact_value, int, float

    :returns: a dict with target_field, style_classes and style_type
    :rtype: dict
    """
    # Create style
    classes = []
    colors = generate_categorical_color_ramp(len(categories))

    for index, category in enumerate(categories):
        hsv = colors['hsv'][index]
        if category == no_data_value:
            label = no_data_label
        else:
            label = '%s %s' % (tr('Category'), category)
        style_class = dict(
            label=label,
            value=category,
            colour=colors['hex'][index],
            border_color=colors['hex'][index],
            border_width=0.8,
            transparency=0,
            size=1)

        if data_defined_saturation_field is not None:
            # expr is like 'color_hsv(270.0, "pop"/9807.0*100, 70.0)'
            expr = 'color_hsv(%s, "%s"/%s*100, %s)' % (
                hsv[0] * 360,
                data_defined_saturation_field,
                max_impact_value,
                hsv[2]*100)
            style_class.update({'data_defined': {'color': expr}})
        classes.append(style_class)

    style_info = dict(target_field=target_field,
                      style_classes=classes,
                      style_type='categorizedSymbol')
    return style_info


def generate_categorical_color_ramp(class_count,
                                    reverse_hue=True,
                                    saturation=0.5,
                                    value=0.7):
    """Makes a color ramp with equal HUE intervals. Sat and value are constant
    :param class_count: amount of hue steps (class count)
    :type: class_count, int

    :param reverse_hue: if true makes red the END, else the START of the scale
    :type: reverse_hue, bool

    :param saturation: saturation for the generated colors. this stays constant
    :type: saturation, float

    :param value: value for the generated colors. this stays constant
    :type: value, float

    :returns: a dict of list containing the HSV, RGB and HEX representation
        of the color ramp. some thing like this:
        {'hsv': [(1.0, 0.5, 0.7),
                (0.8, 0.5, 0.7),
                (0.6, 0.5, 0.7),
                (0.3999999999999999, 0.5, 0.7),
                (0.19999999999999996, 0.5, 0.7)],
        'rgb': [(178.5, 89.25, 89.25),
                (160.65000000000006, 89.25, 178.5),
                (89.25, 124.95000000000003, 178.5),
                (89.25, 178.5, 124.94999999999995),
                (160.65, 178.5, 89.25)],
        'hex': ['#b25959',
                '#a059b2',
                '#597cb2',
                '#59b27c',
                '#a0b259']}
    :rtype: dict
    """

    colors = {'hex': [],
              'rgb': [],
              'hsv': []}
    hue_step = 1 / float(class_count)

    for c in range(class_count):
        hue = c * hue_step
        if reverse_hue:
            hue = 1 - hue
        hsv_color = (hue, saturation, value)
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        rgb_color = (r * 255, g * 255, b * 255)
        hex_color = rgb_to_hex(rgb_color)
        colors['hex'].append(hex_color)
        colors['rgb'].append(rgb_color)
        colors['hsv'].append(hsv_color)
    print colors

    return colors


def hsv_to_hex(hsv):
    """Convert hue, saturation, value tuple to an hex sting.
    :param hsv: a (hue, saturation, value) tuple where hsv are 0-1
    :type: hsv, tuple

    :returns: the hexadecimal color string.
    :rtype: str
    """
    r, g, b = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    return rgb_to_hex((r * 255, g * 255, b * 255))


def rgb_to_hex(rgb):
    """Convert an rgb tuple in an hex sting.
    :param rgb: a (r, g, b) tuple where r, g, b are 0-255
    :type: rgb, tuple

    :returns: the hexadecimal color string.
    :rtype: str
    :see: http://stackoverflow.com/q/214359/#answer-214657"""

    return '#%02x%02x%02x' % rgb
