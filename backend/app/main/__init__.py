import ast
import base64
import os
import sqlalchemy as sql

from flask import Blueprint, request as rq, send_file
from sqlalchemy import or_

from app.auth import http_auth
from app.entities.entity import Session
from app.entities.hike_relations import HikeRelation
from app.entities.user import Permission, User
from app.entities.country import Country
from app.entities.region import Region
from app.entities.activity_type import ActivityType
from app.entities.location_activity import LocationActivity
from app.entities.activity import Activity, ActivityAttributes
from app.entities.location import Location, LocationAttributes
from app.entities.comment import Comment, CommentAttributes
from app.main.error_handling import investigate_integrity_error
from app.utils import responses
from app.utils.responses import ResponseMessages, create_response
from app.utils.helpers import distance_between_coordinates, sort_by_dist
from config import Config

main = Blueprint('main', __name__)


def get_main_app():
    return main


def sort_dict(items):
    return {k: v for k, v in sorted(items, key=lambda item: item[1], reverse=True)}


def check_integrity_error(ie, session, class_type):
    session.rollback()
    session.expunge_all()
    session.close()

    msg = investigate_integrity_error(ie)
    if msg is not None:

        return create_response(msg, responses.INVALID_INPUT_422, ResponseMessages.CREATE_DUPLICATE_PARAMS,
                               class_type.__name__, 422)

    else:
        return None


def count(user, class_type, **kwargs):
    session = Session()
    res = None

    if user not in session:
        user = session.query(User).get(user.id)

    if user is not None and user.can(Permission.READ):

        count = session.query(class_type).filter_by(**kwargs).count()
        res = count
        return create_response(res, responses.SUCCESS_200, ResponseMessages.FIND_SUCCESS, class_type, 200)

    else:
        return create_response(res, responses.UNAUTHORIZED_403, ResponseMessages.FIND_NOT_AUTHORIZED, class_type, 403)


@main.route('/find_tour', methods=['GET'])
@http_auth.login_required
def find_tour():
    session = Session()
    user = http_auth.current_user

    curr_lat = round(float(rq.args.get('lat')), 3)
    curr_long = round(float(rq.args.get('long')), 3)
    max_dist = int(rq.args.get('dist'))

    if user not in session:
        user = session.query(User).get(user.id)

    if user is not None and user.can(Permission.READ):

        if curr_lat:
            record_location = session.query(Location) \
                .filter(Location.lat > curr_lat - 3 * max_dist / 100,
                        Location.lat < curr_lat + 3 * max_dist / 100,
                        Location.long > curr_long - 3 * max_dist / 100,
                        Location.long < curr_long + 3 * max_dist / 100) \
                .all()
        else:
            return create_response(None, responses.MISSING_PARAMETER_422, ResponseMessages.FIND_MISSING_PARAMETER,
                                   Location.__name__, 422)

        schema = Location.get_schema(many=True, only=(str(LocationAttributes.NAME),
                                                      str(LocationAttributes.LATITUDE),
                                                      str(LocationAttributes.LONGITUDE),
                                                      str(LocationAttributes.ID)))
        locations = schema.dump(record_location)

        if record_location is None:
            return create_response(None, responses.BAD_REQUEST_400, ResponseMessages.FIND_NO_RESULTS,
                                   Activity.__name__, 400)
        else:

            for i, loc in enumerate(locations):
                loc.update({"dist": distance_between_coordinates(loc["lat"], loc["long"],
                                                                 curr_lat, curr_long)})
            locations = [i for i in locations if i['dist'] < max_dist]
            locations.sort(key=sort_by_dist)
            locations = dict((item['id'], item) for item in locations)

            record_activities = session.query(Activity) \
                .join(ActivityType) \
                .join(LocationActivity) \
                .join(Location).join(Region) \
                .join(Country) \
                .filter(Location.id.in_(locations.keys())) \
                .all()

            activities = [a.convert_to_presentation_schema(only=(str(ActivityAttributes.NAME),
                                                                 str(ActivityAttributes.ID)
                                                                 ),
                                                           **{
                                                               'location': [loc.location.name
                                                                            for loc in a.locations
                                                                            if locations.get(loc.location_id)][0],
                                                               'region': [loc.location.region.name
                                                                          for loc in a.locations
                                                                          if locations.get(loc.location_id)][0],
                                                               'distance': [locations.get(loc.location_id)['dist']
                                                                            for loc in a.locations
                                                                            if locations.get(loc.location_id)][0]
                                                           }
                                                           ) for a in record_activities]

            activities = sorted(activities, key=lambda k: k['distance'])

            # keep only one entry per activity
            activity_names = set()
            idx_to_keep = []
            for idx, item in enumerate(activities):

                if item["name"] not in activity_names:
                    activity_names.add(item["name"])
                    idx_to_keep.append(idx)

            activities = [activities[i] for i in idx_to_keep]
            if len(activities) > 0:
                return create_response(activities, responses.SUCCESS_200,
                                       ResponseMessages.FIND_SUCCESS, Activity.__name__, 200)
            else:
                return create_response([], responses.BAD_REQUEST_400, ResponseMessages.FIND_NO_RESULTS,
                                       Activity.__name__, 400)

    else:
        return create_response([], responses.UNAUTHORIZED_403, ResponseMessages.FIND_NOT_AUTHORIZED,
                               Activity.__name__, 403)


@main.route('/find_tour_by_term/<term>', methods=['GET'])
@http_auth.login_required
def find_tour_by_term(term):
    session = Session()
    user = http_auth.current_user

    if user not in session:
        user = session.query(User).get(user.id)

    if user is not None and user.can(Permission.READ):

        search_term = '%{}%'.format(term)
        record_activities = session.query(Activity).filter(or_(Activity.name.ilike(search_term),
                                                               Activity.description.ilike(search_term))).all()

        if record_activities is None:
            return create_response(None, responses.BAD_REQUEST_400, ResponseMessages.FIND_NO_RESULTS,
                                   Activity.__name__, 400)
        else:

            activities = [act.convert_to_presentation_schema(only=(str(ActivityAttributes.NAME),
                                                                   str(ActivityAttributes.ID)
                                                                   ),
                                                             **{
                                                                 'location': act.get_location(0, output='name'),
                                                                 'region': act.get_region(0, output='name'),
                                                                 'country_short': act.get_country(0,
                                                                                                  output='abbreviation')
                                                             }
                                                             ) for act in record_activities]

            return create_response(activities, responses.SUCCESS_200, ResponseMessages.FIND_SUCCESS,
                                   Activity.__name__, 200)

    else:
        return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.FIND_NOT_AUTHORIZED,
                               Activity.__name__, 403)


@main.route('/find_tour_by_area/<data_encoded>', methods=['GET'])
@http_auth.login_required
def find_tour_by_area(data_encoded):

    data_string = base64.b64decode(data_encoded).decode()
    data = ast.literal_eval(data_string)

    keys = data.get('keys')
    output = data.get('output')
    order_by = data.get('order_by')

    order_column = getattr(Activity, order_by.get('column'))
    order_func = getattr(sql, order_by.get('dir'))

    session = Session()
    res = session.query(Activity) \
        .join(LocationActivity) \
        .join(Location) \
        .join(Region) \
        .filter_by(**keys) \
        .order_by(Activity.id.asc() if order_by is None else order_func(order_column)) \
        .all()

    activities = [r.convert_to_presentation_schema(only=output, **{
        'location': r.get_location(idx=0, output='name'),
        'region': r.get_region(idx=0, output='name'),

    }) for r in res]

    session.expunge_all()
    session.close()

    return create_response(activities, responses.SUCCESS_200, ResponseMessages.FIND_SUCCESS, Activity.__name__, 200)


@main.route('/hike/<act_id>', methods=['GET'])
@http_auth.login_required
def add_hike(act_id):
    session = Session()
    user = http_auth.current_user
    res = None

    typ = rq.args.get('typ')

    if user not in session:
        user = session.query(User).get(user.id)

    activity = session.query(Activity).filter(Activity.id == act_id).first()

    if activity is None:
        session.expunge_all()
        session.close()
        return create_response(None, responses.BAD_REQUEST_400, ResponseMessages.MAIN_NO_DATA,
                               HikeRelation.__name__, 400)

    if user is not None and user.can(Permission.FOLLOW) and typ is not None:

        if typ == 'add':
            hike = user.add_hike(activity, session)
            res = hike.serialize()
        elif typ == 'check':
            res = True if user.has_hiked(activity) is True else False
        elif typ == 'rem':
            user.delete_hike(activity, session)

        session.expunge_all()
        session.close()
        return create_response(res, responses.SUCCESS_201, ResponseMessages.CREATE_SUCCESS, HikeRelation.__name__, 201)

    else:
        session.expunge_all()
        session.close()
        return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.CREATE_NOT_AUTHORIZED,
                               HikeRelation.__name__, 403)


@main.route('/find/comment/<act_id>')
@http_auth.login_required
def find_comment_by_act(act_id):
    session = Session()
    res = None

    user = http_auth.current_user

    if user not in session:
        user = session.query(User).get(user.id)

    if user is not None and user.can(Permission.READ):
        entities = session.query(Comment) \
            .filter(Comment.activity_id == act_id) \
            .filter(Comment.author_id == User.id) \
            .all()

        if entities is not None:
            res = [e.convert_to_presentation_schema(only=(str(CommentAttributes.ID),
                                                          str(CommentAttributes.BODY),
                                                          str(CommentAttributes.UPDATED_AT)),
                                                    **{
                                                        'author': e.get_author()
                                                    }) for e in entities]
            session.expunge_all()
            session.close()
            return create_response(res, responses.SUCCESS_200, ResponseMessages.FIND_SUCCESS, Comment, 200)
    else:
        session.expunge_all()
        session.close()
        return create_response(res, responses.INVALID_INPUT_422, ResponseMessages.FIND_MISSING_PARAMETER, Comment, 422)


@main.route('/file/<act_id>', methods=['GET'])
@http_auth.login_required
def get_file(act_id):
    session = Session()
    res = None

    user = http_auth.current_user

    if user not in session:
        user = session.query(User).get(user.id)

    if user is not None and user.can(Permission.READ):

        activity = session.query(Activity).get(act_id)

        path_to_file = os.path.join(Config.PATH_PDF_STORAGE, activity.save_path)

        return send_file(path_to_file, as_attachment=True)
    else:
        return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.FIND_NOT_AUTHORIZED, Activity, 403)


@main.route('test')
def test():
    session = Session()

    act = session.query(Activity).get(88)

    return create_response(act.country_all(output='name'), None, None, None, 200)
