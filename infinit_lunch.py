import os
from datetime import datetime

import requests
from flask import Flask
from raven.contrib.flask import Sentry

from restaurants import SafeRestaurant, BednarRestaurant, BreweriaRestaurant, DonQuijoteRestaurant, DreamsRestaurant, \
    GastrohouseRestaurant, JarosovaRestaurant, OtherRestaurant, FormattedMenus
from slack import Channel

# SLACK_HOOK = 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
SLACK_HOOK = os.environ.get('SLACK_HOOK', None)
SECRET_KEY = os.environ.get('SECRET_KEY', None)
DEBUG = bool(os.environ.get('DEBUG', False))

app = Flask(__name__)
sentry = Sentry(app)    # do not forget to set SENTRY_DSN


def is_work_day():
    return datetime.today().weekday() in range(0, 5)


def retrieve_menus():
    return [
        SafeRestaurant(JarosovaRestaurant()).retrieve_menu(),
        SafeRestaurant(BednarRestaurant()).retrieve_menu(),
        SafeRestaurant(BreweriaRestaurant()).retrieve_menu(),
        SafeRestaurant(DonQuijoteRestaurant()).retrieve_menu(),
        SafeRestaurant(DreamsRestaurant()).retrieve_menu(),
        SafeRestaurant(GastrohouseRestaurant()).retrieve_menu(),
        SafeRestaurant(OtherRestaurant()).retrieve_menu(),
    ]


def should_send_to_slack(secret_key):
    return SLACK_HOOK and secret_key == SECRET_KEY


@app.route('/', defaults={'secret_key': 'wrong key'})
@app.route('/<secret_key>')
def hello(secret_key):
    if is_work_day():
        menus = FormattedMenus(retrieve_menus())
        if should_send_to_slack(secret_key):
            Channel(SLACK_HOOK, requests).send(menus)
        return '<pre>{}</pre>'.format(menus)
    else:
        return 'Come on Monday-Friday'


if __name__ == '__main__':
    app.run(debug=DEBUG)
