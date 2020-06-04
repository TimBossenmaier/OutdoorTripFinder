from backend.src.entities.activity_type import ActivityType
from backend.src.entities.activity import Activity
from backend.src.entities.country import Country
from backend.src.entities.location import Location
from backend.src.entities.location_activity import LocationActivity
from backend.src.entities.region import Region
from backend.src.entities.entity import Base, Session, engine
import pandas as pd
import os
import xlrd


def intersection(ids, keys_used):
    lst3 = [v for v in keys_used if v not in ids]
    return lst3

Base.metadata.create_all(engine)
session = Session()

PATH_FILE = 'D:\Outdoor_Activities\import_table.xlsx'

data_countries = pd.read_excel(PATH_FILE, sheet_name="country", header=0,
                               dtype={'id': int, 'name': str, 'creator': str}, skiprows=range(1, 3))

data_regions = pd.read_excel(PATH_FILE, sheet_name="region", header=0,
                             dtype={'id': int, 'name': str, 'country_id': int, 'creator': str}, skiprows=range(1, 3))

data_locations = pd.read_excel(PATH_FILE, sheet_name='localisation', header=0,
                               dtype={'id': int, 'lat': float, 'long': float, 'name': str,
                                      'region_id': int, 'creator': str}, skiprows=range(1, 4))
data_locations.lat = data_locations.lat / 1000
data_locations.long = data_locations.long / 1000

data_activity_types = pd.read_excel(PATH_FILE, sheet_name='activity_type', header=0,
                                    dtype={'id': int, 'name': str, 'creator': str}, skiprows=range(1, 2))

data_activities = pd.read_excel(PATH_FILE, sheet_name='activity', header=0,
                                dtype={'id': int, 'name': str, 'description': str, 'activity_id': int,
                                       'source': str, 'save_path': str, 'creator': str}, skiprows=range(1, 3))

data_mappings = pd.read_excel(PATH_FILE, sheet_name='loc_act', header=0,
                              dtype={'id': int, 'act_id': int, 'loc_id': int, 'creator': str}, skiprows=range(1, 4))

wb = xlrd.open_workbook(PATH_FILE)
sheet_activity = wb.sheet_by_index(0)
sheet_activity_type = wb.sheet_by_index(1)
sheet_country = wb.sheet_by_index(2)
sheet_region = wb.sheet_by_index(3)
sheet_location = wb.sheet_by_index(4)

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

# check presence of all files, resp. validity of save_paths
for each_file in data_activities.save_path:
    if os.path.isfile('D:\Outdoor_Activities\\' + each_file):
        pass
    else:
        print('D:\Outdoor_Activities\\' + each_file + " not found")
        errors_found = True

countries = []
if not errors_found:
    print("yay")
    for idx in data_countries.index:
        countries.append(Country(data_countries.loc[0, "name"], data_countries.loc[0, "creator"]))
    #session.add_all(countries)
    #session.commit()

"""

regions = []
regions.add(Region('Region', 1, 'Admin'))
session.add_all(regions)
session.commit()

locations = []
locations.add(Location(45.0, 10.5, 'Location', 1, 'Admin'))
session.add_all(locations)
session.commit()

activity_types = []
activitty_types.add(ActivitytType('Type', 'Admin')
session.add_all(act)
session.commit()

activities = []
activities.add(Activity('Albsteig', '', 1, 'outdoor', 'file', 'Admin'))'
session.add_all(activities)
session.commit()

loc_act = []
loc_act.add(LocationActivity('act_id', 'loc_id', 'Admin'))
session.add_all(loc_act)
session.commit()

"""

