from flask import Blueprint, request, make_response
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError

from ..entities.entity import Session
from ..entities.user import UserAttributes, User, Permission
from ..entities.country import Country
from ..entities.region import Region, RegionAttributes
from ..entities.location_type import LocationType
from ..entities.activity_type import ActivityType
from ..entities.location_activity import LocationActivity
from ..entities.activity import Activity, ActivityAttributes
from ..entities.location import Location, LocationAttributes
from ..main.error_handling import investigate_integrity_error
from ..utils import responses
from ..utils.responses import create_json_response, ResponseMessages
from ..utils.helpers import distance_between_coordinates, sort_by_dist

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
        return make_response(create_json_response(responses.MISSING_PARAMETER_422,
                                                  ResponseMessages.CREATE_MISSING_PARAM,
                                                  user_data,
                                                  class_type.__name__), 422)

    return user


def check_integrity_error(ie, session, class_type):
    session.rollback()
    session.close()

    msg = investigate_integrity_error(ie)
    if msg is not None:
        return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                  ResponseMessages.CREATE_DUPLICATE_PARAMS,
                                                  msg,
                                                  class_type.__name__), 422)

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

        return make_response(create_json_response(responses.SUCCESS_201,
                                                  ResponseMessages.CREATE_SUCCESS,
                                                  res,
                                                  class_type.__name__), 201)
    else:
        return make_response(create_json_response(responses.UNAUTHORIZED_403,
                                                  ResponseMessages.CREATE_NOT_AUTHORIZED,
                                                  user_data), 403)


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
            return make_response(create_json_response(responses.SUCCESS_200,
                                                      ResponseMessages.UPDATE_SUCCESS,
                                                      res,
                                                      class_type.__name__), 200)
        else:
            session.close()
            return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                      ResponseMessages.UPDATE_FAILED,
                                                      data,
                                                      class_type.__name__), 422)
    else:
        session.close()
        return make_response(create_json_response(responses.UNAUTHORIZED_403,
                                                  ResponseMessages.UPDATE_NOT_AUTHORIZED,
                                                  user_data), 403)


# TOD options for activity type and action_type
def list_all(class_type, term='', keys=None, typ=None):
    session = Session()

    if term != '' and keys is None:
        search_term = '%{}%'.format(term)
        res = session.query(class_type).filter(class_type.name.like(search_term)).order_by(class_type.id.asc()).all()

    elif term == '' and keys is not None:

        if class_type == Country:
            return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                      ResponseMessages.LIST_INVALID_INPUT,
                                                      keys,
                                                      class_type.__name__), 422)
        else:
            if keys.get(RegionAttributes.COUNTRY_ID if class_type == Region else LocationAttributes.REGION_ID):
                res = session.query(Region if class_type == Region else Location).filter(Region.country_id.in_(keys.get(RegionAttributes.COUNTRY_ID))
                                                                                         if class_type == Region else
                                                                                         Location.region_id.in_(keys.get(LocationAttributes.REGION_ID))) \
                                                                                  .order_by(class_type.id.asc()) \
                                                                                  .all()
            else:
                make_response(create_json_response(responses.INVALID_INPUT_422,
                                                   ResponseMessages.LIST_INVALID_INPUT,
                                                   keys,
                                                   class_type.__name__), 422)

    elif term != '' and keys is not None:

        if class_type == Country:
            return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                      ResponseMessages.LIST_INVALID_INPUT,
                                                      keys,
                                                      class_type.__name__), 422)
        else:
            if keys.get(RegionAttributes.COUNTRY_ID if class_type == Region else LocationAttributes.REGION_ID):
                search_term = '%{}%'.format(term)
                res = session.query(Region if class_type == Region else Location).filter(
                    and_(Region.country_id.in_(keys.get(RegionAttributes.COUNTRY_ID)), Region.name.like(search_term)
                    if class_type == Region else Location.region_id.in_(keys.get(LocationAttributes.REGION_ID)),
                         Location.name.like(search_term)))\
                    .order_by(class_type.id.asc())\
                    .all()
            else:
                make_response(create_json_response(responses.INVALID_INPUT_422,
                                                   ResponseMessages.LIST_INVALID_INPUT,
                                                   keys,
                                                   class_type.__name__), 422)
    elif typ is not None:
        if class_type == Location and typ.get(LocationAttributes.LOCATION_TYPE_ID):
            res = session.query(Location)\
                .filter(Location.location_type_id == typ.get(LocationAttributes.LOCATION_TYPE_ID))\
                .order_by(class_type.id.asc())\
                .all()
        elif class_type == Activity and typ.get(ActivityAttributes.ACTIVITY_TYPE_ID):
            res = session.query(Activity)\
                .filter(Activity.activity_type_id == typ.get(ActivityAttributes.ACTIVITY_TYPE_ID))\
                .order_by(class_type.id.asc())\
                .all()
        else:
            return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                      ResponseMessages.LIST_INVALID_INPUT,
                                                      typ,
                                                      class_type.__name__), 422)
    else:
        res = session.query(class_type).order_by(class_type.id.asc()).all()

    if res is None:
        return make_response(create_json_response(responses.INVALID_INPUT_422,
                                                  ResponseMessages.LIST_EMPTY,
                                                  None,
                                                  class_type.__name__), 422)
    else:
        attributes = class_type.get_attributes()
        schema = class_type.get_schema(many=True, only=(str(attributes.NAME), str(attributes.ID)))
        entities = schema.dump(res)

        return make_response(create_json_response(responses.SUCCESS_200,
                                                  ResponseMessages.LIST_SUCCESS,
                                                  entities,
                                                  class_type.__name__), 200)


@main.route('/create/country', methods=['GET', 'POST'])
def create_country():
    resp = create(request, Country)

    return resp


@main.route('/create/region', methods=['GET', 'POST'])
def create_region():
    resp = create(request, Region)

    return resp


@main.route('/create/location_type', methods=['GET', 'POST'])
def create_location_type():
    resp = create(request, LocationType)

    return resp


@main.route('/create/activity_type', methods=['GET', 'POST'])
def create_activity_type():
    resp = create(request, ActivityType)

    return resp


@main.route('/create/location_activity', methods=['GET', 'POST'])
def create_activity_location():
    resp = create(request, LocationActivity)

    return resp


@main.route('/create/activity', methods=['GET', 'POST'])
def create_activity():
    resp = create(request, Activity)

    return resp


@main.route('/create/location', methods=['GET', 'POST'])
def create_location():
    res = create(request, Location)

    return res


@main.route('/update/country', methods=['GET', 'POST'])
def update_country():
    resp = update(request, Country)

    return resp


@main.route('/update/region', methods=['GET', 'POST'])
def update_region():
    res = update(request, Region)

    return res


@main.route('/update/location_type', methods=['GET', 'POST'])
def update_location_type():
    res = update(request, LocationType)

    return res


@main.route('/update/activity_type', methods=['GET', 'POST'])
def update_activity_type():
    res = update(request, ActivityType)

    return res


@main.route('/update/location_activity', methods=['GET', 'POST'])
def update_location_activity():
    res = update(request, LocationActivity)

    return res


@main.route('/update/activity', methods=['GET', 'POST'])
def update_activity():
    res = update(request, Activity)

    return res


@main.route('/update/location', methods=['GET', 'POST'])
def update_location():
    res = update(request, Location)

    return res


@main.route('/list/country', methods=['GET'])
def list_country():
    res = list_all(Country)

    return res


@main.route('/list/region', methods=['GET'])
def list_region():
    res = list_all(Region)

    return res


@main.route('/list/location_type', methods=['GET'])
def list_location_type():
    res = list_all(LocationType)

    return res


@main.route('/list/activity_type', methods=['GET'])
def list_activity_type():
    res = list_all(ActivityType)

    return res


@main.route('/list/location_activity', methods=['GET', 'POST'])
def list_location_activity():
    res = list_all(LocationActivity)

    return res


@main.route('/list/activity', methods=['GET', 'POST'])
def list_activity():
    res = list_all(Activity)

    return res


@main.route('/list/location', methods=['GET', 'POST'])
def list_location():
    res = list_all(Location)

    return res


@main.route('/find_tour', methods=['GET'])
def find_tour():
    user_data, data = extract_json_data(request, Activity)

    session = Session()

    expected_user = extract_user(user_data, session, Activity)

    if isinstance(expected_user, User):
        user = expected_user
    else:
        resp = expected_user
        return resp

    if user is not None and user.can(Permission.READ):

        if data.get("curr_lat"):
            record_location = session.query(Location) \
                .filter(Location.lat > data["curr_lat"] - 3 * data["max_dist"] / 100,
                        Location.lat < data["curr_lat"] + 3 * data["max_dist"] / 100,
                        Location.long > data["curr_long"] - 3 * data["max_dist"] / 100,
                        Location.long < data["curr_long"] + 3 * data["max_dist"] / 100) \
                .all()
        else:
            return make_response(create_json_response(responses.MISSING_PARAMETER_422,
                                                      ResponseMessages.FIND_MISSING_PARAMETER,
                                                      data,
                                                      Location.__name__), 422)
        schema = Location.get_schema(many=True, only=(LocationAttributes.NAME,
                                                      LocationAttributes.LATITUDE,
                                                      LocationAttributes.LONGITUDE,
                                                      LocationAttributes.ID))
        locations = schema.dump(record_location)

        if record_location is None:
            return make_response(create_json_response(responses.BAD_REQUEST_400,
                                                      ResponseMessages.FIND_NO_RESULTS,
                                                      data,
                                                      Location.__name__), 400)
        else:

            for i, loc in enumerate(locations):
                loc.update({"dist": distance_between_coordinates(loc["lat"], loc["long"],
                                                                 data["curr_lat"], data["curr_long"])})
            locations = [i for i in locations if i['dist'] < data["max_dist"]]
            locations.sort(key=sort_by_dist)
            ids = [int(i['id']) for i in locations]

            record_activities = session.query(Activity) \
                .join(ActivityType) \
                .join(LocationActivity) \
                .join(Location).join(Region) \
                .join(Country) \
                .filter(Location.id.in_(ids)) \
                .all()

            schema = Activity.get_presentation_schema(many=True)

            act = []
            for rec in record_activities:
                for loc in rec.locations:
                    activity_pres = {
                        'name': rec.name,
                        'description': rec.description,
                        'activity_type': rec.activity_type.name,
                        'source': rec.source,
                        'save_path': rec.save_path,
                        'location': loc.location.name,
                        'region': loc.location.region.name,
                        'country': loc.location.region.country.name,
                        'distance': [x['dist'] for x in locations if x['id'] == loc.location_id][0] if len(
                            [x['dist'] for x in locations if x['id'] == loc.location_id]) > 0 else 1000
                    }
                    act.append(activity_pres)
            act = sorted(act, key=lambda k: k['distance'])

            # keep only one entry per activity
            activity_names = set()
            idx_to_keep = []
            for idx, item in enumerate(act):

                if item["name"] not in activity_names:
                    activity_names.add(item["name"])
                    idx_to_keep.append(idx)

            act = [act[i] for i in idx_to_keep]
            activities = schema.dump(act)
            if len(activities) > 0:
                return make_response(create_json_response(responses.SUCCESS_200,
                                                          ResponseMessages.FIND_SUCCESS,
                                                          activities,
                                                          Activity.__name__), 200)
            else:
                return make_response(create_json_response(responses.BAD_REQUEST_400,
                                                          ResponseMessages.FIND_NO_RESULTS,
                                                          data,
                                                          Activity.__name__), 400)

    else:
        return make_response(create_json_response(responses.UNAUTHORIZED_403,
                                                  ResponseMessages.FIND_NOT_AUTHORIZED,
                                                  user_data), 403)


@main.route('/find_tour_by_term', methods=['GET'])
def find_tour_by_term():
    user_data, data = extract_json_data(request, Activity)

    session = Session()

    expected_user = extract_user(user_data, session, Activity)

    if isinstance(expected_user, User):
        user = expected_user
    else:
        resp = expected_user
        return resp

    if user is not None and user.can(Permission.READ):

        if data.get('search_term'):
            term = data.get("search_term")
            search_term = '%{}%'.format(term)
            record_activities = session.query(Activity).filter(or_(Activity.name.like(search_term),
                                                                   Activity.description.like(search_term))).all()
        else:
            return make_response(create_json_response(responses.MISSING_PARAMETER_422,
                                                      ResponseMessages.FIND_MISSING_PARAMETER,
                                                      data,
                                                      Activity.__name__), 422)

        if record_activities is None:
            return make_response(create_json_response(responses.BAD_REQUEST_400,
                                                      ResponseMessages.FIND_NO_RESULTS,
                                                      data,
                                                      Activity.__name__), 400)
        else:
            schema = Activity.get_presentation_schema(many=[True if len(record_activities) > 1 else False],
                                                      only=(ActivityAttributes.NAME,
                                                            ActivityAttributes.DESCRIPTION,
                                                            ActivityAttributes.MULTI_DAY,
                                                            'activity_type'))
            activities = schema.dump(record_activities)

            return make_response(create_json_response(responses.SUCCESS_200,
                                                      ResponseMessages.FIND_SUCCESS,
                                                      activities,
                                                      Activity.__name__), 200)

    else:
        return make_response(create_json_response(responses.UNAUTHORIZED_403,
                                                  ResponseMessages.FIND_NOT_AUTHORIZED,
                                                  user_data), 400)
