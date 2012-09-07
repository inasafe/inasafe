"""Implementation of tools to do with system administration made
as platform independent as possible.
"""

import sys
import os
import string
import urllib
import urllib2
import getpass
import tarfile
import warnings

try:
    import hashlib
except ImportError:
    import md5 as hashlib

def get_user_name():
    """Get user name provide by operating system
    """

    if sys.platform == 'win32':
        #user = os.getenv('USERPROFILE')
        user = os.getenv('USERNAME')
    else:
        user = os.getenv('LOGNAME')


    return user

def get_host_name():
    """Get host name provide by operating system
    """

    if sys.platform == 'win32':
        host = os.getenv('COMPUTERNAME')
    else:
        host = os.uname()[1]


    return host


def safe_crc(string):
    """64 bit safe crc computation.

    See http://docs.python.org/library/zlib.html#zlib.crc32:

        To generate the same numeric value across all Python versions
        and platforms use crc32(data) & 0xffffffff.
    """

    from zlib import crc32

    return crc32(string) & 0xffffffff


def compute_checksum(filename, max_length=2**20):
    """Compute the CRC32 checksum for specified file

    Optional parameter max_length sets the maximum number
    of bytes used to limit time used with large files.
    Default = 2**20 (1MB)
    """

    fid = open(filename, 'rb') # Use binary for portability
    crcval = safe_crc(fid.read(max_length))
    fid.close()

    return crcval

def get_pathname_from_package(package):
    """Get pathname of given package (provided as string)

    This is useful for reading files residing in the same directory as
    a particular module. Typically, this is required in unit tests depending
    on external files.

    The given module must start from a directory on the pythonpath
    and be importable using the import statement.

    Example
    path = get_pathname_from_package('anuga.utilities')

    """

    exec('import %s as x' %package)

    path = x.__path__[0]

    return path

    # Alternative approach that has been used at times
    #try:
    #    # When unit test is run from current dir
    #    p1 = read_polygon('mainland_only.csv')
    #except:
    #    # When unit test is run from ANUGA root dir
    #    from os.path import join, split
    #    dir, tail = split(__file__)
    #    path = join(dir, 'mainland_only.csv')
    #    p1 = read_polygon(path)


##
# @brief Split a string into 'clean' fields.
# @param str The string to process.
# @param delimiter The delimiter string to split 'line' with.
# @return A list of 'cleaned' field strings.
# @note Any fields that were initially zero length will be removed.
# @note If a field contains '\n' it isn't zero length.
def clean_line(str, delimiter):
    """Split string on given delimiter, remove whitespace from each field."""

    return [x.strip() for x in str.strip().split(delimiter) if x != '']


################################################################################
# The following two functions are used to get around a problem with numpy and
# NetCDF files.  Previously, using Numeric, we could take a list of strings and
# convert to a Numeric array resulting in this:
#     Numeric.array(['abc', 'xy']) -> [['a', 'b', 'c'],
#                                      ['x', 'y', ' ']]
#
# However, under numpy we get:
#     numpy.array(['abc', 'xy']) -> ['abc',
#                                    'xy']
#
# And writing *strings* to a NetCDF file is problematic.
#
# The solution is to use these two routines to convert a 1-D list of strings
# to the 2-D list of chars form and back.  The 2-D form can be written to a
# NetCDF file as before.
#
# The other option, of inverting a list of tag strings into a dictionary with
# keys being the unique tag strings and the key value a list of indices of where
# the tag string was in the original list was rejected because:
#    1. It's a lot of work
#    2. We'd have to rewite the I/O code a bit (extra variables instead of one)
#    3. The code below is fast enough in an I/O scenario
################################################################################

##
# @brief Convert 1-D list of strings to 2-D list of chars.
# @param l 1-dimensional list of strings.
# @return A 2-D list of 'characters' (1 char strings).
# @note No checking that we supply a 1-D list.
def string_to_char(l):
    '''Convert 1-D list of strings to 2-D list of chars.'''

    if not l:
        return []

    if l == ['']:
        l = [' ']

    maxlen = reduce(max, map(len, l))
    ll = [x.ljust(maxlen) for x in l]
    result = []
    for s in ll:
        result.append([x for x in s])
    return result


##
# @brief Convert 2-D list of chars to 1-D list of strings.
# @param ll 2-dimensional list of 'characters' (1 char strings).
# @return A 1-dimensional list of strings.
# @note Each string has had right-end spaces removed.
def char_to_string(ll):
    '''Convert 2-D list of chars to 1-D list of strings.'''

    return map(string.rstrip, [''.join(x) for x in ll])

################################################################################

##
# @brief Get list of variable names in a python expression string.
# @param source A string containing a python expression.
# @return A list of variable name strings.
# @note Throws SyntaxError exception if not a valid expression.
def get_vars_in_expression(source):
    '''Get list of variable names in a python expression.'''

    import compiler
    from compiler.ast import Node

    ##
    # @brief Internal recursive function.
    # @param node An AST parse Node.
    # @param var_list Input list of variables.
    # @return An updated list of variables.
    def get_vars_body(node, var_list=[]):
        if isinstance(node, Node):
            if node.__class__.__name__ == 'Name':
                for child in node.getChildren():
                    if child not in var_list:
                        var_list.append(child)
            for child in node.getChildren():
                if isinstance(child, Node):
                    for child in node.getChildren():
                        var_list = get_vars_body(child, var_list)
                    break

        return var_list

    return get_vars_body(compiler.parse(source))


##
# @brief Get a file from the web.
# @param file_url URL of the file to fetch.
# @param file_name Path to file to create in the filesystem.
# @param auth Auth tuple (httpproxy, proxyuser, proxypass).
# @param blocksize Read file in this block size.
# @return (True, auth) if successful, else (False, auth).
# @note If 'auth' not supplied, will prompt user.
# @note Will try using environment variable HTTP_PROXY for proxy server.
# @note Will try using environment variable PROXY_USERNAME for proxy username.
# @note Will try using environment variable PROXY_PASSWORD for proxy password.
def get_web_file(file_url, file_name, auth=None, blocksize=1024*1024):
    '''Get a file from the web (HTTP).

    file_url:  The URL of the file to get
    file_name: Local path to save loaded file in
    auth:      A tuple (httpproxy, proxyuser, proxypass)
    blocksize: Block size of file reads

    Will try simple load through urllib first.  Drop down to urllib2
    if there is a proxy and it requires authentication.

    Environment variable HTTP_PROXY can be used to supply proxy information.
    PROXY_USERNAME is used to supply the authentication username.
    PROXY_PASSWORD supplies the password, if you dare!
    '''

    # Simple fetch, if fails, check for proxy error
    try:
        urllib.urlretrieve(file_url, file_name)
        return (True, auth)     # no proxy, no auth required
    except IOError, e:
        if e[1] == 407:     # proxy error
            pass
        elif e[1][0] == 113:  # no route to host
            print 'No route to host for %s' % file_url
            return (False, auth)    # return False
        else:
            print 'Unknown connection error to %s' % file_url
            return (False, auth)

    # We get here if there was a proxy error, get file through the proxy
    # unpack auth info
    try:
        (httpproxy, proxyuser, proxypass) = auth
    except:
        (httpproxy, proxyuser, proxypass) = (None, None, None)

    # fill in any gaps from the environment
    if httpproxy is None:
        httpproxy = os.getenv('HTTP_PROXY')
    if proxyuser is None:
        proxyuser = os.getenv('PROXY_USERNAME')
    if proxypass is None:
        proxypass = os.getenv('PROXY_PASSWORD')

    # Get auth info from user if still not supplied
    if httpproxy is None or proxyuser is None or proxypass is None:
        print '-'*72
        print ('You need to supply proxy authentication information.')
        if httpproxy is None:
            httpproxy = raw_input('                    proxy server: ')
        else:
            print '         HTTP proxy was supplied: %s' % httpproxy
        if proxyuser is None:
            proxyuser = raw_input('                  proxy username: ')
        else:
            print 'HTTP proxy username was supplied: %s' % proxyuser
        if proxypass is None:
            proxypass = getpass.getpass('                  proxy password: ')
        else:
            print 'HTTP proxy password was supplied: %s' % '*'*len(proxyuser)
        print '-'*72

    # the proxy URL cannot start with 'http://', we add that later
    httpproxy = httpproxy.lower()
    if httpproxy.startswith('http://'):
        httpproxy = httpproxy.replace('http://', '', 1)

    # open remote file
    proxy = urllib2.ProxyHandler({'http': 'http://' + proxyuser
                                              + ':' + proxypass
                                              + '@' + httpproxy})
    authinfo = urllib2.HTTPBasicAuthHandler()
    opener = urllib2.build_opener(proxy, authinfo, urllib2.HTTPHandler)
    urllib2.install_opener(opener)
    try:
        webget = urllib2.urlopen(file_url)
    except urllib2.HTTPError, e:
        print 'Error received from proxy:\n%s' % str(e)
        print 'Possibly the user/password is wrong.'
        return (False, (httpproxy, proxyuser, proxypass))

    # transfer file to local filesystem
    fd = open(file_name, 'wb')
    while True:
        data = webget.read(blocksize)
        if len(data) == 0:
            break
        fd.write(data)
    fd.close
    webget.close()

    # return successful auth info
    return (True, (httpproxy, proxyuser, proxypass))


##
# @brief Tar a file (or directory) into a tarfile.
# @param files A list of files (or directories) to tar.
# @param tarfile The created tarfile name.
# @note 'files' may be a string (single file) or a list of strings.
# @note We use gzip compression.
def tar_file(files, tarname):
    '''Compress a file or directory into a tar file.'''

    if isinstance(files, basestring):
        files = [files]

    o = tarfile.open(tarname, 'w:gz')
    for file in files:
        o.add(file)
    o.close()


##
# @brief Untar a file into an optional target directory.
# @param tarname Name of the file to untar.
# @param target_dir Directory to untar into.
def untar_file(tarname, target_dir='.'):
    '''Uncompress a tar file.'''

    o = tarfile.open(tarname, 'r:gz')
    members = o.getmembers()
    for member in members:
        o.extract(member, target_dir)
    o.close()


##
# @brief Return a hex digest (MD5) of a given file.
# @param filename Path to the file of interest.
# @param blocksize Size of data blocks to read.
# @return A hex digest string (16 bytes).
# @note Uses MD5 digest if hashlib not available.
def get_file_hexdigest(filename, blocksize=1024*1024*10):
    '''Get a hex digest of a file.'''

    if hashlib.__name__ == 'hashlib':
        m = hashlib.md5()       # new - 'hashlib' module
    else:
        m = hashlib.new()       # old - 'md5' module - remove once py2.4 gone
    fd = open(filename, 'r')

    while True:
        data = fd.read(blocksize)
        if len(data) == 0:
            break
        m.update(data)

    fd.close()
    return m.hexdigest()


##
# @brief Create a file containing a hexdigest string of a data file.
# @param data_file Path to the file to get the hexdigest from.
# @param digest_file Path to hexdigest file to create.
# @note Uses MD5 digest.
def make_digest_file(data_file, digest_file):
    '''Create a file containing the hex digest string of a data file.'''

    hexdigest = get_file_hexdigest(data_file)
    fd = open(digest_file, 'w')
    fd.write(hexdigest)
    fd.close()


##
# @brief Function to return the length of a file.
# @param in_file Path to file to get length of.
# @return Number of lines in file.
# @note Doesn't count '\n' characters.
# @note Zero byte file, returns 0.
# @note No \n in file at all, but >0 chars, returns 1.
def file_length(in_file):
    '''Function to return the length of a file.'''

    fid = open(in_file)
    data = fid.readlines()
    fid.close()
    return len(data)


