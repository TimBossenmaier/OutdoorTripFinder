from flask import Blueprint, request, make_response, jsonify
from sqlalchemy.exc import IntegrityError

from ..entities.entity import Session
from ..entities.user import UserAttributes, User, Permission
from ..entities.country import Country
from ..entities.region import Region
from ..main.error_handling import investigate_integrity_error
from ..utils import responses
from ..utils.responses import create_json_response, ResponseMessages

main = Blueprint('main', __name__)


def get_main_app():
    return main


def extract_json_data(req, class_type):
    user_data = req.get_json()["user"]
    data = req.get_json()[class_type.__name__.lower()]

    return user_data, data


def extract_user(user_data, session, class_type):

    if user_data.get(str(UserAttributes.USERNAME)):
        user = session.query(User).filter_by(username=user_data.get(str(UserAttributes.USERNAME))).first()
    else:
        session.close()
        return make_response(jsonify(create_json_response(responses.MISSING_PARAMETER_422,
                                                          ResponseMessages.CREATE_MISSING_PARAM,
                                                          user_data,
                                                          class_type.__name__), 422))

    return user


def check_integrity_error(ie, session, class_type):

    session.rollback()
    session.close()

    msg = investigate_integrity_error(ie)
    if msg is not None:
        return make_response(jsonify(create_json_response(responses.INVALID_INPUT_422,
                                                          ResponseMessages.CREATE_DUPLICATE_PARAMS,
                                                          msg,
                                                          class_type.__name__), 422))

    else:
        return None


def create(req, class_type):

    user_data, data = extract_json_data(req, class_type)

    session = Session()

    expected_user = extract_user(user_data, session, class_type)

    if isinstance(expected_user, User):
        user = expected_user
    else:
        resp = expected_user
        return resp

    if user is not None and user.can(Permission.CREATE):
        data.update({'created_by': user.id})
        schema = class_type.get_insert_schema()

        class_instance = class_type(**schema.load(data))

        try:
            res = schema.dump(class_instance.create(session))

        except IntegrityError as ie:

            check_result = check_integrity_error(ie, session, class_type)

            if check_result is None:
                pass
            else:
                resp = check_result
                return resp

        finally:
            session.close()

        return make_response(jsonify(create_json_response(responses.SUCCESS_201,
                                                          ResponseMessages.CREATE_SUCCESS,
                                                          res,
                                                          class_type.__name__), 201))
    else:
        return make_response(jsonify(create_json_response(responses.UNAUTHORIZED_403,
                                                          ResponseMessages.CREATE_NOT_AUTHORIZED,
                                                          user_data), 403))


def update(req, class_type):

    user_data, data = extract_json_data(req, class_type)

    session = Session()
    expected_user = extract_user(user_data, session, class_type)

    if isinstance(expected_user, User):
        user = expected_user
    else:
        resp = expected_user
        return resp

    if user is not None and user.can(Permission.CREATE):
        entity = session.query(class_type).filter_by(id=data.get(str(class_type.get_attributes().ID))).first()
        if entity is not None:

            try:
                entity.update(session, user.id, **data)
            except IntegrityError as ie:

                check_result = check_integrity_error(ie, session, class_type)

                if check_result is None:
                    pass
                else:
                    resp = check_result
                    return resp

            finally:
                    res = entity.convert_to_insert_schema()
                    session.close()
            return make_response(jsonify(create_json_response(responses.SUCCESS_200,
                                                              ResponseMessages.UPDATE_SUCCESS,
                                                              res,
                                                              class_type.__name__), 200))
        else:
            session.close()
            return make_response(jsonify(create_json_response(responses.INVALID_INPUT_422,
                                                              ResponseMessages.UPDATE_FAILED,
                                                              data,
                                                              class_type.__name__), 422))
    else:
        session.close()
        return make_response(jsonify(create_json_response(responses.UNAUTHORIZED_403,
                                                          ResponseMessages.UPDATE_NOT_AUTHORIZED,
                                                          user_data), 403))


def list_all(class_type):

    session = Session()

    res = session.query(class_type).all()
    if res is None:
        return make_response(jsonify(create_json_response(responses.INVALID_INPUT_422,
                                                          ResponseMessages.LIST_EMPTY,
                                                          None,
                                                          class_type.__name__), 422))
    attributes = class_type.get_attributes()
    schema = class_type.get_schema(many=True, only=(str(attributes.NAME), str(attributes.ID)))
    entities = schema.dump(res)

    return make_response(jsonify(create_json_response(responses.SUCCESS_200,
                                                      ResponseMessages.LIST_SUCCESS,
                                                      entities,
                                                      Country.__name__), 200))


@main.route('/create/country', methods=['GET', 'POST'])
def create_country():

    resp = create(request, Country)

    return resp


@main.route('create/region', methods=['GET', 'POST'])
def create_region():

    resp = create(request, Region)

    return resp


@main.route('/update/country', methods=['GET', 'POST'])
def update_country():

    resp = update(request, Country)

    return resp


@main.route('update/region', methods=['GET', 'POST'])
def update_region():

    res = update(request, Region)

    return res

@main.route('/list/country', methods=['GET'])
def list_country():

    res = list_all(Country)

    return res


@main.route('list/region', methods=['GET'])
def list_region():

    res = list_all(Region)

    return res