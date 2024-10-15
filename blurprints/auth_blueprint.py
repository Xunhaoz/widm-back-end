import requests
from flask import Blueprint, current_app, request, make_response, redirect, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, \
    set_access_cookies, set_refresh_cookies, unset_access_cookies, unset_refresh_cookies, get_jwt
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta, timezone

auth_blueprint = Blueprint('auth', __name__)


def get_oauth_access_token(code, state):
    url = ' https://portal.ncu.edu.tw/oauth2/token'
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Basic ' + current_app.config['BASIC_AUTH']
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'state': state,
        'redirect_url': current_app.config['DASH_BOARD_URL'],
    }

    response = requests.post(url, headers=headers, data=data)
    response = response.json()

    return response['access_token']


def get_user_info(access_token):
    url = 'https://portal.ncu.edu.tw/apis/oauth/v1/info'

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)
    response = response.json()

    return response


@auth_blueprint.route('/log_out', methods=['GET'])
@jwt_required(locations=['headers', 'cookies'])
def log_out():
    """
    log_out
    ---
    tags:
      - auth
    responses:
      200:
        description: Return a success message
      404:
        description: Return a client column not found message
    """
    response = make_response(redirect(current_app.config['HOME_PAGE_URL']), 200)
    unset_access_cookies(response)
    unset_refresh_cookies(response)
    return response


@auth_blueprint.route('/return-to', methods=['GET'])
def return_to():
    """
    Return To
    ---
    tags:
      - auth
    parameters:
      - name: code
        in: query
        type: string
        required: true
        description: code
      - name: state
        in: query
        type: integer
        required: true
        description: state
    responses:
      200:
        description: Return a success message
      404:
        description: Return a client column not found message
    """

    code, state = request.args['code'], request.args['state']

    try:
        access_token = get_oauth_access_token(code, state)
        user_info = get_user_info(access_token)
    except Exception as e:
        return redirect(current_app.config['LOGIN_FAILED_URL'])

    if user_info['identifier'] not in current_app.config['WHITE_LIST']:
        return redirect(current_app.config['HOME_PAGE_URL'])

    access_token = create_access_token(identity=user_info)
    refresh_token = create_refresh_token(identity=user_info)
    response = make_response(redirect(current_app.config['DASH_BOARD_URL']), 200)
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 302


@auth_blueprint.route('/user_info', methods=['GET'])
@jwt_required(locations=['headers', 'cookies'])
def user_info():
    """
    User Info
    ---
    tags:
      - auth
    responses:
      200:
        description: Return a success message
      404:
        description: Return a client column not found message
    """
    return get_jwt_identity()


@auth_blueprint.after_request
def refresh_expiring_jwts(response):
    if request.path == '/authentication/sign-out':
        return response
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response
