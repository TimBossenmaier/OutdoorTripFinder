import sqlalchemy as sql

from flask import Blueprint, request as rq

from app.auth import http_auth
from app.entities.activity import Activity
from app.entities.activity_type import ActivityType
from app.entities.comment import Comment
from app.entities.country import Country
from app.entities.entity import Session
from app.entities.hike_relations import HikeRelation
from app.entities.location import Location
from app.entities.location_activity import LocationActivity
from app.entities.location_type import LocationType
from app.entities.region import Region
from app.utils import responses
from app.utils.responses import create_response, ResponseMessages

lst = Blueprint('list', __name__)


def list_all(class_type, rq):
    session = Session()
    res = None

    keys = rq.get_json().get('keys')
    term = rq.get_json().get('term')
    output = rq.get_json().get('output')
    order_by = rq.get_json().get('order_by')

    order_column = getattr(class_type, order_by.get('column'))
    order_func = getattr(sql, order_by.get('dir'))

    if term is not None and keys is None:
        search_term = '%{}%'.format(term)

        res = session \
            .query(class_type) \
            .filter(class_type.name.ilike(search_term)) \
            .order_by(class_type.id.asc() if order_by is None else order_func(order_column)) \
            .all()
    elif term is not None and keys is not None:
        search_term = '%{}%'.format(term)

        res = session \
            .query(class_type) \
            .filter(class_type.name.ilike(search_term)) \
            .filter_by(**keys)\
            .order_by(class_type.id.asc() if order_by is None else order_func(order_column)) \
            .all()

    elif keys is not None:
        res = session \
            .query(class_type) \
            .filter_by(**keys) \
            .order_by(class_type.id.asc() if order_by is None else order_func(order_column)) \
            .all()
    else:
        res = session\
            .query(class_type)\
            .order_by(class_type.id.asc() if order_by is None else order_func(order_column))\
            .all()

    schema = class_type.get_schema(many=True, only=output)

    session.expunge_all()
    session.close()

    return create_response(schema.dump(res), responses.SUCCESS_200, ResponseMessages.FIND_SUCCESS,
                           class_type.__name__, 200)


@lst.route('/country', methods=['POST'])
@http_auth.login_required
def list_country():

    res = list_all(Country, rq)

    return res


@lst.route('/region', methods=['POST'])
@http_auth.login_required
def list_region():

    res = list_all(Region, rq)

    return res


@lst.route('/location_type', methods=['POST'])
@http_auth.login_required
def list_location_type():

    res = list_all(LocationType, rq)

    return res


@lst.route('/activity_type', methods=['POST'])
@http_auth.login_required
def list_activity_type():

    res = list_all(ActivityType, rq)

    return res


@lst.route('/location_activity', methods=['POST'])
@http_auth.login_required
def list_location_activity():

    res = list_all(LocationActivity, rq)

    return res


@lst.route('/activity', methods=['POST'])
@http_auth.login_required
def list_activity():

    res = list_all(Activity, rq)

    return res


@lst.route('/location', methods=['POST'])
@http_auth.login_required
def list_location():

    res = list_all(Location, rq)

    return res


@lst.route('/comment', methods=['POST'])
@http_auth.login_required
def list_comment():

    res = list_all(Comment, rq)

    return res


@lst.route('/list/hikerelation', methods=['POST'])
@http_auth.login_required
def list_hikerelation():

    res = list_all(HikeRelation, rq)

    return res
