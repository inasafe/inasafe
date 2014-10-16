"""Function to manage self-registering plugins

The design is based on http://effbot.org/zone/metaclass-plugins.htm

To register the plugin, the module must be imported by the Python process
using it.
"""


import logging
from math import ceil

import numpy
from safe.common.utilities import OrderedDict

import keyword as python_keywords
from safe.common.polygon import inside_polygon
from safe.common.utilities import ugettext as tr
from safe.common.tables import Table, TableCell, TableRow
from utilities import pretty_string, remove_double_spaces
from safe.metadata import converter_dict


LOGGER = logging.getLogger('InaSAFE')


# Disable lots of pylint for this as it is using magic
# for managing the plugin system devised by Ted Dunstone
# pylint: disable=W0613,C0203
class PluginMount(type):
    """Mount point for a plugin (impact function)."""
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            if cls.__name__ in [c.__name__ for c in cls.plugins]:
                raise LookupError(
                    "Duplicate impact function name %s" % cls.__name__)
            cls.plugins.append(cls)
# pylint: enable=W0613,C0203


class FunctionProvider(object):
    """Mount point for impact_functions.

    Plugins implementing this reference should provide the following method:

    run(layers)::

      layers           A list of layers
      result           A list of layers

    """
    __metaclass__ = PluginMount

    target_field = 'DAMAGE'
    symbol_field = 'USE_MAJOR'


def default_minimum_needs():
    """Helper to get the default minimum needs.

    .. note:: Key names will be translated.
    """
    rice = 'Rice'
    drinking_water = 'Drinking Water'
    water = 'Water'
    family_kits = 'Family Kits'
    toilets = 'Toilets'
    minimum_needs = OrderedDict([
        (rice, 2.8),
        (drinking_water, 17.5),
        (water, 67),
        (family_kits, 0.2),
        (toilets, 0.05)])
    return minimum_needs


def evacuated_population_weekly_needs(
        population,
        minimum_needs=False,
        human_names=False):
    """Calculate estimated needs using BNPB Perka 7/2008 minimum bantuan.

    :param population: The number of evacuated population.
    :type: int, float

    :param human_names: A flag whether to use human names for minimum needs
        items or not
    :type human_names: bool

    :param minimum_needs: Ratios to use when calculating minimum needs.
        Defaults to perka 7 as described in assumptions below.
    :type minimum_needs: dict

    :returns: The weekly needs for the evacuated population.
    :rtype: dict

    Assumptions:
    * 400g rice per person per day
    * 2.5L drinking water per person per day
    * 15L clean water per person per day
    * assume 5 people per family (not in perka - 0.2 people per family)
    * 20 people per toilet (0.05 per person)
    """
    rice = 'Rice'
    drinking_water = 'Drinking Water'
    water = 'Water'
    family_kits = 'Family Kits'
    toilets = 'Toilets'
    if not minimum_needs:
        minimum_needs = default_minimum_needs()

    min_rice = minimum_needs[rice]
    min_drinking_water = minimum_needs[drinking_water]
    min_water = minimum_needs[water]
    min_family_kits = minimum_needs[family_kits]
    min_toilets = minimum_needs[toilets]

    val_rice = int(ceil(population * min_rice))
    val_drinking_water = int(ceil(population * min_drinking_water))
    val_water = int(ceil(population * min_water))
    val_family_kits = int(ceil(population * min_family_kits))
    val_toilets = int(ceil(population * min_toilets))

    if human_names:
        weekly_needs = {
            rice: val_rice,
            drinking_water: val_drinking_water,
            water: val_water,
            family_kits: val_family_kits,
            toilets: val_toilets}
    else:
        weekly_needs = {
            'rice': val_rice,
            'drinking_water': val_drinking_water,
            'water': val_water,
            'family_kits': val_family_kits,
            'toilets': val_toilets}

    return weekly_needs


def get_function_title(func):
    """Get title for impact function

    :param func: Impact function class

    :returns:  It's title if available as an attribute in the class
        description, otherwise what is returned by the function
        pretty_function_name.
    :rtype: str
    """
    if hasattr(func, 'title'):
        title = func.title
    else:
        title = pretty_function_name(func)

    return tr(title)


def get_plugins(name=None):
    """Retrieve a list of plugins that match the name you pass.

       Or all of them if no name is passed.
    """

    plugins_dict = dict([(pretty_function_name(p), p)
                         for p in FunctionProvider.plugins])

    if name is None:
        return plugins_dict

    if isinstance(name, basestring):
        # Add the names
        plugins_dict.update(
            dict([(p.__name__, p) for p in FunctionProvider.plugins]))

        msg = ('No plugin named "%s" was found. '
               'List of available plugins is: \n%s'
               % (name, ',\n '.join(plugins_dict.keys())))
        if name not in plugins_dict:
            raise RuntimeError(msg)

        return [{name: plugins_dict[name]}]
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


# FIXME (Ole): Deprecate this function (see issue #392)
def pretty_function_name(func):
    """Return a human readable name for the function
    if the function has a func.plugin_name use this
    otherwise turn underscores to spaces and Caps to spaces """

    if not hasattr(func, 'plugin_name'):
        nounderscore_name = func.__name__.replace('_', ' ')
        func_name = ''
        for i, c in enumerate(nounderscore_name):
            if c.isupper() and i > 0:
                func_name += ' ' + c
            else:
                func_name += c
    else:
        func_name = func.plugin_name
    return func_name


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
            #print msg
            #logger.error(msg)
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
    except Exception, e:
        msg = ('Requirements header could not compiled: %s. '
               'Original message: %s' % (execstr, e))
        #print msg
        #logger.error(msg)

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


#-------------------------------
# Helpers for individual plugins
#-------------------------------
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


def get_question(hazard_title, exposure_title, func):
    """Rephrase the question asked

    Input
        hazard_title: string
        exposure_title: string
        func: impact function class
    """

    function_title = get_function_title(func)
    return (tr('In the event of <i>%(hazard)s</i> how many '
               '<i>%(exposure)s</i> might <i>%(impact)s</i>')
            % {'hazard': hazard_title.lower(),
               'exposure': exposure_title.lower(),
               'impact': function_title.lower()})


def get_thresholds(layer):
    """Extract thresholds form layer keywords if present
    """

    if 'thresholds' in layer.keywords:
        t_list = layer.keywords['thresholds']
        thresholds = [float(x) for x in t_list]
        thresholds.sort()
    else:
        thresholds = []

    return thresholds


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
    #polygon_attrs = boundaries.get_data()

    points = data.get_geometry()
    attributes = data.get_data()

    result = []
    #for i, polygon in enumerate(polygon_geoms):
    for polygon in polygon_geoms:
        indices = inside_polygon(points, polygon)

        #print 'Found %i points in polygon %i' % (len(indices), i)

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
        #aggregate_point_data(data, boundaries,
        #                     attribute_name, aggregation_function)
        pass
    else:
        msg = ('Input argument "data" must be point or raster data. '
               'I got type: %s' % data.get_geometry_type())
        raise Exception(msg)
    return res


# FIXME (Ole): Maybe filter by name too, rename to get_impact_functions
# and remove some of the other functions.
def get_admissible_plugins(keywords=None):  # , name=None):
    """Get plugins that match specified keywords

    Input:
        keywords: Either dictionary or list of dictionaries containing
                  layer keywords of the form
                  {'category': 'hazard', 'subcategory': 'flood', ...}

                  If None or empty all plugins are returned

        name: Optional impact function name (or part of function name)
         used to further filter the result.

        If None all names are considered to match

    Output:
        Dictionary of impact functions ({name: class})
    """

    # This is very verbose, but sometimes useful
    # LOGGER.debug(keywords_to_str(keywords))

    # Input checks
    if keywords is None:
        keywords = []

    if isinstance(keywords, dict):
        keywords = [keywords]

    convert_to_old_keywords(converter_dict, keywords)

    # Get all impact functions
    plugin_dict = get_plugins()

    # Build dictionary of those that match given keywords
    admissible_plugins = {}
    for f_name, func in plugin_dict.items():

        # Required keywords for func
        requirelines = requirements_collect(func)

        # Keep impact function if requirements are met for all given keywords
        match = True
        for kw_dict in keywords:
            if not requirements_met(requirelines, kw_dict):
                match = False
        if match:
            admissible_plugins[f_name] = func

    # This is very verbose, but sometimes useful
    # LOGGER.debug(admissible_plugins_to_str(admissible_plugins))

    # Return (possibly empty) dictionary
    return admissible_plugins


def parse_single_requirement(requirement):
    '''Parse single requirement from impact function's doc to category,
        subcategory, layertype, datatype, unit, and disabled.'''
    retval = {}
    parts = requirement.split(' and ')
    for part in parts:
        if part.find('==') != -1:
            myKey = part.split('==')[0]
            myValue = part.split('==')[1]
            retval[myKey] = myValue[1:-1]  # Removing single quote
        elif part.find(' in ') != -1:
            myKey = part.split(' in ')[0]
            myListString = part.split(' in ')[1][1:-1]  # Removing '['
            elmtList = myListString.split(', ')
            myList = []
            for elmt in elmtList:
                myList.append(elmt[1:-1])  # Removing single quote
            retval[myKey] = myList
        elif part.find('.startswith') != -1:
            pass  # Not yet implemented
        else:
            pass

    return retval


def get_plugins_as_table(dict_filter=None):
    """Retrieve a table listing all plugins and their requirements.

       Or just a single plugin if name is passed.

       Args:
           * dict_filter = dictionary that contains filters
               - id = list_id
               - title = list_title
               - category : list_category
               - subcategory : list_subcategory
               - layertype : list_layertype
               - datatype : list_datatype
               - unit: list_unit
               - disabled : list_disabled # not included

       Returns:
           * table contains plugins match with dict_filter

       Raises: None
    """

    if dict_filter is None:
        dict_filter = {'id': [],
                       'title': [],
                       'category': [],
                       'subcategory': [],
                       'layertype': [],
                       'datatype': [],
                       'unit': []}

    table_body = []
    # use this list for avoiding wrong order in dict
    atts = ['category', 'subcategory', 'layertype',
            'datatype', 'unit']
    header = TableRow([tr('Title'), tr('ID'), tr('Category'),
                       tr('Sub Category'), tr('Layer type'), tr('Data type'),
                       tr('Unit')],
                      header=True)
    table_body.append(header)

    plugins_dict = dict([(pretty_function_name(p), p)
                         for p in FunctionProvider.plugins])

    not_found_value = 'N/A'
    for key, func in plugins_dict.iteritems():
        for requirement in requirements_collect(func):
            dict_found = {'title': False,
                          'id': False,
                          'category': False,
                          'subcategory': False,
                          'layertype': False,
                          'datatype': False,
                          'unit': False}

            dict_req = parse_single_requirement(str(requirement))

            # If the impact function is disabled, do not show it
            if dict_req.get('disabled', False):
                continue

            for myKey in dict_found.iterkeys():
                myFilter = dict_filter.get(myKey, [])
                if myKey == 'title':
                    myValue = str(get_function_title(func))
                elif myKey == 'id':
                    myValue = str(key)
                else:
                    myValue = dict_req.get(myKey, not_found_value)

                if myFilter != []:
                    for myKeyword in myFilter:
                        if type(myValue) == type(str()):
                            if myValue == myKeyword:
                                dict_found[myKey] = True
                                break
                        elif type(myValue) == type(list()):
                            if myKeyword in myValue:
                                dict_found[myKey] = True
                                break
                        else:
                            if myValue.find(str(myKeyword)) != -1:
                                dict_found[myKey] = True
                                break
                else:
                    dict_found[myKey] = True

            add_row = True
            for found_value in dict_found.itervalues():
                if not found_value:
                    add_row = False
                    break

            if add_row:
                row = []
                row.append(TableCell(get_function_title(func), header=True))
                row.append(key)
                for myKey in atts:
                    myValue = pretty_string(dict_req.get(myKey,
                                                         not_found_value))
                    row.append(myValue)
                table_body.append(TableRow(row))

    cw = 100 / 7
    table_col_width = [str(cw) + '%', str(cw) + '%', str(cw) + '%',
                       str(cw) + '%', str(cw) + '%', str(cw) + '%',
                       str(cw) + '%']
    table = Table(table_body, col_width=table_col_width)
    table.caption = tr('Available Impact Functions')

    return table


def get_unique_values():
    """Get unique possible value for each column in impact functions doc
        table.

        Args: None

        Returns:
            * Dictionary contains list unique value for each column
        """
    atts = ['category', 'subcategory', 'layertype', 'datatype', 'unit']
    dict_retval = {'category': set(),
                   'subcategory': set(),
                   'layertype': set(),
                   'datatype': set(),
                   'unit': set(),
                   'id': set(),
                   'title': set()}

    plugins_dict = dict([(pretty_function_name(p), p)
                         for p in FunctionProvider.plugins])
    for key, func in plugins_dict.iteritems():
        if not is_function_enabled(func):
            continue
        dict_retval['title'].add(get_function_title(func))
        dict_retval['id'].add(key)
        for requirement in requirements_collect(func):
            dict_req = parse_single_requirement(str(requirement))
            for key in dict_req.iterkeys():
                if key not in atts:
                    break
                if type(dict_req[key]) == type(str()):
                    dict_retval[key].add(dict_req[key])
                elif type(dict_req[key]) == type(list()):
                    dict_retval[key] |= set(dict_req[key])

    # convert to list
    for key in dict_retval.iterkeys():
        dict_retval[key] = list(dict_retval[key])
    return dict_retval


def get_metadata(func):
    """Collect metadata for an impact function and return it as a dictionary.

    :param func: Name of function.

    :returns: A dictionary containing:
        * author : string (identified by :author)
        * synopsis : string (first line)
        * rating : integer (identified by :rating)
        * param_req : list of param (identified by :param requires)
        * detail : detail description (function properties)
        * citation : list of citation in string (function properties)
        * limitation : string (function properties)
    :rtype: dict
    """
    retval = OrderedDict()
    retval['unique_identifier'] = func

    plugins_dict = dict([(pretty_function_name(p), p)
                         for p in FunctionProvider.plugins])
    if func not in plugins_dict.keys():
        return None
    else:
        func = plugins_dict[func]

    author_tag = ':author'
    rating_tag = ':rating'

    # attributes
    synopsis = 'synopsis'
    actions = 'actions'
    # citations must be a list
    citations = 'citations'
    detailed_description = 'detailed_description'
    hazard_input = 'hazard_input'
    exposure_input = 'exposure_input'
    limitation = 'limitation'
    output = 'output'

    if hasattr(func, '__doc__') and func.__doc__:
        doc_str = func.__doc__
        for line in doc_str.split('\n'):
            doc_line = remove_double_spaces(line)
            doc_line = doc_line.strip()

            if doc_line.startswith(author_tag):
                retval['author'] = remove_double_spaces(
                    doc_line[len(author_tag) + 1:])
            elif doc_line.startswith(rating_tag):
                retval['rating'] = doc_line[len(rating_tag) + 1:]
    retval['title'] = get_function_title(func)

    if hasattr(func, synopsis):
        retval[synopsis] = func.synopsis
    if hasattr(func, actions):
        retval[actions] = func.actions
    if hasattr(func, citations):
        retval[citations] = func.citations
    if hasattr(func, detailed_description):
        retval[detailed_description] = func.detailed_description
    if hasattr(func, hazard_input):
        retval[hazard_input] = func.hazard_input
    if hasattr(func, exposure_input):
        retval[exposure_input] = func.exposure_input
    if hasattr(func, output):
        retval[output] = func.output
    if hasattr(func, limitation):
        retval[limitation] = func.limitation
    return retval


def get_doc_string(func):
    """Return doc string of an impact function
    """
    return func.__doc__


def is_function_enabled(func):
    """Check whether a function is enabled or not
    :param func:
    :return: False is disabled param is True
    """
    for requirement in requirements_collect(func):
        dict_req = parse_single_requirement(str(requirement))

        # If the impact function is disabled, do not show it
        if dict_req.get('disabled', False):
            return False
    return True


def convert_to_old_keywords(converter, keywords):
    """Convert new keywords system to old keywords system by aliases.

    Since we have new keywords system in metadata.py and assigned by wizard,
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
