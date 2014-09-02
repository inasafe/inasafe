# coding=utf-8
"""Utilities for InaSAFE
"""
import os
import sys
import numpy
import zipfile
import platform
import gettext
from datetime import date
import getpass
from tempfile import mkstemp
from subprocess import PIPE, Popen
import ctypes
from numbers import Integral
import math

from safe.common.exceptions import VerificationError

# Prefer python's own OrderedDict if it exists
try:
    #pylint: disable=W0611
    from collections import OrderedDict
    #pylint: enable=W0611
except ImportError:
    try:
        from collections import OrderedDict
    except ImportError:
        raise RuntimeError(
            'Could not find an available OrderedDict implementation')

import logging
LOGGER = logging.getLogger('InaSAFE')


class MEMORYSTATUSEX(ctypes.Structure):
    """This class is used for getting the free memory on Windows."""
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
    """Verification of logical statement similar to assertions.

    Input:
      statement: expression

      message: error message in case statement evaluates as False

    Output:
        None

    Raises:
        VerificationError in case statement evaluates to False
    """

    if bool(statement) is False:
        # noinspection PyExceptionInherit
        raise VerificationError(message)


def ugettext(s):
    """Translation support."""
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'i18n'))
    if 'LANG' not in os.environ:
        return s
    if not s:
        return s
    lang = os.environ['LANG']
    filename_prefix = 'inasafe'
    t = gettext.translation(
        filename_prefix, path, languages=[lang], fallback=True)
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

    :param sub_dir: Optional argument which will cause an additional
        subdirectory to be created e.g. /tmp/inasafe/foo/
    :type sub_dir: str

    :return: Path to the temp dir that is created.
    :rtype: str

    :raises: Any errors from the underlying system calls.
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

    :file:'/tmp/inasafe/<dd-mm-yyyy>/<user>/impacts'

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
        # Ensure that the dir is world writable by explicitly setting mode
        os.makedirs(kwargs['dir'], 0777)
        # Reinstate the old mask for tmp dir
        os.umask(umask)
    # Now we have the working dir set up go on and return the filename
    handle, filename = mkstemp(**kwargs)

    # Need to close it using the file handle first for windows!
    os.close(handle)
    try:
        os.remove(filename)
    except OSError:
        pass
    return filename


def zip_shp(shp_path, extra_ext=None, remove_file=False):
    """Zip shape file and its gang (.shx, .dbf, .prj).

    Args:
        * shp_path: str - path to the main shape file.
        * extra_ext: [str] - list of extra extensions related to shapefile.

    Returns:
        str: full path to the created shapefile

    Raises:
        None
    """

    # go to the directory
    current_working_dir = os.getcwd()
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

    os.chdir(current_working_dir)


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
        # e.g. output (its a single line) OSX 10.9 Mavericks
        # PhysMem: 6854M used (994M wired), 1332M unused.
        # output on Mountain lion
        # PhysMem: 1491M wired, 3032M active, 1933M inactive,
        # 6456M used, 1735M free.
    except OSError:
        raise OSError
    platform_version = platform.mac_ver()[0]
    # Might get '10.9.1' so strop off the last no
    parts = platform_version.split('.')
    platform_version = parts[0] + '.' + parts[1]
    platform_version = float(platform_version)

    if platform_version > 10.8:
        stdout_list = stdout_string.split(',')
        unused = stdout_list[1].replace('M unused', '').replace(' ', '')
        unused = unused.replace('.', '')
        return int(unused)
    else:
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


def humanize_min_max(min_value, max_value, interval):
    """Return humanize value format for max and min.
    If the range between the max and min is less than one, the original
    value will be returned.

    Args:
        * min_value
        * max_value
        * interval - (float): the interval between classes in the the
            class list where the results will be used.

    Returns:
        A two-tuple consisting of a string for min_value and a string for
            max_value.

    """
    current_interval = max_value - min_value
    if interval > 1:
        # print 'case 1. Current interval : ', current_interval
        humanize_min_value = format_int(int(round(min_value)))
        humanize_max_value = format_int(int(round(max_value)))

    else:
        # print 'case 2. Current interval : ', current_interval
        humanize_min_value = format_decimal(current_interval, min_value)
        humanize_max_value = format_decimal(current_interval, max_value)
    return humanize_min_value, humanize_max_value


def format_decimal(interval, my_number):
    """Return formatted decimal according to interval decimal place
    For example:
    interval = 0.33 (two decimal places)
    my_float = 1.1215454
    Return 1.12 (return only two decimal places as string)
    If interval is an integer return integer part of my_number
    If my_number is an integer return as is
    """
    interval = get_significant_decimal(interval)
    if isinstance(interval, Integral) or isinstance(my_number, Integral):
        return format_int(int(my_number))
    if interval != interval:
        # nan
        return str(my_number)
    if my_number != my_number:
        # nan
        return str(my_number)
    decimal_places = len(str(interval).split('.')[1])
    my_number_int = str(my_number).split('.')[0]
    my_number_decimal = str(my_number).split('.')[1][:decimal_places]
    if len(set(my_number_decimal)) == 1 and my_number_decimal[-1] == '0':
        return my_number_int
    return (format_int(int(my_number_int)) + get_decimal_separator() +
            my_number_decimal)


def get_decimal_separator():
    """Return decimal separator according to the locale."""
    lang = os.getenv('LANG')
    if lang == 'id':
        return ','
    else:
        return '.'


def get_thousand_separator():
    """Return decimal separator according to the locale."""
    lang = os.getenv('LANG')
    if lang == 'id':
        return '.'
    else:
        return ','


def get_significant_decimal(my_decimal):
    """Return a truncated decimal by last three digit after leading zero."""
    if isinstance(my_decimal, Integral):
        return my_decimal
    if my_decimal != my_decimal:
        # nan
        return my_decimal

    my_int_part = str(my_decimal).split('.')[0]
    my_decimal_part = str(my_decimal).split('.')[1]
    first_not_zero = 0
    for i in xrange(len(my_decimal_part)):
        if my_decimal_part[i] == '0':
            continue
        else:
            first_not_zero = i
            break
    my_truncated_decimal = my_decimal_part[:first_not_zero + 3]
    # rounding
    my_leftover_number = my_decimal_part[:first_not_zero + 3:]
    my_leftover_number = int(float('0.' + my_leftover_number))
    round_up = False
    if my_leftover_number == 1:
        round_up = True
    my_truncated = float(my_int_part + '.' + my_truncated_decimal)
    if round_up:
        my_bonus = 1 * 10 ^ (-(first_not_zero + 4))
        my_truncated += my_bonus
    return my_truncated


def humanize_class(my_classes):
    """Return humanize interval of an array.

    For example::

        Original Array:                     Result:
        1.1  -  5754.1                      0  -  1
        5754.1  -  11507.1                  1  -  5,754
                                            5,754  -  11,507

        Original Array:                     Result:
        0.1  -  0.5                         0  -  0.1
        0.5  -  0.9                         0.1  -  0.5
                                            0.5  -  0.9

        Original Array:                     Result:
        7.1  -  7.5                         0  -  7.1
        7.5  -  7.9                         7.1  -  7.5
                                            7.5  -  7.9

        Original Array:                     Result:
        6.1  -  7.2                         0  -  6
        7.2  -  8.3                         6  -  7
        8.3  -  9.4                         7  -  8
                                            8  -  9
    """
    min_value = 0
    if min_value - my_classes[0] == 0:
        return humanize_class(my_classes[1:])
    humanize_classes = []
    interval = my_classes[-1] - my_classes[-2]
    for max_value in my_classes:
        humanize_classes.append(
            humanize_min_max(min_value, max_value, interval))
        min_value = max_value
        try:
            if humanize_classes[-1][0] == humanize_classes[-1][-1]:
                return unhumanize_class(my_classes)
        except IndexError:
            continue
    return humanize_classes


def unhumanize_class(my_classes):
    """Return class as interval without formatting."""
    result = []
    interval = my_classes[-1] - my_classes[-2]
    min_value = 0
    for max_value in my_classes:
        result.append((format_decimal(interval, min_value),
                       format_decimal(interval, max_value)))
        min_value = max_value
    return result


def unhumanize_number(number):
    """Return number without formatting.
    if something goes wrong in the conversion just return the passed number
    We catch AttributeError in case the number has no replace method which
    means it is not a string but already an int or float
    We catch ValueError if number is a sting but not parseable to a number
    like the 'no data' case

    @param number:
    """
    try:
        number = number.replace(get_thousand_separator(), '')
        number = int(float(number))
    except (AttributeError, ValueError):
        pass

    return number


def create_classes(class_list, num_classes):
    """Create classes from class_list.

    Classes will use linspace from numpy.
    It will extend from min and max of elements in class_list. If min == 0,
    it won't be included. The number of classes is equal to num_classes.
    Please see the unit test for this function for more explanation

    :param class_list: All values as a basis to create classes.
    :type class_list: list

    :param num_classes: The number of class to hold all values in class_list.
    :type num_classes: int
    """
    unique_class_list = list(set(class_list))
    min_value = numpy.nanmin(unique_class_list)
    max_value = numpy.nanmax(unique_class_list)

    # If min_value == max_value (it only has 1 unique class), or
    # max_value <= 1.0, then we will populate the classes from 0 - max_value
    if (min_value == max_value) or (max_value <= 1):
        # noinspection PyTypeChecker,PyUnresolvedReferences
        classes = numpy.linspace(0, max_value, num_classes + 1).tolist()
        return classes[1:]

    # Else from above cases, we will populate the 1st class by these rules:
    # 1. The 1st class range: 0 - math.ceil(the smallest value that is not 0)
    # 2. If math.ceil(the smallest value that's not 0) != 1, then subtract by
    #    1 so that the this smallest value goes into the 2nd class.
    # 3. (AG) Yes! The idea is to classify the non affected value to the 1st
    #    class (see #637, #702)

    # Now, Get the smallest value that is not 0
    non_zero_min_value = max_value
    for value in unique_class_list:
        if value < non_zero_min_value and value != 0:
            non_zero_min_value = value

    lower_bound = math.ceil(non_zero_min_value)
    if lower_bound != 1:
        lower_bound -= 1

    # noinspection PyTypeChecker,PyUnresolvedReferences
    classes = numpy.linspace(lower_bound, max_value, num_classes).tolist()

    return classes


def create_label(label_tuple, extra_label=None):
    """Return a label based on my_tuple (a,b) and extra label.

    a and b are string.

    The output will be something like:
                [a - b] extra_label
    """
    if extra_label is not None:
        return '[' + ' - '.join(label_tuple) + '] ' + str(extra_label)
    else:
        return '[' + ' - '.join(label_tuple) + ']'


def get_utm_zone(longitude):
    """Return utm zone."""
    zone = int((math.floor((longitude + 180.0) / 6.0) + 1) % 60)
    if zone == 0:
        zone = 60
    return zone


def get_utm_epsg(longitude, latitude):
    """Return epsg code of the utm zone.

    The code is based on the code:
    http://gis.stackexchange.com/questions/34401
    """
    epsg = 32600
    if latitude < 0.0:
        epsg += 100
    epsg += get_utm_zone(longitude)
    return epsg


def feature_attributes_as_dict(field_map, attributes):
    """Converts list of attributes to dict of attributes.

    :param field_map: Dictionary {'FieldName': FieldIndex}.
    :type field_map: dict

    :param attributes: list of field's values
    :type attributes: list

    :returns: Dictionary {'FieldName': FieldValue}
    :rtype: dict
    """
    res = {}
    for name in field_map:
        res[name] = attributes[field_map[name]]
    return res


def which(name, flags=os.X_OK):
    """Search PATH for executable files with the given name.

    ..note:: This function was taken verbatim from the twisted framework,
      licence available here:
      http://twistedmatrix.com/trac/browser/tags/releases/twisted-8.2.0/LICENSE

    On newer versions of MS-Windows, the PATHEXT environment variable will be
    set to the list of file extensions for files considered executable. This
    will normally include things like ".EXE". This function will also find
    files
    with the given name ending with any of these extensions.

    On MS-Windows the only flag that has any meaning is os.F_OK. Any other
    flags will be ignored.

    :param name: The name for which to search.
    :type name: C{str}

    :param flags: Arguments to L{os.access}.
    :type flags: C{int}

    :returns: A list of the full paths to files found, in the order in which
        they were found.
    :rtype: C{list}
    """
    result = []
    #pylint: disable=W0141
    extensions = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
    #pylint: enable=W0141
    path = os.environ.get('PATH', None)
    # In c6c9b26 we removed this hard coding for issue #529 but I am
    # adding it back here in case the user's path does not include the
    # gdal binary dir on OSX but it is actually there. (TS)
    if sys.platform == 'darwin':  # Mac OS X
        gdal_prefix = (
            '/Library/Frameworks/GDAL.framework/'
            'Versions/Current/Programs/')
        path = '%s:%s' % (path, gdal_prefix)

    LOGGER.debug('Search path: %s' % path)

    if path is None:
        return []

    for p in path.split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            result.append(p)
        for e in extensions:
            path_extensions = p + e
            if os.access(path_extensions, flags):
                result.append(path_extensions)

    return result


def get_non_conflicting_attribute_name(default_name, attribute_names):
    """Get a non conflicting attribute name from a set of attribute names.

    It also complies the shp attribute name restriction that the name length
    must be less than 10 character.

    :param default_name: The default name for the attribute.
    :type default_name: str

    :param attribute_names: Set of attribute names that should not be
        conflicted.
    :type attribute_names: list
    """
    uppercase_attribute_names = [
        x.upper() for x in attribute_names]
    # For shp file, the attribute name must be <= 10
    new_name = default_name[:10]
    i = 0
    while new_name.upper() in uppercase_attribute_names:
        i += 1
        new_name = '%s_%s' % (new_name[:8], i)
    return new_name


def log_file_path():
    """Get InaSAFE log file path.

    :return: InaSAFE log file path.
    :rtype: str
    """
    log_temp_dir = temp_dir('logs')
    path = os.path.join(log_temp_dir, 'inasafe.log')
    return path


def romanise(number):
    """Return the roman numeral for a number.

    Note that this only works for number in interval range [0, 12] since at
    the moment we only use it on realtime earthquake to conver MMI value.

    :param number: The number that will be romanised
    :type number: float

    :return Roman numeral equivalent of the value
    :rtype: str
    """
    if number is None:
        return ''

    roman_list = ['0', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII',
                  'IX', 'X', 'XI', 'XII']
    try:
        roman = roman_list[int(number)]
    except ValueError:
        return None
    return roman
