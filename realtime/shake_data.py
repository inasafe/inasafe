"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Functionality related to shake data files.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '30/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

class ShakeData:
    """A class for retrieving, reading, converting and extracting
       data from shakefiles.

    Shake files are provided on an ftp server. There are two files for every
    event:
       * an 'inp' file
       * an 'out' file

    These files are provided on the ftp server as zip files. For example:
        * `ftp://118.97.83.243/20110413170148.inp.zip`_
        * `ftp://118.97.83.243/20110413170148.out.zip`_

    There are numerous files provided within these two zip files, but there
    are only really two that we are interested in:

        * grid.xyz - which contains all the metadata pertaining to the event
        * mi.grd - which contains the GMT formatted raster shake MMI data.

    This class provides a high level interface for retrieving this data and
    then extracting various by products from it.
    """

    def __init__(self, theEvent=None, theHost='118.97.83.243'):
        """Constructor for the ShakeData class

            Args:
                * theEvent - (Optional) a string representing the event id
                  that this raster is associated with. e.g. 20110413170148.
                  **If no event id is supplied, a query will be made to the
                  ftp server, and the latest event id assigned.**
                * theData - (Optional) a string representing the ip address
                  or host name of the server from which the data should be
                  retrieved. It assumes that the data is in the root directory.
                  Defaults to 118.97.83.243

            Returns:
                None

            Raises:
                None

            """
        self.event = theEvent
        self.host = theHost

    def fetchInput(self):
        """Fetch the input file for the event id associated with this class
        """
        pass

    def fetchOutput(self):
        """Fetch the output file for the event id associated with this class.
        """
        pass

    def fetch(self):
        """Fetch both the input and output shake data from the server for
        the event id associated with this class.
        """

    def fetchLatest(self):
        """Fetch the latest input and output shake data from the server. This
        method will also update the event property to reflect the latest event
        id and clear any state in this class."""
