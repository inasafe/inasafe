Flood Building Impact Function
==============================

Overview
--------

**Unique Identifier**: 
Flood Building Impact Function

**Author**: 
Ole Nielsen, Kristy van Putten

**Rating**: 
0

**Title**: 
Be flooded

**Synopsis**: 
To assess the impacts of (flood or tsunami) inundation on building footprints originating from OpenStreetMap (OSM).

**Actions**: 
Provide details about where critical infrastructure might be flooded

**Hazard Input**: 
A hazard raster layer where each cell represents flood depth (in meters), or a vector polygon layer where each polygon represents an inundated area. In the latter case, the following attributes are recognised (in order): "affected" (True or False) or "FLOODPRONE" (Yes or No). (True may be represented as 1, False as 0

**Exposure Input**: 
Vector polygon layer extracted from OSM where each polygon represents the footprint of a building.

**Output**: 
Vector layer contains building is estimated to be flooded and the breakdown of the building by type.

**Limitation**: 
This function only flags buildings as impacted or not either based on a fixed threshold in case of raster hazard or the the attributes mentioned under input in case of vector hazard.

Details
-------

The inundation status is calculated for each building (using the centroid if it is a polygon) based on the hazard levels provided. if the hazard is given as a raster a threshold of 1 meter is used. This is configurable through the InaSAFE interface. If the hazard is given as a vector polygon layer buildings are considered to be impacted depending on the value of hazard attributes (in order) "affected" or "FLOODPRONE": If a building is in a region that has attribute "affected" set to True (or 1) it is impacted. If attribute "affected" does not exist but "FLOODPRONE" does, then the building is considered impacted if "FLOODPRONE" is "yes". If neither "affected" nor "FLOODPRONE" is available, a building will be impacted if it belongs to any polygon. The latter behaviour is implemented through the attribute "inapolygon" which is automatically assigned.

Docstring
----------

Inundation impact on building data

    :author Ole Nielsen, Kristy van Putten
    # this rating below is only for testing a function, not the real one
    :rating 0
    :param requires category=='hazard' and                     subcategory in ['flood', 'tsunami']

    :param requires category=='exposure' and                     subcategory=='structure' and                     layertype=='vector'
    