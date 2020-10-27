from flask import Blueprint, request, make_response, jsonify
from sqlalchemy.exc import IntegrityError

from ..entities.entity import Session
from ..entities.user import UserAttributes, User, Permission
from ..entities.country import CountryInsertSchema, Country

main = Blueprint('main', __name__)


def get_main_app():
    return main


@main.route('/create/country', methods=['GET', 'POST'])
def create_country():

    user_data = request.get_json()['user']
    country_data = request.get_json()['country']
    session = Session()
    if user_data.get(str(UserAttributes.USERNAME)):
        user = session.query(User).filter_by(username=user_data.get(str(UserAttributes.USERNAME))).first()
    else:
        session.close()
        return make_response(jsonify("No username provided", 422))

    if user is not None and user.can(Permission.CREATE):
        country_data.update({'created_by': user.id})
        country_schema = CountryInsertSchema()
        country = Country(**country_schema.load(country_data))

        try:
            res = country_schema.dump(country.create(session))

        except IntegrityError as ie:
            print(ie)
            session.rollback()
            session.close()

        finally:
            session.close()

        return make_response(jsonify(res, 201))


