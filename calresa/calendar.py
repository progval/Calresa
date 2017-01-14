import datetime
import calendar
import dateutil
import collections
import dateutil.relativedelta

import flask_babel
from babel.dates import format_date

def get_month_name(year, month):
    locale = flask_babel.get_locale()
    date = datetime.date(year=year, month=month, day=1)
    return format_date(date, 'MMMM', locale=locale)

CalendarMonth = collections.namedtuple('CalendarMonth', 'name number year_number weeks')
CalendarWeek = collections.namedtuple('CalendarWeek', 'number days')
CalendarDay = collections.namedtuple('CalendarDay', 'number is_current is_selected')

NO_DAY = CalendarDay(number=None, is_current=False, is_selected=False)

def is_current_day(year, month, day):
    try:
        date = datetime.date(year, month, day)
    except ValueError: # day is out of range for month
        return False
    else:
        return date == datetime.date.today()

def is_selected_day(year, month, day, selected_dates):
    try:
        date = datetime.date(year, month, day)
    except ValueError: # day is out of range for month
        return False
    else:
        return date in selected_dates

def get_calendar_month(year, month, selected_dates):
    (first_weekday, number_of_days) = calendar.monthrange(year, month)
    weeks = []
    days = [NO_DAY]*(first_weekday-1)
    for day in range(number_of_days+1):
        days.append(CalendarDay(number=day,
            is_current=is_current_day(year, month, day),
            is_selected=is_selected_day(year, month, day, selected_dates),
            ))
        if len(days) == 7:
            week_number = datetime.date(year, month, day).isocalendar()[1]
            weeks.append(CalendarWeek(number=week_number, days=days))
            days = []
    if days:
        days += [NO_DAY]*(7-len(days))
        weeks.append(CalendarWeek(number=week_number+1, days=days))
    while len(weeks) < 6:
        weeks.append(CalendarWeek(number=None, days=[NO_DAY]*7))
    return CalendarMonth(name=get_month_name(year, month), number=month, year_number=year, weeks=weeks)

def get_calendar_months(selected_dates, viewed_month):
    today = datetime.datetime.today()
    this_month = viewed_month
    last_month = this_month + dateutil.relativedelta.relativedelta(months=-1)
    next_month = this_month + dateutil.relativedelta.relativedelta(months=+1)
    months = [
            get_calendar_month(last_month.year, last_month.month, selected_dates),
            get_calendar_month(this_month.year, this_month.month, selected_dates),
            get_calendar_month(next_month.year, next_month.month, selected_dates),
            ]
    return months
