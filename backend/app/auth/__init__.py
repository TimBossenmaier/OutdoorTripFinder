from flask import Blueprint, request, jsonify, make_response
from ..entities.user import User
from ..entities.entity import Session

auth = Blueprint('auth', __name__)


@auth.route('/check_login', methods=['GET', 'POST'])
def check_login():

    data = request.get_json()
    session = Session()
    if data.get("username"):
        user = session.query(User).filter_by(username=data["username"]).first()
    elif data.get("email"):
        user = session.query(User).filter_by(email=data["email"]).first()
    else:
        return make_response(jsonify('No username/email provided', 422))

    if user is not None and user.password_hash == data["password_hash"]:
        return make_response(jsonify(True, 201))
    else:
        return make_response(jsonify(False, 201))
