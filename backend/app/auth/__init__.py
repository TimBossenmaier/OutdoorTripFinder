import ast
import base64
import datetime
import os

from flask import Blueprint, request, current_app, url_for, jsonify
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from itsdangerous import TimedJSONWebSignatureSerializer
from flask_httpauth import HTTPBasicAuth

from app.entities.user import User, UserInsertSchema, UserAttributes
from app.entities.entity import Session
from app.email import send_email
from app.main.error_handling import investigate_integrity_error
from app.utils import responses
from app.utils.responses import ResponseMessages, create_response

# create blueprint for all authentication endpoints
auth = Blueprint('auth', __name__)
http_auth = HTTPBasicAuth()


def process_consent(typ, token):
    """
    Processes a confirmation token, both for user confirmation and approval
    Args:
        typ: denotes type of action, e.g. confirm
        token: token that verifies transaction

    """
    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token.encode('utf-8'))
    except:
        return create_response(token, responses.INVALID_INPUT_422, ResponseMessages.AUTH_TOKEN_INVALID,
                               User.__name__, 422)

    session = Session()
    user_id = data.get(typ)
    user = session.query(User).filter_by(id=user_id).first()

    if user is None:
        session.expunge_all()
        session.close()
        return create_response(token, responses.INVALID_INPUT_422, ResponseMessages.AUTH_TOKEN_INVALID,
                               User.__name__, 422)

    elif user.confirmed:
        user = user.serialize()
        session.expunge_all()
        session.close()
        return create_response(user, responses.SUCCESS_200, ResponseMessages.AUTH_USER_CONFIRMED, User.__name__, 200)
    else:

        if typ == 'confirm':
            user.confirm(session)
        else:
            user.approve(session)
            new_token = user.generate_confirmation_token()
            url = url_for('auth.confirm', token=new_token, _external=True)
            send_email(user.email, 'Confirm Your Account', 'email/confirm',
                       username=user.username, url=url)

        user = user.serialize()
        session.expunge_all()
        session.close()
        return create_response(user, responses.SUCCESS_200, ResponseMessages.AUTH_USER_CONFIRMED, User.__name__, 200)


@http_auth.verify_password
def verify_password(email_or_token, password):
    """
    verifies the credentials provided by HTTP Auth, is invoked before endpoint is acessed
    Args:
        email_or_token: email address of user or authentication token
        password: user password (only required in case of login via email)

    Returns:
        Flask response, consisting of response code, response message, affected class, and http code
    """
    session = Session()
    if email_or_token == '':
        return False
    if password == '':  # password is not provided when auth token is used
        http_auth.current_user = User.verify_auth_token(email_or_token, session)
        http_auth.token_used = True
        session.expunge_all()
        session.close()
        return http_auth.current_user is not None
    user = session.query(User).filter(or_(User.email == email_or_token,
                                          User.username == email_or_token)).first()
    session.expunge_all()
    session.close()

    if not user:
        return False
    http_auth.current_user = user
    http_auth.token_used = False
    return create_response(False, responses.UNAUTHORIZED_403, ResponseMessages.AUTH_INVALID_PARAMS, User.__name__, 403)


@http_auth.error_handler
def auth_error():
    """
    is invoked in case any error occurs in HTTP Auth
    Returns:
        Flask response, consisting of response code, response message, affected class, and http code
    """
    return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.AUTH_INVALID_PARAMS, User.__name__, 403)


@auth.route('/tokens/<data_encoded>', methods=['GET'])
@http_auth.login_required
def get_token(data_encoded):
    """
    creates endpoint to retrieve an auth token for an user already authenticated
    Args:
        data_encoded: BASE64 encoded JSON

    Returns:
        Flask response, consisting of encoded user (only containing attributes specified in {output},response code,
         response message, affected class, and http code
    """
    session = Session()
    user = http_auth.current_user

    data_string = base64.b64decode(data_encoded).decode()
    data = ast.literal_eval(data_string)

    if user not in session:
        user = session.query(User).get(user.id)

    if http_auth.current_user is None or http_auth.token_used:
        return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.AUTH_INVALID_PARAMS,
                               User.__name__, 403)
    token = {'token': user.generate_auth_token(expiration=1200,
                                               session=session),
             'expiration_ts': (datetime.datetime.now() + datetime.timedelta(minutes=20)).isoformat()}

    return create_response(user.serialize(only=data.get("ouput"), **token),
                           responses.SUCCESS_200, ResponseMessages.AUTH_LOGIN_SUCCESSFUL, None, 200)


@auth.route('/create_user', methods=['POST'])
def create_user():
    """
    Endpoint to create a new user
    Returns:
        Flask response, consisting of serialized user,response code, response message, affected class, and http code
    """

    # TODO: change to base64 encoded JSON
    data = request.get_json()

    session = Session()
    user_schema = UserInsertSchema()
    user = User(**user_schema.load(data))
    res = None
    try:
        res = user_schema.dump(user.create(session))
    except IntegrityError as ie:
        session.rollback()
        session.expunge_all()
        session.close()
        msg = investigate_integrity_error(ie)
        if msg is not None:
            return create_response(msg, responses.BAD_REQUEST_400, ResponseMessages.AUTH_DUPLICATE_PARAMS,
                                   User.__name__, 400)
    finally:
        session.expunge_all()
        session.close()

    approval_token = user.generate_approval_token()
    url = url_for('auth.approve', token=approval_token, _external=True)
    send_email(os.environ.get('APPROVAL_MAIL'), 'Confirm New User', 'email/new_user',
               username=user.username, url=url, email=user.email)

    return create_response(res, responses.SUCCESS_201, ResponseMessages.AUTH_USER_CONFIRMED, User.__name__, 201)


@auth.route('/approve/<token>')
def approve(token):
    """
    Endpoint to approve a new user (by admin)
    Accessible without authentication
    Args:
        token: approval token to identify user
    Returns:
        response of :func:`~process_consent`
    """
    resp = process_consent('approve', token)

    return resp


@auth.route('/confirm/<token>')
def confirm(token):
    """
    Endpoint to confirm a new account (by user himself)
    Accessible without authentication

    Args:
        token: approval token to identify user
    Returns:
        response of :func:`~process_consent`
    """
    resp = process_consent('confirm', token)

    return resp


@auth.route('/confirm', methods=['GET', 'POST'])
@http_auth.login_required
def resend_confirmation():
    """
    Endpoint to resend confirmation E-Mail
    Returns:
        Flask response, consisting of serialized user, response code, response message, affected class, and http code
    """
    # TODO: change to BASE64 decoded JSON
    data = request.get_json()
    curr_user = http_auth.current_user
    if curr_user is not None:
        if curr_user.confirmed:
            curr_user = curr_user.serialize()
            return create_response(curr_user, responses.INVALID_INPUT_422, ResponseMessages.AUTH_ALREADY_CONFIRMED,
                                   User.__name__, 422)
        else:
            new_token = curr_user.generate_confirmation_token()
            url = url_for('auth.confirm', token=new_token, _external=True)
            send_email(curr_user.email, 'Confirm Your Account', 'email/confirm',
                       username=curr_user.username, url=url)
            curr_user = curr_user.serialize()
            return create_response(curr_user, responses.SUCCESS_200, ResponseMessages.AUTH_CONFIRMATION_RESEND,
                                   User.__name__, 200)
    else:
        return create_response(data, responses.INVALID_INPUT_422, ResponseMessages.AUTH_INVALID_PARAMS,
                               User.__name__, 422)


@auth.route('/change_password', methods=['GET', 'POST'])
@http_auth.login_required
def change_password():
    """
    Endpoint to change the password

    Returns:
         Flask response, consisting of serialized user, response code, response message, affected class, and http code
    """
    # TODO: change to encoded JSON
    data = request.get_json()
    session = Session()

    user = http_auth.current_user
    if user is None:
        session.expunge_all()
        session.close()
        return create_response(data, responses.INVALID_INPUT_422, ResponseMessages.AUTH_USERNAME_NOT_PROVIDED,
                               User.__name__, 422)
    else:
        user.update_password(data["password_new"], session, user.username)
        user = user.serialize()
        session.expunge_all()
        session.close()
        return create_response(user, responses.SUCCESS_200, ResponseMessages.AUTH_PASSWORD_CHANGED, User.__name__, 200)


@auth.route('/reset_cred', methods=['GET', 'POST'])
def password_reset_request():
    """
    Endpoint to reset password, sends out a confirmation mail to authenticate user

    Returns:
         Flask response, consisting of serialized user, response code, response message, affected class, and http code
    """
    data = request.get_json()
    session = Session()

    if data.get(str(UserAttributes.USERNAME)):
        user = session.query(User).filter_by(username=data[str(UserAttributes.USERNAME)]).first()
    else:
        session.expunge_all()
        session.close()
        return create_response(data, responses.MISSING_PARAMETER_422, ResponseMessages.AUTH_USERNAME_NOT_PROVIDED,
                               User.__name__, 422)
    if user is None:
        session.expunge_all()
        session.close()
        return create_response(data, responses.INVALID_INPUT_422, ResponseMessages.AUTH_INVALID_PARAMS,
                               User.__name__, 422)
    else:
        token = user.generate_reset_token()
        url = url_for('auth.password_reset', token=token, _external=True)
        send_email(user.email, 'Reset Your Password', 'email/reset_password',
                   username=user.username, url=url)
        session.expunge_all()
        session.close()
        return create_response(user.serialize(), responses.SUCCESS_200, ResponseMessages.AUTH_PW_REQUESTED,
                               User.__name__, 200)


@auth.route('reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """
    Endpoint to reset the password, after user has requested password reset by :func:`~password_reset_request`
    Args:
        token: token to authenticate user, sent out by password reset mail

    Returns:
        Flask response, consisting of serialized user, response code, response message, affected class, and http code
    """
    data = request.get_json()
    session = Session()
    if not data.get("password"):
        session.expunge_all()
        session.close()
        return create_response(data, responses.MISSING_PARAMETER_422, ResponseMessages.AUTH_PASSWORD_NOT_PROVIDED,
                               User.__name__, 422)
    elif User.reset_password(session, token, data):
        session.expunge_all()
        session.close()
        return create_response(True, responses.SUCCESS_200, ResponseMessages.AUTH_RESET_SUCCESSFUL, User.__name__, 200)
    else:
        session.expunge_all()
        session.close()
        return create_response(data, responses.BAD_REQUEST_400, ResponseMessages.AUTH_RESET_FAILED, User.__name__, 400)


@auth.route('/change_email', methods=['GET', 'POST'])
@http_auth.login_required
def change_email_request():
    """
    Endpoint to change E-Mail, sends out confirmation mail to new endpoint
    Returns:
        Flask response, consisting of serialized user, response code, response message, affected class, and http code
    """
    data = request.get_json()
    session = Session()

    user = http_auth.current_user
    if user is None:
        session.expunge_all()
        session.close()
        return create_response(data, responses.INVALID_INPUT_422, ResponseMessages.AUTH_INVALID_PARAMS,
                               User.__name__, 422)
    elif user.email == data.get(str(UserAttributes.EMAIL)):
        return create_response(data, responses.INVALID_INPUT_422, ResponseMessages.AUTH_EMAIL_EXISTS,
                               User.__name__, 422)
    else:
        email_token = user.generate_email_token(data[str(UserAttributes.EMAIL)],
                                                data.get(str(UserAttributes.USERNAME)))
        url = url_for('auth.change_email', token=email_token, _external=True)
        send_email(data.get(str(UserAttributes.EMAIL)), 'Confirm Your Email Address', 'email/change_email',
                   username=data.get(str(UserAttributes.USERNAME)), url=url)

        user = user.serialize()
        session.expunge_all()
        session.close()
        return create_response(user, responses.SUCCESS_200, ResponseMessages.AUTH_EMAIL_REQUESTED, User.__name__, 200)


@auth.route('/change_email/<token>')
def change_email(token):
    """
    Endpoint to finally change email
    Args:
        token: token from confirmation mail

    Returns:
        Flask response, consisting of serialized user, response code, response message, affected class, and http code
    """
    new_email, username, user_id = User.resolve_email_token(token)
    session = Session()

    if username is not None:
        user = session.query(User).filter_by(username=username).first()
    else:
        session.expunge_all()
        session.close()
        return create_response(None, responses.MISSING_PARAMETER_422, ResponseMessages.AUTH_USERNAME_NOT_PROVIDED,
                               User.__name__, 422)

    if user is None:
        session.expunge_all()
        session.close()
        return create_response(None, responses.INVALID_INPUT_422, ResponseMessages.AUTH_INVALID_PARAMS,
                               User.__name__, 422)
    elif user.change_email(session, new_email, user_id, username):
        user = user.serialize()
        session.expunge_all()
        session.close()
        return create_response(user, responses.SUCCESS_200, ResponseMessages.AUTH_EMAIL_CHANGED, User.__name__, 200)
    else:
        user = user.serialize()
        session.expunge_all()
        session.close()
        return create_response(user, responses.BAD_REQUEST_400, ResponseMessages.AUTH_EMAIL_CHANGED,
                               User.__name__, 400)


@auth.route('user/<data_encoded>')
@http_auth.login_required
def get_user(data_encoded):
    """
    Endpoint returning logged-in user
    Args:
        data_encoded: BASE64 encoded JSON

    Returns:
        Flask response, consisting of serialized user, response code, response message, affected class, and http code
    """
    user = http_auth.current_user

    data_string = base64.b64decode(data_encoded).decode()
    data = ast.literal_eval(data_string)

    session = Session()

    # TODO: not approved or confirmed

    if user is not None:

        if user not in session:
            user = session.query(User).get(user.id)

        token = {'token': user.generate_auth_token(expiration=1200,
                                                   session=session),
                 'expiration_ts': (datetime.datetime.now() + datetime.timedelta(minutes=20)).isoformat()}

        return create_response(user.serialize(only=data.get("ouput"), **token), responses.SUCCESS_200,
                               ResponseMessages.AUTH_LOGIN_SUCCESSFUL, User, 200)
    else:
        return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.AUTH_LOGIN_FAILED, User, 403)
