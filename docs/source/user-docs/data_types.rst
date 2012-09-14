
==========
Data Types
==========

The impact functions essentially combine spatial data in different formats
through a common interpolation library. This essentially allows values from
one data set to be assigned to another independent of their types.
Given two layers H and E, say, the call::

  I = H.interpolate(E)

will produce a new layer with all values from H transferred to E in a manner
appropriate for the data types of H and E. Generally, existing values in
E will be also be carried over to I. Conceptually, the new layer I represents
the values of H interpolated to E.

The following table shows allowed combinations and what interpolation means
in each case.

.. table::

  +-----------------+------------+----------+------+--------------------------+
  |   H             |            |     E    |      |                          |
  +=================+============+==========+=======+=========================+
  |                 | Raster     | Polygon  | Line  | Point                   |
  +-----------------+------------+----------+-------+-------------------------+
  | Raster          | Resampled  | Centroid | Belum | Bilinear Interpolation  |
  +-----------------+------------+----------+-------+-------------------------+
  | Polygon         |     No     |  No      | Belum | Clip and tag            |
  +-----------------+------------+----------+-------+-------------------------+
  | Line            | Not applicable                                          |
  +-----------------+------------+----------+-------+-------------------------+
  | Point           | Not applicable                                          |
  +-----------------+------------+----------+-------+-------------------------+


