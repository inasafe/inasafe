"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**ISImpactCalculator.**

The module provides a high level interface for running SAFE scenarios.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com, ole.moller.nielsen@gmail.com'
__version__ = '0.3.0'
__date__ = '11/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


#Do not import any QGIS or SAFE modules in this module!
import os
import sqlite3 as sqlite
import cPickle as pickle

from is_exceptions import (InsufficientParametersException,
                           KeywordNotFoundException,
                           HashNotFoundException)
from is_safe_interface import (read_layer,
                               get_plugins,
                               calculate_impact)
from is_utilities import getExceptionWithStacktrace
import threading
from PyQt4.QtCore import (QObject,
                          pyqtSignal,
                          QCoreApplication)


def tr(theText):
    """We define a tr() alias here since the ISClipper implementation below
    is not a class and does not inherit from QObject.
    .. note:: see http://tinyurl.com/pyqt-differences
    Args:
       theText - string to be translated
    Returns:
       Translated version of the given string if available, otherwise
       the original string.
    """
    myContext = "ISImpactCalculator"
    return QCoreApplication.translate(myContext, theText)


def getHashForDatasource(theDataSource):
    """
    Args:
        None
    Returns:
        None
    Raises:
        None
    """
    import hashlib
    myHash = hashlib.md5()
    myHash.update(theDataSource)
    myHash = myHash.hexdigest()
    return myHash


def getCursor(theConnection):
    """Get a cursor for the active connection. The cursor can be used to
    execute arbitrary queries against the database. This method also checks
    that the keywords table exists in the schema, and if not, it creates it.
    Args:
        theConnection - a valid, open sqlite3 database connection.
    Returns:
        a valid cursor opened against the connection.
    Raises:
        An sqlite.Error will be raised if anything goes wrong
    """
    try:
        myCursor = theConnection.cursor()
        myCursor.execute('SELECT SQLITE_VERSION()')
        myData = myCursor.fetchone()
        #print "SQLite version: %s" % myData
        # Check if we have some tables, if not create them
        mySQL = 'select sql from sqlite_master where type = \'table\';'
        myCursor.execute(mySQL)
        myData = myCursor.fetchone()
        #print "Tables: %s" % myData
        if myData is None:
            print 'No tables found'
            mySQL = ('create table keyword (hash varchar(32) primary key,'
                     'dict text);')
            print mySQL
            myCursor.execute(mySQL)
            myData = myCursor.fetchone()
        else:
            print 'Keywords table already exists'
            pass
        return myCursor
    except sqlite.Error, e:
        print "Error %s:" % e.args[0]
        raise


def openConnection(thePath=None):
    """Open an sqlite connection to the keywords database.
    By default the keywords database will be used in the plugin dir,
    unless an explicit path is provided. If the db does not exist it will
    be created.
    Args:
        thePath - path to the desired sqlite db to use.
    Returns:
        A valid open connection to the sqlite database
    Raises:
        An sqlite.Error is raised if anything goes wrong
    """
    myConnection = None
    myParentDir = os.path.abspath(
                                os.path.join(os.path.dirname(__file__), '..'))
    if thePath is None:
        thePath = os.path.join(myParentDir, 'keywords.db')
    try:
        myConnection = sqlite.connect(thePath)
    except sqlite.Error, e:
        print "Error %s:" % e.args[0]
        raise
    return myConnection


def closeConnection(theConnection):
    """Given an sqlite3 connection, close it
    Args:
        theConnection - an open SQLITE connection
    Returns:
        None
    Raises:
        None
    """
    if theConnection:
        theConnection.close()


def deleteKeywordsForUri(theUri, theDatabasePath=None):
    """Delete keywords for a URI in the keywords database.
    A hash will be constructed from the supplied uri and a lookup made
    in a local SQLITE database for the keywords. If there is an existing
    record for the hash, the entire record will be erased.

    .. seealso:: writeKeywordsForUri, readKeywordsForUri

    Args:

       * theUri -  a str representing a layer uri as parameter.
         .e.g. 'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
         password=\'bar\' sslmode=disable key=\'id\' srid=4326
       * theDatabasePath - optional string giving path to the sqlite
         database to use. If the database does not exist it will be
         created.

    Returns:
       None

    Raises:
       None
    """
    myHash = getHashForDatasource(theUri)
    myConnection = openConnection(theDatabasePath)
    try:
        myCursor = getCursor(myConnection)
        #now see if we have any data for our hash
        mySQL = 'delete from keyword where hash = \'' + myHash + '\';'
        myCursor.execute(mySQL)
        myConnection.commit()
    except sqlite.Error, e:
        print "SQLITE Error %s:" % e.args[0]
        myConnection.rollback()
    except Exception, e:
        print "Error %s:" % e.args[0]
        myConnection.rollback()
        raise
    finally:
        closeConnection(myConnection)


def writeKeywordsForUri(theUri, theKeywords, theDatabasePath=None):
    """Write keywords for a URI into the keywords database. All the
    keywords for the uri should be written in a single operation.
    A hash will be constructed from the supplied uri and a lookup made
    in a local SQLITE database for the keywords. If there is an existing
    record it will be updated, if not, a new one will be created.

    .. seealso:: readKeywordFromUri, deleteKeywordsForUri

    Args:

       * theUri -  a str representing a layer uri as parameter.
         .e.g. 'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
         password=\'bar\' sslmode=disable key=\'id\' srid=4326
       * keywords - mandatory - the metadata keyword to retrieve e.g. 'title'
       * theDatabasePath - optional string giving path to the sqlite
         database to use. If the database does not exist it will be
         created.

    Returns:
       A string containing the retrieved value for the keyword if
       the keyword argument is specified, otherwise the
       complete keywords dictionary is returned.

    Raises:
       KeywordNotFoundException if the keyword is not recognised.
    """
    myHash = getHashForDatasource(theUri)
    myConnection = openConnection(theDatabasePath)
    try:
        myCursor = getCursor(myConnection)
        #now see if we have any data for our hash
        mySQL = 'select dict from keyword where hash = \'' + myHash + '\';'
        myCursor.execute(mySQL)
        myData = myCursor.fetchone()
        myPickle = pickle.dumps(theKeywords, pickle.HIGHEST_PROTOCOL)
        if myData is None:
            #insert a new rec
            #myCursor.execute('insert into keyword(hash) values(:hash);',
            #             {'hash': myHash})
            myCursor.execute('insert into keyword(hash, dict) values('
                             ':hash, :dict);',
                         {'hash': myHash, 'dict': sqlite.Binary(myPickle)})
            myConnection.commit()
        else:
            #update existing rec
            myCursor.execute('update keyword set dict=? where hash = ?;',
                         (sqlite.Binary(myPickle), myHash))
            myConnection.commit()
    except sqlite.Error, e:
        print "SQLITE Error %s:" % e.args[0]
        myConnection.rollback()
    except Exception, e:
        print "Error %s:" % e.args[0]
        myConnection.rollback()
        raise
    finally:
        closeConnection(myConnection)


def readKeywordFromUri(theUri, theKeyword=None, theDatabasePath=None):
    """Get metadata from the keywords file associated with a
    non local layer (e.g. postgresql connection).

    A hash will be constructed from the supplied uri and a lookup made
    in a local SQLITE database for the keywords. If there is an existing
    record it will be returned, if not and error will be thrown.

    .. seealso:: writeKeywordsForUri,deleteKeywordsForUri

    Args:

       * theUri -  a str representing a layer uri as parameter.
         .e.g. 'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
         password=\'bar\' sslmode=disable key=\'id\' srid=4326
       * keyword - optional - the metadata keyword to retrieve e.g. 'title'
       * theDatabasePath - optional string giving path to the sqlite
         database to use. If the database does not exist it will be
         created.

    Returns:
       A string containing the retrieved value for the keyword if
       the keyword argument is specified, otherwise the
       complete keywords dictionary is returned.

    Raises:
       KeywordNotFoundException if the keyword is not found.
    """
    myHash = getHashForDatasource(theUri)
    myConnection = openConnection(theDatabasePath)
    try:
        myCursor = getCursor(myConnection)
        #now see if we have any data for our hash
        mySQL = 'select dict from keyword where hash = \'' + myHash + '\';'
        myCursor.execute(mySQL)
        myData = myCursor.fetchone()
        #unpickle it to get our dict back
        if myData is None:
            raise HashNotFoundException('No hash found for %s' % myHash)
        myData = myData[0]  # first field
        myDict = pickle.loads(str(myData))
        if theKeyword is None:
            return myDict
        if theKeyword in myDict:
            return myDict[theKeyword]
        else:
            raise KeywordNotFoundException('No hash found for %s' % myHash)

    except sqlite.Error, e:
        print "Error %s:" % e.args[0]
    except Exception, e:
        print "Error %s:" % e.args[0]
        raise
    finally:
        closeConnection(myConnection)


class ISImpactCalculator():
    """A class to compute an impact scenario."""

    def __init__(self):
        """Constructor for the impact calculator."""
        self.__hazard_layer = None
        self.__exposure_layer = None
        self.__function = None

    def getExposureLayer(self):
        """Accessor: exposure layer."""
        return self.__exposure_layer

    def setExposureLayer(self, value):
        """Mutator: exposure layer."""
        self.__exposure_layer = value

    def delExposureLayer(self):
        """Delete: exposure layer."""
        del self.__exposure_layer

    def getHazardLayer(self):
        """Accessor: hazard layer."""
        return self.__hazard_layer

    def setHazardLayer(self, value):
        """Mutator: hazard layer."""
        self.__hazard_layer = str(value)

    def delHazardLayer(self):
        """Delete: hazard layer."""
        del self.__hazard_layer

    def getFunction(self):
        """Accessor: function layer."""
        return self.__function

    def setFunction(self, value):
        """Mutator: function layer."""
        self.__function = str(value)

    def delFunction(self):
        """Delete: function layer."""
        del self.__function

    _hazard_layer = property(getHazardLayer, setHazardLayer,
        delHazardLayer, tr("""Hazard layer property  (e.g. a flood depth
        raster)."""))

    _exposure_layer = property(getExposureLayer, setExposureLayer,
        delExposureLayer, tr("""Exposure layer property (e.g. buildings or
        features that will be affected)."""))

    _function = property(getFunction, setFunction,
        delFunction, tr("""Function property (specifies which
        inasafe function to use to process the hazard and exposure
        layers with."""))

    def getRunner(self):
        """ Factory to create a new runner thread.
        Requires three parameters to be set before execution
        can take place:

        * Hazard layer - a path to a raster (string)
        * Exposure layer - a path to a vector hazard layer (string).
        * Function - a function name that defines how the Hazard assessment
          will be computed (string).

        Args:
           None.
        Returns:
           None
        Raises:
           InsufficientParametersException if not all parameters are
           set.
        """
        self.__filename = None
        self.__result = None
        if not self.__hazard_layer or self.__hazard_layer == '':
            myMessage = tr('Error: Hazard layer not set.')
            raise InsufficientParametersException(myMessage)

        if not self.__exposure_layer or self.__exposure_layer == '':
            myMessage = tr('Error: Exposure layer not set.')
            raise InsufficientParametersException(myMessage)

        if not self.__function or self.__function == '':
            myMessage = tr('Error: Function not set.')
            raise InsufficientParametersException(myMessage)

        # Call impact calculation engine
        myHazardLayer = read_layer(self.__hazard_layer)
        myExposureLayer = read_layer(self.__exposure_layer)
        myFunctions = get_plugins(self.__function)
        myFunction = myFunctions[0][self.__function]
        return ImpactCalculatorThread(myHazardLayer,
                                      myExposureLayer,
                                      myFunction)


class CalculatorNotifier(QObject):
    """A simple notification class so that we can
    listen for signals indicating when processing is
    done.

    Example::

      from impactcalculator import *
      n = CalculatorNotifier()
      n.done.connect(n.showMessage)
      n.done.emit()

    Prints 'hello' to the console
"""
    done = pyqtSignal()

    def showMessage(self):
        print 'hello'


class ImpactCalculatorThread(threading.Thread):
    """A threaded class to compute an impact scenario. Under
        python a thread can only be run once, so the instances
        based on this class are designed to be short lived.
        """

    def __init__(self, theHazardLayer, theExposureLayer,
                 theFunction):
        """Constructor for the impact calculator thread.

        Args:

          * Hazard layer: InaSAFE read_layer object containing the Hazard data.
          * Exposure layer: InaSAFE read_layer object containing the Exposure
            data.
          * Function: a InaSAFE function that defines how the Hazard assessment
            will be computed.

        Returns:
           None
        Raises:
           InsufficientParametersException if not all parameters are
           set.

        Requires three parameters to be set before execution
        can take place:
        """

        threading.Thread.__init__(self)
        self._hazardLayer = theHazardLayer
        self._exposureLayer = theExposureLayer
        self._function = theFunction
        self._notifier = CalculatorNotifier()
        self._impactLayer = None
        self._result = None

    def notifier(self):
        """Return a qobject that will emit a 'done' signal when the
        thread completes."""
        return self._notifier

    def impactLayer(self):
        """Return the InaSAFE layer instance which is the output from the
        last run."""
        return self._impactLayer

    def result(self):
        """Return the result of the last run."""
        return self._result

    def run(self):
        """ Main function for hazard impact calculation thread.
        Requires three properties to be set before execution
        can take place:

        * Hazard layer - a path to a raster,
        * Exposure layer - a path to a vector points layer.
        * Function - a function that defines how the Hazard assessment
          will be computed.

        After the thread is complete, you can use the filename and
        result accessors to determine what the result of the analysis was::

          calculator = ISImpactCalculator()
          rasterPath = os.path.join(TESTDATA, 'xxx.asc')
          vectorPath = os.path.join(TESTDATA, 'xxx.shp')
          calculator.setHazardLayer(self.rasterPath)
          calculator.setExposureLayer(self.vectorPath)
          calculator.setFunction('Flood Building Impact Function')
          myRunner = calculator.getRunner()
          #wait till completion
          myRunner.join()
          myResult = myRunner.result()
          myFilename = myRunner.filename()


        Args:
           None.
        Returns:
           None
        Raises:
           None
           set.
        """
        try:
            myLayers = [self._hazardLayer, self._exposureLayer]
            self._impactLayer = calculate_impact(layers=myLayers,
                                                 impact_fcn=self._function)
        except Exception, e:
            myMessage = tr('Calculation error encountered:\n')
            myMessage += getExceptionWithStacktrace(e, html=True)
            print myMessage
            self._result = myMessage
        else:
            self._result = tr('Calculation completed successfully.')

        #  Let any listending slots know we are done
        self._notifier.done.emit()
