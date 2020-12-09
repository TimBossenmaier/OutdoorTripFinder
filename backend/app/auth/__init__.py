import datetime
import os

from flask import Blueprint, request, make_response, current_app, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from itsdangerous import TimedJSONWebSignatureSerializer
from flask_httpauth import HTTPBasicAuth

from app.entities.user import User, UserInsertSchema, UserAttributes
from app.entities.entity import Session
from app.email import send_email
from app.main.error_handling import investigate_integrity_error
from app.utils import responses
from app.utils.responses import create_json_response, ResponseMessages

auth = Blueprint('auth', __name__)
http_auth = HTTPBasicAuth()


def process_consent(typ, token):
    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token.encode('utf-8'))
    except:
        return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                  ResponseMessages.AUTH_TOKEN_INVALID,
                                                  token), 422)

    session = Session()
    user_id = data.get(typ)
    user = session.query(User).filter_by(id=user_id).first()

    if user is None:
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                  ResponseMessages.AUTH_TOKEN_INVALID,
                                                  token), 422)
    elif user.confirmed:
        user = user.serialize()
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.SUCCESS_200,
                                                  ResponseMessages.AUTH_USER_CONFIRMED,
                                                  user), 200)
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
        return make_response(create_json_response(responses.SUCCESS_200,
                                                  ResponseMessages.AUTH_USER_CONFIRMED,
                                                  user), 201)


@http_auth.verify_password
def verify_password(email_or_token, password):
    session = Session()
    if email_or_token == '':
        return False
    if password == '':
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
    return user.verify_password(password)


@http_auth.error_handler
def auth_error():
    return make_response(create_json_response(responses.UNAUTHORIZED_403,
                                              ResponseMessages.AUTH_INVALID_PARAMS,
                                              None), 403)


@auth.route('/tokens/', methods=['POST'])
@http_auth.login_required
def get_token():
    session = Session()
    if http_auth.current_user is None or http_auth.token_used:
        return make_response(create_json_response(responses.UNAUTHORIZED_403,
                                                  ResponseMessages.AUTH_INVALID_PARAMS,
                                                  None), 403)
    return make_response(create_json_response(responses.SUCCESS_200,
                                              ResponseMessages.AUTH_LOGIN_SUCCESSFUL,
                                              {'token': http_auth.current_user.generate_auth_token(expiration=3600,
                                                                                                   session=session),
                                               'expiration_ts': datetime.datetime.now() + datetime.timedelta(hours=1)}),
                         200)


@auth.route('/create_user', methods=['GET', 'POST'])
def create_user():
    data = request.get_json()

    #TODO: check when user already exists

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
            return make_response(create_json_response(responses.BAD_REQUEST_400,
                                                      ResponseMessages.AUTH_DUPLICATE_PARAMS,
                                                      msg), 422)
    finally:
        session.expunge_all()
        session.close()

    approval_token = user.generate_approval_token()
    url = url_for('auth.approve', token=approval_token, _external=True)
    send_email(os.environ.get('APPROVAL_MAIL'), 'Confirm New User', 'email/new_user',
               username=user.username, url=url, email=user.email)

    return make_response(create_json_response(responses.SUCCESS_201,
                                              ResponseMessages.AUTH_USER_CREATED,
                                              res), 201)


@auth.route('/approve/<token>')
def approve(token):
    resp = process_consent('approve', token)

    return resp


@auth.route('/confirm/<token>')
def confirm(token):
    resp = process_consent('confirm', token)

    return resp


@auth.route('/confirm', methods=['GET', 'POST'])
@http_auth.login_required
def resend_confirmation():
    data = request.get_json()
    curr_user = http_auth.current_user
    if curr_user is not None:
        if curr_user.confirmed:
            curr_user = curr_user.serialize()
            return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                      ResponseMessages.AUTH_ALREADY_CONFIRMED,
                                                      curr_user), 422)
        else:
            new_token = curr_user.generate_confirmation_token()
            url = url_for('auth.confirm', token=new_token, _external=True)
            send_email(curr_user.email, 'Confirm Your Account', 'email/confirm',
                       username=curr_user.username, url=url)
            curr_user = curr_user.serialize()
            return make_response(create_json_response(responses.SUCCESS_200,
                                                      ResponseMessages.AUTH_CONFIRMATION_RESEND,
                                                      curr_user), 200)
    else:
        return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                  ResponseMessages.AUTH_INVALID_PARAMS,
                                                  data), 422)


@auth.route('/change_password', methods=['GET', 'POST'])
@http_auth.login_required
def change_password():
    data = request.get_json()
    session = Session()

    user = http_auth.current_user
    if user is None:
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                  ResponseMessages.AUTH_USERNAME_NOT_PROVIDED,
                                                  data), 422)
    else:
        user.update_password(data["password_new"], session, user.username)
        user = user.serialize()
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.SUCCESS_200,
                                                  ResponseMessages.AUTH_PASSWORD_CHANGED,
                                                  user), 200)


@auth.route('/reset_cred', methods=['GET', 'POST'])
def password_reset_request():
    data = request.get_json()
    session = Session()

    if data.get(str(UserAttributes.USERNAME)):
        user = session.query(User).filter_by(username=data[str(UserAttributes.USERNAME)]).first()
    else:
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.MISSING_PARAMETER_422,
                                                  ResponseMessages.AUTH_USERNAME_NOT_PROVIDED,
                                                  data), 422)

    if user is None:
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                  ResponseMessages.AUTH_INVALID_PARAMS,
                                                  data), 422)
    else:
        token = user.generate_reset_token()
        url = url_for('auth.password_reset', token=token, _external=True)
        send_email(user.email, 'Reset Your Password', 'email/reset_password',
                   username=user.username, url=url)
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.SUCCESS_200,
                                                  ResponseMessages.AUTH_PW_REQUESTED,
                                                  user.serialize()), 200)


@auth.route('reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    data = request.get_json()
    session = Session()
    if not data.get("password"):
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.MISSING_PARAMETER_422,
                                                  ResponseMessages.AUTH_PASSWORD_NOT_PROVIDED,
                                                  data), 422)
    elif User.reset_password(session, token, data):
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.SUCCESS_200,
                                                  ResponseMessages.AUTH_RESET_SUCCESSFUL,
                                                  True), 200)
    else:
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.BAD_REQUEST_400,
                                                  ResponseMessages.AUTH_RESET_FAILED,
                                                  data), 400)


@auth.route('/change_email', methods=['GET', 'POST'])
@http_auth.login_required
def change_email_request():
    data = request.get_json()
    session = Session()

    user = http_auth.current_user
    if user is None:
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                  ResponseMessages.AUTH_INVALID_PARAMS,
                                                  data), 422)
    elif user.email == data.get(str(UserAttributes.EMAIL)):
        return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                  ResponseMessages.AUTH_EMAIL_EXISTS,
                                                  data), 422)
    else:
        email_token = user.generate_email_token(data[str(UserAttributes.EMAIL)],
                                                data.get(str(UserAttributes.USERNAME)))
        url = url_for('auth.change_email', token=email_token, _external=True)
        send_email(data.get(str(UserAttributes.EMAIL)), 'Confirm Your Email Address', 'email/change_email',
                   username=data.get(str(UserAttributes.USERNAME)), url=url)

        user = user.serialize()
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.SUCCESS_200,
                                                  ResponseMessages.AUTH_EMAIL_REQUESTED,
                                                  user), 200)


@auth.route('/change_email/<token>')
def change_email(token):
    new_email, username, user_id = User.resolve_email_token(token)
    session = Session()

    if username is not None:
        user = session.query(User).filter_by(username=username).first()
    else:
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.MISSING_PARAMETER_422,
                                                  ResponseMessages.AUTH_USERNAME_NOT_PROVIDED), 422)

    if user is None:
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                  ResponseMessages.AUTH_INVALID_PARAMS), 422)
    elif user.change_email(session, new_email, user_id, username):
        user = user.serialize()
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.SUCCESS_200,
                                                  ResponseMessages.AUTH_EMAIL_CHANGED,
                                                  user), 200)
    else:
        user = user.serialize()
        session.expunge_all()
        session.close()
        return make_response(create_json_response(responses.BAD_REQUEST_400,
                                                  ResponseMessages.AUTH_EMAIL_FAILED,
                                                  user), 400)
