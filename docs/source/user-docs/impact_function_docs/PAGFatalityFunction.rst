P A G Fatality Function
=======================

Overview
--------

**Unique Identifier**: 
P A G Fatality Function

**Author**: 
Helen Crowley

**Rating**: 
3

**Title**: 
Die or be displaced according Pager model

**Synopsis**: 
To asses the impact of earthquake on population based on Population Vulnerability Model Pager

**Actions**: 
Provide details about the population will be die or displaced

**Citations**: 
 * Jaiswal, K. S., Wald, D. J., and Hearne, M. (2009a).    Estimating casualties for large worldwide earthquakes using    an empirical approach. U.S. Geological Survey Open-File    Report 2009-1136.

**Limitation**: 
No documentation found

Details
-------

No documentation found

Docstring
----------


    Population Vulnerability Model Pager
    Loss ratio(MMI) = standard normal distrib( 1 / BETA * ln(MMI/THETA)).
    Reference:
    Jaiswal, K. S., Wald, D. J., and Hearne, M. (2009a).
    Estimating casualties for large worldwide earthquakes using an empirical
    approach. U.S. Geological Survey Open-File Report 2009-1136.

    :author Helen Crowley
    :rating 3

    :param requires category=='hazard' and                     subcategory=='earthquake' and                     layertype=='raster' and                     unit=='MMI'

    :param requires category=='exposure' and                     subcategory=='population' and                     layertype=='raster'
    