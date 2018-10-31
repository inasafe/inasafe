# coding=utf-8

"""Utilities for InaSAFE."""

import colorsys
import ctypes
import getpass
import logging
import math
import os
import platform
import sys
from datetime import date
from numbers import Integral
from subprocess import PIPE, Popen
from tempfile import mkstemp

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsProject,
    QgsPointXY)

from safe.common.exceptions import VerificationError
from safe.utilities.rounding import (
    thousand_separator, decimal_separator, add_separators)

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


def python2_round(number, ndigits=0):
    """Python 2 round function,
    see: http://python3porting.com/differences.html#rounding-behavior
    The behavior of round has changed in Python 3. In Python 2, rounding of
    halfway cases was away from zero, and round() would always return a float.

    Round a number to a given precision in decimal digits (default 0 digits).
    This returns an int when called with one argument, otherwise the
    same type as the number. ndigits may be negative.


    :param number: float value to round
    :type number: type, float

    :param ndigits: integer decimal places
    :param ndigits: type, integer

    """
    p = 10 ** ndigits
    return float(math.floor((number * p) + math.copysign(0.5, number))) / p


def verify(statement, message=None):
    """Verification of logical statement similar to assertions.

    :param statement: Expression
    :type statement: type, bool

    :param message: error message in case statement evaluates as False
    :type message: str

    :raises: VerificationError
    """
    if bool(statement) is False:
        # noinspection PyExceptionInherit
        raise VerificationError(message)


def safe_dir(sub_dir=None):
    """Absolute path from safe package directory.

    :param sub_dir: Sub directory relative to safe package directory.
    :type sub_dir: str

    :return: The Absolute path.
    :rtype: str
    """
    safe_relative_path = os.path.join(
        os.path.dirname(__file__), '../')
    return os.path.abspath(
        os.path.join(safe_relative_path, sub_dir))


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
        os.makedirs(path, 0o777)
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
    filename = unique_filename(suffix='.foo', dir=tempdir)
    print filename
    /tmp/inasafe/23-08-2012/timlinux/test/tmpyeO5VR.foo

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
        os.makedirs(kwargs['dir'], 0o777)
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


def get_free_memory():
    """Return current free memory on the machine.

    Currently supported for Windows, Linux, MacOS.

    :returns: Free memory in MB unit
    :rtype: int
    """
    if 'win32' in sys.platform:
        # windows
        return get_free_memory_win()
    elif 'linux' in sys.platform:
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
        p = Popen('free -m', shell=True, stdout=PIPE, encoding='utf8')
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
                  shell=True, stdout=PIPE, encoding='utf8')
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
    platform_version = parts[0] + parts[1]
    # We make version a int by concatenating the two parts
    # so that we can successfully determine that 10.10 (release version)
    # is greater than e.g. 10.8 (release version)
    # 1010 vs 108
    platform_version = int(platform_version)

    if platform_version > 108:
        stdout_list = stdout_string.split(',')
        unused = stdout_list[1].replace('M unused', '').replace(' ', '')
        unused = unused.replace('.', '')
        return int(unused)
    else:
        stdout_list = stdout_string.split(',')
        inactive = stdout_list[2].replace('M inactive', '').replace(' ', '')
        free = stdout_list[4].replace('M free.', '').replace(' ', '')
        return int(inactive) + int(free)


def humanize_min_max(min_value, max_value, interval):
    """Return humanize value format for max and min.

    If the range between the max and min is less than one, the original
    value will be returned.

    :param min_value: Minimum value
    :type min_value: int, float

    :param max_value: Maximim value
    :type max_value: int, float

    :param interval: The interval between classes in the
            class list where the results will be used.
    :type interval: float, int

    :returns: A two-tuple consisting of a string for min_value and a string for
            max_value.
    :rtype: tuple
    """
    current_interval = max_value - min_value
    if interval > 1:
        # print 'case 1. Current interval : ', current_interval
        humanize_min_value = add_separators(int(python2_round(min_value)))
        humanize_max_value = add_separators(int(python2_round(max_value)))

    else:
        # print 'case 2. Current interval : ', current_interval
        humanize_min_value = format_decimal(current_interval, min_value)
        humanize_max_value = format_decimal(current_interval, max_value)
    return humanize_min_value, humanize_max_value


def format_decimal(interval, value):
    """Return formatted decimal according to interval decimal place

    For example:
    interval = 0.33 (two decimal places)
    my_float = 1.1215454
    Return 1.12 (return only two decimal places as string)
    If interval is an integer return integer part of my_number
    If my_number is an integer return as is
    """
    interval = get_significant_decimal(interval)
    if isinstance(interval, Integral) or isinstance(value, Integral):
        return add_separators(int(value))
    if interval != interval:
        # nan
        return str(value)
    if value != value:
        # nan
        return str(value)
    decimal_places = len(str(interval).split('.')[1])
    my_number_int = str(value).split('.')[0]
    my_number_decimal = str(value).split('.')[1][:decimal_places]
    if len(set(my_number_decimal)) == 1 and my_number_decimal[-1] == '0':
        return my_number_int
    formatted_decimal = (add_separators(int(my_number_int))
                         + decimal_separator()
                         + my_number_decimal)
    return formatted_decimal


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
    for i in range(len(my_decimal_part)):
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
        if len(my_classes) == 1:
            return [('0', '0')]
        else:
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

    If something goes wrong in the conversion just return the passed number
    We catch AttributeError in case the number has no replace method which
    means it is not a string but already an int or float
    We catch ValueError if number is a sting but not parseable to a number
    like the 'no data' case

    @param number:
    """
    try:
        number = number.replace(thousand_separator(), '')
        number = int(float(number))
    except (AttributeError, ValueError):
        pass

    return number


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


def get_utm_epsg(longitude, latitude, crs=None):
    """Return epsg code of the utm zone according to X, Y coordinates.

    By default, the CRS is EPSG:4326. If the CRS is provided, first X,Y will
    be reprojected from the input CRS to WGS84.

    The code is based on the code:
    http://gis.stackexchange.com/questions/34401

    :param longitude: The longitude.
    :type longitude: float

    :param latitude: The latitude.
    :type latitude: float

    :param crs: The coordinate reference system of the latitude, longitude.
    :type crs: QgsCoordinateReferenceSystem
    """
    if crs is None or crs.authid() == 'EPSG:4326':
        epsg = 32600
        if latitude < 0.0:
            epsg += 100
        epsg += get_utm_zone(longitude)
        return epsg
    else:
        epsg_4326 = QgsCoordinateReferenceSystem('EPSG:4326')
        transform = QgsCoordinateTransform(
            crs, epsg_4326, QgsProject.instance())
        geom = QgsGeometry.fromPointXY(QgsPointXY(longitude, latitude))
        geom.transform(transform)
        point = geom.asPoint()
        # The point is now in 4326, we can call the function again.
        return get_utm_epsg(point.x(), point.y())


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
    # pylint: disable=W0141
    extensions = [
        _f for _f in os.environ.get(
            'PATHEXT',
            '').split(
            os.pathsep) if _f]
    # pylint: enable=W0141
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


def color_ramp(number_of_colour):
    """Generate list of color in hexadecimal.

    This will generate colors using hsl model by playing around with the hue
    see: https://coderwall.com/p/dvsxwg/smoothly-transition-from-green-to-red

    :param number_of_colour: The number of intervals between R and G spectrum.
    :type number_of_colour: int

    :returns: List of color.
    :rtype: list
    """
    if number_of_colour < 1:
        raise Exception('The number of colours should be > 0')

    colors = []
    if number_of_colour == 1:
        hue_interval = 1
    else:
        hue_interval = 1.0 / (number_of_colour - 1)
    for i in range(number_of_colour):
        hue = (i * hue_interval) / 3
        light = 127.5
        saturation = -1.007905138339921
        rgb = colorsys.hls_to_rgb(hue, light, saturation)
        hex_color = '#%02x%02x%02x' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))
        colors.append(hex_color)
    return colors


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


def humanize_file_size(size):
    """Return humanize size from bytes.

    :param size: The size to humanize in bytes.
    :type size: float

    :return: Human readable size.
    :rtype: unicode
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return '%3.1f %s' % (size, x)
        size /= 1024.0


def add_to_list(my_list, my_element):
    """Helper function to add new my_element to my_list based on its type.

    Add as new element if it's not a list, otherwise extend to the list
    if it's a list.
    It's also guarantee that all elements are unique

    :param my_list: A list
    :type my_list: list

    :param my_element: A new element
    :type my_element: str, list

    :returns: A list with unique element
    :rtype: list

    """
    if isinstance(my_element, list):
        for element in my_element:
            my_list = add_to_list(my_list, element)
    else:
        if my_element not in my_list:
            my_list.append(my_element)

    return my_list
