# coding=utf-8
"""Function to manage self-registering plugins

The design is based on http://effbot.org/zone/metaclass-plugins.htm

To register the plugin, the module must be imported by the Python process
using it.
"""

import logging
from math import ceil
import numpy
from collections import OrderedDict
import keyword as python_keywords

from safe.gis.polygon import inside_polygon
from safe.utilities.i18n import tr
from safe.defaults import default_minimum_needs
from utilities import get_function_title
from safe.definitions import converter_dict
from safe.impact_functions.registry import Registry


LOGGER = logging.getLogger('InaSAFE')


def evacuated_population_weekly_needs(
        population,
        minimum_needs=None):
    """Calculate estimated needs using minimum needs as specified or the
    default.

    :param population: The number of evacuated population.
    :type: int, float

    :param minimum_needs: Ratios used to calculate weekly needs in parameter
     form.
    :type minimum_needs: list,

    :returns: The needs for the evacuated population.
    :rtype: dict
    """
    if not minimum_needs:
        minimum_needs = default_minimum_needs()

    population_needs = OrderedDict()
    for resource in minimum_needs:
        resource = resource.serialize()
        amount = resource['value']
        name = resource['name']
        population_needs[name] = int(ceil(population * float(amount)))

    return population_needs


def evacuated_population_needs(population, minimum_needs):
    """Calculate estimated needs using minimum needs configuration provided
    in full_minimum_needs.

    :param population: The number of evacuated population.
    :type: int, float

    :param minimum_needs: Ratios to use when calculating minimum needs.
        Defaults to perka 7 as described in assumptions below.
    :type minimum_needs: list

    :returns: The needs for the evacuated population.
    :rtype: dict
    """
    frequencies = []
    for resource in minimum_needs:
        if resource['frequency'] not in frequencies:
            frequencies.append(resource['frequency'])

    population_needs_by_frequency = OrderedDict([
        [frequency, []] for frequency in frequencies])

    for resource in minimum_needs:
        if resource['unit']['abbreviation']:
            resource_name = '%s [%s]' % (
                resource['name'],
                resource['unit']['abbreviation'])
        else:
            resource_name = resource['name']
        amount_pp = resource['value']
        resource['amount'] = int(ceil(population * float(amount_pp)))
        resource['table name'] = resource_name
        population_needs_by_frequency[resource['frequency']].append(resource)

    return population_needs_by_frequency


def population_rounding_full(number):
    """This function performs a rigorous population rounding.

    :param number: The amount of people as calculated.
    :type number: int, float

    :returns: result and rounding bracket.
    :rtype: (int, int)
    """
    if number < 1000:
        rounding = 10
    elif number < 100000:
        rounding = 100
    else:
        rounding = 1000
    number = int(rounding * ceil(1.0 * number / rounding))
    return number, rounding


def population_rounding(number):
    """A shorthand for population_rounding_full(number)[0].

    :param number: The amount of people as calculated.
    :type number: int, float

    :returns: result and rounding bracket.
    :rtype: int
    """
    return population_rounding_full(number)[0]


def get_plugins(name=None):
    """Retrieve a list of plugins that match the name you pass.

       Or all of them if no name is passed.
    """
    registry = Registry()
    plugins_dict = dict([(f.metadata().as_dict()['name'], f) for f in
                         registry.filter()])
    if name is None:
        return plugins_dict

    if isinstance(name, basestring):
        function = registry.get_class(name)
        if function is None:
            msg = ('No plugin named "%s" was found. '
                   'List of available plugins is: \n%s'
                   % (name, ',\n '.join(plugins_dict.keys())))
            raise RuntimeError(msg)
        return [{function.__name__: function}]
    else:
        msg = ('get_plugins expects either no parameters or a string '
               'with the name of the plugin, you passed: '
               '%s which is a %s' % (name, type(name)))
        raise Exception(msg)


def get_plugin(name):
    """Get plugin that matches given name

    This is just a wrapper around get_plugins to simplify
    the overly complicated way of extracting the function
    """

    plugin_list = get_plugins(name)
    impact_function = plugin_list[0].items()[0][1]

    return impact_function


def unload_plugins():
    """Unload all loaded plugins.

    .. note:: Added in InaSAFE 1.2.
    """
    for p in FunctionProvider.plugins:
        del p


def remove_impact_function(impact_function):
    """Remove an impact_function from FunctionProvider

    :param impact_function: An impact function that want to be removed
    :type impact_function: FunctionProvider

    """
    if impact_function in FunctionProvider.plugins:
        FunctionProvider.plugins.remove(impact_function)
    del impact_function


def requirements_collect(func):
    """Collect the requirements from the plugin function doc

    The requirements need to be specified using

    :param requires::

    <valid python expression>

    The layer keywords are put into the local name space
    each requires should be on a new line
    a '\\' at the end of a line will be a continuation

    returns a (possibly empty) list of Python expressions

    Example of valid requirements expression

    :param requires::

      category=='hazard' and
      subcategory in ['flood', 'tsunami'] and
      layertype=='raster' and
      unit=='m'
    """

    requires_lines = []
    if hasattr(func, '__doc__') and func.__doc__:

        # Define tag that indentifies requirements expressions
        require_cmd = ':param requires'
        indent = len(require_cmd) + 1  # Index where expression starts

        # Collect Python expressions from docstring
        docstr = func.__doc__
        for line in docstr.split('\n'):
            doc_line = line.strip()

            if doc_line.startswith(require_cmd):
                # Extract expression and remove excessive whitespace
                expression = ' '.join(doc_line[indent:].split())
                requires_lines.append(expression)

    # Return list with one item per requirement
    return requires_lines


def requirement_check(params, require_str, verbose=False):
    """Checks a dictionary params against the requirements defined
    in require_str. Require_str must be a valid python expression
    and evaluate to True or False"""

    # Some keyword should never go into the requirement check
    # FIXME (Ole): This is not the most robust way. If we get a
    # more general way of doing metadata we can treat impact_summary and
    # many other things separately. See issue #148
    excluded_keywords = ['impact_summary']

    execstr = 'def check():\n'
    for key in params.keys():
        if key == '':
            if params[''] != '':
                # This should never happen
                msg = ('Empty key found in requirements with '
                       'non-empty value: %s' % params[''])
                raise Exception(msg)
            else:
                continue

        # Check that symbol is not a Python keyword
        if key in python_keywords.kwlist:
            msg = ('Error in plugin requirements'
                   'Must not use Python keywords as params: %s' % key)
            # print msg
            # LOGGER.error(msg)
            return False

        if key in excluded_keywords:
            continue

        if isinstance(params[key], basestring):
            execstr += '  %s = "%s" \n' % (key.strip(), params[key])
        else:
            execstr += '  %s = %s \n' % (key.strip(), params[key])

    execstr += '  return ' + require_str

    if verbose:
        print execstr
    try:
        # pylint: disable=W0122
        exec(compile(execstr, '<string>', 'exec'))
        # pylint: enable=W0122

        # pylint: disable=E0602
        return check()
        # pylint: enable=E0602
    except NameError, e:
        # This condition will happen frequently since the function
        # is evaled against many params that are not relevant and
        # hence correctly return False
        pass
    except Exception, e:  # pylint: disable=broad-except
        msg = ('Requirements header could not compiled: %s. '
               'Original message: %s' % (execstr, e))
        # print msg
        # LOGGER.error(msg)

    return False


def requirements_met(requirements, params):  # , verbose=False):
    """Checks the plugin can run with a given layer.

       Based on the requirements specified in the doc string.

       Returns:
           True:  if there are no requirements or they are all met.
           False: if it has requirements and none of them are met.
    """
    if len(requirements) == 0:
        # If the function has no requirements, then they are all met.
        return True

    for requires in requirements:
        if requirement_check(params, requires):
            return True

    # If none of the conditions above is met, return False.
    return False


def compatible_layers(func, layer_descriptors):
    """Fetches all the layers that match the plugin requirements.

    Input
        func: ? (FIXME(Ole): Ted, can you fill in here?
        layer_descriptor: Layer names and meta data (keywords, type, etc)

    Output:
        Array of compatible layers, can be an empty list.
    """

    layers = []
    requirements = requirements_collect(func)

    for layer_name, layer_params in layer_descriptors:
        if requirements_met(requirements, layer_params):
            layers.append(layer_name)

    return layers


# -------------------------------
# Helpers for individual plugins
# -------------------------------
def get_hazard_layers(layers):
    """Get list of layers that have category=='hazard'
    """

    return extract_layers(layers, 'category', 'hazard')


def get_hazard_layer(layers):
    """Get hazard layer from list of layers

    If there are more than one, only the first is returned.
    Use get_hazard_layers if more are expected and needed

    If no layers fit the description None is returned
    """

    L = get_hazard_layers(layers)
    if len(L) > 0:
        return L[0]
    else:
        return None


def get_exposure_layers(layers):
    """Get list of layers that have category=='exposure'
    """

    return extract_layers(layers, 'category', 'exposure')


def get_exposure_layer(layers):
    """Get exposure layer from list of layers

    If there are more than one, only the first is returned.
    Use get_hazard_layers if more are expected and needed

    If no layers fit the description None is returned
    """

    L = get_exposure_layers(layers)
    if len(L) > 0:
        return L[0]
    else:
        return None


def extract_layers(layers, keyword, value):
    """Extract layers with specified keyword/value pair
    """

    extracted_layers = []
    for layer in layers:
        if value in layer.get_keywords(keyword):
            extracted_layers.append(layer)

    return extracted_layers


def get_question(hazard_title, exposure_title, impact_function):
    """Rephrase the question asked.

    :param hazard_title: Hazard title.
    :type hazard_title: str

    :param exposure_title: Exposure title.
    :type exposure_title: str

    :param impact_function: An impact function object.
    :type impact_function: ImpactFunction
    """

    function_title = get_function_title(impact_function)
    return (tr('In the event of <i>%(hazard)s</i> how many '
               '<i>%(exposure)s</i> might <i>%(impact)s</i>')
            % {'hazard': hazard_title.lower(),
               'exposure': exposure_title.lower(),
               'impact': function_title.lower()})


def aggregate_point_data(data=None, boundaries=None,
                         attribute_name=None,
                         aggregation_function='count'):
    """Clip data to boundaries and aggregate their values for each.

    Input
        data: Point dataset
        boundaries: Polygon dataset
        attribute_name: Name of attribute to aggrate over.
        aggregation_function: Function to apply ('count' or 'sum')

    Output
        List of aggregated values for each polygon.

    Note
        Aggregated values depend on aggregation function:

        'sum': Sum of values for attribute_name

        'count': Dictionary with counts of occurences of each value
        of attribute_name

    """

    msg = ('Input argument "data" must be point type. I got type: %s'
           % data.get_geometry_type())
    if not data.is_point_data:
        raise Exception(msg)

    msg = ('Input argument "boundaries" must be polygon type. I got type: %s'
           % boundaries.get_geometry_type())
    if not boundaries.is_polygon_data:
        raise Exception(msg)

    polygon_geoms = boundaries.get_geometry()
    # polygon_attrs = boundaries.get_data()

    points = data.get_geometry()
    attributes = data.get_data()

    result = []
    # for i, polygon in enumerate(polygon_geoms):
    for polygon in polygon_geoms:
        indices = inside_polygon(points, polygon)

        # print 'Found %i points in polygon %i' % (len(indices), i)

        # Aggregate numbers
        if aggregation_function == 'count':
            bins = {}
            for att in numpy.take(attributes, indices):
                val = att[attribute_name]

                # Count occurences of val
                if val not in bins:
                    bins[val] = 0
                bins[val] += 1
            result.append(bins)
        elif aggregation_function == 'sum':
            sum_ = 0
            for att in numpy.take(attributes, indices):
                val = att[attribute_name]
                sum_ += val
            result.append(sum_)

    return result


def aggregate(data=None, boundaries=None,
              attribute_name=None,
              aggregation_function='count'):
    """Clip data to boundaries and aggregate their values for each.

    Input:
        data: Point or Raster dataset

        boundaries: Polygon dataset

        attribute_name: Name of attribute to aggrate over.
         This is only applicable for vector data

        aggregation_function: Function to apply ('count' or 'sum')

    Output:
        Dictionary of {boundary_name: aggregated value}
    """
    res = None
    if data.is_point_data:
        res = aggregate_point_data(data, boundaries,
                                   attribute_name, aggregation_function)
    elif data.is_raster_data:
        # Convert to point data
        # Call point aggregation function
        # aggregate_point_data(data, boundaries,
        #                     attribute_name, aggregation_function)
        pass
    else:
        msg = ('Input argument "data" must be point or raster data. '
               'I got type: %s' % data.get_geometry_type())
        raise Exception(msg)
    return res


def convert_to_old_keywords(converter, keywords):
    """Convert new keywords system to old keywords system by aliases.

    Since we have new keywords system in definitions.py and assigned by wizard,
    it will have backward incompatibility because the current impact function
    selector still use the old system.

     This method will convert new keywords to old keyword that has the same
     objective.

     :param converter: a dictionary that contains all possible aliases
        from new keywords to old keywords.
     :type converter: dict

     :param keywords: list of dictionary keyword
     :type keywords: list

     .. versionadded:: 2.1
    """
    for keyword in keywords:
        for key, value in keyword.iteritems():
            try:
                aliases = converter[key]
                for alias_key, alias_value in aliases.iteritems():
                    if value.lower() in alias_value:
                        keyword[key] = alias_key
                        break
            except KeyError:
                pass
