from PyQt4.QtGui import QSortFilterProxyModel


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

        if item.metaObject().className() in [
                'QgsMssqlRootItem',
                'QgsSLRootItem',
                'QgsOWSRootItem',
                'QgsWCSRootItem',
                'QgsWFSRootItem',
                'QgsWMSRootItem']:
            return False

        if (item.metaObject().className() in [
                'QgsLayerItem',
                'QgsOgrLayerItem'] and
                item.path().endswith('.xml')):
            return False

        return True
