from flask import Blueprint, request as rq
from flask_cors import cross_origin
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError

from app.auth import http_auth
from app.entities.entity import Session
from app.entities.hike_relations import HikeRelation
from app.entities.user import Permission, User
from app.entities.country import Country
from app.entities.region import Region, RegionAttributes
from app.entities.location_type import LocationType
from app.entities.activity_type import ActivityType
from app.entities.location_activity import LocationActivity
from app.entities.activity import Activity, ActivityAttributes
from app.entities.location import Location, LocationAttributes
from app.entities.comment import Comment
from app.main.error_handling import investigate_integrity_error
from app.utils import responses
from app.utils.responses import ResponseMessages, create_response
from app.utils.helpers import distance_between_coordinates, sort_by_dist

main = Blueprint('main', __name__)


def get_main_app():
    return main


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


def create(req, user, class_type):
    session = Session()
    data = req.get_json()

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
                               class_type.__name__, 201)


def update(req, user, class_type):
    session = Session()
    data = req.get_json()

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
                                                                'activity_type': entity.activity_type.name
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


def list_all(class_type, keys, typ, term=''):
    session = Session()
    res = None

    if term != '' and keys is None:
        search_term = '%{}%'.format(term)
        res = session.query(class_type).filter(class_type.name.ilike(search_term)).order_by(class_type.id.asc()).all()
    elif term == '' and keys is not None:

        if class_type == Country:
            session.expunge_all()
            session.close()
            return create_response(keys, responses.INVALID_INPUT_422, ResponseMessages.LIST_INVALID_INPUT,
                                   class_type.__name__, 422)
        else:
            if keys.get(
                    str(RegionAttributes.COUNTRY_ID)
                    if class_type == Region
                    else str(LocationAttributes.REGION_ID)):
                res = session.query(Region if class_type == Region else Location).filter(
                    Region.country_id.in_(keys.get(str(RegionAttributes.COUNTRY_ID)))
                    if class_type == Region else
                    Location.region_id.in_(keys.get(str(LocationAttributes.REGION_ID)))) \
                    .order_by(class_type.id.asc()) \
                    .all()
            else:
                session.expunge_all()
                session.close()
                return create_response(keys, responses.INVALID_INPUT_422, ResponseMessages.LIST_INVALID_INPUT,
                                       class_type.__name__, 422)

    elif term != '' and keys is not None:

        if class_type == Country:
            session.expunge_all()
            session.close()
            return create_response(keys, responses.INVALID_INPUT_422, ResponseMessages.LIST_INVALID_INPUT,
                                   class_type.__name__, 422)
        else:
            if keys.get(
                    str(RegionAttributes.COUNTRY_ID) if class_type == Region else str(LocationAttributes.REGION_ID)):
                search_term = '%{}%'.format(term)
                if keys.get(str(RegionAttributes.COUNTRY_ID)) is not None:
                    res = session.query(Region).filter(
                        and_(
                            Region.country_id.in_(list(keys.get(str(RegionAttributes.COUNTRY_ID)))),
                            Region.name.ilike(search_term))
                    ) \
                        .order_by(class_type.id.asc()) \
                        .all()
                elif keys.get(str(LocationAttributes.REGION_ID)) is not None:
                    res = session.query(Location).filter(
                        and_(
                            Location.region_id.in_(keys.get(str(LocationAttributes.REGION_ID))),
                            Location.name.ilike(search_term))
                    ) \
                        .order_by(class_type.id.asc()) \
                        .all()
            else:
                session.expunge_all()
                session.close()
                return create_response(keys, responses.INVALID_INPUT_422, ResponseMessages.LIST_INVALID_INPUT,
                                       class_type.__name__, 422)
    elif typ is not None:
        if class_type == Location and typ.get(str(LocationAttributes.LOCATION_TYPE_ID)):
            res = session.query(Location) \
                .filter(Location.location_type_id == typ.get(str(LocationAttributes.LOCATION_TYPE_ID))) \
                .order_by(class_type.id.asc()) \
                .all()
        elif class_type == Activity and typ.get(str(ActivityAttributes.ACTIVITY_TYPE_ID)):
            res = session.query(Activity) \
                .filter(Activity.activity_type_id == typ.get(str(ActivityAttributes.ACTIVITY_TYPE_ID))) \
                .order_by(class_type.id.asc()) \
                .all()
        else:
            session.expunge_all()
            session.close()
            return create_response(typ, responses.INVALID_INPUT_422, ResponseMessages.LIST_INVALID_INPUT,
                                   class_type.__name__, 422)
    else:
        res = session.query(class_type).order_by(class_type.id.asc()).all()

    if res is None:
        session.expunge_all()
        session.close()
        return create_response(None, responses.INVALID_INPUT_422, ResponseMessages.LIST_EMPTY, class_type.__name__, 422)
    else:
        attributes = class_type.get_attributes()
        if class_type == LocationActivity:
            schema = LocationActivity.get_schema(many=True, only=[str(attributes.ID),
                                                                  str(attributes.ACTIVITY_ID),
                                                                  str(attributes.LOCATION_ID)])
        elif class_type == HikeRelation:
            schema = HikeRelation.get_schema(many=True, only=(str(attributes.ID),
                                                              str(attributes.USER_ID),
                                                              str(attributes.ACTIVITY_ID)))
        elif class_type == Comment:
            schema = Comment.get_schema(many=True, only=(str(attributes.ID),
                                                         str(attributes.BODY),
                                                         str(attributes.AUTHOR_ID),
                                                         str(attributes.ACTIVITY_ID)))
        else:
            schema = class_type.get_schema(many=True,
                                           only=((str(attributes.NAME), str(attributes.ID), str(attributes.REGION_ID))
                                                 if class_type == Location
                                                 else (str(attributes.NAME), str(attributes.ID))))
        entities = schema.dump(res)

        session.expunge_all()
        session.close()
        return create_response(entities, responses.SUCCESS_200, ResponseMessages.LIST_SUCCESS, class_type.__name__, 200)


@main.route('/create/country', methods=['GET', 'POST'])
@http_auth.login_required
def create_country():
    resp = create(req=rq, user=http_auth.current_user, class_type=Country)

    return resp


@main.route('/create/region', methods=['GET', 'POST'])
@http_auth.login_required
def create_region():
    resp = create(req=rq, user=http_auth.current_user, class_type=Region)

    return resp


@main.route('/create/location_type', methods=['GET', 'POST'])
@http_auth.login_required
def create_location_type():
    resp = create(req=rq, user=http_auth.current_user, class_type=LocationType)

    return resp


@main.route('/create/activity_type', methods=['GET', 'POST'])
@http_auth.login_required
def create_activity_type():
    resp = create(req=rq, user=http_auth.current_user, class_type=ActivityType)

    return resp


@main.route('/create/location_activity', methods=['GET', 'POST'])
@http_auth.login_required
def create_activity_location():
    resp = create(req=rq, user=http_auth.current_user, class_type=LocationActivity)

    return resp


@main.route('/create/activity', methods=['GET', 'POST'])
@http_auth.login_required
def create_activity():
    resp = create(req=rq, user=http_auth.current_user, class_type=Activity)

    return resp


@main.route('/create/location', methods=['GET', 'POST'])
@http_auth.login_required
def create_location():
    resp = create(req=rq, user=http_auth.current_user, class_type=Location)

    return resp


@main.route('/create/comment', methods=["GET", "POST"])
@http_auth.login_required
def create_comment():
    resp = create(req=rq, user=http_auth.current_user, class_type=Comment)

    return resp


@main.route('/update/country', methods=['GET', 'POST'])
@http_auth.login_required
def update_country():
    resp = update(req=rq, user=http_auth.current_user, class_type=Country)

    return resp


@main.route('/update/region', methods=['GET', 'POST'])
@http_auth.login_required
def update_region():
    resp = update(req=rq, user=http_auth.current_user, class_type=Region)

    return resp


@main.route('/update/location_type', methods=['GET', 'POST'])
@http_auth.login_required
def update_location_type():
    resp = update(req=rq, user=http_auth.current_user, class_type=LocationType)

    return resp


@main.route('/update/activity_type', methods=['GET', 'POST'])
@http_auth.login_required
def update_activity_type():
    resp = update(req=rq, user=http_auth.current_user, class_type=ActivityType)

    return resp


@main.route('/update/location_activity', methods=['GET', 'POST'])
@http_auth.login_required
def update_location_activity():
    resp = update(req=rq, user=http_auth.current_user, class_type=LocationActivity)

    return resp


@main.route('/update/activity', methods=['GET', 'POST'])
@http_auth.login_required
def update_activity():
    resp = update(req=rq, user=http_auth.current_user, class_type=Activity)

    return resp


@main.route('/update/location', methods=['GET', 'POST'])
@http_auth.login_required
def update_location():
    resp = update(req=rq, user=http_auth.current_user, class_type=Location)

    return resp


@main.route('/update/comment', methods=['GET', 'POST'])
@http_auth.login_required
def update_comment():
    resp = update(req=rq, user=http_auth.current_user, class_type=Comment)

    return resp


@main.route('/list/country', methods=['GET'])
@http_auth.login_required
def list_country():
    res = list_all(Country)

    return res


@main.route('/list/country', methods=['GET'])
@http_auth.login_required
def list_country_param():
    res = list_all(Country, keys=rq.args.get('keys'), typ=rq.args.get('typ'), term=rq.args.get('term'))

    return res


@main.route('/list/region', methods=['GET'])
@http_auth.login_required
def list_region():
    res = list_all(Region)

    return res


@main.route('/list/region', methods=['GET'])
@http_auth.login_required
def list_region_param():
    res = list_all(Region, keys=rq.args.get('keys'), typ=rq.args.get('typ'), term=rq.args.get('term'))

    return res


@main.route('/list/location_type', methods=['GET'])
@http_auth.login_required
def list_location_type():
    res = list_all(LocationType)

    return res


@main.route('/list/location_type', methods=['GET'])
@http_auth.login_required
def list_location_type_param():
    res = list_all(LocationType, keys=rq.args.get('keys'), typ=rq.args.get('typ'), term=rq.args.get('term'))

    return res


@main.route('/list/activity_type', methods=['GET'])
@http_auth.login_required
def list_activity_type():
    res = list_all(ActivityType)

    return res


@main.route('/list/activity_type', methods=['GET'])
@http_auth.login_required
def list_activity_type_param():
    res = list_all(ActivityType, keys=rq.args.get('keys'), typ=rq.args.get('typ'), term=rq.args.get('term'))

    return res


@main.route('/list/location_activity', methods=['GET'])
@http_auth.login_required
def list_location_activity():
    res = list_all(LocationActivity)

    return res


@main.route('/list/activity', methods=['GET'])
@http_auth.login_required
def list_activity():
    res = list_all(Activity)

    return res


@main.route('/list/activity', methods=['GET'])
@http_auth.login_required
def list_activity_param():
    res = list_all(Activity, keys=rq.args.get('keys'), typ=rq.args.get('typ'), term=rq.args.get('term'))

    return res


@main.route('/list/location', methods=['GET'])
@http_auth.login_required
def list_location_param():
    res = list_all(Location, keys=rq.args.get('keys'), typ=rq.args.get('typ'), term=rq.args.get('term'))

    return res


@main.route('/list/location', methods=['GET'])
@http_auth.login_required
def list_location():
    res = list_all(Location)

    return res


@main.route('/list/comment', methods=['GET'])
@http_auth.login_required
def list_comment():
    res = list_all(Comment)

    return res


@main.route('/list/hikerelation', methods=['GET'])
@http_auth.login_required
def list_hikerelation():
    res = list_all(HikeRelation)

    return res


@main.route('/country/<id>', methods=['GET'])
@http_auth.login_required()
def country_by_id(id):
    res = by_id(user=http_auth.current_user, id=id, classtype=Country)

    return res


@main.route('/region/<id>', methods=['GET'])
@http_auth.login_required()
def region_by_id(id):
    res = by_id(user=http_auth.current_user, id=id, classtype=Region)

    return res


@main.route('/location_type/<id>', methods=['GET'])
@http_auth.login_required()
def location_type_by_id(id):
    res = by_id(user=http_auth.current_user, id=id, classtype=LocationType)

    return res


@main.route('/activity_type/<id>', methods=['GET'])
@http_auth.login_required()
def activity_type_by_id(id):
    res = by_id(user=http_auth.current_user, id=id, classtype=ActivityType)

    return res


@main.route('/location/<id>', methods=['GET'])
@http_auth.login_required()
def location_by_id(id):
    res = by_id(user=http_auth.current_user, id=id, classtype=Location)

    return res


@main.route('/activity/<id>', methods=['GET'])
@http_auth.login_required()
def activity_by_id(id):
    res = by_id(user=http_auth.current_user, id=id, classtype=Activity)
    return res


@main.route('/find_tour', methods=['GET'])
@http_auth.login_required
def find_tour():
    session = Session()
    user = http_auth.current_user

    curr_lat = float(rq.args.get('lat'))
    curr_long = float(rq.args.get('long'))
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
                                                        'location': a.locations[0].location.name,
                                                        'region': a.locations[0].location.region.name,
                                                        'distance': locations.get(a.id)['dist'] if locations.get(a.id)
                                                        else None
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
                return create_response(None, responses.BAD_REQUEST_400, ResponseMessages.FIND_NO_RESULTS,
                                       Activity.__name__, 400)

    else:
        return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.FIND_NOT_AUTHORIZED,
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
                                                                 'location': act.locations[0].location.name,
                                                                 'region': act.locations[0].location.region.name
                                                             }
                                                             ) for act in record_activities]

            return create_response(activities, responses.SUCCESS_200, ResponseMessages.FIND_SUCCESS,
                                   Activity.__name__, 200)

    else:
        return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.FIND_NOT_AUTHORIZED,
                               Activity.__name__, 403)


@main.route('/hike/<act_id>', methods=['POST'])
@http_auth.login_required
def add_hike(act_id):
    session = Session()
    user = http_auth.current_user

    if user not in session:
        user = session.query(User).get(user.id)

    activity = session.query(Activity).filter(Activity.id == act_id).first()

    if activity is None:
        session.expunge_all()
        session.close()
        return create_response(None, responses.BAD_REQUEST_400, ResponseMessages.MAIN_NO_DATA,
                               HikeRelation.__name__, 400)

    if user is not None and user.can(Permission.FOLLOW):
        hike = user.add_hike(activity, session)
        res = hike.serialize()
        session.expunge_all()
        session.close()
        return create_response(res, responses.SUCCESS_201, ResponseMessages.CREATE_SUCCESS, HikeRelation.__name__, 201)

    else:
        session.expunge_all()
        session.close()
        return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.CREATE_NOT_AUTHORIZED,
                               HikeRelation.__name__, 403)


@main.route('/un_hike/<act_id>', methods=['POST'])
@http_auth.login_required
def rem_hike(act_id):
    session = Session()
    user = http_auth.current_user

    if user not in session:
        user = session.query(User).get(user.id)

    activity = session.query(Activity).filter(Activity.id == act_id).first()

    if activity is None:
        session.expunge_all()
        session.close()
        return create_response(None, responses.BAD_REQUEST_400, ResponseMessages.MAIN_NO_DATA,
                               HikeRelation.__name__, 400)

    if user is not None and user.can(Permission.FOLLOW):
        user.delete_hike(activity, session)
        session.expunge_all()
        session.close()
        return create_response(None, responses.SUCCESS_201, ResponseMessages.CREATE_SUCCESS, HikeRelation.__name__, 201)

    else:
        session.expunge_all()
        session.close()
        return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.CREATE_NOT_AUTHORIZED,
                               HikeRelation.__name__, 403)
