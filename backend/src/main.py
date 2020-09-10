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

# ONLY FOR DEV PURPOSE #
@app.route('/get_tour_demo')
def get_tour_demo():

    curr_lat = 47.996
    curr_long = 7.849
    max_dist = 25

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

    for i, act in zip(range(len(activities)),activities):
        act.update({'id': i})

    return jsonify(activities)

# ONLY FOR DEV PURPOSE #
@app.route('/get_by_id')
def get_by_id():
    activities = [
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Keine deutsche Stadt bekommt so viel Sonne ab wie Freiburg, und ringsum locken herrliche Wanderungen. ",
    "distance": 0.0,
    "id": 0,
    "location": "Freiburg im Breisgau",
    "name": "Auf der Wonnenseite",
    "region": "Schwarzwald",
    "save_path": "Europa\\Deutschland\\Auf_Der_Wonnenseite.pdf",
    "source": "Outdoor 05 2020"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Auf dem Zwei-Täler-Steig im Naturpark Südschwarzwald lernen Wanderer zwei Gesichter der Region kennen.",
    "distance": 14.0,
    "id": 1,
    "location": "Waldkirch",
    "name": "Zwei-Täler-Steig",
    "region": "Schwarzwald",
    "save_path": "Europa\\Deutschland\\Zwei_Taeler_Steig.pdf",
    "source": "Outdoor 04 2020"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Die Triberger Wasserfälle zählen zum Pflichtprogramm für Schwarzwaldtouristen. Wer jedoch idyllische Wasserfälle abseits des Tourismustrubels erleben möchte, der kann auf einer drei- bis vierstündigen, abwechslungsreichen Wanderung die Zweribach- und die Hirschbachfälle erkunden.",
    "distance": 19.0,
    "id": 2,
    "location": "Sankt Märgen",
    "name": "Zweribachfälle",
    "region": "Schwarzwald",
    "save_path": "Europa\\Deutschland\\Zweribachfaelle.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Rad fahren",
    "country": "Deutschland",
    "description": "Sportliche Tour, die gemütlich beginnt und uns am Titisee entlang in das idyllische Seebachtal führt. Auf gut ausgebauten Wegen fahren wir an schönen Aussichtspunkten vorbei zum Feldsee und von oben herab in das malerische Hinterzarten.",
    "distance": 22.0,
    "id": 3,
    "location": "Hinterzarten",
    "name": "Zwei Seen Tour",
    "region": "Schwarzwald",
    "save_path": "Europa\\Deutschland\\Zwei_Seen_Tour.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Der Albsteig ist nah am Wasser gebaut: Er folgt dem gleichnamigen Fluss auf gut 83 Kilometern von Albbruck am Hochrhein bis zur Quelle am Schwarzwaldkönig Feldberg (1493 m).",
    "distance": 23.0,
    "id": 4,
    "location": "Feldberg",
    "name": "Albsteig",
    "region": "Schwarzwald",
    "save_path": "Europa\\Deutschland\\Albsteig.pdf",
    "source": "Outdoor 04 2020"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Je nach Kondition der kleinen Wanderer kann die Kinder-Wanderung auf dem Wichtelweg am Feldberg mit der Gipfelrunde über Seebuck und Feldberg, einer zünftigen Einkehr in einer der Berghütten und einer Fahrt mit der modernen Seilbahn erweitert werden.",
    "distance": 23.0,
    "id": 5,
    "location": "Feldberg",
    "name": "Feldberg mit Kindern",
    "region": "Schwarzwald",
    "save_path": "Europa\\Deutschland\\Feldberg_Mit_Kindern.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Ein Klassiker in der Wanderregion Südschwarzwald ist sicherlich der Feldberg. Diese Tour führt zwar „nur\" auf den Vorgipfel Seebuck (ein Abstecher zum Hauptgipfel ist von dort ohne große Orientierungsprobleme machbar), dafür geht es davor um den Feldsee und zum Raimartihof. ",
    "distance": 23.0,
    "id": 6,
    "location": "Feldberg",
    "name": "Feldsee & Feldberg",
    "region": "Schwarzwald",
    "save_path": "Europa\\Deutschland\\Feldsee_Und_Feldberg.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Der Belchen ist zwar nicht der höchste Schwarzwaldgipfel, gilt aber nicht zuletzt wegen der Aussicht als schönster Wanderberg des Schwarzwaldes. Die Wanderung von Neuenweg aus verbindet die Gipfelwanderung mit dem Naturerlebnis am sagenumwobenen Nonnenmattweiher. Die Orientierung am Belchen ist relativ leicht: Der Ausschilderung mit der blauen Raute aufwärts folgen, nach der Gipfelrunde führt die rote Raute hinab zum Haldenhof. ",
    "distance": 23.0,
    "id": 7,
    "location": "Böllen",
    "name": "Belchen",
    "region": "Schwarzwald",
    "save_path": "Europa\\Deutschland\\Belchen.pdf",
    "source": "Südkurier"
  }
]

    id = int(request.args.get('id'))

    for act in activities:
        if act['id'] == id:
            return act


app.config['JSON_AS_ASCII'] = False
app.run(debug=True, use_reloader=False, host='0.0.0.0')
