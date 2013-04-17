Categorised Hazard Population Impact Function
=============================================

Overview
--------

**Unique Identifier**: 
Categorised Hazard Population Impact Function

**Author**: 
AIFDR

**Rating**: 
2

**Title**: 
Be impacted

**Synopsis**: 
To assess the impacts of categorized hazard in rasterformat on population raster layer.

**Actions**: 
Provide details about how many people would likely need to be impacted for each cateogory.

**Hazard Input**: 
A hazard raster layer where each cell represents the categori of the hazard. There should be 3 categories: 1, 2, dan 3.

**Exposure Input**: 
An exposure raster layer where each cell represent population count.

**Output**: 
Map of population exposed to high category and a table with number of people in each category

**Limitation**: 
The number of categories is three.

Details
-------

The function will calculated how many people will be impactedper each category for all categories in hazard layer. Currentlythere should be 3 categories in the hazard layer. After thatit will show the result and the total of people will be impactedfor the hazard given.

Docstring
----------

Plugin for impact of population as derived by categorised hazard

    :author AIFDR
    :rating 2
    :param requires category=='hazard' and                     unit=='normalised' and                     layertype=='raster'

    :param requires category=='exposure' and                     subcategory=='population' and                     layertype=='raster'
    