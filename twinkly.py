import sys
import json
import urllib.request
import codecs

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
TURN_ON_DATA = {MODE: MODE_ON}
TURN_OFF_DATA = {MODE: MODE_OFF}


def format_data(data):
    return json.dumps(data).encode('utf8')


def process_request(request):
    return urllib.request.urlopen(request)


def process_request_json(request):
    login_response = process_request(request)
    reader = codecs.getreader("utf-8")
    return json.load(reader(login_response))


# login to api - get challenge response and auth token
loginRequest = urllib.request.Request(url=LOGIN_URL, headers=HEADERS, data=format_data(LOGIN_DATA))
loginData = process_request_json(loginRequest)

challengeResponse = loginData[CHALLENGE_RESPONSE]
authToken = loginData[AUTHENTICATION_TOKEN]

HEADERS[AUTH_HEADER] = authToken
verifyData = {CHALLENGE_RESPONSE: challengeResponse}

# verify token by responding with challenge response
verifyRequest = urllib.request.Request(url=VERIFY_URL, headers=HEADERS, data=format_data(verifyData))
verifyData = process_request_json(verifyRequest)


def turn_on():
    on_request = urllib.request.Request(url=MODE_URL, headers=HEADERS, data=format_data(TURN_ON_DATA))
    process_request(on_request)
    print(1)


def turn_off():
    off_request = urllib.request.Request(url=MODE_URL, headers=HEADERS, data=format_data(TURN_OFF_DATA))
    process_request(off_request)
    print(0)


def get_state():
    mode_request = urllib.request.Request(url=MODE_URL, headers=HEADERS)
    mode_data = process_request_json(mode_request)

    if mode_data[MODE] != MODE_OFF:
        print(1)
    else:
        print(0)


def main():
    if ARG_ACTION == ARG_ON:
        turn_on()
    elif ARG_ACTION == ARG_OFF:
        turn_off()
    elif ARG_ACTION == ARG_STATE:
        get_state()
