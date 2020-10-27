from flask import Blueprint, request, make_response, jsonify
from sqlalchemy.exc import IntegrityError

from ..entities.entity import Session
from ..entities.user import UserAttributes, User, Permission
from ..entities.country import CountryInsertSchema, Country, CountryAttributes, CountrySchema
from ..main.error_handling import investigate_integrity_error

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
            session.rollback()
            session.close()
            msg = investigate_integrity_error(ie)
            if msg is not None:
                return make_response(jsonify(msg), 422)

        finally:
            session.close()

        return make_response(jsonify(res, 201))
    else:
        return make_response(jsonify('Not authorized', 403))


@main.route('/update/country', methods=['GET', 'POST'])
def update_country():

    user_data = request.get_json()['user']
    country_data = request.get_json()['country']
    session = Session()
    if user_data.get(str(UserAttributes.USERNAME)):
        user = session.query(User).filter_by(username=user_data.get(str(UserAttributes.USERNAME))).first()
    else:
        session.close()
        return make_response(jsonify("No username provided", 422))

    if user is not None and user.can(Permission.CREATE):
        country = session.query(Country).filter_by(id=country_data.get(str(CountryAttributes.ID))).first()
        if country is not None:

            try:
                country.update(session, user.id, **country_data)
            except IntegrityError as ie:
                session.rollback()
                session.close()
                msg = investigate_integrity_error(ie)
                if msg is not None:
                    return make_response(jsonify(msg), 422)

            finally:
                session.close()
            return make_response(jsonify('successfully updated', 201))
        else:
            session.close()
            return make_response(jsonify('country update not successfully', 400))
    else:
        session.close()
        return make_response(jsonify('country update not successfully', 400))


@main.route('/discover/country', methods=['GET'])
def list_country():

    session = Session()

    res = session.query(Country).all()
    schema = CountrySchema(many=True, only=(str(CountryAttributes.NAME), str(CountryAttributes.ID)))
    countries = schema.dump(res)

    return make_response(jsonify(countries, 201))
