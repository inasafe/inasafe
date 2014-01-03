# coding=utf-8
"""Simple helper for when you already have the grid.xml and just want a map."""
#Tim Sutton, April 2013.

from shake_event import ShakeEvent
# myId = '20120118231542_se'
# myShakeEvent = ShakeGridConverter(
#     theEventId=myId,
#     theLocale='en',
#     theForceFlag=False,
#     theDataIsLocalFlag=True)
# myShakeEvent.render_map(theForceFlag=False)
#
# myId = '20120118231552_se'
# myShakeEvent = ShakeGridConverter(
#     theEventId=myId,
#     theLocale='en',
#     theForceFlag=False,
#     theDataIsLocalFlag=True)
# myShakeEvent.render_map(theForceFlag=False)
#
#
# myId = '20120118231562_se'
# myShakeEvent = ShakeGridConverter(
#     theEventId=myId,
#     theLocale='en',
#     theForceFlag=False,
#     theDataIsLocalFlag=True)
# myShakeEvent.render_map(theForceFlag=False)

myId = '20130224200633'
myShakeEvent = ShakeEvent(
    event_id=myId,
    locale='en',
    force_flag=False,
    data_is_local_flag=True)
myShakeEvent.render_map(force_flag=False)
