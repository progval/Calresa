import os
import json
import urllib
import datetime
import collections

import flask
from flask import request
from babel import negotiate_locale
import flask_babel
import ics

from .calendar import get_calendar_months
from .state import State
from .roomstate import build_table

AVAILABLE_LOCALES = ['fr', 'en']

app = flask.Flask(__name__)
app.config['CAS_AFTER_LOGIN'] = 'booking_view'
app.config.from_envvar('CALRESA_SETTINGS')
babel = flask_babel.Babel(app)

if app.config['CAS_SERVER']:
    from flask_cas import CAS, login_required
    cas = CAS(app)
else:
    cas = None
    login_required = lambda f: f

def render_template(*args, **kwargs):
    kwargs['url_for_view_prev_month'] = url_for_view_prev_month
    kwargs['url_for_view_next_month'] = url_for_view_next_month
    kwargs['url_for_unselect_date'] = url_for_unselect_date
    kwargs['url_for_select_date'] = url_for_select_date
    kwargs['url_for_room_selection'] = url_for_room_selection
    kwargs['url_for_change_rooms'] = url_for_change_rooms
    resp = flask.make_response(flask.render_template(*args, **kwargs))
    resp.headers['Content-type'] = 'application/xhtml+xml; charset=utf-8'
    return resp

def url_for_view_prev_month():
    state = State.from_request_args(request.args)
    state = state.show_prev_month()
    return flask.url_for('booking_view', **state.to_request_args())

def url_for_view_next_month():
    state = State.from_request_args(request.args)
    state = state.show_next_month()
    return flask.url_for('booking_view', **state.to_request_args())

def url_for_unselect_date(year, month, day):
    state = State.from_request_args(request.args)
    state = state.unselect_date(datetime.date(year, month, day))
    return flask.url_for('booking_view', **state.to_request_args())

def url_for_select_date(year, month, day):
    state = State.from_request_args(request.args)
    state = state.select_date(datetime.date(year, month, day))
    return flask.url_for('booking_view', **state.to_request_args())

def url_for_room_selection():
    state = State.from_request_args(request.args)
    return flask.url_for('room_selection', **state.to_request_args())

def url_for_change_rooms():
    state = State.from_request_args(request.args)
    return flask.url_for('change_rooms', **state.to_request_args())

@babel.localeselector
def get_locale():
    preferred = [x.replace('-', '_') for x in request.accept_languages.values()]
    return negotiate_locale(preferred, AVAILABLE_LOCALES)

_calendar_cache = {} # id -> (last_update, calendar)
def load_calendar(id_):
    global _calendar_cache
    path = os.path.join(app.config['ICS_DIR'], '{}.ics'.format(id_))
    last_update = os.stat(path).st_mtime
    if id_ not in _calendar_cache or _calendar_cache[id_][0] < last_update:
        with open(path, encoding='utf8') as fd:
            calendar = ics.Calendar(fd.read())
        _calendar_cache[id_] = (last_update, calendar)
        return calendar
    else:
        return _calendar_cache[id_][1]


@app.route('/')
@login_required
def booking_view():
    with open(app.config['NAMES_JSON']) as fd:
        room_names = json.load(fd)

    state = State.from_request_args(request.args)
    room_calendars = []
    for room in state.rooms:
        room_calendars.append(load_calendar(room))
    return render_template('booking_view.xhtml',
            rooms=[(n, room_names[str(n)]) for n in state.rooms],
            months=get_calendar_months(state.dates, state.viewed_month),
            selected_dates=state.dates,
            quarterhours=build_table(state.dates, room_calendars),
            )

@app.route('/select-rooms/')
@login_required
def room_selection():
    with open(app.config['NAMES_JSON']) as fd:
        room_names = json.load(fd)

    state = State.from_request_args(request.args)
    return render_template('room_selection.xhtml',
            selected_rooms=state.rooms,
            all_rooms=[(int(i), n) for (i,n) in room_names.items()],
            serialized_state=urllib.parse.urlencode(state.to_request_args()),
            )

@app.route('/select-rooms/form-target', methods={'POST'})
@login_required
def change_rooms():
    state = State.from_request_args(request.args)
    if 'update' in request.form:
        rooms = map(int, request.form.getlist('room'))
        state = state.update_room_selection(rooms)
    url = flask.url_for('booking_view', **state.to_request_args())
    return flask.redirect(url)
