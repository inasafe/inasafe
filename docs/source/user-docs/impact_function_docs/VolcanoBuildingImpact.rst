Volcano Building Impact
=======================

Overview
--------

**Unique Identifier**: 
Volcano Building Impact

**Author**: 
AIFDR

**Rating**: 
4

**Title**: 
Be affected

**Synopsis**: 
To assess the impacts of volcano eruption on building.

**Actions**: 
Provide details about how many building would likely be affected by each hazard zones.

**Hazard Input**: 
A hazard vector layer can be polygon or point. If polygon, it must have "KRB" attribute and the valuefor it are "Kawasan Rawan Bencana I", "Kawasan Rawan Bencana II", or "Kawasan Rawan Bencana III." If youwant to see the name of the volcano in the result, you need to add "NAME" attribute for point data or "GUNUNG" attribute for polygon data.

**Exposure Input**: 
Vector polygon layer extracted from OSM where each polygon represents the footprint of a building.

**Output**: 
Vector layer contains Map of building exposed to volcanic hazard zones for each Kawasan Rawan Bencana or radius.

Details
-------

No documentation found

Docstring
----------

Risk plugin for volcano evacuation

    :author AIFDR
    :rating 4
    :param requires category=='hazard' and                     subcategory in ['volcano'] and                     layertype=='vector'

    :param requires category=='exposure' and                     subcategory=='structure' and                     layertype=='vector'
    