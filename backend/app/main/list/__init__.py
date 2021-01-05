import sqlalchemy as sql
import base64
import ast

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


def list_all(class_type, data_encoded):
    session = Session()
    res = None

    data_string = base64.b64decode(data_encoded).decode()
    data = ast.literal_eval(data_string)

    keys = data.get('keys')
    term = data.get('term')
    output = data.get('output')
    order_by = data.get('order_by')

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

    if class_type == Comment:
        authors = [r.get_author() for r in res]

    session.expunge_all()
    session.close()

    res = schema.dump(res)

    if class_type == Comment:
        [r.update({'author': authors[idx]}) for idx, r in enumerate(res)]

    return create_response(res, responses.SUCCESS_200, ResponseMessages.FIND_SUCCESS,
                           class_type.__name__, 200)


@lst.route('/country/<data>', methods=['GET'])
@http_auth.login_required
def list_country(data):

    res = list_all(Country, data_encoded=data)

    return res


@lst.route('/region/<data>', methods=['GET'])
@http_auth.login_required
def list_region(data):

    res = list_all(Region, data_encoded=data)

    return res


@lst.route('/location_type/<data>', methods=['GET'])
@http_auth.login_required
def list_location_type(data):

    res = list_all(LocationType, data_encoded=data)

    return res


@lst.route('/activity_type/<data>', methods=['GET'])
@http_auth.login_required
def list_activity_type(data):

    res = list_all(ActivityType, data_encoded=data)

    return res


@lst.route('/location_activity/<data>', methods=['GET'])
@http_auth.login_required
def list_location_activity(data):

    res = list_all(LocationActivity, data_encoded=data)

    return res


@lst.route('/activity/<data>', methods=['GET'])
@http_auth.login_required
def list_activity(data):

    res = list_all(Activity, data_encoded=data)

    return res


@lst.route('/location/<data>', methods=['GET'])
@http_auth.login_required
def list_location(data):

    res = list_all(Location, data_encoded=data)

    return res


@lst.route('/comment/<data>', methods=['GET'])
@http_auth.login_required
def list_comment(data):

    res = list_all(Comment, data_encoded=data)

    return res


@lst.route('/hikerelation/<data>', methods=['GET'])
@http_auth.login_required
def list_hikerelation(data):

    res = list_all(HikeRelation, data_encoded=data)

    return res
