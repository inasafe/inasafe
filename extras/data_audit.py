"""Track IP of data files in an entire directory tree.
See docstring for the public function IP_verified()
for details on algorithm.

An example of the XML format expected by this module is


<?xml version="1.0" encoding="iso-8859-1"?>

<ga_license_file>
  <metadata>
    <author>Ole Nielsen</author>
  </metadata>

  <datafile>
    <filename>channel1.png</filename>
    <checksum>1339122967</checksum>
    <publishable>Yes</publishable>
    <accountable>Ole Nielsen</accountable>
    <source>Generated by ANUGA development team</source>
    <IP_owner>Geoscience Australia</IP_owner>
    <IP_info>For use with ANUGA manual</IP_info>
  </datafile>

</ga_license_file>


There can be more than one <datafile> element to cover files
with different extensions.


Here's a DTD format, we might implement one day

   <!DOCTYPE ga_license_file [
      <!ELEMENT ga_license_file (source, datafile+)>
      <!ELEMENT metadata (author, svn_keywords)>
      <!ELEMENT svn_keywords (author, date, revision, url, id)>
      <!ELEMENT datafile (filename, publishable, accountable,
      			owner, location, IP_info)>
      <!ELEMENT filename (#PCDATA)>
      <!ELEMENT publishable (#PCDATA)>
      <!ELEMENT accountable (#PCDATA)>
      <!ELEMENT source (#PCDATA)>
      <!ELEMENT IP_owner (#PCDATA)>
      <!ELEMENT IP_info (#PCDATA)>
  ]>



"""
from __future__ import print_function
from __future__ import absolute_import

from builtins import str
from os import remove, walk, sep
from os.path import join, splitext

# Don't add anuga.utilities to these imports
# EQRM also uses this file, but has a different directory structure
from .xml_tools import xml2object, XML_element
from .system_tools import compute_checksum


# Audit exceptions
class NotPublishable(Exception): pass
class FilenameMismatch(Exception): pass
class CRCMismatch(Exception): pass
class Invalid(Exception): pass
class WrongTags(Exception): pass
class Empty(Exception): pass

audit_exceptions = (NotPublishable,
                    FilenameMismatch,
                    CRCMismatch,
                    Invalid,
                    WrongTags,
                    Empty)


def IP_verified(directory,
                extensions_to_ignore=None,
                directories_to_ignore=None,
                files_to_ignore=None,
                verbose=False):
    """Find and audit potential data files that might violate IP

    This is the public function to be used to ascertain that
    all data in the specified directory tree has been audited according
    to the GA data IP tracking process.

    if IP_verified is False:
        # Stop and take remedial action
        ...
    else:
        # Proceed boldly with confidence

    verbose controls standard output.
    If verbose is False, only diagnostics about failed audits will appear.
    All files that check OK will pass silently.

    Optional arguments extensions_to_ignore, directories_to_ignore, and
    files_to_ignore are lists of things to skip.

    Examples are:
    extensions_to_ignore = ['.py','.c','.h', '.f'] # Ignore source code
    files_to_ignore = ['README.txt']
    directories_to_ignore = ['.svn', 'misc']

    None is also OK for these parameters.

    """

    # Identify data files
    oldpath = None
    all_files = 0
    ok_files = 0
    all_files_accounted_for = True
    for dirpath, filename in identify_datafiles(directory,
                                                extensions_to_ignore,
                                                directories_to_ignore,
                                                files_to_ignore):


        if oldpath != dirpath:
            # Decide if dir header needs to be printed
            oldpath = dirpath
            first_time_this_dir = True



        all_files += 1

        basename, ext = splitext(filename)
        license_filename = join(dirpath, basename + '.lic')


        # Look for a XML license file with the .lic
        status = 'OK'
        try:
            fid = open(license_filename)
        except IOError:
            status = 'NO LICENSE FILE'
            all_files_accounted_for = False
        else:
            fid.close()

            try:
                license_file_is_valid(license_filename,
                                      filename,
                                      dirpath,
                                      verbose=False)
            except audit_exceptions as e:
                all_files_accounted_for = False
                status = 'LICENSE FILE NOT VALID\n'
                status += 'REASON: %s\n' %e

                try:
                    doc = xml2object(license_filename)
                except:
                    status += 'XML file %s could not be read:'\
                              %license_filename
                    fid = open(license_filename)
                    status += fid.read()
                    fid.close()
                else:
                    pass
                    #if verbose is True:
                    #    status += str(doc)



        if status == 'OK':
            ok_files += 1
        else:
            # Only print status if there is a problem (no news is good news)
            if first_time_this_dir is True:
                print()
                msg = ('Files without licensing info in dir: %s'
                       % dirpath)
                # fix_print_with_import
                print('.' * len(msg))
                # fix_print_with_import
                print(msg)
                # fix_print_with_import
                print('.' * len(msg))
                first_time_this_dir = False


            # fix_print_with_import
            print(filename + ' (Checksum = %s): '\
                  %str(compute_checksum(join(dirpath, filename))),\
                  status)


    if verbose is True:
        print()
        # fix_print_with_import
        print('---------------------')
        # fix_print_with_import
        print('Audit result for dir: %s:' %directory)
        # fix_print_with_import
        print('---------------------')
        # fix_print_with_import
        print('Number of files audited:  %d' %(all_files))
        # fix_print_with_import
        print('Number of files verified: %d' %(ok_files))
        print()

    # Return result
    return all_files_accounted_for



#------------------
# Private functions
#------------------
def identify_datafiles(root,
                       extensions_to_ignore=None,
                       directories_to_ignore=None,
                       files_to_ignore=None):
    """ Identify files that might contain data

    See function IP_verified() for details about optinoal parmeters
    """

    for dirpath, dirnames, filenames in walk(root):

        for ignore in directories_to_ignore:
            if ignore in dirnames:
                dirnames.remove(ignore)  # don't visit ignored directories


        for filename in filenames:


            # Ignore extensions that need no IP check
            ignore = False
            for ext in extensions_to_ignore:
                if filename.endswith(ext):
                    ignore = True

            if filename in files_to_ignore:
                ignore = True

            if ignore is False:
                yield dirpath, filename


def license_file_is_valid(license_filename, data_filename,
                          dirpath='.', verbose=False):
    """Check that XML license file for given filename_to_verify is valid.

    Input:
        license_filename: XML license file (must be an absolute path name)
        data_filename: The data filename that is being audited
        dir_path: Where the files live
        verbose: Optional verbosity


    Check for each datafile listed that

    * Datafile tags are there and match the one specified
    * Fields are non empty (except IP_info which can be left blank)
    * Datafile exists
    * Checksum is correct
    * Datafile is flagged as publishable

    If anything is violated an appropriate exception is raised.
    If everything is honky dory the function will return True.
    """

    if verbose:
        # fix_print_with_import
        print('Parsing', license_filename)

    doc = xml2object(license_filename)

    # Check that file is valid (e.g. all elements there)
    if 'ga_license_file' not in doc:
        msg = 'License file %s must have two elements' %license_filename
        msg += ' at the root level. They are\n'
        msg += '  <?xml version="1.0" encoding="iso-8859-1"?>\n'
        msg += '  <ga_license_file>\n'
        msg += 'The second element was found to be %s' %list(doc.keys())
        raise WrongTags(msg)


    # Validate elements: metadata, datafile, datafile, ...
    # FIXME (Ole): I'd like this to verified by the parser
    # using a proper DTD template one day....
    # For not, let's check the main ones.
    elements = doc['ga_license_file']
    if 'metadata' not in elements:
        msg = 'Tag %s must have the element "metadata"'\
              %list(doc.keys())[0]
        msg += 'The element found was %s' %elements[0].nodeName
        raise WrongTags(msg)

    if 'datafile' not in elements:
        msg = 'Tag %s must have the element "datafile"'\
              %list(doc.keys())[0]
        msg += 'The element found was %s' %elements[0].nodeName
        raise WrongTags(msg)

    for key in list(elements.keys()):
        msg = 'Invalid tag: %s' %key
        if not key in ['metadata', 'datafile']:
            raise WrongTags(msg)


    # Extract information for metadata section
    if verbose: print()
    metadata = elements['metadata']

    author = metadata['author']
    if verbose: # fix_print_with_import
 print('Author:   ', author)
    if author == '':
        msg = 'Missing author'
        raise Exception(msg)

    #svn_keywords = metadata['svn_keywords']
    #if verbose: print 'SVN keywords:   ', svn_keywords


    # Extract information for datafile sections
    datafile = elements['datafile']
    if isinstance(datafile, XML_element):
        datafile = [datafile]


    # Check that filename to verify is listed in license file
    found = False
    for data in datafile:
        if data['filename'] == data_filename:
            found = True
            break

    if not found:
        msg = 'Specified filename to verify %s ' %data_filename
        msg += 'did not appear in license file %s' %license_filename
        raise FilenameMismatch(msg)


    # Check contents for selected data_filename
    #for data in datafile:
    #    if verbose: print

    # Filename
    if data['filename'] == '':
        msg = 'Missing filename'
        raise FilenameMismatch(msg)
    else:
        filename = join(dirpath, data['filename'])
        if verbose: # fix_print_with_import
 print('Filename: "%s"' %filename)
        try:
            fid = open(filename, 'r')
        except:
            msg = 'Specified filename %s could not be opened'\
                  %filename
            raise FilenameMismatch(msg)

    # CRC
    reported_crc = data['checksum']
    if verbose: # fix_print_with_import
 print('Checksum: "%s"' %reported_crc)

    file_crc = str(compute_checksum(filename))
    if reported_crc != file_crc:
        msg = 'Bad checksum (CRC).\n'
        msg += '  The CRC reported in license file "%s" is "%s"\n'\
               %(license_filename, reported_crc)
        msg += '  The CRC computed from file "%s" is "%s"'\
               %(filename, file_crc)
        raise CRCMismatch(msg)

    # Accountable
    accountable = data['accountable']
    if verbose: # fix_print_with_import
 print('Accountable: "%s"' %accountable)
    if accountable == '':
        msg = 'No accountable person specified'
        raise Empty(msg)

    # Source
    source = data['source']
    if verbose: # fix_print_with_import
 print('Source: "%s"' %source)
    if source == '':
        msg = 'No source specified'
        raise Empty(msg)

    # IP owner
    ip_owner = data['IP_owner']
    if verbose: # fix_print_with_import
 print('IP owner: "%s"' %ip_owner)
    if ip_owner == '':
        msg = 'No IP owner specified'
        raise Empty(msg)

    # IP info
    ip_info = data['IP_info']
    if verbose: # fix_print_with_import
 print('IP info: "%s"' %ip_info)
    #if ip_info == '':
    #    msg = 'No IP info specified'
    #    raise Empty, msg

    # Publishable
    publishable = data['publishable']
    if verbose: # fix_print_with_import
 print('Publishable: "%s"' %publishable)
    if publishable == '':
        msg = 'No publishable value specified'
        raise NotPublishable(msg)

    if publishable.upper() != 'YES':
        msg = 'Data file %s is not flagged as publishable'\
              %fid.name
        raise NotPublishable(msg)



    # If we get this far, the license file is OK
    return True
