"""Library of styles that can be used by impact functions

E.g.

from impact_functions.styles import flood_population_style as style_info

# Create raster object with this style and return
R = Raster(I,
           projection=inundation.get_projection(),
           geotransform=inundation.get_geotransform(),
           name='Penduduk yang %s' % (self.plugin_name.lower()),
           keywords={'impact_summary': impact_summary},
           style_info=style_info)
return R

"""
from storage.utilities import ugettext as _

# Flood population impact raster style
style_classes = [dict(colour='#FFFFFF', quantity=2, transparency=100),
                 dict(label=_('Low'), colour='#38A800', quantity=5,
                      transparency=0),
                 dict(colour='#79C900', quantity=10, transparency=0),
                 dict(colour='#CEED00', quantity=20, transparency=0),
                 dict(label=_('Medium'), colour='#FFCC00', quantity=50,
                      transparency=0),
                 dict(colour='#FF6600', quantity=100, transparency=0),
                 dict(colour='#FF0000', quantity=200, transparency=0),
                 dict(label=_('High'), colour='#7A0000', quantity=300,
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
#                 dict(label=_('High'), colour='#500000', quantity=100,
#                      transparency=0)]
#earthquake_fatality_style = dict(target_field=None,
#                                 style_classes=style_classes)

#style_classes = [dict(colour='#65FF00', quantity=1.085168, transparency=100, label=_('Low')),
#                 dict(colour='#A1FF0B', quantity=1.686112, transparency=0),
#                 dict(colour='#EAFF15', quantity=2.287056, transparency=0),
#                 dict(colour='#FAFF19', quantity=2.888001, transparency=0),
#                 dict(colour='#FEFF21', quantity=3.488945, transparency=0),
#                 dict(colour='#FFFB23', quantity=4.089890, transparency=0),
#                 dict(colour='#FFFA2A', quantity=4.690834, transparency=0, label=_('Mid')),
#                 dict(colour='#FFBC50', quantity=5.291779, transparency=0),
#                 dict(colour='#FF6053', quantity=5.892723, transparency=0),
#                 dict(colour='#FF4038', quantity=6.493667, transparency=0),
#                 dict(colour='#FF4190', quantity=7.094612, transparency=0),
#                 dict(colour='#ED14B0', quantity=7.695556, transparency=0),
#                 dict(colour='#800A90', quantity=8.296501, transparency=0, label=_('High'))]

style_classes = [dict(colour='#EEFFEE', quantity=0.01, transparency=100, label=_('Low')),
                 dict(colour='#38A800', quantity=1.05, transparency=0),
                 dict(colour='#79C900', quantity=2.08, transparency=0),
                 dict(colour='#CEED00', quantity=3.12, transparency=0),
                 dict(colour='#FFCC00', quantity=4.15, transparency=0, label=_('Mid')),
                 dict(colour='#FF6600', quantity=5.19, transparency=0),
                 dict(colour='#FF0000', quantity=6.22, transparency=0),
                 dict(colour='#7A0000', quantity=7.26, transparency=0),
                 dict(colour='#660000', quantity=8.30, transparency=0, label=_('High'))]
earthquake_fatality_style = dict(target_field=None,
                                 style_classes=style_classes)
