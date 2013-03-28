"""Utilities for InaSAFE
"""
import os
import sys
import zipfile
import gettext
from datetime import date
import getpass
from tempfile import mkstemp
from subprocess import PIPE, Popen
import ctypes

from safe.common.exceptions import VerificationError


class MEMORYSTATUSEX(ctypes.Structure):
    """
    This class is used for getting the free memory on Windows
    """
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]

    def __init__(self):
        # have to initialize this to the size of MEMORYSTATUSEX
        self.dwLength = ctypes.sizeof(self)
        super(MEMORYSTATUSEX, self).__init__()


def verify(statement, message=None):
    """Verification of logical statement similar to assertions
    Input
        statement: expression
        message: error message in case statement evaluates as False

    Output
        None
    Raises
        VerificationError in case statement evaluates to False
    """

    if bool(statement) is False:
        raise VerificationError(message)


def ugettext(s):
    """Translation support
    """
    path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '..', 'i18n'))
    if 'LANG' not in os.environ:
        return s
    lang = os.environ['LANG']
    filename_prefix = 'inasafe'
    t = gettext.translation(filename_prefix,
                            path, languages=[lang], fallback=True)
    return t.ugettext(s)


def temp_dir(sub_dir='work'):
    """Obtain the temporary working directory for the operating system.

    An inasafe subdirectory will automatically be created under this and
    if specified, a user subdirectory under that.

    .. note:: You can use this together with unique_filename to create
       a file in a temporary directory under the inasafe workspace. e.g.

       tmpdir = temp_dir('testing')
       tmpfile = unique_filename(dir=tmpdir)
       print tmpfile
       /tmp/inasafe/23-08-2012/timlinux/testing/tmpMRpF_C

    If you specify INASAFE_WORK_DIR as an environment var, it will be
    used in preference to the system temp directory.

    Args:
        sub_dir str - optional argument which will cause an additional
                subirectory to be created e.g. /tmp/inasafe/foo/

    Returns:
        Path to the output clipped layer (placed in the system temp dir).

    Raises:
       Any errors from the underlying system calls.
    """
    user = getpass.getuser().replace(' ', '_')
    current_date = date.today()
    date_string = current_date.isoformat()
    if 'INASAFE_WORK_DIR' in os.environ:
        new_directory = os.environ['INASAFE_WORK_DIR']
    else:
        # Following 4 lines are a workaround for tempfile.tempdir()
        # unreliabilty
        handle, filename = mkstemp()
        os.close(handle)
        new_directory = os.path.dirname(filename)
        os.remove(filename)

    path = os.path.join(new_directory, 'inasafe', date_string, user, sub_dir)

    if not os.path.exists(path):
        # Ensure that the dir is world writable
        # Umask sets the new mask and returns the old
        old_mask = os.umask(0000)
        os.makedirs(path, 0777)
        # Reinstate the old mask for tmp
        os.umask(old_mask)
    return path


def unique_filename(**kwargs):
    """Create new filename guaranteed not to exist previously

    Use mkstemp to create the file, then remove it and return the name

    If dir is specified, the tempfile will be created in the path specified
    otherwise the file will be created in a directory following this scheme:

    :file:`/tmp/inasafe/<dd-mm-yyyy>/<user>/impacts'

    See http://docs.python.org/library/tempfile.html for details.

    Example usage:

    tempdir = temp_dir(sub_dir='test')
    filename = unique_filename(suffix='.keywords', dir=tempdir)
    print filename
    /tmp/inasafe/23-08-2012/timlinux/test/tmpyeO5VR.keywords

    Or with no preferred subdir, a default subdir of 'impacts' is used:

    filename = unique_filename(suffix='.shp')
    print filename
    /tmp/inasafe/23-08-2012/timlinux/impacts/tmpoOAmOi.shp

    """

    if 'dir' not in kwargs:
        path = temp_dir('impacts')
        kwargs['dir'] = path
    else:
        path = temp_dir(kwargs['dir'])
        kwargs['dir'] = path
    if not os.path.exists(kwargs['dir']):
        # Ensure that the dir mask won't conflict with the mode
        # Umask sets the new mask and returns the old
        umask = os.umask(0000)
        # Ensure that the dir is world writable by explictly setting mode
        os.makedirs(kwargs['dir'], 0777)
        # Reinstate the old mask for tmp dir
        os.umask(umask)
    # Now we have the working dir set up go on and return the filename
    handle, filename = mkstemp(**kwargs)

    # Need to close it using the filehandle first for windows!
    os.close(handle)
    try:
        os.remove(filename)
    except OSError:
        pass
    return filename

try:
    from safe_qgis.utilities import getDefaults as get_qgis_defaults

    def get_defaults(default=None):
        return get_qgis_defaults(theDefault=default)
except ImportError:
    #this is used when we are in safe without access to qgis (e.g. web )
    from safe.defaults import DEFAULTS

    def get_defaults(default=None):
        if default is None:
            return DEFAULTS
        elif default in DEFAULTS:
            return DEFAULTS[default]
        else:
            return None


def zip_shp(shp_path, extra_ext=None, remove_file=False):
    """Zip shape file and its gang (.shx, .dbf, .prj)
    and extra_file is a list of another ext related to shapefile, if exist
    The zip file will be put in the same directory
    """

    # go to the directory
    my_cwd = os.getcwd()
    shp_dir, shp_name = os.path.split(shp_path)
    os.chdir(shp_dir)

    shp_basename, _ = os.path.splitext(shp_name)
    exts = ['.shp', '.shx', '.dbf', '.prj']
    if extra_ext is not None:
        exts.extend(extra_ext)

    # zip files
    zip_filename = shp_basename + '.zip'
    zip_object = zipfile.ZipFile(zip_filename, 'w')
    for ext in exts:
        if os.path.isfile(shp_basename + ext):
            zip_object.write(shp_basename + ext)
    zip_object.close()

    if remove_file:
        for ext in exts:
            if os.path.isfile(shp_basename + ext):
                os.remove(shp_basename + ext)

    os.chdir(my_cwd)


def get_free_memory():
    """Return current free memory on the machine.
    Currently supported for Windows, Linux
    Return in MB unit
    """
    if 'win32' in sys.platform:
        # windows
        return get_free_memory_win()
    elif 'linux2' in sys.platform:
        # linux
        return get_free_memory_linux()
    elif 'darwin' in sys.platform:
        # mac
        return get_free_memory_osx()


def get_free_memory_win():
    """Return current free memory on the machine for windows.
    Warning : this script is really not robust
    Return in MB unit
    """
    stat = MEMORYSTATUSEX()
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    return int(stat.ullAvailPhys / 1024 / 1024)


def get_free_memory_linux():
    """Return current free memory on the machine for linux.
    Warning : this script is really not robust
    Return in MB unit
    """
    try:
        p = Popen('free -m', shell=True, stdout=PIPE)
        stdout_string = p.communicate()[0].split('\n')[2]
    except OSError:
        raise OSError
    stdout_list = stdout_string.split(' ')
    stdout_list = [x for x in stdout_list if x != '']
    return int(stdout_list[3])


def get_free_memory_osx():
    """Return current free memory on the machine for mac os.
    Warning : this script is really not robust
    Return in MB unit
    """
    try:
        p = Popen('echo -e "\n$(top -l 1 | awk \'/PhysMem/\';)\n"',
                  shell=True, stdout=PIPE)
        stdout_string = p.communicate()[0].split('\n')[1]
        # e.g. output (its a single line)
        # PhysMem: 1491M wired, 3032M active, 1933M inactive,
        # 6456M used, 1735M free.
    except OSError:
        raise OSError
    stdout_list = stdout_string.split(',')
    inactive = stdout_list[2].replace('M inactive', '').replace(' ', '')
    free = stdout_list[4].replace('M free.', '').replace(' ', '')
    return int(inactive) + int(free)


def format_int(x):
    """Format integer with separator between thousands.

    Args:
        x: int - a number to be formatted in a locale friendly way.

    Returns:
        str - a locale friendly formatted string e.g. 1,000,0000.00
            representing the original x. If a ValueError exception occurs,
            x is simply returned.

    Raises:
        None

    From http://stackoverflow.com/questions/5513615/
                add-thousands-separators-to-a-number

    # FIXME (Ole)
    Currently not using locale coz broken

    Instead use this:
    http://docs.python.org/library/string.html#formatspec

    """

    # This is broken
    #import locale
    #locale.setlocale(locale.LC_ALL, '')  # Broken, why?
    #s = locale.format('%d', x, 1)
    lang = os.getenv('LANG')
    try:
        s = '{0:,}'.format(x)
        #s = '{0:n}'.format(x)  # n means locale aware (read up on this)
    # see issue #526
    except ValueError:
        return x

    # Quick solution for the moment
    if lang == 'id':
        # Replace commas with dots
        s = s.replace(',', '.')
    return s


def round_thousand(my_int):
    """Round an integer to the nearest thousand if my_int
    is more than a thousand
    """
    if my_int > 1000:
        my_int = my_int // 1000 * 1000
    return my_int
