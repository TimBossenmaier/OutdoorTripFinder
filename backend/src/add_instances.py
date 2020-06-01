from backend.src.entities.activity_type import ActivityType
from backend.src.entities.activity import Activity
from backend.src.entities.country import Country
from backend.src.entities.location import Location
from backend.src.entities.location_activity import LocationActivity
from backend.src.entities.region import Region
from backend.src.entities.entity import Base, Session, engine
import pandas as pd
import os

Base.metadata.create_all(engine)
session = Session()

PATH_FILE = 'D:\Outdoor_Activities\import_table.xlsx'

data_countries = pd.read_excel(PATH_FILE, sheet_name="country", header=0,
                               dtype={'id': int, 'name': str, 'creator': str})

data_regions = pd.read_excel(PATH_FILE, sheet_name="region", header=0,
                             dtype={'id': int, 'name': str, 'country_id': int, 'creator': str})

data_locations = pd.read_excel(PATH_FILE, sheet_name='localisation', header=0,
                               dtype={'id': int, 'lat': float, 'long': float, 'name': str,
                                      'region_id': int, 'creator': str})
data_locations.lat = data_locations.lat / 1000
data_locations.long = data_locations.long / 1000

data_activity_types = pd.read_excel(PATH_FILE, sheet_name='activity_type', header=0,
                                     dtype={'id': int, 'name': str, 'creator': str})

data_activities = pd.read_excel(PATH_FILE, sheet_name='activity', header=0,
                              dtype={'id': int, 'name': str, 'description': str, 'activity_id': int,
                                     'source': str, 'save_path': str, 'creator': str})

data_mappings = pd.read_excel(PATH_FILE, sheet_name='loc_act', header=0,
                              dtype={'id': int, 'act_id': int, 'loc_id': int, 'creator': str})

errors_found = False
for each_file in data_activities.save_path:
    if os.path.isfile('D:\Outdoor_Activities\\' + each_file):
        errors_found = True
    else:
        print('D:\Outdoor_Activities\\' + each_file + " not found")

countries = []
if not errors_found:
    for idx, each_count in data_countries.iterrows():
        countries.append(Country(each_count.name, each_count.creator))

"""session.add_all(countries)
session.commit()

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

