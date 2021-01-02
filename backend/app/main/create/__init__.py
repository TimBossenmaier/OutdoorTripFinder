from flask import Blueprint, request as rq
from sqlalchemy.exc import IntegrityError

from app.auth import http_auth
from app.entities.activity import Activity
from app.entities.activity_type import ActivityType
from app.entities.comment import Comment
from app.entities.country import Country
from app.entities.entity import Session
from app.entities.location import Location
from app.entities.location_activity import LocationActivity
from app.entities.location_type import LocationType
from app.entities.region import Region
from app.entities.role import Permission
from app.entities.user import User
from app.main import check_integrity_error
from app.utils import responses
from app.utils.responses import create_response, ResponseMessages

crt = Blueprint('create', __name__)


def create(data, user, class_type):
    session = Session()

    if user not in session:
        user = session.query(User).get(user.id)

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
            session.expunge_all()
            session.close()

        return create_response(res, responses.SUCCESS_201, ResponseMessages.CREATE_SUCCESS, class_type.__name__, 201)
    else:
        session.expunge_all()
        session.close()
        return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.CREATE_NOT_AUTHORIZED,
                               class_type.__name__, 403)


@crt.route('/country', methods=['POST'])
@http_auth.login_required
def create_country():
    resp = create(data=rq.get_json(), user=http_auth.current_user, class_type=Country)

    return resp


@crt.route('/region', methods=['POST'])
@http_auth.login_required
def create_region():
    resp = create(data=rq.get_json(), user=http_auth.current_user, class_type=Region)

    return resp


@crt.route('/location_type', methods=['POST'])
@http_auth.login_required
def create_location_type():
    resp = create(data=rq.get_json(), user=http_auth.current_user, class_type=LocationType)

    return resp


@crt.route('/activity_type', methods=['POST'])
@http_auth.login_required
def create_activity_type():
    resp = create(data=rq.get_json(), user=http_auth.current_user, class_type=ActivityType)

    return resp


@crt.route('/location_activity', methods=['POST'])
@http_auth.login_required
def create_activity_location():
    resp = create(data=rq.get_json(), user=http_auth.current_user, class_type=LocationActivity)

    return resp


@crt.route('/activity', methods=['POST'])
@http_auth.login_required
def create_activity():
    resp = create(data=rq.get_json(), user=http_auth.current_user, class_type=Activity)

    return resp


@crt.route('/location', methods=['POST'])
@http_auth.login_required
def create_location():
    resp = create(data=rq.get_json(), user=http_auth.current_user, class_type=Location)

    return resp


@crt.route('/comment', methods=['POST'])
@http_auth.login_required
def create_comment():
    resp = create(data=rq.get_json(), user=http_auth.current_user, class_type=Comment)

    return resp
