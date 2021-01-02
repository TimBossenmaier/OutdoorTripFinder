import os
import click
import unittest

from flask_cors import CORS
from app import create_app, db
from app.entities.user import User
from app.entities.role import Role
from app.entities.country import Country
from app.entities.region import Region
from app.entities.location_type import LocationType
from app.entities.location_activity import LocationActivity
from app.entities.location import Location
from app.entities.activity import Activity
from app.entities.activity_type import ActivityType
from app.entities.hike_relations import HikeRelation
from app.entities.comment import Comment

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Country=Country, Region=Region, LocationType=LocationType,
                LocationActivity=LocationActivity, Location=Location, Activity=Activity, ActivityType=ActivityType,
                HikeRelation=HikeRelation, Comment=Comment)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
