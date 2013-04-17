# Simple helper for when you already have the grid.xml and you just want a
# map.
#
# Tim Sutton, April 2013

from shake_event import ShakeEvent
# myId = '20120118231542_se'
# myShakeEvent = ShakeEvent(
#     theEventId=myId,
#     theLocale='en',
#     theForceFlag=False,
#     theDataIsLocalFlag=True)
# myShakeEvent.renderMap(theForceFlag=False)
#
# myId = '20120118231552_se'
# myShakeEvent = ShakeEvent(
#     theEventId=myId,
#     theLocale='en',
#     theForceFlag=False,
#     theDataIsLocalFlag=True)
# myShakeEvent.renderMap(theForceFlag=False)
#
#
# myId = '20120118231562_se'
# myShakeEvent = ShakeEvent(
#     theEventId=myId,
#     theLocale='en',
#     theForceFlag=False,
#     theDataIsLocalFlag=True)
# myShakeEvent.renderMap(theForceFlag=False)

myId = '20130224200633'
myShakeEvent = ShakeEvent(
    theEventId=myId,
    theLocale='en',
    theForceFlag=False,
    theDataIsLocalFlag=True)
myShakeEvent.renderMap(theForceFlag=False)
