# coding=utf-8

"""Mock like implementation for the QgsLegendInterface - used for testing."""
from builtins import object

from qgis.core import QgsMapLayerRegistry


class QgisLegend(object):

    """A fake QgsLegendInterface with minimal implementation."""

    def __init__(self, canvas):
        """Constructor.

        :param canvas: A QgsMapCanvas instance - we will assume that all
            canvas layers are in the legend and are visible.
        :type canvas: QgsMapCanvas
        """
        self.canvas = canvas

    def layers(self):
        """Fake implementation for QgisLegendInterface.layers.

        :returns: A list of QgsMapLayers - one per layer present in the
            map layer list will be returned.
        :rtype: list
        """
        layers = list(QgsProject.instance().mapLayers().values())
        return layers

    # noinspection PyPep8Naming
    def isLayerVisible(self, layer):
        """Fake implementation for QgisLegendInterface.isLayerVisible.

        Since this is a fake interface
        pretending to be a real running QGIS app and we do not have
        a legend, we work on the premise that if a layer is in the
        canvas, it is also in the (fake) legend.

        :param layer: A QgsMapLayer that we want to determine if
            it is visible or not.
        :type layer: QgsMapLayer

        :returns: Hard coded to always return true if the layer is in
            the canvas!
        :rtype: bool
        """
        layers = self.canvas.layers()
        if layer in layers:
            return True
        else:
            return False

    # noinspection PyPep8Naming
    def setLayerVisible(self, layer, visibility):
        """Fake implementation for QgisLegendInterface.setLayerVisible.

        Since this is a fake interface pretending to be a real running QGIS
        app and we do not have a legend, we work on the premise that the layer
        is in the fake legend and we toggle the visibility.

        :param layer: A QgsMapLayer that we want to set visible.
        :type layer: QgsMapLayer

        :param visibility: A boolean to set the layer visible or not.
        :type visibility: bool
        """
        pass
