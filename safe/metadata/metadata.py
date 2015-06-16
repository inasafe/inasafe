# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **metadata module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from safe.metadata.utils import TYPE_CONVERSIONS

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# using this approach:
# http://eli.thegreenplace.net/2009/02/06/getters-and-setters-in-python

from datetime import datetime

from safe.metadata.provenance import Provenance


class Metadata(object):

    def __init__(self, layer):
        # private members
        self._layer = layer
        self._last_update = datetime.now()
        self._provenance = Provenance()
        self._xml_properties = {}

    @property
    # there is no setter because the layer should not change overtime
    def layer(self):
        return self._layer

    @property
    def last_update(self):
        return self._last_update

    @last_update.setter
    def last_update(self, time):
        self._last_update = time

    def set_last_update_to_now(self):
        self._last_update = datetime.now()

    @property
    # there is no setter. provenance can only grow. use append_provenance_step
    def provenance(self):
        return self._provenance

    def get_properties(self):
        return self._xml_properties

    def get(self, xml_property_name):
        return self._xml_properties[xml_property_name].xml_value

    def get_property(self, xml_property_name):
        return self._xml_properties[xml_property_name]

    def update(self, name, value):
        self.get_property(name).value = value

    def set(self, name, value, xml_path, xml_type):
        # check if the desired type is supported
        try:
            property_class = TYPE_CONVERSIONS[xml_type]
        except KeyError:
            raise KeyError('The xml type %s is not supported yet' % xml_type)

        metadata_property = property_class(name, value, xml_path, xml_type)
        self._xml_properties[name] = metadata_property
        self.set_last_update_to_now()

    def append_provenance_step(self, name, description):
        step_time = self._provenance.append_step(name, description)
        self.last_update = step_time

    def save(self, destination_path):
        # TODO (MB): implement this
        print destination_path
        print self
        raise NotImplementedError('Still need to write this')
