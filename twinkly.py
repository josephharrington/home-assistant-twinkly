import os
import sys
import json
import urllib.request
import codecs
from pprint import pformat

ARG_ON = 'on'
ARG_OFF = 'off'
ARG_STATE = 'state'

ARG_IP = sys.argv[1]
ARG_ACTION = sys.argv[2]

URL = "http://" + ARG_IP + "/xled/v1/"

LOGIN_URL = URL + "login"
VERIFY_URL = URL + "verify"
MODE_URL = URL + "led/mode"

AUTH_HEADER = 'X-Auth-Token'

AUTHENTICATION_TOKEN = 'authentication_token'
CHALLENGE_RESPONSE = 'challenge-response'
MODE = 'mode'
MODE_ON = 'color'
MODE_OFF = 'off'

HEADERS = {'Content-Type': 'application/json'}
LOGIN_DATA = {'challenge': 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8='}

STATES_FILE = '/tmp/twinklystates.json'


def load_saved_states():
    try:
        with open(STATES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_states(states):
    with open(STATES_FILE, 'w') as f:
        json.dump(states, f)


def debug(msg):
    if os.environ['TWINKLY_DEBUG']:
        if isinstance(msg, dict):
            msg = pformat(msg)
        print(msg, file=sys.stderr)


def _format_data(data):
    return json.dumps(data).encode('utf8')


def _req(url, data=None, headers=None):
    request = urllib.request.Request(
        url=url,
        headers=headers or HEADERS,
        data=_format_data(data) if data else None
    )
    response = urllib.request.urlopen(request)
    debug(f'{"POST" if data else "GET"} {url} {response.code}')
    reader = codecs.getreader('utf-8')
    data = json.load(reader(response))

    debug(data)
    debug('\n')
    return data


def get(url, headers=None):
    return _req(url, headers=headers)


def post(url, data, headers=None):
    return _req(url, data, headers=headers)


def turn_on():
    saved_states = load_saved_states()
    last_mode = saved_states.get(ARG_IP, {}).get('mode', MODE_ON)
    post(MODE_URL, {MODE: last_mode})
    print(1)


def turn_off():
    post(MODE_URL, {MODE: MODE_OFF})
    print(0)


def get_state():
    mode_data = get(MODE_URL, HEADERS)

    saved_states = load_saved_states()
    saved_states.setdefault(ARG_IP, {})['mode'] = mode_data[MODE]
    save_states(saved_states)

    if mode_data[MODE] != MODE_OFF:
        print(1)
    else:
        print(0)


def main():
    # login to api - get challenge response and auth token
    login_data = post(LOGIN_URL, LOGIN_DATA)
    auth_token = login_data[AUTHENTICATION_TOKEN]
    HEADERS[AUTH_HEADER] = auth_token

    # verify token by responding with challenge response
    verify_data = {CHALLENGE_RESPONSE: login_data[CHALLENGE_RESPONSE]}
    post(VERIFY_URL, verify_data)

    if ARG_ACTION == ARG_ON:
        turn_on()
    elif ARG_ACTION == ARG_OFF:
        turn_off()
    elif ARG_ACTION == ARG_STATE:
        get_state()


if __name__ == '__main__':
    main()
