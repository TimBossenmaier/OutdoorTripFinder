from flask import Blueprint


app_main = Blueprint('main', __name__)


def get_main_app():
    return app_main
