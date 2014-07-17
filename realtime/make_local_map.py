# coding=utf-8
"""Simple helper for when you already have the grid.xml and just want a map."""
#Tim Sutton, April 2013.

from shake_event import ShakeEvent

if __name__ == '__main__':
    SHAKE_ID = '20131105060809'
    # To ensure that realtime is working for not just en locale, use other
    # locale here to test realtime
    locales = ['en', 'id']
    for locale in locales:
        shake_event = ShakeEvent(
            event_id=SHAKE_ID,
            locale=locale,
            force_flag=False,
            data_is_local_flag=True)
        shake_event.render_map(force_flag=False)
