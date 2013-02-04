__author__ = 'bungcip'


from third_party.lightmaps import LightMaps, SlippyMap, tdim

ZOOM_LEVEL_DEGREE = [
    360,
    180,
    90,
    45,
    22.5,
    11.25,
    5.625,
    2.813,
    1.406,
    0.703,
    0.352,
    0.176,
    0.088,
    0.044,
    0.022,
    0.011,
    0.005,
    0.003,
    0.001
]

class InasafeSlippyMap(SlippyMap):
    def invalidate(self, emitSignal=True):
        SlippyMap.invalidate(self, emitSignal)
        self.calculateExtent()

    def calculateExtent(self):
        degree = ZOOM_LEVEL_DEGREE[self.zoom]
        tileCountX = float(self.width) / tdim
        widthInDegree = tileCountX * degree
        tileCountY  = float(self.height) / tdim
        heightInDegree = tileCountY * degree
        offsetX = widthInDegree / 2
        offsetY = heightInDegree / 2

        minX = self.latitude - offsetY
        minY = self.longitude - offsetX

        maxX = self.latitude + offsetY
        maxY = self.longitude + offsetX

        def flipNumber(n, limit):
            if n > limit:
                return -limit + (n - limit)
            elif n < -limit:
                return limit  - (n + limit)
            else:
                return n

        self.tlLat = flipNumber(minX, 90)
        self.brLat = flipNumber(maxX, 90)
        self.tlLng = flipNumber(minY, 180)
        self.brLng = flipNumber(maxY, 180)


class InasafeLightMaps(LightMaps):
    def __init__(self, parent):
        LightMaps.__init__(self, parent, InasafeSlippyMap)

    def getExtent(self):
        return (self.m_normalMap.tlLat, self.m_normalMap.tlLng, self.m_normalMap.brLat, self.m_normalMap.brLng)

