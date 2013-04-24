I T B Fatality Function
=======================

Overview
--------

**Unique Identifier**: 
I T B Fatality Function

**Author**: 
Hadi Ghasemi

**Rating**: 
3

**Title**: 
Die or be displaced

**Synopsis**: 
To asses the impact of earthquake on population based on earthquake model developed by ITB

**Actions**: 
Provide details about the population will be die or displaced

**Citations**: 
 * Indonesian Earthquake Building-Damage and Fatality Models and    Post Disaster Survey Guidelines Development Bali, 27-28    February 2012, 54pp.
 * Allen, T. I., Wald, D. J., Earle, P. S., Marano, K. D.,    Hotovec, A. J., Lin, K., and Hearne, M., 2009. An Atlas    of ShakeMaps and population exposure catalog for    earthquake loss modeling, Bull. Earthq. Eng. 7, 701-718.
 * Jaiswal, K., and Wald, D., 2010. An empirical model for    global earthquake fatality estimation, Earthq. Spectra    26, 1017-1037.


**Limitation**: 
 - The model is based on limited number of observed fatality    rates during 4 past fatal events. 
 - The model clearly over-predicts the fatality rates at    intensities higher than VIII.
 - The model only estimates the expected fatality rate    for a given intensity level; however the associated    uncertainty for the proposed model is not addressed.
 - There are few known mistakes in developing the current    model:

   * rounding MMI values to the nearest 0.5,
   * Implementing Finite-Fault models of candidate events, and
   * consistency between selected GMPEs with those in use by      BMKG.


Details
-------

This model was developed by Institut Tecknologi Bandung (ITB) and implemented by Dr Hadi Ghasemi, Geoscience Australia
Algorithm:
In this study, the same functional form as Allen (2009) is adopted o express fatality rate as a function of intensity (see Eq. 10 in the report). The Matlab built-in function (fminsearch) for  Nelder-Mead algorithm was used to estimate the model parameters. The objective function (L2G norm) that is minimized during the optimisation is the same as the one used by Jaiswal et al. (2010).
The coefficients used in the indonesian model are x=0.62275231, y=8.03314466, zeta=2.15

Docstring
----------

Indonesian Earthquake Fatality Model

    This model was developed by Institut Tecknologi Bandung (ITB) and
    implemented by Dr Hadi Ghasemi, Geoscience Australia


    Reference:

    Indonesian Earthquake Building-Damage and Fatality Models and
    Post Disaster Survey Guidelines Development,
    Bali, 27-28 February 2012, 54pp.


    Algorithm:

    In this study, the same functional form as Allen (2009) is adopted
    to express fatality rate as a function of intensity (see Eq. 10 in the
    report). The Matlab built-in function (fminsearch) for  Nelder-Mead
    algorithm was used to estimate the model parameters. The objective
    function (L2G norm) that is minimised during the optimisation is the
    same as the one used by Jaiswal et al. (2010).

    The coefficients used in the indonesian model are
    x=0.62275231, y=8.03314466, zeta=2.15

    Allen, T. I., Wald, D. J., Earle, P. S., Marano, K. D., Hotovec, A. J.,
    Lin, K., and Hearne, M., 2009. An Atlas of ShakeMaps and population
    exposure catalog for earthquake loss modeling, Bull. Earthq. Eng. 7,
    701-718.

    Jaiswal, K., and Wald, D., 2010. An empirical model for global earthquake
    fatality estimation, Earthq. Spectra 26, 1017-1037.


    Caveats and limitations:

    The current model is the result of the above mentioned workshop and
    reflects the best available information. However, the current model
    has a number of issues listed below and is expected to evolve further
    over time.

    1 - The model is based on limited number of observed fatality
        rates during 4 past fatal events.
    2 - The model clearly over-predicts the fatality rates at
        intensities higher than VIII.
    3 - The model only estimates the expected fatality rate for a given
        intensity level; however the associated uncertainty for the proposed
        model is not addressed.
    4 - There are few known mistakes in developing the current model:
        - rounding MMI values to the nearest 0.5,
        - Implementing Finite-Fault models of candidate events, and
        - consistency between selected GMPEs with those in use by BMKG.
          These issues will be addressed by ITB team in the final report.

    Note: Because of these caveats, decisions should not be made solely on
    the information presented here and should always be verified by ground
    truthing and other reliable information sources.

    :author Hadi Ghasemi
    :rating 3

    :param requires category=='hazard' and                     subcategory=='earthquake' and                     layertype=='raster' and                     unit=='MMI'

    :param requires category=='exposure' and                     subcategory=='population' and                     layertype=='raster'

    