from safe.utilities.i18n import tr

__author__ = 'timlinux'
category_question = tr(
    'By following the simple steps in this wizard, you can assign '
    'keywords to your layer: <b>%s</b>. First you need to define '
    'the purpose of your layer.')  # (layer name)
category_question_hazard = tr(
    'You have selected a layer that needs to have keywords assigned or '
    'updated. In the next steps you can assign keywords to that layer. '
    'First you need to confirm the layer represents a hazard.')
category_question_exposure = tr(
    'You have selected a layer that needs to have keywords assigned or '
    'updated. In the next steps you can assign keywords to that layer. '
    'First you need to confirm the layer represents an exposure.')
category_question_aggregation = tr(
    'You have selected a layer that needs to have keywords assigned or '
    'updated. In the next steps you can assign keywords to that layer. '
    'First you need to confirm the layer is an aggregation layer.')
hazard_category_question = tr(
    'What type of <b>hazard scenario</b> does this layer represent? '
    'Is it a single event or a zone of multiple hazards?')
hazard_question = tr(
    'What kind of <b>hazard</b> does this '
    'layer represent? The choice you make here will determine '
    'which impact functions this hazard layer can be used with. '
    'For example, if you choose <b>flood</b> you will be '
    'able to use this hazard layer with impact functions such '
    'as <b>flood impact on population</b>.')
exposure_question = tr(
    'What kind of <b>exposure</b> does this '
    'layer represent? The choice you make here will determine '
    'which impact functions this exposure layer can be used with. '
    'For example, if you choose <b>population</b> you will be '
    'able to use this exposure layer with impact functions such '
    'as <b>flood impact on population</b>.')
layermode_raster_question = tr(
    'You have selected <b>%s %s</b> '
    'for this raster layer. We need to know whether each cell '
    'in this raster represents a continuous '
    'value or a classified code.')  # (subcategory, category)
layermode_vector_question = tr(
    'You have selected <b>%s %s</b> for this layer. '
    'We need to know whether attribute data of this vector '
    'represents a continuous value or a classified code.'
)  # (subcategory, category)
unit_question = tr(
    'You have selected <b>%s</b> for this <b>%s</b> '
    'layer type. We need to know what units the continuous '
    'data are in. For example in a raster layer, each cell might '
    'represent depth in metres or depth in feet.'
)  # (subcategory, category)
allow_resampling_question = tr(
    'You have selected <b>%s %s</b> for this <b>%s data</b> raster layer. '
    'For some exposure types you may not want InaSAFE to resample the raster '
    'to the hazard layer resolution during analyses. Please select the '
    'check box below if you want to set the <i>allow_resampling</i> '
    'keyword to <i>False</i>.')  # (subcategory, category, layer_mode)
flood_metres_depth_question = tr(
    'flood depth in meters')
flood_feet_depth_question = tr(
    'flood depth in feet')
flood_wetdry_question = tr(
    'flood extent as wet/dry')
tsunami_metres_depth_question = tr(
    'tsunami depth in meters')
tsunami_feet_depth_question = tr(
    'tsunami depth in feet')
tsunami_wetdry_question = tr(
    'tsunami extent as wet/dry')
earthquake_mmi_question = tr(
    'earthquake intensity in MMI')
tephra_kgm2_question = tr(
    'tephra intensity in kg/m<sup>2</sup>')
volcano_volcano_categorical_question = tr(
    'volcano hazard categorical level')
population_number_question = tr(
    'the number of people')
population_density_question = tr(
    'people density in people/km<sup>2</sup>')
road_road_type_question = tr(
    'type for your road')
structure_building_type_question = tr(
    'type for your building')
field_question_subcategory_unit = tr(
    'You have selected a <b>%s %s</b> layer measured in '
    '<b>%s</b>, and the selected layer is a vector layer. Please '
    'select the attribute in this layer that represents %s.'
)  # (category, subcategory, unit, subcategory-unit relation)
field_question_subcategory_classified = tr(
    'You have selected a <b>classified %s %s</b> layer, and the selected '
    'layer is a vector layer. Please select the attribute in this layer '
    'that represents the classes.')  # (category, subcategory)
field_question_aggregation = tr(
    'You have selected an aggregation layer, and it is a vector '
    'layer. Please select the attribute in this layer that represents '
    'names of the aggregation areas.')
classification_question = tr(
    'You have selected <b>%s %s</b> for this classified data. '
    'Please select type of classification you want to use. '
)  # (subcategory, category)
classify_vector_question = tr(
    'You have selected <b>%s %s</b> classified by <b>%s</b>, '
    'and the data column is <b>%s</b>. Below on the left you '
    'can see all unclassified unique values found in that column. Please '
    'drag them to the right panel in order to classify them to appropriate '
    'categories.')  # (subcategory, category, classification, field)
classify_raster_question = tr(
    'You have selected <b>%s %s</b> classified by <b>%s</b>, '
    'and the layer is a raster layer. Below on the left you '
    'can see all unclassified unique values found in the raster. Please '
    'drag them to the right panel in order to classify them to appropriate '
    'categories.')  # (subcategory, category, classification)
select_function_constraints2_question = tr(
    'You selected <b>%s</b> Hazard and <b>%s</b> Exposure. Now, please '
    'select the <b>geometry types</b> for the hazard and exposure layers '
    'you want to use. Click on the cell in the table below that matches '
    'the geometry type for each.')  # (hazard, exposure)
select_function_question = tr(
    '<p>You selected <b>%s %s</b> Hazard and <b>%s %s</b> Exposure. Below '
    'you can see a list of available <b>impact functions</b> matching the '
    'selected hazard, exposure and their geometries. Please choose which '
    'impact function would you like to use from the list below.</p> '
    '<p>Please note some functions may require either continuous or '
    'classified input data. A <b>continuous</b> raster is one where cell '
    'values are real data values such as: depth of flood water in meters or '
    'the number of people per cell. A <b>classified</b> raster is one where '
    'cell values represent classes or zones such as: high hazard zone, '
    'medium hazard zone, low hazard zones.</p>'
)  # (haz_geom, haz, expo_geom, exp)
select_hazard_origin_question = tr(
    '<p>You selected <b>%s %s</b> as Hazard input to <b>%s</b> function.</p> '
    '<p>Please help us to find your <b>hazard</b> layer. A hazard layer '
    'represents something that will impact the people or infrastructure '
    'in an area. '
    'For example flood, earthquake and tsunami inundation are all different '
    'kinds of hazards. Select the appropriate option below to indicate '
    'where you data resides:</p>')  # (hazard_geom, hazard, imfunc)
select_hazlayer_from_canvas_question = tr(
    '<p>You selected <b>%s %s</b> as Hazard input to <b>%s</b> function.</p> '
    '<p>These are suitable layers currently loaded in QGIS. Please choose '
    'one layer that you would like to use as hazard for your assessment.</p>'
)  # (hazard_geom, hazard, imfunc)
select_hazlayer_from_browser_question = tr(
    '<p>You selected <b>%s %s</b> as Hazard input to <b>%s</b> '
    'function.</p> '
    '<p>Please choose one layer that you would like to use as hazard '
    'for your assessment.</p>')  # (exposure_geom, exposure, imfunc)
select_exposure_origin_question = tr(
    '<p>You selected <b>%s %s</b> as Exposure input to <b>%s</b> '
    'function.</p>'
    '<p>Please help us to find your <b>exposure</b> layer. An exposure layer '
    'represents people, property or infrastructure that may be affected in '
    'the event of a flood, earthquake, volcano etc. Select an appropriate '
    'option below to indicate where your data can be found:</p>'
)  # (exposure_geom, exposure, imfunc)
select_explayer_from_canvas_question = tr(
    '<p>You selected <b>%s %s</b> as Exposure input to <b>%s</b> '
    'function.</p>'
    '<p>These are suitable layers currently loaded in QGIS. Please choose '
    'one layer that you would like to use as exposure for your '
    'assessment.</p>')  # (exposure_geom, exposure, imfunc)
select_explayer_from_browser_question = tr(
    '<p>You selected <b>%s %s</b> as Exposure input to <b>%s</b> '
    'function.</p> '
    '<p>Please choose one layer that you would like to use as exposure '
    'for your assessment.</p>')  # (exposure_geom, exposure, imfunc)
create_postGIS_connection_first = tr(
    '<html>In order to use PostGIS layers, please close the wizard, '
    'create a new PostGIS connection and run the wizard again. <br/><br/> '
    'You can manage connections under the '
    '<i>Layer</i> > <i>Add Layer</i> > <i>Add PostGIS Layers</i> '
    'menu.</html>')
