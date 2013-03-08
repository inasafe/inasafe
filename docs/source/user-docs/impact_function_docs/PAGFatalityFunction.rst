P A G Fatality Function
=======================

Overview
--------

**Unique Identifier**: P A G Fatality Function

**Author**: Helen Crowley

**Rating**: 3

**Title**: Die or be displaced according Pager model

**Synopsis**: To asses the impact of earthquake on population based on Population Vulnerability Model Pager

**Actions**: Provide details about the population will be die or displaced

**Citations**: 

* Jaiswal, K. S., Wald, D. J., and Hearne, M. (2009a). Estimating casualties for large worldwide earthquakes using an empirical approach. U.S. Geological Survey Open-File Report 2009-1136.


**Limitation**: No documentation found

Details
-------

This model was developed by Institut Tecknologi Bandung (ITB) and implemented by Dr Hadi Ghasemi, Geoscience Australia
Algorithm:
In this study, the same functional form as Allen (2009) is adopted o express fatality rate as a function of intensity (see Eq. 10 in the report). The Matlab built-in function (fminsearch) for  Nelder-Mead algorithm was used to estimate the model parameters. The objective function (L2G norm) that is minimized during the optimisation is the same as the one used by Jaiswal et al. (2010).
The coefficients used in the indonesian model are x=0.62275231, y=8.03314466, zeta=2.15