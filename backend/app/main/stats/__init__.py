from flask import Blueprint

from app.auth import http_auth
from app.entities.entity import Session
from app.entities.activity import Activity
from app.entities.activity_type import ActivityType
from app.entities.country import Country
from app.entities.hike_relations import HikeRelation
from app.entities.location import Location
from app.entities.location_activity import LocationActivity
from app.entities.region import Region
from app.main import count, sort_dict
from app.utils import responses
from app.utils.responses import ResponseMessages, create_response


stats = Blueprint('stats', __name__)


@stats.route('/hikes/<act_id>', methods=['GET'])
@http_auth.login_required
def get_no_hikes(act_id):
    res = count(user=http_auth.current_user, class_type=HikeRelation, **{'activity_id': act_id})

    return res


@stats.route('', methods=['GET'])
@http_auth.login_required
def stats_general():
    no_tours = count(user=http_auth.current_user, class_type=Activity).get_json()
    no_country = count(user=http_auth.current_user, class_type=Country).get_json()
    no_regions = count(user=http_auth.current_user, class_type=Region).get_json()
    no_locations = count(user=http_auth.current_user, class_type=Location).get_json()

    session = Session()

    result = session.query(LocationActivity).join(Location).all()
    countries = {}
    regions = {}
    for r in result:

        if r.locations.region.country.abbreviation in countries.keys():
            countries[r.locations.region.country.abbreviation] += 1
        else:
            countries.update({r.locations.region.country.abbreviation: 1})

        if r.locations.region.name in regions.keys():
            regions[r.locations.region.name] += 1
        else:
            regions.update({r.locations.region.name: 1})
    countries = sort_dict(countries.items())
    regions = sort_dict(regions.items())

    result = session.query(Activity).join(ActivityType).all()
    act_types = {}
    for r in result:
        if r.activity_type.name in act_types.keys():
            act_types[r.activity_type.name] += 1
        else:
            act_types.update({r.activity_type.name: 1})
    act_types = sort_dict(act_types.items())

    result = session.query(HikeRelation).join(Activity).all()
    activities = {}
    for r in result:
        if r.activity.name in activities.keys():
            activities[r.activity.name] += 1
        else:
            activities.update({r.activity.name: 1})
    activities = sort_dict(activities.items())

    result = {
        'noTours': no_tours,
        'noCountry': no_country,
        'noRegion': no_regions,
        'noLocation': no_locations,
        'popCountry': list(countries.keys())[0] if len(countries) > 0 else '',
        'popRegion': list(regions.keys())[0] if len(regions) > 0 else '',
        'popActivityType': list(act_types.keys())[0] if len(act_types) > 0 else '',
        'popActivity': list(activities.keys())[0] if len(activities) > 0 else ''
    }

    return create_response(result, responses.SUCCESS_200, ResponseMessages.FIND_SUCCESS, None, 200)

