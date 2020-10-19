from backend.app.entities.activity_type import ActivityType
from backend.app.entities.activity import Activity
from backend.app.entities.country import Country
from backend.app.entities.location import Location
from backend.app.entities.location_activity import LocationActivity
from backend.app.entities.region import Region
from backend.app.entities.entity import Base, Session, engine
from backend.app.entities.location_type import LocationType
import pandas as pd
import os
import xlrd


def intersection(ids, keys_used):
    lst3 = [v for v in keys_used if v not in ids]
    return lst3


Base.metadata.create_all(engine)
session = Session()

PATH_FILE = 'E:\Outdoor_Activities\import_table.xlsx'

data_countries = pd.read_excel(PATH_FILE, sheet_name="country", header=0,
                               dtype={'id': int, 'name': str, 'creator': str})#, skiprows=range(1, 13))

data_regions = pd.read_excel(PATH_FILE, sheet_name="region", header=0,
                             dtype={'id': int, 'name': str, 'country_id': int, 'creator': str})#, skiprows=range(1, 85))

data_location_types = pd.read_excel(PATH_FILE, sheet_name='location_type', header=0,
                                    dtype={'id': int, 'name': str, 'creator': str})#, skiprows=range(1, 1))

data_locations = pd.read_excel(PATH_FILE, sheet_name='localisation', header=0,
                               dtype={'id': int, 'lat': float, 'long': float, 'name': str, 'location_type_id': int,
                                      'region_id': int, 'creator': str},)# skiprows=range(1, 404))
data_locations.lat = data_locations.lat / 1000
data_locations.long = data_locations.long / 1000

data_activity_types = pd.read_excel(PATH_FILE, sheet_name='activity_type', header=0,
                                    dtype={'id': int, 'name': str, 'creator': str})#, skiprows=range(1, 4))

data_activities = pd.read_excel(PATH_FILE, sheet_name='activity', header=0,
                                dtype={'id': int, 'name': str, 'description': str, 'activity_id': int,
                                       'source': str, 'save_path': str, 'multi-day': bool, 'creator': str})#,
                                #skiprows=range(1, 149))

data_mappings = pd.read_excel(PATH_FILE, sheet_name='loc_act', header=0,
                              dtype={'id': int, 'act_id': int, 'loc_id': int, 'creator': str})#, skiprows=range(1, 454))

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
ids_location_types = []
for value in sheet_location_type.col_values(0):
    if isinstance(value, float):
        ids_location_types.append(int(value))
ids_activities = []
for value in sheet_activity.col_values(0):
    if isinstance(value, float):
        ids_activities.append(int(value))
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
    print("The following activity ids are used but not define",
          intersection(ids_activities, list(data_mappings.act_id)))

if len(intersection(ids_locations, list(data_mappings.loc_id))) > 0:
    errors_found = True
    print("The following location ids are used but not defined",
          intersection(ids_locations, list(data_mappings.loc_id)))

if len(intersection(ids_activity_types, data_activities.activity_id)) > 0:
    errors_found = True
    print("The following activity_type ids are used but not defined",
          intersection(ids_activity_types, list(data_activities.activity_id)))

# check if coordinates have plausible values
# latitude ranges from -90.0 to 90.0 and longitude from -180.0 to 180.0
# ref: https://de.wikipedia.org/wiki/Geographische_Koordinaten

for _, row in data_locations.iterrows():
    if abs(row.lat) > 90.0:
        print("Location {} has a invalid value for latitude ({})".format(row.name, row.lat))
        errors_found = True
    if abs(row.long) > 180.0:
        print('Location {} has a invalid value for latitude ({})'.format(row.name, row.long))
        errors_found = True

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
        countries.append(Country(data_countries.loc[idx, "name"], data_countries.loc[idx, "creator"]))
    #session.add_all(countries)
    #session.commit()

    for idx in data_regions.index:
        regions.append(Region(data_regions.loc[idx, "name"], int(data_regions.loc[idx, "country_id"]),
                              data_regions.loc[idx, "creator"]))
    #session.add_all(regions)
    #session.commit()

    for idx in data_location_types.index:
        location_types.append(LocationType(data_location_types.loc[idx, "name"],
                                           data_location_types.loc[idx, "creator"]))
    #session.add_all(location_types)
    #session.commit()

    for idx in data_locations.index:
        locations.append(Location(data_locations.loc[idx, "lat"], data_locations.loc[idx, "long"],
                                  data_locations.loc[idx, "name"], int(data_locations.loc[idx, 'location_type_id']),
                                  int(data_locations.loc[idx, "region_id"]), data_locations.loc[idx, "creator"]))
    session.add_all(locations)
    session.commit()

    for idx in data_activity_types.index:
        activity_types.append(ActivityType(data_activity_types.loc[idx, "name"],
                                           data_activity_types.loc[idx, "creator"]))
    session.add_all(activity_types)
    session.commit()

    for idx in data_activities.index:
        activities.append(Activity(data_activities.loc[idx, "name"], data_activities.loc[idx, "description"],
                                   int(data_activities.loc[idx, "activity_id"]), data_activities.loc[idx, "source"],
                                   data_activities.loc[idx, "save_path"], data_activities.loc[idx, "multi-day"],
                                   data_activities.loc[idx, "creator"]))
    session.add_all(activities)
    session.commit()

    for idx in data_mappings.index:
        mappings.append(LocationActivity(int(data_mappings.loc[idx, "act_id"]), int(data_mappings.loc[idx, "loc_id"]),
                                         data_mappings.loc[idx, "creator"]))
    session.add_all(mappings)
    session.commit()
