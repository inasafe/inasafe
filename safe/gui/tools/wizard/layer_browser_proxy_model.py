# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**Wizard Utilities.**

This module provides a filter proxy model for Wizard's layer browser.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from qgis.PyQt.QtCore import QSortFilterProxyModel


class LayerBrowserProxyModel(QSortFilterProxyModel):

    """Proxy model for hiding unsupported branches in the layer browser."""

    def __init__(self, parent):
        """Constructor for the model.

        :param parent: Parent widget of this model.
        :type parent: QWidget
        """
        QSortFilterProxyModel.__init__(self, parent)

    def filterAcceptsRow(self, source_row, source_parent):
        """The filter method

        .. note:: This filter hides top-level items of unsupported branches
                  and also leaf items containing xml files.

           Enabled root items: QgsDirectoryItem, QgsFavouritesItem,
           QgsPGRootItem.

           Disabled root items: QgsMssqlRootItem, QgsSLRootItem,
           QgsOWSRootItem, QgsWCSRootItem, QgsWFSRootItem, QgsWMSRootItem.

           Disabled leaf items: QgsLayerItem and QgsOgrLayerItem with path
           ending with '.xml'

        :param source_row: Parent widget of the model
        :type source_row: int

        :param source_parent: Parent item index
        :type source_parent: QModelIndex

        :returns: Item validation result
        :rtype: bool
        """
        source_index = self.sourceModel().index(source_row, 0, source_parent)
        item = self.sourceModel().dataItem(source_index)

        if item.metaObject().className() not in [
                'QgsPGRootItem',
                'QgsPGConnectionItem',
                'QgsPGSchemaItem',
                'QgsPGLayerItem',
                'QgsFavoritesItem',
                'QgsDirectoryItem',
                'QgsLayerItem',
                'QgsGdalLayerItem',
                'QgsOgrLayerItem']:
            return False

        if item.path().endswith('.xml'):
            return False

        return True
