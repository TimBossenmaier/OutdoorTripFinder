from backend.src.entities.activity_type import ActivityType
from backend.src.entities.activity import Activity
from backend.src.entities.country import Country
from backend.src.entities.location import Location
from backend.src.entities.location_activity import LocationActivity
from backend.src.entities.region import Region
from backend.src.entities.entity import Base, Session, engine
import pandas as pd

Base.metadata.create_all(engine)
session = Session()

data_countries = pd.read

"""
countries = []
countries.add(Country('Land', 'Admin'))
session.add_all(countries)
session.commit()

regions = []
regions.add(Region('Region', 1, 'Admin'))
session.add_all(regions)
session.commit()

locations = []
locations.add(Location(45.0, 10.5, 'Location', 1, 'Admin'))
session.add_all(locations)
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

