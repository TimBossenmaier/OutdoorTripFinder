# coding=utf-8

from backend.src.entities.activity import Activity, ActivitySchema, ActivityPresentationSchema
from backend.src.entities.activity_type import ActivityType
from backend.src.entities.country import Country
from backend.src.entities.location_type import LocationType
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

    curr_lat = 48.087
    curr_long = 9.203
    max_dist = 45


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
        if item["name"] not in activity_names:
            activity_names.add(item["name"])
            idx_to_keep.append(idx)

    act = [act[i] for i in idx_to_keep]
    activities = schema.dump(act)

    for i, act in zip(range(len(activities)), activities):
        act.update({'id': i})

    return jsonify(activities)

# ONLY FOR DEV PURPOSE #
@app.route('/get_by_id')
def get_by_id():
    activities = [
  {
    "activity_type": "Kanu",
    "country": "Deutschland",
    "description": "NaN",
    "distance": 2.0,
    "id": 0,
    "location": "Sigmaringen",
    "name": "Donau",
    "region": "Donautal",
    "save_path": "Europa\\Deutschland\\Donau.pdf",
    "source": "Outdoor 04 2020"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Das obere Donautal ist ein Paradies für Radler, Kletterer, Freizeit- oder Tourenpaddler, aber natürlich auch für Wanderer. Beeindruckend ist neben dem Donaudurchbruch zwischen Fridigen und Beuron (wurde im Vorjahr als Radtour vorgestellt) aber auch ein Kleinod in Inzigkofen, der von der Sigmaringer Fürstin Amalie Zephyrine (1760—1841) angelegte Inzigkofer Landschaftspark. ",
    "distance": 3.0,
    "id": 1,
    "location": "Inzigkofen",
    "name": "Amalien-Park",
    "region": "Donautal",
    "save_path": "Europa\\Deutschland\\Amalien_Park.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Das Donautal bei Beuron gehört zu den schönsten Wandergebieten unserer Region. Bizarre Felsen ragen an den Seiten des Tals in den Himmel, oben thronen Burgen in herrlichster Lage. Die Wildenstein-Tour führt zur gleichnamigen Burg, einer beliebten Jugendherberge, und zu drei benachbarten Felsen mit spektakulärer Aussicht. Der erste Abschnitt im Natur-Spielplatz macht vor allem Kindern Spaß.",
    "distance": 15.0,
    "id": 2,
    "location": "Leibertingen",
    "name": "Wildensteiner Felsen",
    "region": "Donautal",
    "save_path": "Europa\\Deutschland\\Wildensteiner_Felsen.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Das Donautal mit seinen wildromantischen Felsengärten und Steilhängen bietet unzählige Tourmöglichkeiten. Der Donauschleifen-Weg führt von Kloster Beuron über die Aussichtspunkte Rauher Stein und Eichfelsen vorbei am Imdorfer Felsengarten, der mit einzigartigen Pflanzen aufwartet. Uralte Steintunnel für Wanderer \nerwarten uns, das Infozentrum „Haus der Natur\" und natürlich die weithin bekannte Kirche des Benediktinerklosters Beuron.",
    "distance": 19.0,
    "id": 3,
    "location": "Beuron",
    "name": "Donauschleifen-Weg",
    "region": "Donautal",
    "save_path": "Europa\\Deutschland\\Donauschleifen_Weg.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Kultue, Natur und Genuss vereinen sich auf dieser Wanderung im Donautal. Sie verbindet landschaftliche und kulturelle Höhepunkte aus mehreren tausend Jahren zwischen Kloster Beuron und dem Jägerhaus.",
    "distance": 19.0,
    "id": 4,
    "location": "Beuron",
    "name": "Durch's Donautal",
    "region": "Donautal",
    "save_path": "Europa\\Deutschland\\Durchs_Donautal.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Der Große Trauben ist das zweitgrößte Moorgebiet in Südwestdeutschland und der größten Bannwald Baden-Württembergs. Entlang der Rundwanderung informieren Tafeln über das Ried, die Nutzung durch den Menschen und die heimische Tier- und Pflanzenwelt. ",
    "distance": 27.0,
    "id": 5,
    "location": "Riedhausen",
    "name": "Großer Trauben",
    "region": "Schwaben",
    "save_path": "Europa\\Deutschland\\Großer_Trauben.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Mit einer Reihe von erstklassig ausgeschilderten Wanderwegen unter dem Titel „Traufgänge\" (www.traufgaenge.de) präsentiert sich die Alb-Region rund um Albstadt als ein ausgezeichnetes Wandergebiet. Bei der vom Wandermagazin durchgeführten Wahl der schönsten deutschen Wanderwege kam der Zollernburg-Panoramaweg, der über die Albhochfläche und entlang des Albtraufs führt, im Jahr 2011 auf den 2. Platz. ",
    "distance": 27.0,
    "id": 6,
    "location": "Onstmettingen",
    "name": "Zollernburg-Panorama",
    "region": "Schwäbische Alp",
    "save_path": "Europa\\Deutschland\\Zollernburg_Panorama.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Der neue Premiumwanderweg im Donaubergland, die mittlerweise sechste \"Donauwelle\", erschließt due Wacholderheiden und Trockentäler rund um den Alten Berg. Schmale Wanderpfade durch Wald und Wiesen sorgen für viel Abwechslung. Wer bei schönem Wetter wander, kann vom Alten Berg bis zum Schwarzwald und zu den Alpen schauen.",
    "distance": 28.0,
    "id": 7,
    "location": "Mahlstetten",
    "name": "Alter Schäferweg",
    "region": "Schwäbische Alp",
    "save_path": "Europa\\Deutschland\\Alter_Schaeferweg.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Die Wanderung führt rund um Stockach und enthüllt viele Geheimnisse. Etwa, was es mit der „Stockemer Fasnet\" von 1351 und ihrem Erznarren Hans Kuony auf sich hat. Die Tour führt auch zu geheimnisvollen Höhlen im Sandstein bei Stockach-Zizenhausen. Und wir treffen auf einige der sage und schreibe 1000 Quellen, die um die Stadt sprudeln. Gutes Schuhwerk plus Taschenlampe sind für den Höhlen-Pfad ratsam.",
    "distance": 29.0,
    "id": 8,
    "location": "Bleiche",
    "name": "Heidenhöhen",
    "region": "Hegau",
    "save_path": "Europa\\Deutschland\\Heidenhoehen.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Die Wanderung führt durch die Wald- und Agrarlandschaften des Linzgaus zur herrlich gelegenen Wallfahrtskapelle Maria im Stein im Aachtobel. Der Anstieg nach Hohenbodman strengt an, belohnt aber mit prächtiger Fernsicht vom Burgturm.",
    "distance": 30.0,
    "id": 9,
    "location": "Hohenbodman",
    "name": "Hohenbodman",
    "region": "Bodensee",
    "save_path": "Europa\\Deutschland\\Hohenbodman.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Direkt oberhalb des Parkplatzes beim Aussichtsturm liegt der kleine Ort Hohenbodman, in dessen Zentrum sich die älteste Linde Deutschlands befindet. Abwechslungsreich geht es entlang der Seefelder Aach durch eines der ältesten Naturschutzgebiete Deutschlands. Am Ende des Tobels geht der Weg zwar wieder hinauf nach Hohenbodman, doch lohnt noch zuvor ein Abstecher an die Naturkapelle Maria Stein. ",
    "distance": 30.0,
    "id": 10,
    "location": "Hohenbodman",
    "name": "Aachtobel",
    "region": "Bodensee",
    "save_path": "Europa\\Deutschland\\Aachtobel.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Eine leichte Wanderung auf zumeist asphaltierten oder gekiesten Güterwegen oder Feld- und Forstwegen durch die Obstgartenlandschaft rund um Frickingen. Einzig im Aachtobel und Frickinger Tobel sind die Wege etwas steiler und schmäler. Abkürzungsmöglichkeit auf dem Apfelrundweg.",
    "distance": 30.0,
    "id": 11,
    "location": "Altheim (Frickingen)",
    "name": "Linzgauer Obsttour",
    "region": "Bodensee",
    "save_path": "Europa\\Deutschland\\Linzgauer_Obsttour.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Der „Krebsbachputzer\" ist einer von aktuell acht Premiumwanderwegen im „Hegauer Kegelspiel\". Die Tour folgt von der Lochmühle bei Eigeltingen dem Lauf des Krebsbaches, erst oberhalb am Talrand, dann entlang des munter plätschernden Baches durch dessen ursprüngliche Schlucht.",
    "distance": 32.0,
    "id": 12,
    "location": "Reute im Hegau",
    "name": "Krebsbachputzer",
    "region": "Bodensee",
    "save_path": "Europa\\Deutschland\\Krebsbachputzer.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Der Überlinger See ist einer der schönsten Abschnitte des Bodensees. Sein langgezogener Finger reicht bis nach Bodman-Ludwigshafen, dem Seeende. Rund um diesen Abschnitt schwingt sich im Bogen unsere Tour. Ganz stramme Wanderer schaffen die mehr als 30 Kilometer an einem Tag. Alle anderen können sich zwei Tage Zeit lassen, in Bodman oder Ludwigshafen nächtigen oder bequem mit dem Zug zum nächsten Start oder Ziel fahren.",
    "distance": 32.0,
    "id": 13,
    "location": "Bodman-Ludwigshafen",
    "name": "Seebogen-Weg",
    "region": "Bodensee",
    "save_path": "Europa\\Deutschland\\Seebogen_Weg.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Eine beeindruckende Panoramawanderung vorbei an Naturdenkmälern am Nordwestende des Bodensees.",
    "distance": 34.0,
    "id": 14,
    "location": "Sipplingen",
    "name": "Sipplinger Berg",
    "region": "Bodensee",
    "save_path": "Europa\\Deutschland\\Sipplinger_Berg.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Eine Rundtour an sieben Weihern und Teichen entlang führt ins Umland des Klosters Salem und nach Uhldingen-MühI-hofen am Bodensee. Die Gewässer liegen still und ruhig in Wäldern und auf Lichtungen. Es sind reine Paradiese für heimische Wasservögel. Tierisch viel los ist auch auf dem Affenberg Salem, an dem die Klosterweg-Wanderung vorbei führt. \nEin Teilstück der Route gehört zum bekannten Prälatenweg.",
    "distance": 37.0,
    "id": 15,
    "location": "Salem",
    "name": "Klosterweiher-Weg",
    "region": "Bodensee",
    "save_path": "Europa\\Deutschland\\Klosterweiher_Weg.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Rad fahren",
    "country": "Deutschland",
    "description": "Auf dieser abwechslungreichen und interessanten Tour erleben wir die Geschichte am Bodensee von der Steinzeit übers Mittelalter bis heute. Wir machen dabei einen Streifzug durch das von Wiesen, Wäldern und Seen geprägte Hinterland mit einem Besuch im Kloster Salem.",
    "distance": 37.0,
    "id": 16,
    "location": "Salem",
    "name": "Linzgau-Tour",
    "region": "Bodensee",
    "save_path": "Europa\\Deutschland\\Linzgau_Tour.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Im nördlichen Hegau, an der Grenze zur Baar-Landschaft, schlummert ein Kleinod: der frühere Vulkan Höwenegg. Der einst stolze Bergrücken wurde zur Basaltgewinnung abgebaut, füllte sich mit Wasser und bietet heute einen ungewöhnlichen Kratersee. Unsere Tour umrundet diesen türkis funkelnden \nSee, führt durch Naturschutzgebiete und durch das Umweltvorreiterdorf Mauenheim, Baden-Württembergs erstes Dorf, das ganz alleine seine Energie für Strom und Wärme erzeugt. ",
    "distance": 37.0,
    "id": 17,
    "location": "Hattingen (Immendingen)",
    "name": "Vulkansee-Weg",
    "region": "Hegau",
    "save_path": "Europa\\Deutschland\\Vulkansee_Weg.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Rad fahren",
    "country": "Deutschland",
    "description": "Ein Streifzug durch den Hegau mit herrlichem Blick auf die von Feuer und Eis geformten, alles überragenden Vulkanberge, durch geschützte Auen, Wiesen und Flusslandschaften sowie mit „steinigen\" Abstechern zu idyllisch gelegenen Zeitzeugen des Mittelalters.",
    "distance": 38.0,
    "id": 18,
    "location": "Aach",
    "name": "Hegau-Rundtour",
    "region": "Bodensee",
    "save_path": "Europa\\Deutschland\\Hegau_Rundtour.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Diese Rundwanderung verbindet die Radolfzeller Runden \"Mindelsee-Runde\", \" Bodanrück-Runde\", \"Muckeseckele-Runde\" und \"Mühlsberg-Runde\" zu einer Wander-Acht, die mitSchnittpunkt Liggeringen auch leicht auf zwei Wandertage verteilt werden kann.",
    "distance": 38.0,
    "id": 19,
    "location": "Liggeringen",
    "name": "Mindelsee",
    "region": "Bodensee",
    "save_path": "Europa\\Deutschland\\Mindelsee.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Die Marienschlucht zählt zu den populärsten Wanderzielen am Bodenseeufer. Erst vor kurzem wurde sie nach aufwändiger Sanierung wieder der Öffentlichkeit zugänglich gemacht. Nun kann man durch die enge, wildromantische Schlucht wieder vom Bodenseeufer hinauf zur Ruine Kargegg \nwandern.",
    "distance": 39.0,
    "id": 20,
    "location": "Wallhausen",
    "name": "Marienschlucht",
    "region": "Bodensee",
    "save_path": "Europa\\Deutschland\\Marienschlucht.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Diese Tour führt über die höchsten und markantesten Höhen des Hegaus und hat es daher, sowohl was die Distanz als auch was die zu absolvierenden Höhenmeter angeht, in sich, kann aber problemlos abgekürzt werden. Die Orientierung auf dieser Hegau-Tour ist unkompliziert, da man die Etappenziele fast ständig im Blick hat und da die Tour über weite Strecken dem Europäischen Fernwanderweg Nr. 1 (rot/weiße Raute) folgt. ",
    "distance": 42.0,
    "id": 21,
    "location": "Engen",
    "name": "Hegauhöhen",
    "region": "Bodensee",
    "save_path": "Europa\\Deutschland\\Hegauhoehen.pdf",
    "source": "Südkurier"
  },
  {
    "activity_type": "Wandern",
    "country": "Deutschland",
    "description": "Die recht lange und erlebnisreiche Wanderung von Singen über die Hegauburgen bis Engen kann Dank der seehas-Haltestellen Mühlhausen-Ehingen (auf halber Strecke) und Welschingen-Neuhausen abgekürzt oder auf zwei bequeme Wandertage aufgeteilt werden. Die Rückfahrt erfolgt mit dem seehas ab Bahnhof Engen.",
    "distance": 42.0,
    "id": 22,
    "location": "Engen",
    "name": "Vukan- und Burgen-Tour",
    "region": "Bodensee",
    "save_path": "Europa\\Deutschland\\Vulkan_Und_Burgen_Tour.pdf",
    "source": "Südkurier"
  }
]

    id = int(request.args.get('id'))

    for act in activities:
        if act['id'] == id:
            return act


app.config['JSON_AS_ASCII'] = False
app.run(debug=True, use_reloader=False, host='0.0.0.0')
