# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid **String for Wizard Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

from safe.utilities.i18n import tr

__author__ = 'timlinux'

category_question = tr(
    'By following the simple steps in this wizard, you can assign '
    'keywords to your layer: <b>%s</b>. First you need to define the purpose '
    'of your layer. Is it a <b>hazard</b>, <b>exposure</b>, or '
    '<b>aggregation</b> layer? ')  # (layer name)
category_question_hazard = tr(
    'You have selected a layer that needs to have keywords assigned or '
    'updated. In the next steps you can assign keywords to that layer. '
    'First you need to confirm the layer is a <b>hazard</b> layer.')
category_question_exposure = tr(
    'You have selected a layer that needs to have keywords assigned or '
    'updated. In the next steps you can assign keywords to that layer. '
    'First you need to confirm the layer is an <b>exposure</b>.')
category_question_aggregation = tr(
    'You have selected a layer that needs to have keywords assigned or '
    'updated. In the next steps you can assign keywords to that layer. '
    'First you need to confirm the layer is an <b>aggregation</b> layer.')
hazard_category_question = tr(
    'What type of <b>hazard scenario</b> does this layer represent? '
    '<p>Does it represent a <b>single event</b> or <b>multiple events</b>?'
    '</p>')
hazard_question = tr(
    'What kind of <b>hazard</b> does this layer represent? '
    '<p>The choice you make here will determine which impact functions this '
    'hazard layer can be used with. For example, if you choose <b>flood</b> '
    'you will be able to use this hazard layer with impact functions such '
    'as <b>flood impact on population</b>.</p>')
exposure_question = tr(
    'What kind of <b>exposure</b> does this layer represent? '
    'Is it a <b>population</b>, <b>structure</b>, or <b>road</b> layer? '
    '<p>The choice you make here will determine '
    'which impact functions this exposure layer can be used with. '
    'For example, if you choose <b>population</b> you will be able to use '
    'this exposure layer with impact functions such as <b>flood impact on '
    'population</b>.</p>')
layermode_raster_question = tr(
    'You have selected <b>%s %s</b> for this raster layer. '
    '<p>We need to know whether each cell '
    'in this raster represents <b>continuous</b> data or if the data have '
    'been <b>classified</b>.</p>')  # (subcategory, category)
layermode_vector_question = tr(
    'You have selected <b>%s</b> for this <b>%s</b> layer. '
    '<p>We need to confirm that attribute values in this vector layer have '
    'been <b>classified</b> and are represented by a '
    'code.</p>')  # (subcategory, category)
unit_question = tr(
    'You have selected <b>%s</b> for this <b>%s</b> layer type. '
    '<p>We need to know what units the continuous data are in. For example in '
    'a raster layer, each cell might represent depth in metres or depth in '
    'feet.</p>')  # (subcategory, category)
allow_resampling_question = tr(
    'You have selected <b>%s %s</b> for this <b>%s data</b> raster layer. '
    '<p>For some exposure types you may not want InaSAFE to resample the '
    'raster to the hazard layer resolution during analyses. Please select the '
    'check box below if you want to set the <i>allow_resampling</i> '
    'keyword to <i>False</i>.</p>')  # (subcategory, category, layer_mode)
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
    'You have selected a <b>%s %s</b> for the vector layer measured in '
    '<b>%s</b>. Please select the attribute in this layer that represents %s.'
)  # (category, subcategory, unit, subcategory-unit relation)
field_question_subcategory_classified = tr(
    'You have selected <b>classified</b> data for the vector <b>%s</b> layer. '
    'Please select the attribute in this layer that represents the classes.'
)  # (category, subcategory)
field_question_aggregation = tr(
    'You have selected a vector <b>aggregation</b> layer. Please select the '
    'attribute in this layer that has the names of the aggregation areas.')
classification_question = tr(
    'You have selected <b>%s %s</b> for this classified data. '
    'Please select the type of classification you want to use. '
)  # (subcategory, category)
classify_vector_question = tr(
    'You have selected <b>%s %s</b> classified by <b>%s</b>, '
    'and the attribute is <b>%s</b>. '
    'Please drag unique values from the list on the left '
    'into the panel on the right and place them in the appropriate categories.'
)      # (subcategory, category, classification, field)
classify_raster_question = tr(
    'You have selected <b>%s %s</b> classified by <b>%s</b>, '
    'for the raster layer. '
    'Please drag unique values from the list on the left '
    'into the panel on the right and place them in the appropriate categories.'
)  # (subcategory, category, classification)
select_function_constraints2_question = tr(
    'You selected <b>%s</b> hazard and <b>%s</b> exposure. Now, select the '
    '<b>geometry types</b> for the hazard and exposure layers you want to '
    'use. Click on the cell in the table below that matches '
    'the geometry type for each.')  # (hazard, exposure)
select_function_question = tr(
    '<p>You have selected <b>%s %s</b> hazard and <b>%s %s</b> exposure. '
    'Below you can see a list of available <b>impact functions</b> matching '
    'the selected hazard, exposure and their geometries. Please choose which '
    'impact function you would like to use from the list below.</p> '
    '<p>Please note some functions may require either continuous or '
    'classified input data. A <b>continuous</b> raster is one where cell '
    'values are real data values such as: depth of flood water in meters or '
    'the number of people per cell. A <b>classified</b> raster is one where '
    'cell values represent classes or zones such as: high hazard zone, '
    'medium hazard zone, low hazard zone.</p>'
)  # (haz_geom, haz, expo_geom, exp)
select_hazard_origin_question = tr(
    '<p>You selected <b>%s %s</b> as hazard input to <b>%s</b> function.</p> '
    '<p>Please help us to find your <b>hazard</b> layer. A hazard layer '
    'represents something that will impact the people or infrastructure '
    'in an area. '
    'For example flood, earthquake and tsunami inundation are all different '
    'kinds of hazards. Select the appropriate option below to indicate '
    'where your data resides:</p>')  # (hazard_geom, hazard, imfunc)
select_hazlayer_from_canvas_question = tr(
    '<p>You selected <b>%s %s</b> as hazard input to <b>%s</b> function.</p> '
    '<p>These are suitable layers currently loaded in QGIS. Please choose '
    'the hazard layer that you would like to use for your assessment.</p>'
)  # (hazard_geom, hazard, imfunc)
select_hazlayer_from_browser_question = tr(
    '<p>You selected <b>%s %s</b> as hazard input to <b>%s</b> '
    'function.</p> '
    '<p>Please choose the hazard layer that you would like to use '
    'for your assessment.</p>')  # (exposure_geom, exposure, imfunc)
select_exposure_origin_question = tr(
    '<p>You selected <b>%s %s</b> as exposure input to <b>%s</b> '
    'function.</p>'
    '<p>Please help us to find your <b>exposure</b> layer. An exposure layer '
    'represents people, property or infrastructure that may be affected in '
    'the event of a flood, earthquake, volcano etc. Select an appropriate '
    'option below to indicate where your data can be found:</p>'
)  # (exposure_geom, exposure, imfunc)
select_explayer_from_canvas_question = tr(
    '<p>You selected <b>%s %s</b> as exposure input to <b>%s</b> '
    'function.</p>'
    '<p>These are suitable layers currently loaded in QGIS. Please choose '
    'the exposure layer that you would like to use for your '
    'assessment.</p>')  # (exposure_geom, exposure, imfunc)
select_explayer_from_browser_question = tr(
    '<p>You selected <b>%s %s</b> as exposure input to <b>%s</b> '
    'function.</p> '
    '<p>Please choose the exposure layer that you would like to use '
    'for your assessment.</p>')  # (exposure_geom, exposure, imfunc)
create_postGIS_connection_first = tr(
    '<html>In order to use PostGIS layers, please close the wizard, '
    'create a new PostGIS connection and run the wizard again. <br/><br/> '
    'You can manage connections under the '
    '<i>Layer</i> > <i>Add Layer</i> > <i>Add PostGIS Layers</i> '
    'menu.</html>')
