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

updt = Blueprint('update', __name__)


def update(data, user, class_type):
    session = Session()

    if user not in session:
        user = session.query(User).get(user.id)

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
                session.expunge_all()
                session.close()
            return create_response(res, responses.SUCCESS_200, ResponseMessages.UPDATE_SUCCESS,
                                   class_type.__name__, 200)

        else:
            session.expunge_all()
            session.close()
            return create_response(data, responses.INVALID_INPUT_422, ResponseMessages.UPDATE_FAILED,
                                   class_type.__name__, 422)
    else:
        session.expunge_all()
        session.close()
        return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.UPDATE_NOT_AUTHORIZED,
                               class_type.__name__, 403)


@updt.route('/country', methods=['POST'])
@http_auth.login_required
def update_country():
    resp = update(data=rq.get_json(), user=http_auth.current_user, class_type=Country)

    return resp


@updt.route('/region', methods=['POST'])
@http_auth.login_required
def update_region():
    resp = update(data=rq.get_json(), user=http_auth.current_user, class_type=Region)

    return resp


@updt.route('/location_type', methods=['POST'])
@http_auth.login_required
def update_location_type():
    resp = update(data=rq.get_json(), user=http_auth.current_user, class_type=LocationType)

    return resp


@updt.route('/activity_type', methods=['POST'])
@http_auth.login_required
def update_activity_type():
    resp = update(data=rq.get_json(), user=http_auth.current_user, class_type=ActivityType)

    return resp


@updt.route('/location_activity', methods=['POST'])
@http_auth.login_required
def update_location_activity():
    resp = update(data=rq.get_json(), user=http_auth.current_user, class_type=LocationActivity)

    return resp


@updt.route('/activity', methods=['POST'])
@http_auth.login_required
def update_activity():
    resp = update(data=rq.get_json(), user=http_auth.current_user, class_type=Activity)

    return resp


@updt.route('/location', methods=['POST'])
@http_auth.login_required
def update_location():
    resp = update(data=rq.get_json(), user=http_auth.current_user, class_type=Location)

    return resp


@updt.route('/comment', methods=['POST'])
@http_auth.login_required
def update_comment():
    resp = update(data=rq.get_json(), user=http_auth.current_user, class_type=Comment)

    return resp
