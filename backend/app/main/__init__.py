from flask import Blueprint, request, make_response, jsonify
from sqlalchemy.exc import IntegrityError

from ..entities.entity import Session
from ..entities.user import UserAttributes, User, Permission
from ..entities.country import CountryInsertSchema, Country, CountryAttributes, CountrySchema
from ..main.error_handling import investigate_integrity_error
from ..utils import responses
from ..utils.responses import create_json_response, ResponseMessages

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
        return make_response(jsonify(create_json_response(responses.MISSING_PARAMETER_422,
                                                          ResponseMessages.CREATE_MISSING_PARAM,
                                                          user_data,
                                                          Country.__name__), 422))

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

        return make_response(jsonify(create_json_response(responses.SUCCESS_201,
                                                          ResponseMessages.CREATE_SUCCESS,
                                                          res,
                                                          Country.__name__), 201))
    else:
        return make_response(jsonify(create_json_response(responses.UNAUTHORIZED_403,
                                                          ResponseMessages.CREATE_NOT_AUTHORIZED,
                                                          user_data), 403))


@main.route('/update/country', methods=['GET', 'POST'])
def update_country():

    user_data = request.get_json()['user']
    country_data = request.get_json()['country']
    session = Session()
    if user_data.get(str(UserAttributes.USERNAME)):
        user = session.query(User).filter_by(username=user_data.get(str(UserAttributes.USERNAME))).first()
    else:
        session.close()
        return make_response(jsonify(create_json_response(responses.MISSING_PARAMETER_422,
                                                          ResponseMessages.UPDATE_MISSING_PARAM,
                                                          user_data,
                                                          Country.__name__), 422))

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
            return make_response(jsonify(create_json_response(responses.SUCCESS_200,
                                                              ResponseMessages.UPDATE_SUCCESS,
                                                              country,
                                                              Country.__name__), 200))
        else:
            session.close()
            return make_response(jsonify(create_json_response(responses.INVALID_INPUT_422,
                                                              ResponseMessages.UPDATE_FAILED,
                                                              country_data,
                                                              Country.__name__), 422))
    else:
        session.close()
        return make_response(jsonify(create_json_response(responses.UNAUTHORIZED_403,
                                                          ResponseMessages.UPDATE_NOT_AUTHORIZED,
                                                          user_data), 403))


@main.route('/discover/country', methods=['GET'])
def list_country():

    session = Session()

    res = session.query(Country).all()
    if res is None:
        return make_response(jsonify(create_json_response(responses.INVALID_INPUT_422,
                                                          ResponseMessages.LIST_EMPTY,
                                                          None,
                                                          Country.__name__), 422))
    schema = CountrySchema(many=True, only=(str(CountryAttributes.NAME), str(CountryAttributes.ID)))
    countries = schema.dump(res)

    return make_response(jsonify(create_json_response(responses.SUCCESS_200,
                                                      ResponseMessages.LIST_SUCCESS,
                                                      countries,
                                                      Country.__name__), 200))
