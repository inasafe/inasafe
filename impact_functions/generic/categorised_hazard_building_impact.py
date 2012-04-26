from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.vector import Vector
from storage.utilities import ugettext as _

#FIXME: need to normalise all raster data Ole/Kristy
class CatergorisedHazardBuildingImpactFunction(FunctionProvider):
    """Impact plugin for categorising hazard impact on building data

    :param requires category=='hazard' and \
                    unit=='normalised' and \
                    layertype=='raster'

    :param requires category=='exposure' and \
                    subcategory=='building' and \
                    layertype=='vector'
    """

    target_field = 'ICLASS'

    def run(self, layers):
        """Impact plugin for hazard impact
        """

        # Extract data
        H = get_hazard_layer(layers)    # Value
        E = get_exposure_layer(layers)  # Building locations

        # Interpolate hazard level to building locations
        Hi = H.interpolate(E)

        # Extract relevant numerical data
        coordinates = Hi.get_geometry()
        category = Hi.get_data()
        N = len(category)

        # List attributes to carry forward to result layer
        attributes = E.get_attribute_names()

        # Calculate building impact according to guidelines
        count2 = 0
        count1 = 0
        count0 = 0
        building_impact = []
        for i in range(N):
            # Get catergory value
            val = float(category[i].values()[0])

            # Classify buildings according to value
            if val >= 2.0/3:
                affected = 2  
                count2 += 1          
            elif 1.0/3 <= val < 2.0/3:
                affected = 1
                count1 += 1
            else:
                affected = 0
                count0 += 1
            
            # Collect depth and calculated damage
            result_dict = {self.target_field: affected,
                           'CATEGORY': val}

            # Carry all original attributes forward
            # FIXME: This should be done in interpolation. Check.
            for key in attributes:
                result_dict[key] = E.get_data(key, i)

            # Record result for this feature
            building_impact.append(result_dict)

        # Create report
        #FIXME: makes the output format the same as all other results
        
        impact_summary = ('<table border="0" width="320px">'
                   '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                   '   <tr></tr>'
                   '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                   '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                   '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                   '</table>' % (_('Category'), _('Affected'),
                                 _('Low'), count0,
                                 _('Medium'), count1,
                                 _('High'), count2))

        # Create style
        style_classes = [dict(label= _('Low'), min=0, max=1,
                              colour='#1EFC7C', transparency=0,size=1),
                         dict(label= _('Medium'), min=1, max=2,
                              colour='#FFA500', transparency=0,size=1),
                         dict(label= _('High'), min=2, max=4,
                              colour='#F31A1C', transparency=0,size=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        name = 'Buildings Affected'

        V = Vector(data=building_impact,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   keywords={'impact_summary': impact_summary},
                   geometry_type=Hi.geometry_type,
                   name=name,
                   style_info=style_info)
        return V

