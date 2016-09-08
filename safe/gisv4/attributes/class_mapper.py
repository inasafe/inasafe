# This module contains code for mapping class_id's to their nammes
# and writing the names to the attribute table as a new column.

def write_class_names(hazard_layer, custom_classification=None):
    """
    This will modify a layer in place, adding a new field 'class_name'.

    The class_name field will be populated by looking up the class_id in the
    threshold profile and then assigning it to a new column in the attribute
    table.

    :param hazard_layer: The hazard layer that has class_id's but no
        class_names defined.
    :type hazard_layer: QgsVectorLayer

    :param custom_classification: An ordered dictionary where the keys are
        class_id's and the values are a list of [min, max, class_name]
        properties. If not threshold profile is given, the default
        classifcation for the hazard definition (see definitions) will be used.
    :type custom_classification: OrderedDict

    :rtype: bool
    :return: False if the operation failed, otherwise True
    """
    return False
