from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

from app.main import main as main_blueprint
from app.auth import auth as auth_blueprint
from app.main.stats import stats as stats_blueprint
from app.main.create import crt as create_blueprint
from app.main.update import updt as update_blueprint
from app.main.find import find as find_blueprint
from app.main.list import lst as list_blueprint
from config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()


def create_app(config_name):

    load_dotenv('../.env')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    app.register_blueprint(main_blueprint, url_prefix='/main')
    app.register_blueprint(stats_blueprint, url_prefix='/main/stats')
    app.register_blueprint(create_blueprint, url_prefix='/main/create')
    app.register_blueprint(update_blueprint, url_prefix='/main/update')
    app.register_blueprint(list_blueprint, url_prefix='/main/list')
    app.register_blueprint(find_blueprint, url_prefix='/main/find')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    return app
