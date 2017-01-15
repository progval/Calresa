import arrow
import datetime
import collections

_State = collections.namedtuple('_State', 'dates viewed_month rooms')

def parse_date(s):
    (year, month, day) = s.split('-')
    return datetime.date(year=int(year), month=int(month), day=int(day))

def format_date(date):
    return '{0.year}-{0.month}-{0.day}'.format(date)

def parse_month(s):
    (year, month) = s.split('-')
    return arrow.get(int(year), int(month), 1)

def format_month(date):
    return '{0.year}-{0.month}'.format(date)

class State(_State):
    @classmethod
    def from_request_args(Cls, args):
        today = datetime.date.today()
        if 'viewed_month' in args:
            viewed_month = parse_month(args['viewed_month'])
        else:
            viewed_month = arrow.get(year=today.year, month=today.year, day=1)
        if 'dates' in args:
            dates = tuple(sorted(map(parse_date, args['dates'].split())))
        else:
            dates = (today,)
        rooms = tuple(map(int, filter(bool, args.get('rooms', '').split())))
        return Cls(viewed_month=viewed_month, dates=dates, rooms=rooms)

    def to_request_args(self):
        return dict(
                viewed_month=format_month(self.viewed_month),
                dates=' '.join(map(format_date, self.dates)),
                rooms=' '.join(map(str, self.rooms)),
                )

    def show_prev_month(self):
        viewed_month = self.viewed_month.replace(months=-1)
        dates = self.dates
        rooms = self.rooms
        return self.__class__(viewed_month=viewed_month, dates=dates, rooms=rooms)

    def show_next_month(self):
        viewed_month = self.viewed_month.replace(months=+1)
        dates = self.dates
        rooms = self.rooms
        return self.__class__(viewed_month=viewed_month, dates=dates, rooms=rooms)

    def unselect_date(self, date):
        viewed_month = self.viewed_month
        dates = tuple(d for d in self.dates if d != date)
        rooms = self.rooms
        return self.__class__(viewed_month=viewed_month, dates=dates, rooms=rooms)

    def select_date(self, date):
        viewed_month = self.viewed_month
        if date in self.dates:
            dates = self.dates
        else:
            dates = self.dates + (date,)
        rooms = self.rooms
        return self.__class__(viewed_month=viewed_month, dates=dates, rooms=rooms)

    def update_room_selection(self, rooms):
        viewed_month = self.viewed_month
        dates = self.dates
        rooms = tuple(rooms)
        return self.__class__(viewed_month=viewed_month, dates=dates, rooms=rooms)
