"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **IS Keyword IO implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.3.0'
__date__ = '29/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
from PyQt4.QtCore import QCoreApplication, QSettings
import sqlite3 as sqlite
import cPickle as pickle
from is_exceptions import (HashNotFoundException,
                           KeywordNotFoundException)
from is_safe_interface import (verify,
                               readKeywordsFromFile,
                               writeKeywordsToFile)


def tr(theText):
    """We define a tr() alias here since the ISKwywordIO implementation below
    is not a class and does not inherit from QObject.
    .. note:: see http://tinyurl.com/pyqt-differences
    Args:
       theText - string to be translated
    Returns:
       Translated version of the given string if available, otherwise
       the original string.
    """
    myContext = "ISKeywordIO"
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


def defaultKeywordDbPath():
    """Helper to get the default path for the keywords file (which is
    <plugin dir>/keywords.db)
    Args:
        None
    Returns:
        A string representing the path to where the keywords file is to be.
    Raises:
        None
    """
    myParentDir = os.path.abspath(
                                os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(myParentDir, 'keywords.db')


def keywordDbPath():
    """Helper to get the active path for the keywords
    Args:
        None
    Returns:
        A string representing the path to where the keywords file is to be.
        If the user has never specified what this path is, the
        defaultKeywordDbPath is returned.
    Raises:
        None
    """
    mySettings = QSettings()
    myPath = mySettings.value(
                            'inasafe/keywordCachePath',
                            defaultKeywordDbPath()).toString()
    return myPath


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
    if thePath is None:
        thePath = keywordDbPath()
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


def copyKeywords(sourceFile, destinationFile, theExtraKeywords=None):
    """Helper to copy the keywords file from a source dataset
    to a destination dataset.

    e.g.::

    copyKeywords('foo.shp', 'bar.shp')

    Will result in the foo.keywords file being copied to bar.keyword.

    Optional argument extraKeywords is a dictionary with additional
    keywords that will be added to the destination file
    e.g::

    copyKeywords('foo.shp', 'bar.shp', {'resolution': 0.01})
    """

    # FIXME (Ole): Need to turn qgis strings into normal strings earlier
    mySourceBase = os.path.splitext(str(sourceFile))[0]
    myDestinationBase = os.path.splitext(destinationFile)[0]
    myNewSource = mySourceBase + '.keywords'
    myNewDestination = myDestinationBase + '.keywords'

    if not os.path.isfile(myNewSource):
        myMessage = tr('Keywords file associated with dataset could not be '
                       'found: \n%s' % myNewSource)
        raise KeywordNotFoundException(myMessage)

    if theExtraKeywords is None:
        theExtraKeywords = {}
    myMessage = tr('Expected extraKeywords to be a dictionary. Got %s'
           % str(type(theExtraKeywords))[1:-1])
    verify(isinstance(theExtraKeywords, dict), myMessage)

    try:
        mySourceKeywords = readKeywordsFromFile(myNewSource)
        myDestinationKeywords = mySourceKeywords
        for key in theExtraKeywords:
            myDestinationKeywords[key] = theExtraKeywords[key]
        writeKeywordsToFile(myDestinationKeywords, myNewDestination)
    except Exception, e:
        myMessage = tr('Failed to copy keywords file from :\n%s\nto\%s: %s' %
               (myNewSource, myNewDestination, str(e)))
        raise Exception(myMessage)

    #try:
    #    shutil.copyfile(myNewSource, myNewDestination)
    #except Exception, e:
    #    myMessage = ('Failed to copy keywords file from :\n%s\nto\%s: %s' %
    #           (myNewSource, myNewDestination, str(e)))
    #    raise Exception(myMessage)

    return