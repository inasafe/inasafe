
==========
Data Types
==========

The impact functions essentially combine spatial data in different formats
through a common interpolation library. This essentially allows values from
one data set to be assigned to another independent of their types.
Given two layers H and E, say, the call::

  I = assign_hazard_values_to_exposure_data(H, E, ...)

will produce a new layer with all values from H transferred to E in a manner
appropriate for the data types of H and E. Generally, existing values in
E will be also be carried over to I. Conceptually, the new layer I represents
the values of H interpolated to E.

The function takes a number of optional keyword arguments that pertain to certain type combinations. They are

* layer_name: Optional name of returned layer. If None (default) the name of the exposure layer is used.
* attribute_name:

  - If hazard layer is of type raster, this is the name for new attribute in the result containing the hazard level.
    If None (default) the name of hazard is used
  - If hazard layer is of type vector, it is the name of the attribute to transfer from the hazard layer into the result.
    If None (default) all attributes are transferred.
* mode: Interpolation mode for raster to point interpolation only. Options are 'linear' (default) or 'constant'


The following table shows allowed combinations and what interpolation means
in each case.

.. table::

  +---------+---------+---------------------------------------------------------------+--------------+
  | H       | E       |  Methodology                                                  | Return value |
  +=========+=========+===============================================================+==============+
  | Polygon | Point   | Clip points to polygon and assign all attributes              | Point        |
  +---------+---------+---------------------------------------------------------------+--------------+
  | Polygon | Line    | Clip segments to polygon and assign all attributes (slow)     | Line         |
  +---------+---------+---------------------------------------------------------------+--------------+
  | Polygon | Polygon |                                                               | N/A          |
  +---------+---------+---------------------------------------------------------------+--------------+
  | Polygon | Raster  | Convert to points and use Polygon-Point algorithm             | Point        |
  +---------+---------+---------------------------------------------------------------+--------------+
  | Raster  | Point   | Bilinear or piecewise constant interpolation                  | Point        |
  +---------+---------+---------------------------------------------------------------+--------------+
  | Raster  | Line    |                                                               | N/A          |
  +---------+---------+---------------------------------------------------------------+--------------+
  | Raster  | Polygon | Convert to centroids and use Raster-Point algorithm           | Polygon      |
  +---------+---------+---------------------------------------------------------------+--------------+
  | Raster  | Raster  | Check that rasters are aligned and return E                   | Raster       +
  +---------+---------+---------------------------------------------------------------+--------------+


