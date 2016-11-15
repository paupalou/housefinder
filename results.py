from flask import Flask, render_template, redirect, url_for, session, request
from flask_pymongo import PyMongo
from oauth2client import client
from httplib2 import Http

from googleapiclient import discovery

from uuid import uuid4

from housefinder.config import GoogleCredentials
import json

app = Flask(__name__)
app.secret_key = str(uuid4())
app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_DBNAME'] = 'housefinder'
app.config['MONGO_CONNECT'] = False
app.config['DEBUG'] = True
app.debug = True
app.config['PROPAGATE_EXCEPTIONS'] = True
mongo = PyMongo(app, config_prefix='MONGO')

# filters params values
filter_fields = ['price', 'meters', 'rooms']
filter_types = ['lt', 'gt']


def list(items, errors=[]):
    return render_template(
            'list.html',
            items=items,
            errors=errors,
            results=items.count()
            )


@app.route('/housefinder/login')
def login():
    if 'credentials' not in session:
        return redirect(url_for('auth'))

    credentials = client.OAuth2Credentials.from_json(session['credentials'])

    if credentials.access_token_expired:
        return redirect(url_for('auth'))
    else:
        return redirect(url_for('welcome'))


@app.route('/housefinder/auth')
def auth():
    google_credentials = GoogleCredentials()
    flow = client.OAuth2WebServerFlow(
            client_id=google_credentials.get('client_id'),
            client_secret=google_credentials.get('client_secret'),
            scope='https://www.googleapis.com/auth/drive',
            redirect_uri=google_credentials.get('redirect_uri'))

    if 'code' not in request.args:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        session['credentials'] = credentials.to_json()
        return redirect(url_for('welcome'))


@app.route('/housefinder/welcome')
def welcome():
    if 'credentials' not in session:
        return redirect(url_for('auth'))

    credentials = client.OAuth2Credentials.from_json(session['credentials'])

    if credentials.access_token_expired:
        return redirect(url_for('auth'))
    else:
        http_auth = credentials.authorize(Http())
        userfile = __get_userfile(http_auth)
        if not userfile:
            userfile = __create(http_auth)
        return render_template(
                'welcome.html',
                user=credentials.client_id)


@app.route('/housefinder/modif')
def modif():
    if 'credentials' not in session:
        return redirect(url_for('auth'))

    credentials = client.OAuth2Credentials.from_json(session['credentials'])

    if credentials.access_token_expired:
        return redirect(url_for('auth'))
    else:
        http_auth = credentials.authorize(Http())
        userfile = __get_userfile(http_auth)
        if not userfile:
            userfile = __create(http_auth)
        import json
        return json.dumps(userfile)
        # drive_service = discovery.build('drive', 'v3', http_auth)
        # userfile.__iter__
        # drive_service.files().update(
        #         fileId=userfile['id'],
        #         media_body=yaml.dump("{'test': 'abc'}")) .execute()


def __get_userfile(auth):
    drive_service = discovery.build('drive', 'v3', auth)
    file_list = drive_service.files().list(
            q="name='housefinder_user.yaml'"
            ).execute()
    if len(file_list.get('files', [])) > 0:
        userfile_id = file_list.get('files').pop()['id']
        userfile = drive_service.files().get(fileId=userfile_id).execute()
        return userfile
    return False


def __create(auth):
    drive_service = discovery.build('drive', 'v3', auth)
    body = {'name': 'housefinder_user.yaml', 'mimeType': 'text/plain'}
    newfile = drive_service.files().create(body=body).execute()
    return json.dumps(newfile)


@app.route('/housefinder')
def all():
    return list(mongo.db.houses.find())


@app.route('/housefinder/<filter>/<type>/<int:quantity>')
def filter_results(filter, type, quantity):
    def _check_params(errors):
        if filter not in filter_fields:
            errors.append('Filter introduced is not correct')
            return False
        if type not in filter_types:
            errors.append('Type introduced is not correct')
            return False
        if not isinstance(quantity, int):
            errors.append('Quantity is not numeric')
            return False
        return True

    errors = []
    houses = []

    if _check_params(errors):
        condition = {filter: {'$'+type: quantity}}
        houses = mongo.db.houses.find(condition).sort(''+filter, 1)

    return list(houses, errors)
