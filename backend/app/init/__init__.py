import ast
import base64
import os

import pandas as pd
import xlrd

from flask import Blueprint

from app.auth import http_auth
from app.entities.activity import Activity
from app.entities.activity_type import ActivityType
from app.entities.country import Country
from app.entities.entity import Session, Base, engine
from app.entities.location import Location
from app.entities.location_activity import LocationActivity
from app.entities.location_type import LocationType
from app.entities.region import Region
from app.entities.role import Permission, Role
from app.entities.user import User
from app.utils import responses
from app.utils.helpers import intersection
from app.utils.responses import create_response, ResponseMessages

init = Blueprint('init', __name__)


@init.route('/load_tours/<data_encoded>', methods=['GET'])
@http_auth.login_required
def import_tours(data_encoded):
    data_string = base64.b64decode(data_encoded).decode()
    data = ast.literal_eval(data_string)

    session = Session()
    user = http_auth.current_user

    classes = [Country, Region, LocationType, Location, ActivityType, Activity, LocationActivity]
    last_index = {}
    for c in classes:
        res = session.query(c).order_by(c.id.desc()).first()
        last_index.update({c.__name__: res.id})

    if user not in session:
        user = session.query(User).get(user.id)

    if user is not None and user.can(Permission.ADMIN):

        PATH_FILE = data.get('path_file')

        data_countries = pd.read_excel(PATH_FILE, sheet_name="country", header=0,
                                       dtype={'id': int, 'name': str, 'abbreviation': str,
                                              'creator': str}, skiprows=range(1, last_index['Country'] + 1))

        data_regions = pd.read_excel(PATH_FILE, sheet_name="region", header=0,
                                     dtype={'id': int, 'name': str, 'country_id': int,
                                            'creator': str}, skiprows=range(1, last_index['Region'] + 1))

        data_location_type = pd.read_excel(PATH_FILE, sheet_name="location_type", header=0,
                                           dtype={'id': int, 'name': str, 'creator': str},
                                           skiprows=range(1, last_index['LocationType'] + 1))

        data_locations = pd.read_excel(PATH_FILE, sheet_name='localisation', header=0,
                                       dtype={'id': int, 'lat': float, 'long': float, 'name': str,
                                              'location_type_id': int, 'region_id': int,
                                              'creator': str}, skiprows=range(1, last_index['Location'] + 1))

        data_locations.lat = data_locations.lat / 1000
        data_locations.long = data_locations.long / 1000

        data_activity_types = pd.read_excel(PATH_FILE, sheet_name='activity_type', header=0,
                                            dtype={'id': int, 'name': str, 'creator': str},
                                            skiprows=range(1, last_index['ActivityType'] + 1))

        data_activities = pd.read_excel(PATH_FILE, sheet_name='activity', header=0,
                                        dtype={'id': int, 'name': str, 'description': str, 'activity_id': int,
                                               'source': str,
                                               'save_path': str, 'multi-day': bool,
                                               'creator': str},
                                        skiprows=range(1, last_index['Activity'] + 1))

        data_mappings = pd.read_excel(PATH_FILE, sheet_name='loc_act', header=0,
                                      dtype={'id': int, 'act_id': int, 'loc_id': int,
                                             'creator': str}, skiprows=range(1, last_index['LocationActivity'] + 1))

        wb = xlrd.open_workbook(PATH_FILE)
        sheet_activity = wb.sheet_by_index(0)
        sheet_activity_type = wb.sheet_by_index(1)
        sheet_country = wb.sheet_by_index(2)
        sheet_region = wb.sheet_by_index(3)
        sheet_location = wb.sheet_by_index(4)
        sheet_location_type = wb.sheet_by_index(6)

        ids_country = []
        for value in sheet_country.col_values(0):
            if isinstance(value, float):
                ids_country.append(int(value))
        ids_regions = []
        for value in sheet_region.col_values(0):
            if isinstance(value, float):
                ids_regions.append(int(value))
        ids_activities = []
        for value in sheet_activity.col_values(0):
            if isinstance(value, float):
                ids_activities.append(int(value))
        ids_location_types = []
        for value in sheet_location_type.col_values(0):
            if isinstance(value, float):
                ids_location_types.append(int(value))
        ids_locations = []
        for value in sheet_location.col_values(0):
            if isinstance(value, float):
                ids_locations.append(int(value))
        ids_activity_types = []
        for value in sheet_activity_type.col_values(0):
            if isinstance(value, float):
                ids_activity_types.append(int(value))

        errors_found = False
        errors = []
        # check whether only valid foreign keys are use
        if len(intersection(ids_country, list(data_regions.country_id))) > 0:
            errors_found = True
            errors.append(["The following country ids are used but not defined",
                           intersection(ids_country, list(data_regions.country_id))])

        if len(intersection(ids_regions, list(data_locations.region_id))) > 0:
            errors_found = True
            errors.append(["The following region ids are used but not defined",
                           intersection(ids_regions, list(data_locations.region_id))])

        if len(intersection(ids_location_types, list(data_locations.location_type_id))) > 0:
            errors_found = True
            errors.append(["The following region ids are used but not defined",
                           intersection(ids_location_types, list(data_locations.location_type_id))])

        if len(intersection(ids_activities, list(data_mappings.act_id))) > 0:
            errors_found = True
            errors.append(["The following activity ids are used but not defined",
                           intersection(ids_activities, list(data_mappings.act_id))])

        if len(intersection(ids_locations, list(data_mappings.loc_id))) > 0:
            errors_found = True
            errors.append(["The following location ids are used but not defined",
                           intersection(ids_locations, list(data_mappings.loc_id))])

        if len(intersection(ids_activity_types, data_activities.activity_id)) > 0:
            errors_found = True
            errors.append(["The following activity_type ids are used but not defined",
                           intersection(ids_activity_types, list(data_activities.activity_id))])

        # check presence of all files, resp. validity of save_paths
        for each_file in data_activities.save_path:
            if os.path.isfile('E:\Outdoor_Activities\\' + each_file):
                pass
            else:
                errors.append(['Not found', 'E:\Outdoor_Activities\\' + each_file])
                errors_found = True

        countries = []
        regions = []
        location_types = []
        locations = []
        activity_types = []
        activities = []
        mappings = []
        if not errors_found:

            for idx in data_countries.index:
                countries.append(Country(data_countries.loc[idx, "name"], data_countries.loc[idx, "abbreviation"],
                                         user.id))
            session.add_all(countries)
            session.commit()

            for idx in data_regions.index:
                regions.append(Region(data_regions.loc[idx, "name"], int(data_regions.loc[idx, "country_id"]),
                                      user.id))
            session.add_all(regions)
            session.commit()

            for idx in data_location_type.index:
                location_types.append(LocationType(data_location_type.loc[idx, "name"], user.id))
            session.add_all(location_types)
            session.commit()

            for idx in data_locations.index:
                locations.append(Location(data_locations.loc[idx, "lat"], data_locations.loc[idx, "long"],
                                          data_locations.loc[idx, "name"],
                                          int(data_locations.loc[idx, "location_type_id"]),
                                          int(data_locations.loc[idx, "region_id"]), user.id))
            session.add_all(locations)
            session.commit()

            for idx in data_activity_types.index:
                activity_types.append(ActivityType(data_activity_types.loc[idx, "name"],
                                                   user.id))
            session.add_all(activity_types)
            session.commit()

            for idx in data_activities.index:
                activities.append(Activity(data_activities.loc[idx, "name"], data_activities.loc[idx, "description"],
                                           int(data_activities.loc[idx, "activity_id"]),
                                           data_activities.loc[idx, "source"],
                                           data_activities.loc[idx, "save_path"], data_activities.loc[idx, "multi-day"],
                                           user.id))
            session.add_all(activities)
            session.commit()

            for idx in data_mappings.index:
                mappings.append(
                    LocationActivity(int(data_mappings.loc[idx, "act_id"]), int(data_mappings.loc[idx, "loc_id"]),
                                     user.id))
            session.add_all(mappings)
            session.commit()

            session.expunge_all()
            session.close()

            return create_response(None, responses.SUCCESS_201, ResponseMessages.INIT_SUCCESS, None, 201)
        else:
            session.expunge_all()
            session.close()
            return create_response(errors, responses.BAD_REQUEST_400, ResponseMessages.INIT_ERROR_DURING_CREATE, None,
                                   400)
    else:
        return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.INIT_NOT_AUTHORIZED, None, 403)


@init.route('/db', methods=['GET'])
def init_db():

    session = Session()

    Base.metadata.create_all(engine)
    Role.insert_roles(session)

    session.expunge_all()
    session.close()

    return create_response(None, responses.SUCCESS_201, ResponseMessages.INIT_SUCCESS, None, 201)
