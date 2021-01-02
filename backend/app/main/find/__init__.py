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


def by_id(user, id, classtype):
    session = Session()
    res = None

    if user not in session:
        user = session.query(User).get(user.id)

    if user is not None and user.can(Permission.READ):
        entity = session.query(classtype).get(id)

        if entity is not None:
            if classtype == Activity:
                res = entity.convert_to_presentation_schema(only=(str(ActivityAttributes.NAME),
                                                                  str(ActivityAttributes.ID),
                                                                  str(ActivityAttributes.DESCRIPTION),
                                                                  str(ActivityAttributes.SOURCE)),
                                                            **{
                                                                'activity_type': entity.get_activity_type(session, output='name'),
                                                                'locations': entity.get_location_all(output='name'),
                                                                'location_types': entity.get_location_type_all(),
                                                                'countries': entity.get_country_all(output='abbreviation')
                                                            })
            else:
                res = entity.convert_to_presentation_schema(only=(str(ActivityAttributes.NAME),
                                                                  str(ActivityAttributes.ID)))
            session.expunge_all()
            session.close()
            return create_response(res, responses.SUCCESS_200, ResponseMessages.LIST_SUCCESS, classtype.__name__, 200)
        else:
            session.expunge_all()
            session.close()
            return create_response(res, responses.INVALID_INPUT_422, ResponseMessages.LIST_INVALID_INPUT,
                                   classtype.__name__, 200)


@find.route('/country/<identifier>', methods=['GET'])
@http_auth.login_required()
def country_by_id(identifier):
    res = by_id(user=http_auth.current_user, id=identifier, classtype=Country)

    return res


@find.route('/region/<identifier>', methods=['GET'])
@http_auth.login_required()
def region_by_id(identifier):
    res = by_id(user=http_auth.current_user, id=identifier, classtype=Region)

    return res


@find.route('/location_type/<identifier>', methods=['GET'])
@http_auth.login_required()
def location_type_by_id(identifier):
    res = by_id(user=http_auth.current_user, id=identifier, classtype=LocationType)

    return res


@find.route('/activity_type/<identifier>', methods=['GET'])
@http_auth.login_required()
def activity_type_by_id(identifier):
    res = by_id(user=http_auth.current_user, id=identifier, classtype=ActivityType)

    return res


@find.route('/location/<identifier>', methods=['GET'])
@http_auth.login_required()
def location_by_id(identifier):
    res = by_id(user=http_auth.current_user, id=identifier, classtype=Location)

    return res


@find.route('/activity/<identifier>', methods=['GET'])
@http_auth.login_required()
def activity_by_id(identifier):
    res = by_id(user=http_auth.current_user, id=identifier, classtype=Activity)
    return res
