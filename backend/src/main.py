# coding=utf-8

from backend.src.entities.activity import Activity, ActivitySchema, ActivityPresentationSchema
from backend.src.entities.activity_type import ActivityType
from backend.src.entities.country import Country
from backend.src.entities.location import Location, LocationSchema
from backend.src.entities.location_activity import LocationActivity
from backend.src.entities.region import Region
from backend.src.entities.entity import Session, engine, Base
from backend.src.helpers import distance_between_coordinates, sort_by_dist
from flask import Flask, request, jsonify
from flask_cors import CORS


""" WRITE
Base.metadata.create_all(engine)
session = Session()

entity = LocationActivity(2, 3, "Admin")

session.add(entity)
session.commit()
"""
"""
records = session.query(Activity).join(ActivityType)\
                                  .join(LocationActivity)\
                                  .join(Location)\
                                  .all()
for record in records:

    recordObject = {'name': record.name,
                    'description': record.description,
                    'activity_type': record.activity_type.name,
                    'source': record.source,
                    'save_path': record.save_path,
                    'locations': []}
    for loc in record.locations:
        location = {'lat': loc.locations.lat}
        recordObject['locations'].append(location)
    print(recordObject)
"""

app = Flask(__name__)
CORS(app)
Base.metadata.create_all(engine)


@app.route('/test')
def test():
    return 'Test'


@app.route('/get_tour')
def get_tour():

    curr_lat = float(request.args.get('lat'))
    curr_long = float(request.args.get('long'))
    max_dist = float(request.args.get('dist'))

    session = Session()

    record_location = session.query(Location)\
                             .filter(Location.lat > curr_lat - 3 * max_dist / 100,
                                     Location.lat < curr_lat + 3 * max_dist / 100,
                                     Location.long > curr_long - 3 * max_dist / 100,
                                     Location.long < curr_long + 3 * max_dist / 100)\
                             .all()

    schema = LocationSchema(many=True, only=('name', 'lat', 'long', 'id'))
    locations = schema.dump(record_location)

    for i, loc in enumerate(locations):
        loc.update({"dist": distance_between_coordinates(loc["lat"], loc["long"], curr_lat, curr_long)})
    locations = [i for i in locations if i['dist'] < max_dist]
    locations.sort(key=sort_by_dist)
    ids = [int(i['id']) for i in locations]

    record_activities = session.query(Activity)\
                               .join(ActivityType)\
                               .join(LocationActivity)\
                               .join(Location).join(Region)\
                               .join(Country)\
                               .filter(Location.id.in_(ids))\
                               .all()

    schema = ActivityPresentationSchema(many=True)

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
                'distance': [x['dist'] for x in locations if x['id'] == loc.location_id] [0] if len([x['dist'] for x in locations if x['id'] == loc.location_id]) > 0 else 1000
            }
            act.append(activity_pres)
    act = sorted(act, key=lambda k: k['distance'])

    # keep only one entry per activity
    activity_names = set()
    idx_to_keep = []
    for idx, item in enumerate(act):
        print(idx)
        if item["name"] not in activity_names:
            activity_names.add(item["name"])
            idx_to_keep.append(idx)

    act = [act[i] for i in idx_to_keep]
    activities = schema.dump(act)
    if len(activities) > 0:
        return jsonify(activities)
    else:
        return "Sorry, no results available"


app.config['JSON_AS_ASCII'] = False
app.run(debug=True, use_reloader=False, host='0.0.0.0')
