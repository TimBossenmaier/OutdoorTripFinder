import ast
import base64

from flask import Blueprint

from app.auth import http_auth
from app.entities.activity import Activity, ActivityAttributes
from app.entities.activity_type import ActivityType
from app.entities.country import Country
from app.entities.entity import Session
from app.entities.location import Location
from app.entities.location_type import LocationType
from app.entities.region import Region
from app.entities.role import Permission
from app.entities.user import User
from app.utils import responses
from app.utils.responses import create_response, ResponseMessages

find = Blueprint('find', __name__)


def by_id(user, id, classtype, data_encoded):
    session = Session()
    res = None

    data_string = base64.b64decode(data_encoded).decode()
    data = ast.literal_eval(data_string)

    output = data.get('output')

    if user not in session:
        user = session.query(User).get(user.id)

    if user is not None and user.can(Permission.READ):
        entity = session.query(classtype).get(id)

        if entity is not None:
            if classtype == Activity:
                res = entity.convert_to_presentation_schema(only=output,
                                                            **{
                                                                'activity_type': entity.get_activity_type(session, output='name'),
                                                                'locations': entity.get_location_all(output='name'),
                                                                'location_types': entity.get_location_type_all(),
                                                                'countries': entity.get_country_all(output='abbreviation')
                                                            })
            else:
                res = entity.convert_to_presentation_schema(only=output)
            session.expunge_all()
            session.close()
            return create_response(res, responses.SUCCESS_200, ResponseMessages.LIST_SUCCESS, classtype.__name__, 200)
        else:
            session.expunge_all()
            session.close()
            return create_response(res, responses.INVALID_INPUT_422, ResponseMessages.LIST_INVALID_INPUT,
                                   classtype.__name__, 200)


@find.route('/country/<identifier>/<data>', methods=['GET'])
@http_auth.login_required()
def country_by_id(identifier, data):
    res = by_id(user=http_auth.current_user, id=identifier, classtype=Country, data_encoded=data)

    return res


@find.route('/region/<identifier>/<data>', methods=['GET'])
@http_auth.login_required()
def region_by_id(identifier, data):
    res = by_id(user=http_auth.current_user, id=identifier, classtype=Region, data_encoded=data)

    return res


@find.route('/location_type/<identifier>/<data>', methods=['GET'])
@http_auth.login_required()
def location_type_by_id(identifier, data):
    res = by_id(user=http_auth.current_user, id=identifier, classtype=LocationType, data_encoded=data)

    return res


@find.route('/activity_type/<identifier>/<data>', methods=['GET'])
@http_auth.login_required()
def activity_type_by_id(identifier, data):
    res = by_id(user=http_auth.current_user, id=identifier, classtype=ActivityType, data_encoded=data)

    return res


@find.route('/location/<identifier>/<data>', methods=['GET'])
@http_auth.login_required()
def location_by_id(identifier, data):
    res = by_id(user=http_auth.current_user, id=identifier, classtype=Location, data_encoded=data)

    return res


@find.route('/activity/<identifier>/<data>', methods=['GET'])
@http_auth.login_required()
def activity_by_id(identifier, data):
    res = by_id(user=http_auth.current_user, id=identifier, classtype=Activity, data_encoded=data)
    return res
