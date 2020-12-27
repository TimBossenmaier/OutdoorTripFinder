import datetime
import os
import xlrd
import pandas as pd

from flask import Blueprint, request, current_app, url_for, jsonify
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from itsdangerous import TimedJSONWebSignatureSerializer
from flask_httpauth import HTTPBasicAuth

from app.entities.activity_type import ActivityType
from app.entities.activity import Activity
from app.entities.country import Country
from app.entities.location import Location
from app.entities.location_activity import LocationActivity
from app.entities.region import Region
from app.entities.entity import Base, engine
from app.entities.location_type import LocationType
from app.entities.user import User, UserInsertSchema, UserAttributes
from app.entities.entity import Session
from app.email import send_email
from app.main.error_handling import investigate_integrity_error
from app.utils import responses
from app.utils.responses import ResponseMessages, create_response

auth = Blueprint('auth', __name__)
http_auth = HTTPBasicAuth()


def process_consent(typ, token):
    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token.encode('utf-8'))
    except:
        return create_response(token, responses.INVALID_INPUT_422, ResponseMessages.AUTH_TOKEN_INVALID,
                               User.__name__, 422)

    session = Session()
    user_id = data.get(typ)
    user = session.query(User).filter_by(id=user_id).first()

    if user is None:
        session.expunge_all()
        session.close()
        return create_response(token, responses.INVALID_INPUT_422, ResponseMessages.AUTH_TOKEN_INVALID,
                               User.__name__, 422)

    elif user.confirmed:
        user = user.serialize()
        session.expunge_all()
        session.close()
        return create_response(user, responses.SUCCESS_200, ResponseMessages.AUTH_USER_CONFIRMED, User.__name__, 200)
    else:

        if typ == 'confirm':
            user.confirm(session)
        else:
            user.approve(session)
            new_token = user.generate_confirmation_token()
            url = url_for('auth.confirm', token=new_token, _external=True)
            send_email(user.email, 'Confirm Your Account', 'email/confirm',
                       username=user.username, url=url)

        user = user.serialize()
        session.expunge_all()
        session.close()
        return create_response(user, responses.SUCCESS_200, ResponseMessages.AUTH_USER_CONFIRMED, User.__name__, 200)


@http_auth.verify_password
def verify_password(email_or_token, password):
    session = Session()
    if email_or_token == '':
        return False
    if password == '':
        http_auth.current_user = User.verify_auth_token(email_or_token, session)
        http_auth.token_used = True
        session.expunge_all()
        session.close()
        return http_auth.current_user is not None
    user = session.query(User).filter(or_(User.email == email_or_token,
                                          User.username == email_or_token)).first()
    session.expunge_all()
    session.close()

    if not user:
        return False
    http_auth.current_user = user
    http_auth.token_used = False
    return user.verify_password(password)


@http_auth.error_handler
def auth_error():
    return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.AUTH_INVALID_PARAMS, User.__name__, 403)


@auth.route('/tokens/', methods=['POST'])
@http_auth.login_required
def get_token():
    session = Session()
    if http_auth.current_user is None or http_auth.token_used:
        return create_response(None, responses.UNAUTHORIZED_403, ResponseMessages.AUTH_INVALID_PARAMS,
                               User.__name__, 403)
    return create_response({'token': http_auth.current_user.generate_auth_token(expiration=3600,
                                                                                session=session),
                            'expiration_ts': datetime.datetime.now() + datetime.timedelta(hours=1)},
                           responses.SUCCESS_200, ResponseMessages.AUTH_LOGIN_SUCCESSFUL, 200)


@auth.route('/create_user', methods=['GET', 'POST'])
def create_user():
    data = request.get_json()

    session = Session()
    user_schema = UserInsertSchema()
    user = User(**user_schema.load(data))
    res = None
    try:
        res = user_schema.dump(user.create(session))
    except IntegrityError as ie:
        session.rollback()
        session.expunge_all()
        session.close()
        msg = investigate_integrity_error(ie)
        if msg is not None:
            return create_response(msg, responses.BAD_REQUEST_400, ResponseMessages.AUTH_DUPLICATE_PARAMS,
                                   User.__name__, 400)
    finally:
        session.expunge_all()
        session.close()

    approval_token = user.generate_approval_token()
    url = url_for('auth.approve', token=approval_token, _external=True)
    send_email(os.environ.get('APPROVAL_MAIL'), 'Confirm New User', 'email/new_user',
               username=user.username, url=url, email=user.email)

    return create_response(res, responses.SUCCESS_201, ResponseMessages.AUTH_USER_CONFIRMED, User.__name__, 201)


@auth.route('/approve/<token>')
def approve(token):
    resp = process_consent('approve', token)

    return resp


@auth.route('/confirm/<token>')
def confirm(token):
    resp = process_consent('confirm', token)

    return resp


@auth.route('/confirm', methods=['GET', 'POST'])
@http_auth.login_required
def resend_confirmation():
    data = request.get_json()
    curr_user = http_auth.current_user
    if curr_user is not None:
        if curr_user.confirmed:
            curr_user = curr_user.serialize()
            return create_response(curr_user, responses.INVALID_INPUT_422, ResponseMessages.AUTH_ALREADY_CONFIRMED,
                                   User.__name__, 422)
        else:
            new_token = curr_user.generate_confirmation_token()
            url = url_for('auth.confirm', token=new_token, _external=True)
            send_email(curr_user.email, 'Confirm Your Account', 'email/confirm',
                       username=curr_user.username, url=url)
            curr_user = curr_user.serialize()
            return create_response(curr_user, responses.SUCCESS_200, ResponseMessages.AUTH_CONFIRMATION_RESEND,
                                   User.__name__, 200)
    else:
        return create_response(data, responses.INVALID_INPUT_422, ResponseMessages.AUTH_INVALID_PARAMS,
                               User.__name__, 422)


@auth.route('/change_password', methods=['GET', 'POST'])
@http_auth.login_required
def change_password():
    data = request.get_json()
    session = Session()

    user = http_auth.current_user
    if user is None:
        session.expunge_all()
        session.close()
        return create_response(data, responses.INVALID_INPUT_422, ResponseMessages.AUTH_USERNAME_NOT_PROVIDED,
                               User.__name__, 422)
    else:
        user.update_password(data["password_new"], session, user.username)
        user = user.serialize()
        session.expunge_all()
        session.close()
        return create_response(user, responses.SUCCESS_200, ResponseMessages.AUTH_PASSWORD_CHANGED, User.__name__, 200)


@auth.route('/reset_cred', methods=['GET', 'POST'])
def password_reset_request():
    data = request.get_json()
    session = Session()

    if data.get(str(UserAttributes.USERNAME)):
        user = session.query(User).filter_by(username=data[str(UserAttributes.USERNAME)]).first()
    else:
        session.expunge_all()
        session.close()
        return create_response(data, responses.MISSING_PARAMETER_422, ResponseMessages.AUTH_USERNAME_NOT_PROVIDED,
                               User.__name__, 422)
    if user is None:
        session.expunge_all()
        session.close()
        return create_response(data, responses.INVALID_INPUT_422, ResponseMessages.AUTH_INVALID_PARAMS,
                               User.__name__, 422)
    else:
        token = user.generate_reset_token()
        url = url_for('auth.password_reset', token=token, _external=True)
        send_email(user.email, 'Reset Your Password', 'email/reset_password',
                   username=user.username, url=url)
        session.expunge_all()
        session.close()
        return create_response(user.serialize(), responses.SUCCESS_200, ResponseMessages.AUTH_PW_REQUESTED,
                               User.__name__, 200)


@auth.route('reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    data = request.get_json()
    session = Session()
    if not data.get("password"):
        session.expunge_all()
        session.close()
        return create_response(data, responses.MISSING_PARAMETER_422, ResponseMessages.AUTH_PASSWORD_NOT_PROVIDED,
                               User.__name__, 422)
    elif User.reset_password(session, token, data):
        session.expunge_all()
        session.close()
        return create_response(True, responses.SUCCESS_200, ResponseMessages.AUTH_RESET_SUCCESSFUL, User.__name__, 200)
    else:
        session.expunge_all()
        session.close()
        return create_response(data, responses.BAD_REQUEST_400, ResponseMessages.AUTH_RESET_FAILED, User.__name__, 400)


@auth.route('/change_email', methods=['GET', 'POST'])
@http_auth.login_required
def change_email_request():
    data = request.get_json()
    session = Session()

    user = http_auth.current_user
    if user is None:
        session.expunge_all()
        session.close()
        return create_response(data, responses.INVALID_INPUT_422, ResponseMessages.AUTH_INVALID_PARAMS,
                               User.__name__, 422)
    elif user.email == data.get(str(UserAttributes.EMAIL)):
        return create_response(data, responses.INVALID_INPUT_422, ResponseMessages.AUTH_EMAIL_EXISTS,
                               User.__name__, 422)
    else:
        email_token = user.generate_email_token(data[str(UserAttributes.EMAIL)],
                                                data.get(str(UserAttributes.USERNAME)))
        url = url_for('auth.change_email', token=email_token, _external=True)
        send_email(data.get(str(UserAttributes.EMAIL)), 'Confirm Your Email Address', 'email/change_email',
                   username=data.get(str(UserAttributes.USERNAME)), url=url)

        user = user.serialize()
        session.expunge_all()
        session.close()
        return create_response(user, responses.SUCCESS_200, ResponseMessages.AUTH_EMAIL_REQUESTED, User.__name__, 200)


@auth.route('/change_email/<token>')
def change_email(token):
    new_email, username, user_id = User.resolve_email_token(token)
    session = Session()

    if username is not None:
        user = session.query(User).filter_by(username=username).first()
    else:
        session.expunge_all()
        session.close()
        return create_response(None, responses.MISSING_PARAMETER_422, ResponseMessages.AUTH_USERNAME_NOT_PROVIDED,
                               User.__name__, 422)

    if user is None:
        session.expunge_all()
        session.close()
        return create_response(None, responses.INVALID_INPUT_422, ResponseMessages.AUTH_INVALID_PARAMS,
                               User.__name__, 422)
    elif user.change_email(session, new_email, user_id, username):
        user = user.serialize()
        session.expunge_all()
        session.close()
        return create_response(user, responses.SUCCESS_200, ResponseMessages.AUTH_EMAIL_CHANGED, User.__name__, 200)
    else:
        user = user.serialize()
        session.expunge_all()
        session.close()
        return create_response(user, responses.BAD_REQUEST_400, ResponseMessages.AUTH_EMAIL_CHANGED,
                               User.__name__, 400)


@auth.route('/import', methods=['GET'])
def import_tours():

    def intersection(ids, keys_used):
        lst3 = [v for v in keys_used if v not in ids]
        return lst3

    Base.metadata.create_all(engine)
    session = Session()

    PATH_FILE = 'E:\Outdoor_Activities\import_table.xlsx'

    data_countries = pd.read_excel(PATH_FILE, sheet_name="country", header=0,
                                   dtype={'id': int, 'name': str, 'abbreviation': str, 'creator': str})  # , skiprows=range(1, 21))

    data_regions = pd.read_excel(PATH_FILE, sheet_name="region", header=0,

                                 dtype={'id': int, 'name': str, 'country_id': int,
                                        'creator': str})  # , skiprows=range(1, 156))

    data_location_type = pd.read_excel(PATH_FILE, sheet_name="location_type", header=0,
                                       dtype={'id': int, 'name': str, 'creator': str})  # , skiprows=range(1, 7))

    data_locations = pd.read_excel(PATH_FILE, sheet_name='localisation', header=0,
                                   dtype={'id': int, 'lat': float, 'long': float, 'name': str, 'location_type_id': int,
                                          'region_id': int, 'creator': str})  # , skiprows=range(1, 985))

    data_locations.lat = data_locations.lat / 1000
    data_locations.long = data_locations.long / 1000

    data_activity_types = pd.read_excel(PATH_FILE, sheet_name='activity_type', header=0,
                                        dtype={'id': int, 'name': str, 'creator': str})  # , skiprows=range(1, 6))

    data_activities = pd.read_excel(PATH_FILE, sheet_name='activity', header=0,
                                    dtype={'id': int, 'name': str, 'description': str, 'activity_id': int,
                                           'source': str,

                                           'save_path': str, 'multi-day': bool,
                                           'creator': str})  # , skiprows=range(1, 267))

    data_mappings = pd.read_excel(PATH_FILE, sheet_name='loc_act', header=0,
                                  dtype={'id': int, 'act_id': int, 'loc_id': int,
                                         'creator': str})  # , skiprows=range(1, 1089))

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
    # check whether only valid foreign keys are use
    if len(intersection(ids_country, list(data_regions.country_id))) > 0:
        errors_found = True
        print("The following country ids are used but not defined",
              intersection(ids_country, list(data_regions.country_id)))

    if len(intersection(ids_regions, list(data_locations.region_id))) > 0:
        errors_found = True
        print("The following region ids are used but not defined",
              intersection(ids_regions, list(data_locations.region_id)))

    if len(intersection(ids_location_types, list(data_locations.location_type_id))) > 0:
        errors_found = True
        print("The following region ids are used but not defined",
              intersection(ids_location_types, list(data_locations.location_type_id)))

    if len(intersection(ids_activities, list(data_mappings.act_id))) > 0:
        errors_found = True
        print("The following activity ids are used but not defined",
              intersection(ids_activities, list(data_mappings.act_id)))

    if len(intersection(ids_locations, list(data_mappings.loc_id))) > 0:
        errors_found = True
        print("The following location ids are used but not defined",
              intersection(ids_locations, list(data_mappings.loc_id)))

    if len(intersection(ids_activity_types, data_activities.activity_id)) > 0:
        errors_found = True
        print("The following activity_type ids are used but not defined",
              intersection(ids_activity_types, list(data_activities.activity_id)))

    # check presence of all files, resp. validity of save_paths
    for each_file in data_activities.save_path:
        if os.path.isfile('E:\Outdoor_Activities\\' + each_file):
            pass
        else:
            print('E:\Outdoor_Activities\\' + each_file + " not found")
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
            countries.append(Country(data_countries.loc[idx, "name"], data_countries.loc[idx, "abbreviation"], 16))
        session.add_all(countries)
        session.commit()

        for idx in data_regions.index:
            regions.append(Region(data_regions.loc[idx, "name"], int(data_regions.loc[idx, "country_id"]),
                                  16))
        session.add_all(regions)
        session.commit()

        for idx in data_location_type.index:
            location_types.append(LocationType(data_location_type.loc[idx, "name"], 16))
        session.add_all(location_types)
        session.commit()

        for idx in data_locations.index:
            locations.append(Location(data_locations.loc[idx, "lat"], data_locations.loc[idx, "long"],
                                      data_locations.loc[idx, "name"], int(data_locations.loc[idx, "location_type_id"]),
                                      int(data_locations.loc[idx, "region_id"]), 16))
        session.add_all(locations)
        session.commit()

        for idx in data_activity_types.index:
            activity_types.append(ActivityType(data_activity_types.loc[idx, "name"],
                                               16))
        session.add_all(activity_types)
        session.commit()

        for idx in data_activities.index:
            activities.append(Activity(data_activities.loc[idx, "name"], data_activities.loc[idx, "description"],
                                       int(data_activities.loc[idx, "activity_id"]), data_activities.loc[idx, "source"],
                                       data_activities.loc[idx, "save_path"], data_activities.loc[idx, "multi-day"],
                                       16))
        session.add_all(activities)
        session.commit()

        for idx in data_mappings.index:
            mappings.append(
                LocationActivity(int(data_mappings.loc[idx, "act_id"]), int(data_mappings.loc[idx, "loc_id"]),
                                 16))
        session.add_all(mappings)
        session.commit()

    return jsonify("Hallo")