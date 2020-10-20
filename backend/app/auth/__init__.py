from flask import Blueprint, request, jsonify, make_response
from ..entities.user import User

auth = Blueprint('auth', __name__)


@auth.route('/check_login', methods=['GET', 'POST'])
def check_login():

    data = request.get_json()

    if data["username"]:
        user = User.query.filter_by(username=data["username"]).first()
    elif data["email"]:
        user = User.query.filter_by(email=data["email"]).first()
    else:
        return make_response(jsonify('No username/email provided', 422))

    if user is not None and user.password_hash == data["password_hash"]:
        return make_response(jsonify(True, 201))
    else:
        return make_response(jsonify(False, 201))
