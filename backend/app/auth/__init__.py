import re
from flask import Blueprint, request, jsonify, make_response, current_app, url_for
from sqlalchemy import exc
from itsdangerous import TimedJSONWebSignatureSerializer
from ..entities.user import User, UserInsertSchema, UserAttributes
from ..entities.entity import Session
from ..email import send_email

auth = Blueprint('auth', __name__)


# TODO change make_responses strings with enum
@auth.route('/check_login', methods=['GET', 'POST'])
def check_login():

    data = request.get_json()
    session = Session()
    if data.get(UserAttributes.USERNAME):
        user = session.query(User).filter_by(username=data[UserAttributes.USERNAME]).first()
    elif data.get(UserAttributes.EMAIL):
        user = session.query(User).filter_by(email=data[UserAttributes.EMAIL]).first()
        session.close()
    else:
        return make_response(jsonify('No username/email provided', 422))
    if user is not None and user.verify_password(data["password"]):
        return make_response(jsonify(True, 201))
    else:
        return make_response(jsonify(False, 201))


@auth.route('/create_user', methods=['GET', 'POST'])
def create_user():

    data = request.get_json()

    session = Session()
    user_schema = UserInsertSchema()
    user = User(**user_schema.load(data))
    try:
        res = user_schema.dump(user.create(session))
    except exc.IntegrityError as ie:
        session.rollback()
        error_detail = ie.orig.args[0]
        affected_attr = str(re.search(r'DETAIL:  Schlüssel »\([a-zA-Z]+\)', error_detail))
        if UserAttributes.USERNAME in affected_attr:
            msg = {"existing": UserAttributes.USERNAME}
            return make_response(jsonify(msg, 422))
        if UserAttributes.EMAIL in affected_attr:
            msg = {"existing": UserAttributes.EMAIL}
            return make_response(jsonify(msg, 422))
    finally:
        session.close()

    confirmation_token = user.generate_confirmation_token()
    url = url_for('auth.confirm', token=confirmation_token, _external=True)
    send_email(user.email, 'Confirm Your Account', 'auth/email/confirm',
               username=user.username, url=url)

    return make_response(jsonify(res, 201))


@auth.route('/confirm/<token>')
def confirm(token):
    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token.encode('utf-8'))
    except:
        return make_response(jsonify({'error': 'token expired or link invalid'}, 422))

    session = Session()
    user_id = data.get("confirm")
    user = session.query(User).filter_by(id=user_id).first()

    if user is None:
        session.close()
        return make_response(jsonify({'error': 'token expired or link invalid'}, 422))
    elif user.confirmed:
        return make_response(jsonify('successfully confirmed', 201))
    else:
        user.confirm(session)
        session.close()
        return make_response(jsonify('successfully confirmed', 201))

# TODO auf JSON umbauen
@auth.route('/confirm/<username>')
def resend_confirmation(username):

    session = Session()
    curr_user = session.query(User).filter_by(username=username).first()
    session.close()

    if curr_user is not None:
        new_token = curr_user.generate_confirmation_token()
        url = url_for('auth.confirm', token=new_token, _external=True)
        send_email(curr_user.email, 'Confirm Your Account', 'auth/email/confirm',
                   username=curr_user.username, url=url)
        return make_response(jsonify('successfully resend', 201))
    else:
        return make_response(jsonify('user does not exist'), 422)


@auth.route('/change_password', methods=['GET', 'POST'])
def change_password():

    data = request.get_json()
    session = Session()

    if data.get(UserAttributes.USERNAME):
        user = session.query(User).filter_by(username=data[UserAttributes.USERNAME]).first()
    else:
        session.close()
        return make_response(jsonify('No username provided', 422))

    if user is None:
        session.close()
        return make_response(jsonify('username does not exist', 422))
    elif user.verify_password(data["password_old"]):
        user.update_password(data["password_new"], session, data[UserAttributes.UPDATED_BY])
        session.close()
        return make_response(jsonify('password successfully changed', 201))
    else:
        return make_response(jsonify('old password is invalid', 422))


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():

    data = request.get_json()
    session = Session()

    if data.get(UserAttributes.USERNAME):
        user = session.query(User).filter_by(username=data[UserAttributes.USERNAME]).first()
    else:
        session.close()
        return make_response(jsonify('No username provided', 422))

    if user is None:
        session.close()
        return make_response(jsonify('username does not exist', 422))
    else:
        token = user.generate_reset_token()
        url = url_for('auth.reset', token=token, _external=True)
        send_email(user.email, 'Reset Your Password', 'auth/email/reset_password',
                   username=user.username, url=url)
        session.close()
        return make_response(jsonify('successfully requested', 201))


@auth.route('reset/<token>', methods=['GET', 'POST'])
def password_reset(token):

    data = request.json()
    session = Session()
    if not data.get("password") or not data.get(UserAttributes.UPDATED_BY):
        session.close()
        return make_response(jsonify('No password provided', 422))
    elif User.reset_password(session, token, data):
        session.close()
        return make_response(jsonify('password successfully reset', 201))
    else:
        session.close()
        return make_response(jsonify('Password reset not possible', 400))


@auth.route('/change_email', methods=['GET', 'POST'])
def change_email_request():

    data = request.get_json()
    session = Session()

    if data.get(UserAttributes.USERNAME):
        user = session.query(User).filter_by(username=data[UserAttributes.USERNAME])
    else:
        session.close()
        return make_response(jsonify('no username provided', 422))

    if user is None:
        session.close()
        return make_response(jsonify('username does not exist', 422))
    elif user.email == data.get("email_new"):
        return make_response(jsonify("given email is old email"), 422)
    else:
        email_token = user.generate_email_token(data["email_new"])
        url = url_for('auth.change_email', token=email_token, _external=True)
        send_email(data.get("email_new"), 'Confirm Your Email Address', 'auth/email/change_email',
                   username=data[UserAttributes.USERNAME], url=url)
        session.close()
        return make_response(jsonify('successfully requested', 201))


@auth.route('/change_email/<token>')
def change_email(token):

    data = request.json()
    session = Session()

    if data.get(UserAttributes.USERNAME):
        user = session.query(User).filter_by(username=data[UserAttributes.USERNAME])
    else:
        session.close()
        return make_response(jsonify('no username provided', 422))

    if user is None:
        session.close()
        return make_response(jsonify('username does not exist', 422))
    elif user.change_email(session, token, data[UserAttributes.UPDATED_BY]):
        session.close()
        return make_response(jsonify('successfully changed email'), 201)
    else:
        session.close()
        return make_response(jsonify('email change not possible'), 400)
