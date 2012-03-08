"""Library of styles that can be used by impact functions

E.g.

from impact_functions.styles import flood_population_style as style_info

# Create raster object with this style and return
R = Raster(I,
           projection=inundation.get_projection(),
           geotransform=inundation.get_geotransform(),
           name='Penduduk yang %s' % (self.plugin_name.lower()),
           keywords={'caption': caption},
           style_info=style_info)
return R

"""

# Flood population impact raster style
style_classes = [dict(colour='#38A800', quantity=2, transparency=100),
                 dict(colour='#38A800', quantity=5, transparency=0),
                 dict(colour='#79C900', quantity=10, transparency=0),
                 dict(colour='#CEED00', quantity=20, transparency=0),
                 dict(colour='#FFCC00', quantity=50, transparency=0),
                 dict(colour='#FF6600', quantity=100, transparency=0),
                 dict(colour='#FF0000', quantity=200, transparency=0),
                 dict(colour='#7A0000', quantity=300, transparency=0)]
flood_population_style = dict(target_field=None,
                              style_classes=style_classes)

# Flood population impact raster style
# FIXME (Ole): The styler cannot handle floats yet. Issue #126
style_classes = [dict(colour='#38A800', quantity=0.000002, transparency=100),
                 dict(colour='#38A800', quantity=0.000005, transparency=0),
                 dict(colour='#79C900', quantity=0.000010, transparency=0),
                 dict(colour='#CEED00', quantity=0.000050, transparency=0),
                 dict(colour='#FFCC00', quantity=0.000100, transparency=0),
                 dict(colour='#FF6600', quantity=0.000200, transparency=0),
                 dict(colour='#FF0000', quantity=0.000500, transparency=0),
                 dict(colour='#7A0000', quantity=0.001000, transparency=0)]
earthquake_fatality_style = dict(target_field=None,
                                 style_classes=style_classes)
