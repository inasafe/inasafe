========================
Impact Function Tutorial
========================

This is a simple tutorial for writing of InaSAFE impact functions.

.. note:: This is an old text that needs to be verified, but it may be helpful and can serve as
a starting point for additional documentation.


------------
Introduction
------------

InaSAFE contains a plugin system that allows complex impact functions to be implemented in Python (http://www.python.org) whilst (ideally) minimizing
the need to understand all the complexity of the handling the hazard and exposure layers. Features of the
impact function system are:

* Auto registration of new impact functions after restart
* Derivation of more complex impact functions from simpler ones
* Auto hiding for impact functions that aren't appropriate (depending on the requirements)
* Allow for additional functionality to be added easily
* Provide up-to-date documentation on impact functions functionality

----------------------------------------------------
Writing a Simple Raster impact function: Tutorial 01
----------------------------------------------------

This section provides a beginners tutorial on writing a simple earthquke impact function from scratch. You will need to be familiar with the basics of Python to be able to write and debug impact functions - if you are new to Python the standard Python tutorial is a great place to start (http://docs.python.org/tutorial/).

For this impact function we want to calculate a simple impact by using the following function of
the severity of hazard (i.e. the amount of ground shaking - H) by the exposure
(i.e. the number of people in that area - P). e.g.::

    Impact  = 10 ** (a * H - b) * P

    where
          H: Raster layer of MMI ground shaking
          P: Raster layer of population data on the same grid as H
          a,b: Parameters that were tuned from real world data


Defining the impact class
+++++++++++++++++++++++++

As the first step we need to define the impact function class.::

    class SimpleImpactEarthquakeFunction(FunctionProvider)

Every impact function must be subclassed from FunctionProvider. This is the
method of registration for the impact function and allows the Risiko Plugin
Manager to know what impact functions are available.

Impact Parameters
+++++++++++++++++

Each impact function needs to be used in the correct context. Using a flood impact function for earthquakes will likely yield misleading
results at best! As such pugins may have a variety of conditions that need to be met before they can be run. Such conditions
may include:

* The type of hazard
* The type of exposure
* The form of the layer data (raster or vector)
* The measure or unit type of a layer
* Any other meta data defined in the layer

In the future impact functions may also support filtering by:
* The geographic location
* The avaliable layer meta data

InaSAFE will try to show users only those impact functions that can be validly run.

These parameters required to run the impact function, and indeed all specific parameters,
are defined in the doc string of the class::

     class SimpleImpactEarthquakeFunction(FunctionProvider):
        """Simple impact function for earthquakes

        :author Allen
        :rating 1
        :param requires category=='hazard' and \
                subcategory.startswith('earthquake') and \
                layer_type=='raster'
        :param requires category=='exposure' and \
                subcategory.startswith('population') and \
                layer_type=='raster'
        """

This tells InaSAFE that this impact function requires at a minimum inputs of

* category of 'hazard', with a layer subcategory of 'earthquake' and it must be a layerType of 'Raster'
* category of 'exposure', with a layer subcategory of 'earthquake' and it must be a layerType of 'Raster'

The `require` expression can be any artibary python expression that can be evaluated.

.. note::
	1. Lines can be broken using the line continuation character '\\' at the end of a line
	2. If any one of the conditions is not met the plugin will not be visible from the impact selection box.

The calculation function
++++++++++++++++++++++++

Each impact function must then define a `run` method which contains the execution code::

    def run(self, input):

The parameters are passed in as a dictionary. It is up to the framework to populate the
dictionary correctly in this case with keys containing relavent data for the exposure and hazard.::

    def run(self, layers,
            a=0.97429, b=11.037):
        """Risk plugin for earthquake fatalities

        Input
          layers: List of layers expected to contain
              H: Raster layer of MMI ground shaking
              P: Raster layer of population data on the same grid as H
        """

        # Identify input layers
        intensity = layers[0]
        population = layers[1]

        # Extract data
        H = intensity.get_data(nan=0)
        P = population.get_data(nan=0)

        # Calculate impact
        F = 10 ** (a * H - b) * P

        # Create new layer and return
        R = Raster(F,
                   projection=population.get_projection(),
                   geotransform=population.get_geotransform(),
                   name='Estimated fatalities')
        return R



At the end of the function the calculated impact layer R is returned. This return layer
in our example is a Raster layer the correct projection for this layer is ensured by passing
in the input layer projections.


Installing the impact function
++++++++++++++++++++++++++++++

The whole impact function file will now read::

    from impact.plugins.core import FunctionProvider
    from impact.storage.raster import Raster

    class SimpleImpactEarthquakeFunction(FunctionProvider):
	    """Simple plugin for earthquake damage

	    :author Allen
	    :rating 1
	    :param requires category=='hazard' and \
	                    subcategory.startswith('earthquake') and \
	                    layer_type=='raster'
	    :param requires category=='exposure' and \
	                    subcategory.startswith('population') and \
	                    layer_type=='raster'
	    """

	    @staticmethod
	    def run(layers,
	            a=0.97429, b=11.037):
	        """Risk plugin for earthquake fatalities

	        Input
	          layers: List of layers expected to contain
	              H: Raster layer of MMI ground shaking
	              P: Raster layer of population data on the same grid as H
	        """

	        # Identify input layers
	        intensity = layers[0]
	        population = layers[1]

	        # Extract data
	        H = intensity.get_data(nan=0)
	        P = population.get_data(nan=0)

	        # Calculate impact
	        F = 10 ** (a * H - b) * P

	        # Create new layer and return
	        R = Raster(F,
	                   projection=population.get_projection(),
	                   geotransform=population.get_geotransform(),
	                   name='Estimated fatalities')
	        return R

Save this as SimpleImpactEarthquakeFunction.py into into the following directory::

	[root InaSAFE dir]/safe/impact_functions/earthquake

Then start QGis and activate InaSAFE.



Testing the plugin
++++++++++++++++++

Load the following data

* Earthquake ground shaking
* Glp10ag (Population for Indonesia)

...

