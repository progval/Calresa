import math
import datetime
import collections

import arrow
import flask_babel
from babel.dates import format_date

QuarterHour = collections.namedtuple('QuarterHour', 'roomstates')
RoomState = collections.namedtuple('RoomState', 'rowspan period class_ description')

def format_hour(a):
    locale = flask_babel.get_locale()
    date = datetime.time(hour=a.hour, minute=a.minute)
    return format_date(date, 'H:mm', locale=locale)

def build_table(dates, room_calendars):
    roomstates = [[] for _ in range(0, 24*4)]
    for date in dates:
        arrow_date = arrow.get(date.year, date.month, date.day)
        for room_calendar in room_calendars:
            events = room_calendar.events.on(arrow_date)
            events = sorted(events, key=lambda e: e.begin)
            for (event, next_event) in zip([None] + events, events + [None]):
                if event is not None:
                    begin_time = event.begin.hour + event.begin.minute/60.
                    end_time = event.end.hour + event.end.minute/60.
                    duration_time = event.duration.seconds/3600

                    begin_fmt = format_hour(event.begin)
                    end_fmt = format_hour(event.end)

                    roomstates[int(begin_time*4.)].append(RoomState(
                        rowspan=math.ceil(duration_time*4.),
                        class_="reserved",
                        period='{} - {}'.format(begin_fmt, end_fmt),
                        description=event.name or '(no description)',
                        ))
                else:
                    end_time = 0

                if next_event is None:
                    next_begin_time = 24.
                else:
                    next_begin_time = next_event.begin.hour + next_event.begin.minute/60.
                for i in range(int(end_time*4.), int(next_begin_time*4.)):
                    roomstates[i].append(RoomState(
                        rowspan=1,
                        class_="unused",
                        period=None,
                        description=None,
                        ))

    return roomstates
