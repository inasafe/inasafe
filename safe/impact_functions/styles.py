"""Library of styles that can be used by impact functions

E.g.

from impact_functions.styles import flood_population_style as style_info
from impact_functions.core import get_function_title

# Create raster object with this style and return
R = Raster(I,
           projection=inundation.get_projection(),
           geotransform=inundation.get_geotransform(),
           name='Penduduk yang %s' % (get_function_title(self)),
           keywords={'impact_summary': impact_summary},
           style_info=style_info)
return R

"""

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
